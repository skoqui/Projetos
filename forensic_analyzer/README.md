# 🔍 Forensic Log Analyzer
### Analisador Forense de Logs de Segurança

> **Projeto de Horas Complementares — UNIP · Segurança da Informação**

---

![alt text](</forensic_analyzer/imagens/1.png>)

![alt text](</forensic_analyzer/imagens/2.png>)

![alt text](</forensic_analyzer/imagens/3.png>)

![alt text](</forensic_analyzer/imagens/4.png>)

![alt text](</forensic_analyzer/imagens/5.png>)

---

## 📌 Descrição

Ferramenta de análise forense de logs desenvolvida em Python com interface web.
Detecta automaticamente padrões suspeitos em arquivos de log e gera relatórios de segurança.

---

## 🎯 Funcionalidades

| Funcionalidade | Detalhes |
|---|---|
| 🌐 Análise de logs web | Apache, Nginx (Combined Log Format) |
| 🔐 Análise SSH | Falhas de login, usuários inválidos, brute force |
| 💉 Detecção de ataques | SQL Injection, XSS, Path Traversal |
| 🤖 Scanners | Nikto, sqlmap, Nmap, Metasploit, etc. |
| 📊 Relatório visual | Dashboard com alertas, IPs, timeline |
| ⚡ Brute Force | Detecta IPs com 5+ tentativas falhas |

---

## 🚀 Como Executar

### 1. Pré-requisitos
- Python 3.8+
- pip

### 2. Instalar dependências
```bash
pip install -r requirements.txt
```

### 3. Rodar o servidor
```bash
python app.py
```

### 4. Acessar no navegador
```
http://localhost:5000
```

---

## 📂 Estrutura do Projeto

```
forensic_analyzer/
├── app.py              # Backend Python / Flask + Motor forense
├── requirements.txt    # Dependências
├── README.md           # Esta documentação
├── templates/
│   └── index.html      # Interface web (HTML + CSS + JS)
└── uploads/            # Arquivos enviados (temporários)
```

---

## 🔬 Como Funciona — Conceitos de Segurança

### Análise Forense Digital
A ferramenta aplica técnicas de **Digital Forensics and Incident Response (DFIR)**:

1. **Parsing de Logs**: Expressões Regulares (Regex) para extrair campos estruturados
2. **Correlação de Eventos**: Agrupa eventos por IP, usuário e período
3. **Detecção de Anomalias**: Identifica padrões fora do comportamento normal
4. **Geração de Timeline**: Ordena eventos cronologicamente para reconstruir incidentes

### Padrões Detectados
- **SQL Injection**: `UNION SELECT`, `DROP TABLE`, `1=1`, etc.
- **XSS**: `<script>`, `document.cookie`, `eval()`, etc.
- **Path Traversal**: `../`, `%2e%2e%2f`, etc.
- **Brute Force**: ≥ 5 tentativas de login falhadas do mesmo IP
- **Scanner Tools**: Identificação de User-Agents maliciosos

---

## 🛠️ Tecnologias Utilizadas

| Tecnologia | Uso |
|---|---|
| **Python 3** | Linguagem principal |
| **Flask** | Framework web |
| **re (Regex)** | Parsing e detecção de padrões |
| **collections** | Counter e defaultdict para análise |
| **HTML5 / CSS3** | Interface visual |
| **JavaScript** | Comunicação assíncrona (fetch API) |

---

## 📋 Formatos de Log Suportados

- Apache/Nginx Combined Log Format
- SSH / auth.log (Linux)
- Syslog genérico
- Qualquer log com IPs e palavras-chave de segurança

---

## 👨‍🎓 Informações Acadêmicas

- **Instituição**: UNIP — Universidade Paulista
- **Curso**: Segurança da Informação
- **Tipo**: Projeto de Horas Complementares
- **Área**: Forense Digital / Análise de Logs
- **Linguagem**: Python 3

---

*Desenvolvido como atividade prática de horas complementares, aplicando conceitos de
segurança da informação, análise forense e desenvolvimento de software.*
