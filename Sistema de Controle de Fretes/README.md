# Sistema de Gestão de Fretes – Flask

![alt text](<New Project.gif>)

Sistema web desenvolvido em **Flask + SQLite** com o objetivo de **auxiliar e minimizar o tempo de trabalho operacional**, facilitando a **troca e organização de documentos de frete entre duas pessoas**.

Antes da aplicação, os documentos eram enviados de forma descentralizada por **WhatsApp e e-mail**, o que gerava retrabalho, perda de arquivos e dificuldade de controle.  
Este projeto centraliza todo o processo em um único sistema, tornando o fluxo mais rápido, organizado e confiável.

## Objetivo do Projeto

- Reduzir o tempo gasto no envio e recebimento de documentos
- Centralizar arquivos em um único local
- Evitar perda de informações trocadas por WhatsApp ou e-mail
- Facilitar o acompanhamento do status de cada frete
- Tornar o processo mais organizado e rastreável

## Funcionalidades

- Cadastro de fretes
- Upload e download de documentos
- Listagem de fretes
- Visualização detalhada
- Marcação de frete como concluído
- Controle de status (Em andamento / Concluído)

## Tecnologias Utilizadas

- Python 3
- Flask
- SQLite
- HTML + Bootstrap

## Como executar o projeto

### 1 Clone o repositório
```bash
git clone https://github.com/seu-usuario/fretes-app.git
cd fretes-app
```

### 2 Crie e ative o ambiente virtual
```bash
python -m venv venv
source venv/bin/activate   # Linux
venv\Scripts\activate      # Windows
```

### 3 Instale as dependências
```bash
pip install -r requirements.txt
```

### 4 Execute a aplicação
```bash
python app.py
```
Acesse no navegador:
```cpp
http://127.0.0.1:5000
```

### Observações Importantes
- O arquivo banco.db é gerado localmente e não faz parte do repositório.
- A pasta uploads/ é criada automaticamente para armazenar os documentos enviados.
- Projeto desenvolvido para uso interno e fins educacionais.


### Licença
Projeto de uso livre para estudo e adaptação.

