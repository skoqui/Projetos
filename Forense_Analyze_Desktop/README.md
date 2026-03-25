<div align="center">

# 🔍 Forensic Log Analyzer — Desktop Edition

**Analisador Forense de Logs · Software Desktop com Interface Gráfica**

![Python](/Forense_Analyze_Desktop/Imagens/capa.png)
![Tkinter](/Forense_Analyze_Desktop/Imagens/demonstração.png)


*Projeto de Horas Complementares — Segurança da Informação · UNIP*


</div>

---

## 📌 O que é

Software desktop de **análise forense de logs** com interface gráfica (GUI) desenvolvido em Python puro com Tkinter. Analisa arquivos de log reais (Apache, Nginx, SSH, Syslog) e detecta automaticamente ataques e comportamentos suspeitos, gerando um relatório visual com alertas classificados por severidade.

Não requer instalação de dependências externas — pode ser distribuído como um único arquivo `.exe` portátil via PyInstaller.

---

## ⚡ Funcionalidades

| Detecção | Descrição |
|---|---|
| 🔐 **Brute Force** | IPs com 5+ tentativas de login falhadas (SSH e web) |
| 💉 **SQL Injection** | `UNION SELECT`, `DROP TABLE`, `1=1`, `xp_cmdshell`, etc. |
| 🕷️ **XSS** | `<script>`, `document.cookie`, `eval()`, `onerror=` |
| 📂 **Path Traversal** | `../../etc/passwd`, `%2e%2e%2f`, etc. |
| 🤖 **Scanner Tools** | sqlmap, nikto, gobuster, nmap, metasploit, burpsuite |
| ⚠️ **Erros Críticos** | `CRITICAL`, `FATAL`, `ALERT`, `UNAUTHORIZED`, `BREACH` |
| 🌐 **Status HTTP** | Classificação de códigos 2xx / 3xx / 4xx / 5xx |
| 📊 **Top IPs** | Ranking dos IPs com mais requisições |

---

## 🖥️ Interface

Software com tema escuro estilo terminal, organizado em abas:

- **🚨 Alertas** — Lista todos os alertas com severidade `CRÍTICO`, `ALTO`, `ATENÇÃO`
- **📋 Eventos** — Tabela completa com cada evento detectado linha a linha
- **🌐 IPs** — Ranking de IPs suspeitos com destaque para Brute Force
- **📄 Log Bruto** — Visualização do arquivo original carregado

Painel superior com cards de resumo mostrando contagem por severidade e indicador de status em tempo real.

---

## 🚀 Como usar

### Opção 1 — Rodar direto com Python

```bash
# Não precisa instalar nada além do Python
python app.py
```

### Opção 2 — Gerar executável .exe (Windows)

```bash
# Instalar PyInstaller
pip install pyinstaller

# Gerar o .exe
pyinstaller --onefile --windowed --name "ForensicLogAnalyzer" app.py

# O executável estará em:
# dist/ForensicLogAnalyzer.exe
```

> O `.exe` gerado roda em qualquer Windows com dois cliques, sem precisar instalar Python.

---

## 📂 Estrutura

```
forensic-desktop/
├── app.py                  # Código completo (motor forense + GUI)
├── COMO_GERAR_EXE.txt      # Instruções para gerar o .exe
└── README.md               # Esta documentação
```

---

## 🧪 Testando com log real no Linux (Ubuntu)

```bash
# Log de autenticação SSH
sudo tail -300 /var/log/auth.log > meu_auth.log

# Log do Apache
sudo tail -500 /var/log/apache2/access.log > meu_apache.log
```

Abra o arquivo gerado pelo botão **"Abrir Arquivo de Log"** na interface.

---

## 🔬 Como funciona

1. **Parsing com Regex** — cada linha é testada contra padrões compilados para extrair IP, método, path, status e usuário
2. **Detecção de ataques** — matches geram eventos com severidade `CRÍTICO`, `ALTO`, `ATENÇÃO` ou `INFO`
3. **Correlação de Brute Force** — IPs com 5+ falhas de login são sinalizados automaticamente
4. **Exportação** — relatório `.txt` completo com todos os eventos, alertas e top IPs

---

## 🛠️ Tecnologias

| Tecnologia | Uso |
|---|---|
| **Python 3** | Linguagem principal |
| **Tkinter** | Interface gráfica nativa |
| **re (Regex)** | Parsing e detecção de padrões |
| **collections.Counter** | Ranking e contagem de eventos |
| **PyInstaller** | Empacotamento em `.exe` portátil |

---

## 📚 Conceitos aplicados

- Digital Forensics and Incident Response **(DFIR)**
- Análise de logs e correlação de eventos
- **OWASP Top 10** — SQL Injection, XSS, Path Traversal
- Detecção de intrusão por padrões comportamentais
- Desenvolvimento de software desktop com Python

---

## 👨‍🎓 Contexto acadêmico

| | |
|---|---|
| **Instituição** | UNIP — Universidade Paulista |
| **Curso** | Segurança da Informação |
| **Atividade** | Horas Complementares |
| **Área** | Forense Digital / Análise de Logs |

---

<div align="center">

Feito por [skoqui](https://github.com/skoqui) · UNIP · Segurança da Informação

</div>
