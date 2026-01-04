import streamlit as st
import requests
import os
from dotenv import load_dotenv

# Carrega a API Key
load_dotenv()
api_key = os.getenv("OPENROUTER_API_KEY")

# Verifica se a chave foi carregada
if not api_key:
    st.error("API KEY não encontrada. Verifique seu .env ou Streamlit Secrets.")
    st.stop()

# Configura a página
st.set_page_config(page_title="Chatbot da FURIA", page_icon="🐆")

st.title("🤖 Chatbot da FURIA")
st.caption("Powered by DeepSeek R1 (via OpenRouter)")

# Inicia histórico da conversa
if "history" not in st.session_state:
    st.session_state.history = [
        {"role": "system", "content": "Você é um bot educado e simpático que responde como um membro do time FURIA, de forma leve e direta."}
    ]

# Botão para limpar conversa
if st.button("🔁 Limpar conversa"):
    st.session_state.history = [
        {"role": "system", "content": "Você é um bot educado e simpático que responde como um membro do time FURIA, de forma leve e direta."}
    ]
    st.success("Conversa reiniciada!")

# Exibir histórico anterior
for msg in st.session_state.history:
    if msg["role"] == "system":
        continue  # não exibe a mensagem do system
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Campo de entrada do usuário
user_input = st.chat_input("Digite sua mensagem:")

if user_input:
    # Adiciona entrada do usuário ao histórico
    st.session_state.history.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Envia para OpenRouter (DeepSeek R1)
    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "HTTP-Referer": "https://furia-chatbot.streamlit.app",
            "X-Title": "Chatbot da FURIA"
        },
        json={
            "model": "deepseek/deepseek-r1:free",
            "messages": st.session_state.history,
            "temperature": 0.7
        }
    )

    if response.status_code == 200:
        reply = response.json()["choices"][0]["message"]["content"]
        st.session_state.history.append({"role": "assistant", "content": reply})
        with st.chat_message("assistant"):
            st.markdown(reply)
    else:
        st.error(f"Erro {response.status_code}: {response.text}")
