# Port Scanner Simples - GUI

Um scanner de portas básico com interface gráfica em Python usando Tkinter.  
Permite escanear faixas de portas TCP de um host/IP, com suporte a múltiplos parâmetros semelhantes ao Nmap, como `-sV`, `-A`, `-v` e `-vv` para diferentes níveis de verbosidade.

---

## Funcionalidades

- Escaneamento de faixa de portas TCP com múltiplas threads.
- Suporte a parâmetros comuns de enumeração (`-sV`, `-A`, `-v`, `-vv`).
- Exibição dos resultados em tempo real.
- Botão para parar o escaneamento a qualquer momento.
- Opção de salvar resultados em `.txt`.
- Interface gráfica amigável e simples com Tkinter.

---

## Como usar

1. Insira o **Host ou IP** que deseja escanear.
2. Defina a **porta inicial e final** da faixa.
3. Escolha o **número de threads** (ex: `10`).
4. No campo **Parâmetros**, insira os parâmetros desejados (ex: `-sV -A -v`).
5. Clique em **Iniciar Scan**.
6. Use os botões:
   - **Parar** para interromper,
   - **Limpar** para apagar os resultados,
   - **Salvar** para exportar os resultados.

---

## Requisitos

- Python 3.x
- `tkinter` (normalmente já incluído no Python)

---

## Instalação

Clone o repositório e execute o script:

```bash
git clone https://github.com/skoqui/PortScan
cd PortScan
python portscan.py
```


## Avisos
     • Esta ferramenta é educacional e não substitui scanners profissionais como o Nmap.
     • Utilize somente em redes e dispositivos com permissão legal.
