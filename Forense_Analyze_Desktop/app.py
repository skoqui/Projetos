#!/usr/bin/env python3
"""
=============================================================
  FORENSIC LOG ANALYZER — Desktop Edition
  Interface gráfica com Tkinter
  UNIP · Segurança da Informação · Horas Complementares
=============================================================
"""

import re
import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from collections import defaultdict, Counter
from datetime import datetime

# ─────────────────────────────────────────────────────────────
#  PADRÕES DE DETECÇÃO
# ─────────────────────────────────────────────────────────────

PATTERNS = {
    "web_log": re.compile(
        r'(?P<ip>[\d\.]+)\s.*\[(?P<datetime>[^\]]+)\]\s"(?P<method>\w+)\s(?P<path>\S+)\s\S+"\s(?P<status>\d{3})\s(?P<size>\d+|-)'
    ),
    "ssh_failed": re.compile(
        r"(?P<datetime>\w+\s+\d+\s[\d:]+).*Failed password for (?:invalid user )?(?P<user>\S+) from (?P<ip>[\d\.]+)"
    ),
    "ssh_accepted": re.compile(
        r"(?P<datetime>\w+\s+\d+\s[\d:]+).*Accepted password for (?P<user>\S+) from (?P<ip>[\d\.]+)"
    ),
    "ssh_invalid_user": re.compile(
        r"(?P<datetime>\w+\s+\d+\s[\d:]+).*Invalid user (?P<user>\S+) from (?P<ip>[\d\.]+)"
    ),
    "ip_generic": re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b"),
    "critical_errors": re.compile(
        r"(?i)(CRITICAL|EMERGENCY|ALERT|FATAL|ERROR|FAILURE|FAILED|DENIED|UNAUTHORIZED|FORBIDDEN|BREACH)"
    ),
    "sql_injection": re.compile(
        r"(?i)(union\s+select|drop\s+table|insert\s+into|delete\s+from|exec\s*\(|xp_cmdshell|\'.*?or.*?\'|1=1|0x[0-9a-f]+)"
    ),
    "xss_attempt": re.compile(
        r"(?i)(<script|javascript:|on\w+=|alert\s*\(|document\.cookie|eval\s*\()"
    ),
    "path_traversal": re.compile(r"(\.\./|\.\.\\|%2e%2e%2f|%252e%252e%252f)"),
    "suspicious_ua": re.compile(
        r"(?i)(sqlmap|nikto|nmap|masscan|burpsuite|metasploit|nessus|openvas|dirbuster|gobuster|wfuzz)"
    ),
}

# ─────────────────────────────────────────────────────────────
#  MOTOR FORENSE
# ─────────────────────────────────────────────────────────────


class ForensicAnalyzer:
    def __init__(self):
        self.reset()

    def reset(self):
        self.total_lines = 0
        self.events = []
        self.ip_counter = Counter()
        self.error_counter = Counter()
        self.alerts = []
        self.status_codes = Counter()
        self.top_paths = Counter()
        self.failed_logins = defaultdict(int)
        self.brute_force_suspects = []

    def analyze(self, content):
        self.reset()
        lines = content.splitlines()
        self.total_lines = len(lines)
        for i, line in enumerate(lines):
            self._parse_line(line, i + 1)
        self._detect_brute_force()
        return self._build_report()

    def _parse_line(self, line, line_num):
        m = PATTERNS["web_log"].search(line)
        if m:
            ip = m.group("ip")
            status = m.group("status")
            path = m.group("path")
            self.ip_counter[ip] += 1
            self.status_codes[status] += 1
            self.top_paths[path] += 1
            severity = "INFO"
            event_type = "Requisição Web"

            if PATTERNS["sql_injection"].search(path):
                self._add_alert(
                    "CRÍTICO", f"SQL Injection detectado (linha {line_num})", ip, line
                )
                severity = "CRÍTICO"
                event_type = "SQL Injection"
            elif PATTERNS["xss_attempt"].search(path):
                self._add_alert(
                    "ALTO", f"Tentativa de XSS (linha {line_num})", ip, line
                )
                severity = "ALTO"
                event_type = "XSS"
            elif PATTERNS["path_traversal"].search(path):
                self._add_alert(
                    "ALTO", f"Path Traversal detectado (linha {line_num})", ip, line
                )
                severity = "ALTO"
                event_type = "Path Traversal"

            if PATTERNS["suspicious_ua"].search(line):
                self._add_alert(
                    "ALTO",
                    f"Scanner/ferramenta de ataque detectado (linha {line_num})",
                    ip,
                    line,
                )
                severity = "ALTO"
                event_type = "Scanner"

            if status.startswith("4") or status.startswith("5"):
                if severity == "INFO":
                    severity = "ATENÇÃO"

            self.events.append((line_num, severity, event_type, ip, path[:60]))
            return

        m = PATTERNS["ssh_failed"].search(line)
        if m:
            ip = m.group("ip")
            user = m.group("user")
            self.failed_logins[ip] += 1
            self.ip_counter[ip] += 1
            self.events.append(
                (line_num, "ATENÇÃO", "SSH Falha Login", ip, f"user: {user}")
            )
            return

        m = PATTERNS["ssh_accepted"].search(line)
        if m:
            ip = m.group("ip")
            user = m.group("user")
            self.ip_counter[ip] += 1
            self.events.append((line_num, "INFO", "SSH Login OK", ip, f"user: {user}"))
            return

        m = PATTERNS["ssh_invalid_user"].search(line)
        if m:
            ip = m.group("ip")
            user = m.group("user")
            self.failed_logins[ip] += 1
            self.ip_counter[ip] += 1
            self.events.append(
                (line_num, "ATENÇÃO", "SSH Usuário Inválido", ip, f"user: {user}")
            )
            return

        m = PATTERNS["critical_errors"].search(line)
        if m:
            keyword = m.group(1).upper()
            self.error_counter[keyword] += 1
            ips = PATTERNS["ip_generic"].findall(line)
            ip = ips[0] if ips else "N/A"
            self.events.append(
                (line_num, "ATENÇÃO", f"Palavra-chave: {keyword}", ip, line[:60])
            )

        for ip in PATTERNS["ip_generic"].findall(line):
            self.ip_counter[ip] += 1

    def _detect_brute_force(self):
        for ip, count in self.failed_logins.items():
            if count >= 5:
                self.brute_force_suspects.append((ip, count))
                self._add_alert(
                    "CRÍTICO",
                    f"Brute Force: {count} tentativas falhadas do IP {ip}",
                    ip,
                    "",
                )

    def _add_alert(self, severity, message, ip, raw):
        self.alerts.append(
            {
                "severity": severity,
                "message": message,
                "ip": ip,
                "raw": raw[:100],
                "time": datetime.now().strftime("%H:%M:%S"),
            }
        )

    def _build_report(self):
        critical = sum(1 for e in self.events if e[1] == "CRÍTICO")
        high = sum(1 for e in self.events if e[1] == "ALTO")
        warnings = sum(1 for e in self.events if e[1] == "ATENÇÃO")
        return {
            "total_lines": self.total_lines,
            "total_events": len(self.events),
            "critical": critical,
            "high": high,
            "warnings": warnings,
            "unique_ips": len(self.ip_counter),
            "top_ips": self.ip_counter.most_common(10),
            "status_codes": dict(self.status_codes.most_common()),
            "alerts": self.alerts,
            "events": self.events,
            "brute_force": self.brute_force_suspects,
            "errors": dict(self.error_counter.most_common()),
        }


# ─────────────────────────────────────────────────────────────
#  INTERFACE GRÁFICA — TKINTER
# ─────────────────────────────────────────────────────────────

BG = "#0d1117"
BG2 = "#161b22"
BG3 = "#21262d"
BORDER = "#30363d"
GREEN = "#3fb950"
CYAN = "#58a6ff"
RED = "#f85149"
ORANGE = "#d29922"
YELLOW = "#e3b341"
WHITE = "#e6edf3"
MUTED = "#8b949e"
FONT_MONO = ("Consolas", 10)
FONT_UI = ("Segoe UI", 10)
FONT_BIG = ("Segoe UI", 11, "bold")
FONT_H = ("Segoe UI", 13, "bold")

SEV_COLORS = {
    "CRÍTICO": RED,
    "ALTO": ORANGE,
    "ATENÇÃO": YELLOW,
    "INFO": CYAN,
}


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Forensic Log Analyzer  ·  UNIP Segurança da Informação")
        self.geometry("1100x720")
        self.minsize(900, 600)
        self.configure(bg=BG)
        self.analyzer = ForensicAnalyzer()
        self.report = None
        self._build_ui()

    # ── BUILD UI ──────────────────────────────────────────────

    def _build_ui(self):
        self._style()
        self._header()
        self._toolbar()
        self._stat_bar()
        self._notebook()
        self._statusbar()

    def _style(self):
        s = ttk.Style(self)
        s.theme_use("clam")

        s.configure(".", background=BG, foreground=WHITE, font=FONT_UI)
        s.configure("TFrame", background=BG)
        s.configure("TLabel", background=BG, foreground=WHITE, font=FONT_UI)
        s.configure(
            "TButton",
            background=BG3,
            foreground=WHITE,
            font=FONT_UI,
            padding=6,
            relief="flat",
        )
        s.map("TButton", background=[("active", BORDER)])
        s.configure(
            "Accent.TButton",
            background=CYAN,
            foreground=BG,
            font=FONT_BIG,
            padding=8,
            relief="flat",
        )
        s.map("Accent.TButton", background=[("active", "#79c0ff")])
        s.configure("TNotebook", background=BG, borderwidth=0)
        s.configure(
            "TNotebook.Tab",
            background=BG2,
            foreground=MUTED,
            padding=(14, 6),
            font=FONT_UI,
        )
        s.map(
            "TNotebook.Tab",
            background=[("selected", BG3)],
            foreground=[("selected", WHITE)],
        )
        s.configure(
            "Treeview",
            background=BG2,
            foreground=WHITE,
            fieldbackground=BG2,
            rowheight=24,
            font=FONT_MONO,
            borderwidth=0,
        )
        s.configure(
            "Treeview.Heading",
            background=BG3,
            foreground=MUTED,
            font=("Segoe UI", 9, "bold"),
            relief="flat",
        )
        s.map("Treeview", background=[("selected", "#1f6feb")])
        s.configure("TSeparator", background=BORDER)
        s.configure(
            "TScrollbar",
            background=BG3,
            troughcolor=BG2,
            borderwidth=0,
            arrowcolor=MUTED,
        )

    def _header(self):
        h = tk.Frame(self, bg=BG2, height=56)
        h.pack(fill="x")
        h.pack_propagate(False)
        tk.Label(h, text="🔍", bg=BG2, font=("Segoe UI", 20)).pack(
            side="left", padx=(16, 8), pady=8
        )
        lf = tk.Frame(h, bg=BG2)
        lf.pack(side="left", pady=6)
        tk.Label(
            lf,
            text="Forensic Log Analyzer",
            bg=BG2,
            fg=CYAN,
            font=("Segoe UI", 13, "bold"),
        ).pack(anchor="w")
        tk.Label(
            lf,
            text="UNIP · Segurança da Informação · Horas Complementares",
            bg=BG2,
            fg=MUTED,
            font=("Segoe UI", 8),
        ).pack(anchor="w")
        self._dot = tk.Label(
            h, text="● AGUARDANDO", bg=BG2, fg=MUTED, font=("Consolas", 9)
        )
        self._dot.pack(side="right", padx=16)

    def _toolbar(self):
        tb = tk.Frame(self, bg=BG, pady=8)
        tb.pack(fill="x", padx=16)
        ttk.Button(
            tb,
            text="📂  Abrir Arquivo de Log",
            style="Accent.TButton",
            command=self.open_file,
        ).pack(side="left", padx=(0, 8))
        ttk.Button(tb, text="▶  Carregar Demo", command=self.load_demo).pack(
            side="left", padx=(0, 8)
        )
        ttk.Button(
            tb, text="💾  Exportar Relatório .txt", command=self.export_report
        ).pack(side="left", padx=(0, 8))
        ttk.Button(tb, text="🗑  Limpar", command=self.clear).pack(side="left")
        self._file_lbl = tk.Label(
            tb, text="Nenhum arquivo carregado", bg=BG, fg=MUTED, font=("Segoe UI", 9)
        )
        self._file_lbl.pack(side="right")

    def _stat_bar(self):
        sb = tk.Frame(self, bg=BG, pady=4)
        sb.pack(fill="x", padx=16)
        self._stats = {}
        items = [
            ("total_lines", "Linhas", WHITE),
            ("total_events", "Eventos", CYAN),
            ("critical", "Críticos", RED),
            ("high", "Alto Risco", ORANGE),
            ("warnings", "Alertas", YELLOW),
            ("unique_ips", "IPs Únicos", GREEN),
        ]
        for key, label, color in items:
            card = tk.Frame(sb, bg=BG2, padx=16, pady=8, relief="flat")
            card.pack(side="left", padx=(0, 8))
            val = tk.Label(
                card, text="—", bg=BG2, fg=color, font=("Consolas", 18, "bold")
            )
            val.pack()
            tk.Label(card, text=label, bg=BG2, fg=MUTED, font=("Segoe UI", 8)).pack()
            self._stats[key] = val

    def _notebook(self):
        self._nb = ttk.Notebook(self)
        self._nb.pack(fill="both", expand=True, padx=16, pady=(8, 0))
        self._tab_alerts()
        self._tab_events()
        self._tab_ips()
        self._tab_raw()

    def _tab_alerts(self):
        f = ttk.Frame(self._nb)
        self._nb.add(f, text="  🚨 Alertas  ")
        self._alert_tree = self._make_tree(
            f, ("Severidade", "Mensagem", "IP", "Trecho"), (90, 380, 130, 300)
        )

    def _tab_events(self):
        f = ttk.Frame(self._nb)
        self._nb.add(f, text="  📋 Eventos  ")
        self._event_tree = self._make_tree(
            f, ("Linha", "Severidade", "Tipo", "IP", "Detalhe"), (60, 90, 160, 130, 400)
        )

    def _tab_ips(self):
        f = ttk.Frame(self._nb)
        self._nb.add(f, text="  🌐 IPs  ")
        self._ip_tree = self._make_tree(
            f, ("IP", "Requisições", "Observação"), (160, 120, 300)
        )

    def _tab_raw(self):
        f = ttk.Frame(self._nb)
        self._nb.add(f, text="  📄 Log Bruto  ")
        self._raw_text = scrolledtext.ScrolledText(
            f,
            bg=BG2,
            fg=WHITE,
            font=("Consolas", 9),
            insertbackground=WHITE,
            relief="flat",
            borderwidth=0,
        )
        self._raw_text.pack(fill="both", expand=True)
        self._raw_text.insert(
            "end", "Abra um arquivo de log para visualizar o conteúdo aqui."
        )
        self._raw_text.configure(state="disabled")

    def _statusbar(self):
        sb = tk.Frame(self, bg=BG2, height=24)
        sb.pack(fill="x", side="bottom")
        sb.pack_propagate(False)
        self._status_lbl = tk.Label(
            sb,
            text="Pronto. Abra um arquivo de log para iniciar a análise.",
            bg=BG2,
            fg=MUTED,
            font=("Segoe UI", 8),
        )
        self._status_lbl.pack(side="left", padx=12)
        tk.Label(
            sb,
            text="Forensic Log Analyzer v2.0  ·  UNIP SI",
            bg=BG2,
            fg=MUTED,
            font=("Segoe UI", 8),
        ).pack(side="right", padx=12)

    def _make_tree(self, parent, cols, widths):
        frame = tk.Frame(parent, bg=BG)
        frame.pack(fill="both", expand=True)
        vsb = ttk.Scrollbar(frame, orient="vertical")
        hsb = ttk.Scrollbar(frame, orient="horizontal")
        tree = ttk.Treeview(
            frame,
            columns=cols,
            show="headings",
            yscrollcommand=vsb.set,
            xscrollcommand=hsb.set,
        )
        vsb.configure(command=tree.yview)
        hsb.configure(command=tree.xview)
        vsb.pack(side="right", fill="y")
        hsb.pack(side="bottom", fill="x")
        tree.pack(fill="both", expand=True)
        for col, w in zip(cols, widths):
            tree.heading(col, text=col)
            tree.column(col, width=w, minwidth=40)
        # Row tags
        tree.tag_configure("CRÍTICO", foreground=RED)
        tree.tag_configure("ALTO", foreground=ORANGE)
        tree.tag_configure("ATENÇÃO", foreground=YELLOW)
        tree.tag_configure("INFO", foreground=CYAN)
        tree.tag_configure("bf", foreground=RED, font=("Consolas", 10, "bold"))
        return tree

    # ── AÇÕES ─────────────────────────────────────────────────

    def open_file(self):
        path = filedialog.askopenfilename(
            title="Selecionar arquivo de log",
            filetypes=[("Arquivos de Log", "*.log *.txt *.csv"), ("Todos", "*.*")],
        )
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            self._file_lbl.config(text=os.path.basename(path))
            self._run_analysis(content)
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível ler o arquivo:\n{e}")

    def load_demo(self):
        self._file_lbl.config(text="[DEMO] log_contaminado.log")
        self._run_analysis(DEMO_LOG)

    def clear(self):
        for tree in (self._alert_tree, self._event_tree, self._ip_tree):
            tree.delete(*tree.get_children())
        self._raw_text.configure(state="normal")
        self._raw_text.delete("1.0", "end")
        self._raw_text.insert(
            "end", "Abra um arquivo de log para visualizar o conteúdo aqui."
        )
        self._raw_text.configure(state="disabled")
        for v in self._stats.values():
            v.config(text="—")
        self._dot.config(text="● AGUARDANDO", fg=MUTED)
        self._file_lbl.config(text="Nenhum arquivo carregado")
        self._status("Tela limpa. Pronto para nova análise.")
        self.report = None

    def export_report(self):
        if not self.report:
            messagebox.showwarning("Aviso", "Nenhuma análise realizada ainda.")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Arquivo de Texto", "*.txt")],
            initialfile=f'relatorio_forense_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt',
        )
        if not path:
            return
        r = self.report
        lines = [
            "=" * 60,
            "  FORENSIC LOG ANALYZER — RELATÓRIO FORENSE",
            f'  Gerado em: {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}',
            "=" * 60,
            "",
            "── RESUMO ──────────────────────────────────────────────",
            f'  Total de linhas analisadas : {r["total_lines"]}',
            f'  Total de eventos           : {r["total_events"]}',
            f'  Eventos CRÍTICOS           : {r["critical"]}',
            f'  Eventos ALTO RISCO         : {r["high"]}',
            f'  Alertas                    : {r["warnings"]}',
            f'  IPs únicos detectados      : {r["unique_ips"]}',
            "",
            "── ALERTAS DE SEGURANÇA ────────────────────────────────",
        ]
        if r["alerts"]:
            for a in r["alerts"]:
                lines.append(f'  [{a["severity"]}] {a["message"]}')
                lines.append(f'         IP: {a["ip"]}')
                if a["raw"]:
                    lines.append(f'         >> {a["raw"]}')
        else:
            lines.append("  Nenhum alerta detectado.")

        lines += ["", "── TOP IPs ─────────────────────────────────────────────"]
        for ip, cnt in r["top_ips"]:
            bf = " ⚠ BRUTE FORCE" if any(b[0] == ip for b in r["brute_force"]) else ""
            lines.append(f"  {ip:<20} {cnt} requisições{bf}")

        lines += ["", "── CÓDIGOS HTTP ────────────────────────────────────────"]
        for code, cnt in r["status_codes"].items():
            lines.append(f"  HTTP {code} : {cnt}x")

        lines += ["", "── EVENTOS DETECTADOS ──────────────────────────────────"]
        for ev in r["events"]:
            lines.append(
                f"  Linha {ev[0]:<5} [{ev[1]:<8}] {ev[2]:<25} IP: {ev[3]:<18} {ev[4]}"
            )

        lines += ["", "=" * 60, "  FIN DO RELATÓRIO", "=" * 60]

        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        messagebox.showinfo("Exportado", f"Relatório salvo em:\n{path}")

    def _run_analysis(self, content):
        self._status("Analisando...")
        self.update_idletasks()
        self.report = self.analyzer.analyze(content)
        self._render(content)

    def _render(self, raw_content):
        r = self.report

        # Stats
        for key in (
            "total_lines",
            "total_events",
            "critical",
            "high",
            "warnings",
            "unique_ips",
        ):
            self._stats[key].config(text=str(r[key]))

        # Dot
        if r["critical"] > 0:
            self._dot.config(text="● AMEAÇAS DETECTADAS", fg=RED)
        elif r["high"] > 0:
            self._dot.config(text="● RISCO ALTO", fg=ORANGE)
        else:
            self._dot.config(text="● ANÁLISE OK", fg=GREEN)

        # Alerts tab
        self._alert_tree.delete(*self._alert_tree.get_children())
        for a in r["alerts"]:
            self._alert_tree.insert(
                "",
                "end",
                values=(a["severity"], a["message"], a["ip"], a["raw"]),
                tags=(a["severity"],),
            )

        # Events tab
        self._event_tree.delete(*self._event_tree.get_children())
        for ev in r["events"]:
            self._event_tree.insert("", "end", values=ev, tags=(ev[1],))

        # IPs tab
        self._ip_tree.delete(*self._ip_tree.get_children())
        bf_ips = {b[0]: b[1] for b in r["brute_force"]}
        for ip, cnt in r["top_ips"]:
            obs = f"⚠ BRUTE FORCE ({bf_ips[ip]} tentativas)" if ip in bf_ips else ""
            tag = "bf" if ip in bf_ips else "INFO"
            self._ip_tree.insert("", "end", values=(ip, cnt, obs), tags=(tag,))

        # Raw log
        self._raw_text.configure(state="normal")
        self._raw_text.delete("1.0", "end")
        self._raw_text.insert("end", raw_content)
        self._raw_text.configure(state="disabled")

        total = r["total_lines"]
        alerts = len(r["alerts"])
        self._status(
            f'Análise concluída — {total} linhas · {alerts} alertas gerados · {r["unique_ips"]} IPs únicos'
        )
        self._nb.select(0)  # Vai para aba de alertas

    def _status(self, msg):
        self._status_lbl.config(text=msg)
        self.update_idletasks()


# ─────────────────────────────────────────────────────────────
#  LOG DE DEMONSTRAÇÃO
# ─────────────────────────────────────────────────────────────

DEMO_LOG = """192.168.1.10 - - [15/Mar/2025:08:00:01 +0000] "GET /index.html HTTP/1.1" 200 4096
192.168.1.15 - - [15/Mar/2025:08:01:00 +0000] "GET /produtos HTTP/1.1" 200 8192
185.220.101.45 - - [15/Mar/2025:08:15:00 +0000] "POST /login HTTP/1.1" 401 256
185.220.101.45 - - [15/Mar/2025:08:15:01 +0000] "POST /login HTTP/1.1" 401 256
185.220.101.45 - - [15/Mar/2025:08:15:02 +0000] "POST /login HTTP/1.1" 401 256
185.220.101.45 - - [15/Mar/2025:08:15:03 +0000] "POST /login HTTP/1.1" 401 256
185.220.101.45 - - [15/Mar/2025:08:15:04 +0000] "POST /login HTTP/1.1" 401 256
185.220.101.45 - - [15/Mar/2025:08:15:05 +0000] "POST /login HTTP/1.1" 401 256
185.220.101.45 - - [15/Mar/2025:08:15:06 +0000] "POST /login HTTP/1.1" 200 2048
45.33.32.156 - - [15/Mar/2025:08:20:10 +0000] "GET /produto?id=1' OR '1'='1 HTTP/1.1" 200 4096
45.33.32.156 - - [15/Mar/2025:08:20:15 +0000] "GET /busca?q=1' UNION SELECT username,password FROM users-- HTTP/1.1" 500 256
45.33.32.156 - - [15/Mar/2025:08:20:25 +0000] "GET /admin?id=1; DROP TABLE usuarios-- HTTP/1.1" 403 128
203.0.113.99 - - [15/Mar/2025:08:30:00 +0000] "GET /comentario?texto=<script>alert(1)</script> HTTP/1.1" 200 512
203.0.113.99 - - [15/Mar/2025:08:30:05 +0000] "GET /perfil?nome=<script>document.cookie</script> HTTP/1.1" 200 512
91.108.4.200 - - [15/Mar/2025:08:40:00 +0000] "GET /../../../etc/passwd HTTP/1.1" 403 256
91.108.4.200 - - [15/Mar/2025:08:40:10 +0000] "GET /static/%2e%2e%2f%2e%2e%2fetc%2fpasswd HTTP/1.1" 400 128
Mar 15 08:10:01 srv01 sshd[4421]: Failed password for root from 10.0.0.77 port 52341 ssh2
Mar 15 08:10:02 srv01 sshd[4422]: Failed password for root from 10.0.0.77 port 52342 ssh2
Mar 15 08:10:03 srv01 sshd[4423]: Failed password for admin from 10.0.0.77 port 52343 ssh2
Mar 15 08:10:04 srv01 sshd[4424]: Failed password for admin from 10.0.0.77 port 52344 ssh2
Mar 15 08:10:05 srv01 sshd[4425]: Invalid user oracle from 10.0.0.77 port 52345
Mar 15 08:10:06 srv01 sshd[4426]: Invalid user postgres from 10.0.0.77 port 52346
Mar 15 08:10:07 srv01 sshd[4427]: Invalid user ubuntu from 10.0.0.77 port 52347
Mar 15 08:10:10 srv01 sshd[4430]: Accepted password for deploy from 192.168.1.50 port 22 ssh2
78.46.60.71 - - [15/Mar/2025:09:00:00 +0000] "GET / HTTP/1.1" 200 4096 "-" "sqlmap/1.7.8"
198.51.100.5 - - [15/Mar/2025:09:05:00 +0000] "GET / HTTP/1.1" 200 4096 "-" "Nikto/2.1.6"
2025-03-15 09:20:00 CRITICAL Authentication service crashed
2025-03-15 09:20:15 WARNING Unauthorized access attempt from 45.33.32.156
2025-03-15 09:25:10 CRITICAL Root login via SSH detected from 185.220.101.45
"""


# ─────────────────────────────────────────────────────────────
#  MAIN
# ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app = App()
    app.mainloop()
