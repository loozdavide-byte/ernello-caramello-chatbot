import streamlit as st
from groq import Groq
import base64
import os

# --- 1. CONFIGURAZIONE PAGINA (Dark Mode) ---
st.set_page_config(page_title="Ernello Dark", page_icon="🌙", layout="wide")

def applica_stile_dark(nome_file):
    # CSS per look dark, pulito e ordinato
    css_dark = """
    <style>
        /* Sfondo principale nero */
        .stApp { background-color: #000000; color: #ffffff; }
        
        /* Messaggi puliti e minimalisti */
        .stChatMessage {
            background-color: #1a1a1a !important;
            border-radius: 12px;
            padding: 15px;
            margin-bottom: 15px;
            border: 1px solid #333;
        }
        
        /* Sidebar scura */
        [data-testid="stSidebar"] { background-color: #0d0d0d; border-right: 1px solid #333; }
        
        /* Input pulito */
        .stChatInput { background-color: #1a1a1a !important; }
        
        /* Rimuove elementi extra per pulizia */
        .block-container { padding-top: 2rem; }
    </style>
    """
    
    # Se c'è una foto, la applichiamo con opacità per non disturbare il testo
    if os.path.exists(nome_file):
        with open(nome_file, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        st.markdown(f"""
        <style>
            .stApp {{
                background: linear-gradient(rgba(0,0,0,0.85), rgba(0,0,0,0.85)), url("data:image/jpeg;base64,{b64}");
                background-size: cover;
                background-attachment: fixed;
            }}
        </style>
        """, unsafe_allow_html=True)
    
    st.markdown(css_dark, unsafe_allow_html=True)

applica_stile_dark("sfondo.jpg")

# --- 2. LOGICA BOT (Invariata ma più pulita) ---
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except:
    st.error("⚠️ Chiave API mancante!")
    st.stop()

# (Il resto della logica rimane identica alla versione precedente per mantenere la potenza!)
with st.sidebar:
    st.title("🌙 Ernello Control")
    modello_scelto = st.selectbox("Motore:", ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"])
    system_prompt = st.text_area("Personalità:", "Tu sei Ernello, assistente AI preciso e ordinato.")
    if "all_chats" not in st.session_state: st.session_state.all_chats = {"Chat 1": []}
    st.session_state.active_chat = st.radio("Le tue chat:", list(st.session_state.all_chats.keys()))
    if st.button("➕ Nuova"):
        nome = f"Chat {len(st.session_state.all_chats) + 1}"
        st.session_state.all_chats[nome] = []
        st.rerun()

messages = st.session_state.all_chats[st.session_state.active_chat]
for m in messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

if testo_inviato := st.chat_input("Scrivi a Ernello..."):
    st.session_state.all_chats[st.session_state.active_chat].append({"role": "user", "type": "text", "content": testo_inviato})
    with st.chat_message("user"): st.markdown(testo_inviato)
    
    api_messages = [{"role": "system", "content": system_prompt}] + [{"role": m["role"], "content": m["content"]} for m in messages]
    
    with st.chat_message("assistant"):
        stream = client.chat.completions.create(model=modello_scelto, messages=api_messages, stream=True)
        risposta = st.write_stream(stream)
        st.session_state.all_chats[st.session_state.active_chat].append({"role": "assistant", "type": "text", "content": risposta})
