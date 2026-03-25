import streamlit as st
import mysql.connector
import hashlib
import os
import base64
import pyngrok
from pyngrok import ngrok

@st.cache_resource
def start_ngrok():
    tunnel = pyngrok.ngrok.connect(8501, proto="http")
    return tunnel.public_url


public_url = start_ngrok()
# =========================
# CONFIGURAÇÃO DA PÁGINA
# =========================
st.set_page_config(page_title="Aura demais", page_icon="✨", layout="centered")

# =========================
# CONEXÃO COM O BANCO
# =========================
def conectar():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Vinitata",
        database="base_streamlit"
    )

# =========================
# FUNÇÕES DE SENHA
# =========================
def gerar_hash_senha(senha):
    salt = os.urandom(16)
    hash_senha = hashlib.pbkdf2_hmac(
        "sha256",
        senha.encode("utf-8"),
        salt,
        100000
    )
    return base64.b64encode(salt + hash_senha).decode("utf-8")

def verificar_senha(senha_digitada, senha_guardada):
    dados = base64.b64decode(senha_guardada.encode("utf-8"))
    salt = dados[:16]
    hash_armazenado = dados[16:]

    hash_digitado = hashlib.pbkdf2_hmac(
        "sha256",
        senha_digitada.encode("utf-8"),
        salt,
        100000
    )
    return hash_digitado == hash_armazenado

# =========================
# ESTADO DA SESSÃO
# =========================
if "logado" not in st.session_state:
    st.session_state.logado = False
if "usuario" not in st.session_state:
    st.session_state.usuario = None

# =========================
# LOGOUT
# =========================
if st.session_state.logado:
    st.success(f"Bem-vindo, {st.session_state.usuario['nome']}!")

    if st.button("Sair"):
        st.session_state.logado = False
        st.session_state.usuario = None
        st.rerun()

    st.stop()

# =========================
# TELA DE LOGIN / CADASTRO
# =========================
st.title("Sistema de usuários")

opcao = st.radio("Escolha uma opção", ["Login", "Cadastro"], horizontal=True)

# =========================
# CADASTRO
# =========================
if opcao == "Cadastro":
    st.subheader("Cadastrar usuário")

    nome = st.text_input("Nome")
    email = st.text_input("E-mail")
    senha = st.text_input("Senha", type="password")

    if st.button("Salvar cadastro"):
        if not nome or not email or not senha:
            st.error("Preencha todos os campos.")
        else:
            conn = conectar()
            cursor = conn.cursor()

            try:
                cursor.execute("SELECT id FROM usuarios WHERE email = %s", (email,))
                existe = cursor.fetchone()

                if existe:
                    st.error("Esse e-mail já está cadastrado.")
                else:
                    senha_hash = gerar_hash_senha(senha)

                    sql = "INSERT INTO usuarios (nome, email, senha) VALUES (%s, %s, %s)"
                    valores = (nome, email, senha_hash)

                    cursor.execute(sql, valores)
                    conn.commit()

                    st.success("Usuário cadastrado com sucesso!")
            except mysql.connector.Error as e:
                st.error(f"Erro no banco: {e}")
            finally:
                cursor.close()
                conn.close()

# =========================
# LOGIN
# =========================
elif opcao == "Login":
    st.subheader("Entrar no sistema")

    email = st.text_input("E-mail")
    senha = st.text_input("Senha", type="password")

    if st.button("Entrar"):
        if not email or not senha:
            st.error("Preencha e-mail e senha.")
        else:
            conn = conectar()
            cursor = conn.cursor(dictionary=True)

            try:
                cursor.execute(
                    "SELECT id, nome, email, senha FROM usuarios WHERE email = %s",
                    (email,)
                )
                usuario = cursor.fetchone()

                if usuario and verificar_senha(senha, usuario["senha"]):
                    st.session_state.logado = True
                    st.session_state.usuario = {
                        "id": usuario["id"],
                        "nome": usuario["nome"],
                        "email": usuario["email"]
                    }
                    st.success("Login realizado com sucesso!")
                    st.rerun()
                else:
                    st.error("E-mail ou senha inválidos.")
            except mysql.connector.Error as e:
                st.error(f"Erro no banco: {e}")
            finally:
                cursor.close()
                conn.close()