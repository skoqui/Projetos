import streamlit as st
import pandas as pd

st.set_page_config(page_title="Vire um membro FãFURIA - FURIA", layout="centered")

#  Logo 
col1, col2, col3 = st.columns(3)

with col1:
    st.image("ffuria.png", width=150)
with col2:
    st.image("furia-logo.png", width=150)
with col3:
    st.image("ffuria.png", width=150)


# Título principal
st.title("🔥 Bem vindo(a) ao FãFURIA 🔥")
st.markdown("Preencha para receber nossos lançamentos e participar dos nossos sorteios. 🐆")

# Entrada de dados - Dados Pessoais
st.subheader("Dados Pessoais")
nome = st.text_input("Qual seu nome?")
email = st.text_input("Qual seu e-mail?")
idade = st.slider("Qual sua idade?", 10, 60)
genero = st.selectbox("Gênero (opcional)", ["Selecione", "Masculino", "Feminino", "Outros", "Prefiro não informar"])
ocupacao = st.text_input("Qual sua ocupação? (ex.: Estudante, Profissional)")

# Entrada de dados - Redes Sociais
st.subheader("Redes Sociais")
handle_x = st.text_input("Qual seu handle no X? (ex.: @seuusuario)")
plataformas_conteudo = st.multiselect("Quais plataformas você usa para acompanhar eSports?",
                                     ["Twitch", "YouTube", "X", "Instagram", "TikTok"])
interesses_conteudo = st.multiselect("Que tipo de conteúdo você curte?",
                                     ["Lives", "Highlights", "Bastidores", "Memes", "Entrevistas"])

# Entrada de dados - Interações
st.subheader("Interações com a FURIA")
plataforma = st.selectbox("Onde você mais acompanha a FURIA?", ["Selecione", "YouTube", "Twitch", "Twitter", "Instagram"])
jogo = st.selectbox("Qual game tem mais o seu coração?", ["Selecione", "Counter-Strike", "VALORANT", "League Of Legends"])
intensidade = st.selectbox("Com que frequência você acompanha os jogos?", ["Selecione", "Sempre", "Às vezes", "Quase nunca"])
eventos_assistidos = st.multiselect("Quais eventos da FURIA você acompanhou?",
                                    ["CS:GO Major", "VCT Americas", "CBLOL Split", "Nenhum"])
engajamento = st.slider("Quão engajado você é com a FURIA? (1 = só assisto, 5 = comento tudo)", 1, 5)
jogador_favorito = st.text_input("Quem é seu jogador favorito da FURIA? (ex.: KSCERATO, FalleN...)")

# Análise
if st.button("Analisar Perfil"):
    if "Selecione" in (plataforma, jogo, intensidade):
        st.warning("Por favor, preencha todas as opções corretamente.")
    else:

        # Mensagem de bem vindo
        st.success(f"Bem vindo {nome.upper()}. Você agora faz parte da torcida mais furiosa do Brasil! 🐆🔥")
        # t.balloons()


        # Tipo de fã
        if intensidade == "Sempre":
            tipo = "Fã Hardcore? 🔥"
        elif intensidade == "Às vezes":
            tipo = "Fã Casual? 😎"
        else:
            tipo = "Fã Fantasma? 👻"

        st.subheader(f"Então você é um {tipo}")
        st.write("Acesse o link e você estará concorrendo a:")
        
        if tipo == "Fã Hardcore? 🔥":
            st.markdown("-  Uma camiseta oficial da FURIA")
            st.markdown("-  Um ingresso para a final: FURIA vs TIME")
            st.markdown("-  Acesso VIP a área dos jogadores")
            st.markdown(" ")
            st.markdown("👉 [Clique aqui para concorrer](https://furia.gg) 👈")
        elif tipo == "Fã Casual? 😎":
            st.markdown("-  Uma camiseta oficial da FURIA")
            st.markdown("-  Um ingresso para a final: FURIA vs TIME")
            st.markdown("-  Acesso VIP a área dos jogadores")
            st.markdown(" ")
            st.markdown("👉 [Clique aqui para concorrer](https://furia.gg) 👈")
        else:
            st.markdown("-  Que tal conhecer mais do melhor time E-sporte atual?")
            st.markdown("-  Acompanhe nossas lives na [Twitch](https:twitch.tv/furiatv)")
            st.markdown("-  Acompanhe também nossos jogadores e membros [@furia](https://www.twitch.tv/team/furia)")
            st.markdown(" ")
            st.markdown("👉 [Clique aqui para concorrer](https://furia.gg) 👈")

        # st.markdown("---")
        # st.subheader("Avalie sua experiência:")
        # feedback = st.slider("De 1 a 5 estrelas:", 1, 5)

        # if feedback:
        #     st.write(f"Obrigado! Sua nota foi: {feedback} ⭐")

        
                
        
        # Notícias por jogo
        st.subheader(f"📰 Últimas notícias da FURIA em {jogo}:")

        noticias_cs = [
            " arT diz: 'Estamos confiantes pro próximo Major!'",
            " KSCERATO lidera estatísticas de headshot da temporada!",
            " Nova lineup de treinos surpreende os fãs!",
        ]

        noticias_valorant = [
            " FURIA VALORANT vence série contra LOUD por 2x0!",
            " raafa lidera estratégia em jogo decisivo!",
            " Nova agente testada pela line-up surpreende os fãs.",
        ]

        noticias_lol = [
            " FURIA garante vitória em partida acirrada contra paiN!",
            " Mid laner da FURIA bate recorde de abates com Azir!",
            " Anúncio de nova comissão técnica para o CBLOL!",
        ]

        if jogo == "Counter-Strike":
            for noticia in noticias_cs:
                st.markdown(f"- {noticia}")
        elif jogo == "VALORANT":
            for noticia in noticias_valorant:
                st.markdown(f"- {noticia}")
        elif jogo == "League Of Legends":
            for noticia in noticias_lol:
                st.markdown(f"- {noticia}")

        # Notícia especial
        st.markdown("---")
        st.markdown("### 🏆 **Notícia Especial!**")
        st.success("🚨 skoqui é o mais novo estagiário contratado da FURIA! Seja bem-vindo ao time, guerreiro!")

        # Links oficiais ao final da página
        st.markdown("---")
        st.markdown("""
        ###  Links Oficiais da FURIA

        -  [Site Oficial](https://www.furia.gg/)
        -  [Loja Oficial da FURIA](https://www.furia.gg/produtos)

        ###  Redes Sociais

        -  [X](https://x.com/FURIA)
        -  [Instagram](https://www.instagram.com/furiagg/)
        -  [Twitch](https://www.twitch.tv/furiatv)
        """)


