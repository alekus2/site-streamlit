from pyngrok import ngrok
import streamlit as st

st.set_page_config(page_title="Aura demais", page_icon="✨", layout="centered")

ngrok.set_auth_token("3B8w5noCyridWzHLiK9RdzjPJ3D_5TvGTRdTVuy7dsxAL6sEh")
public_url = ngrok.connect(addr="8501", proto="http")

st.title("Aura demais")
st.write("O site mais aura de todos os tempos")
