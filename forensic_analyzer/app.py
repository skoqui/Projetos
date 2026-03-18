#!/usr/bin/env python3
"""
=============================================================
  FORENSIC LOG ANALYZER - Analisador Forense de Logs
  Projeto de Horas Complementares - UNIP
  Curso: Segurança da Informação
=============================================================
"""

import os
import re
import json
from datetime import datetime
from collections import defaultdict, Counter
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "uploads"
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16MB max
ALLOWED_EXTENSIONS = {"log", "txt", "csv"}

# ─────────────────────────────────────────────────────────────
#  PADRÕES REGEX PARA ANÁLISE FORENSE
# ─────────────────────────────────────────────────────────────

PATTERNS = {
    # Apache / Nginx combined log format
    "web_log": re.compile(
        r'(?P<ip>[\d\.]+)\s.*\[(?P<datetime>[^\]]+)\]\s"(?P<method>\w+)\s(?P<path>\S+)\s\S+"\s(?P<status>\d{3})\s(?P<size>\d+|-)'
    ),
    # SSH / auth.log
    "ssh_failed": re.compile(
        r"(?P<datetime>\w+\s+\d+\s[\d:]+).*Failed password for (?:invalid user )?(?P<user>\S+) from (?P<ip>[\d\.]+)"
    ),
    "ssh_accepted": re.compile(
        r"(?P<datetime>\w+\s+\d+\s[\d:]+).*Accepted password for (?P<user>\S+) from (?P<ip>[\d\.]+)"
    ),
    "ssh_invalid_user": re.compile(
        r"(?P<datetime>\w+\s+\d+\s[\d:]+).*Invalid user (?P<user>\S+) from (?P<ip>[\d\.]+)"
    ),
    # Genérico: IPs em qualquer log
    "ip_generic": re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b"),
    # Timestamps genéricos ISO 8601
    "timestamp_iso": re.compile(r"\d{4}-\d{2}-\d{2}[T\s]\d{2}:\d{2}:\d{2}"),
    # Erros críticos
    "critical_errors": re.compile(
        r"(?i)(CRITICAL|EMERGENCY|ALERT|FATAL|ERROR|FAILURE|FAILED|DENIED|UNAUTHORIZED|FORBIDDEN|BREACH)"
    ),
    # SQL Injection básico
    "sql_injection": re.compile(
        r"(?i)(union\s+select|drop\s+table|insert\s+into|delete\s+from|exec\s*\(|xp_cmdshell|\'.*?or.*?\'|1=1|0x[0-9a-f]+)"
    ),
    # XSS básico
    "xss_attempt": re.compile(
        r"(?i)(<script|javascript:|on\w+=|alert\s*\(|document\.cookie|eval\s*\()"
    ),
    # Path traversal
    "path_traversal": re.compile(r"(\.\./|\.\.\\|%2e%2e%2f|%252e%252e%252f)"),
    # Scanning de portas / user-agents suspeitos
    "suspicious_ua": re.compile(
        r"(?i)(sqlmap|nikto|nmap|masscan|burpsuite|metasploit|nessus|openvas|dirbuster|gobuster|wfuzz)"
    ),
}

# ─────────────────────────────────────────────────────────────
#  MOTOR DE ANÁLISE FORENSE
# ─────────────────────────────────────────────────────────────


class ForensicAnalyzer:
    def __init__(self):
        self.reset()

    def reset(self):
        self.total_lines = 0
        self.events = []
        self.ip_counter = Counter()
        self.error_counter = Counter()
        self.timeline = []
        self.alerts = []
        self.status_codes = Counter()
        self.top_paths = Counter()
        self.failed_logins = defaultdict(int)
        self.brute_force_suspects = []
        self.attack_attempts = []

    def analyze(self, content):
        self.reset()
        lines = content.splitlines()
        self.total_lines = len(lines)

        for i, line in enumerate(lines):
            self._parse_line(line, i + 1)

        self._detect_brute_force()
        self._generate_summary()
        return self._build_report()

    def _parse_line(self, line, line_num):
        # Web log (Apache/Nginx)
        m = PATTERNS["web_log"].search(line)
        if m:
            ip = m.group("ip")
            status = m.group("status")
            path = m.group("path")
            self.ip_counter[ip] += 1
            self.status_codes[status] += 1
            self.top_paths[path] += 1

            severity = "info"
            event_type = "web_request"

            # Detecta ataques via path/query
            if PATTERNS["sql_injection"].search(path):
                self._add_alert(
                    "CRÍTICO",
                    f"Tentativa de SQL Injection da linha {line_num}",
                    ip,
                    line,
                )
                severity = "critical"
                event_type = "sql_injection"
            elif PATTERNS["xss_attempt"].search(path):
                self._add_alert(
                    "ALTO", f"Tentativa de XSS da linha {line_num}", ip, line
                )
                severity = "high"
                event_type = "xss_attempt"
            elif PATTERNS["path_traversal"].search(path):
                self._add_alert(
                    "ALTO", f"Path Traversal detectado na linha {line_num}", ip, line
                )
                severity = "high"
                event_type = "path_traversal"

            if PATTERNS["suspicious_ua"].search(line):
                self._add_alert(
                    "ALTO",
                    f"Ferramenta de ataque detectada na linha {line_num}",
                    ip,
                    line,
                )
                severity = "high"
                event_type = "scanner_tool"

            if status.startswith("4") or status.startswith("5"):
                severity = "warning" if severity == "info" else severity

            self.events.append(
                {
                    "line": line_num,
                    "type": event_type,
                    "ip": ip,
                    "status": status,
                    "path": path[:80],
                    "severity": severity,
                }
            )
            return

        # SSH falha
        m = PATTERNS["ssh_failed"].search(line)
        if m:
            ip = m.group("ip")
            user = m.group("user")
            self.failed_logins[ip] += 1
            self.ip_counter[ip] += 1
            self.events.append(
                {
                    "line": line_num,
                    "type": "ssh_failed_login",
                    "ip": ip,
                    "user": user,
                    "severity": "warning",
                }
            )
            return

        # SSH aceito
        m = PATTERNS["ssh_accepted"].search(line)
        if m:
            ip = m.group("ip")
            user = m.group("user")
            self.ip_counter[ip] += 1
            self.events.append(
                {
                    "line": line_num,
                    "type": "ssh_accepted",
                    "ip": ip,
                    "user": user,
                    "severity": "info",
                }
            )
            return

        # SSH usuário inválido
        m = PATTERNS["ssh_invalid_user"].search(line)
        if m:
            ip = m.group("ip")
            user = m.group("user")
            self.failed_logins[ip] += 1
            self.ip_counter[ip] += 1
            self.events.append(
                {
                    "line": line_num,
                    "type": "ssh_invalid_user",
                    "ip": ip,
                    "user": user,
                    "severity": "warning",
                }
            )
            return

        # Erros críticos genéricos
        m = PATTERNS["critical_errors"].search(line)
        if m:
            keyword = m.group(1).upper()
            self.error_counter[keyword] += 1
            ips = PATTERNS["ip_generic"].findall(line)
            self.events.append(
                {
                    "line": line_num,
                    "type": "critical_keyword",
                    "keyword": keyword,
                    "ip": ips[0] if ips else "N/A",
                    "severity": "warning",
                }
            )

        # IPs genéricos
        for ip in PATTERNS["ip_generic"].findall(line):
            self.ip_counter[ip] += 1

    def _detect_brute_force(self):
        """IPs com mais de 10 falhas de login = suspeito de brute force"""
        for ip, count in self.failed_logins.items():
            if count >= 5:
                self.brute_force_suspects.append({"ip": ip, "attempts": count})
                self._add_alert(
                    "CRÍTICO",
                    f"Possível Brute Force: {count} tentativas falhas de login do IP {ip}",
                    ip,
                    f"{count} tentativas de login falhadas",
                )

    def _add_alert(self, severity, message, ip, raw):
        self.alerts.append(
            {
                "severity": severity,
                "message": message,
                "ip": ip,
                "raw": raw[:120],
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
        )

    def _generate_summary(self):
        total_events = len(self.events)
        critical = sum(1 for e in self.events if e["severity"] == "critical")
        high = sum(1 for e in self.events if e["severity"] == "high")
        warnings = sum(1 for e in self.events if e["severity"] == "warning")

        self.summary = {
            "total_lines": self.total_lines,
            "total_events": total_events,
            "critical": critical,
            "high": high,
            "warnings": warnings,
            "unique_ips": len(self.ip_counter),
            "top_ips": self.ip_counter.most_common(10),
            "top_paths": self.top_paths.most_common(5),
            "status_codes": dict(self.status_codes.most_common(10)),
            "error_keywords": dict(self.error_counter.most_common(10)),
            "brute_force_suspects": self.brute_force_suspects,
            "alerts": self.alerts,
        }

    def _build_report(self):
        return {
            "summary": self.summary,
            "events": self.events[:200],  # Limita para performance no front
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }


analyzer = ForensicAnalyzer()

# ─────────────────────────────────────────────────────────────
#  ROTAS FLASK
# ─────────────────────────────────────────────────────────────


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/analyze", methods=["POST"])
def analyze():
    # Upload de arquivo
    if "file" in request.files and request.files["file"].filename:
        file = request.files["file"]
        if not allowed_file(file.filename):
            return (
                jsonify({"error": "Formato não permitido. Use .log, .txt ou .csv"}),
                400,
            )
        content = file.read().decode("utf-8", errors="ignore")

    # Texto colado diretamente
    elif "log_text" in request.form and request.form["log_text"].strip():
        content = request.form["log_text"]

    else:
        return jsonify({"error": "Nenhum log fornecido."}), 400

    if not content.strip():
        return jsonify({"error": "Arquivo vazio."}), 400

    report = analyzer.analyze(content)
    return jsonify(report)


@app.route("/demo")
def demo():
    """Gera um log de demonstração para apresentação"""
    demo_log = generate_demo_log()
    report = analyzer.analyze(demo_log)
    return jsonify(report)


def generate_demo_log():
    return """192.168.1.105 - - [15/Mar/2025:08:12:01 +0000] "GET /index.html HTTP/1.1" 200 1024
10.0.0.55 - - [15/Mar/2025:08:12:15 +0000] "POST /login HTTP/1.1" 401 512
10.0.0.55 - - [15/Mar/2025:08:12:16 +0000] "POST /login HTTP/1.1" 401 512
10.0.0.55 - - [15/Mar/2025:08:12:17 +0000] "POST /login HTTP/1.1" 401 512
10.0.0.55 - - [15/Mar/2025:08:12:18 +0000] "POST /login HTTP/1.1" 401 512
10.0.0.55 - - [15/Mar/2025:08:12:19 +0000] "POST /login HTTP/1.1" 401 512
10.0.0.55 - - [15/Mar/2025:08:12:20 +0000] "POST /login HTTP/1.1" 200 2048
45.33.32.156 - - [15/Mar/2025:08:15:00 +0000] "GET /admin/../../../etc/passwd HTTP/1.1" 403 256
45.33.32.156 - - [15/Mar/2025:08:15:03 +0000] "GET /page?id=1' UNION SELECT * FROM users-- HTTP/1.1" 500 128
45.33.32.156 - - [15/Mar/2025:08:15:10 +0000] "GET /search?q=<script>alert(document.cookie)</script> HTTP/1.1" 200 512
203.0.113.42 - - [15/Mar/2025:08:20:00 +0000] "GET /robots.txt HTTP/1.1" 200 64
203.0.113.42 - - [15/Mar/2025:08:20:01 +0000] "GET /wp-admin HTTP/1.1" 404 128
203.0.113.42 - - [15/Mar/2025:08:20:02 +0000] "GET /.env HTTP/1.1" 404 128
203.0.113.42 - - [15/Mar/2025:08:20:03 +0000] "GET /config.php HTTP/1.1" 404 128
192.168.1.200 - - [15/Mar/2025:09:00:00 +0000] "GET /dashboard HTTP/1.1" 200 4096
Mar 15 08:12:10 server sshd[1234]: Failed password for root from 10.0.0.55 port 22 ssh2
Mar 15 08:12:11 server sshd[1234]: Failed password for root from 10.0.0.55 port 22 ssh2
Mar 15 08:12:12 server sshd[1234]: Failed password for admin from 10.0.0.55 port 22 ssh2
Mar 15 08:12:13 server sshd[1234]: Failed password for admin from 10.0.0.55 port 22 ssh2
Mar 15 08:12:14 server sshd[1234]: Failed password for admin from 10.0.0.55 port 22 ssh2
Mar 15 08:12:15 server sshd[1234]: Invalid user oracle from 10.0.0.55 port 22
Mar 15 08:12:16 server sshd[1234]: Invalid user postgres from 10.0.0.55 port 22
Mar 15 09:05:00 server sshd[2000]: Accepted password for deploy from 192.168.1.200 port 22 ssh2
2025-03-15 10:00:00 CRITICAL authentication service crashed unexpectedly
2025-03-15 10:01:00 ERROR failed to connect to database from 192.168.1.100
2025-03-15 10:02:00 WARNING unauthorized access attempt detected from 45.33.32.156
78.46.60.71 - - [15/Mar/2025:11:00:00 +0000] "GET /vulnerabilities/sqli/?id=1 HTTP/1.1" 200 1024 "sqlmap/1.7"
"""


if __name__ == "__main__":
    os.makedirs("uploads", exist_ok=True)
    print("\n" + "=" * 60)
    print("  FORENSIC LOG ANALYZER - UNIP | Segurança da Informação")
    print("=" * 60)
    print("  Acesse: http://localhost:5000")
    print("=" * 60 + "\n")
    app.run(debug=True, host="0.0.0.0", port=5000)
