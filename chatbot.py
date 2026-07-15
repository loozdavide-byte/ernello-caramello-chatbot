import streamlit as st
from groq import Groq
from pptx import Presentation
import io

# --- 1. CONFIGURAZIONE ---
st.set_page_config(page_title="Ernello", page_icon="⚡", layout="wide")

# --- CSS "GEMINI CLONE" ---
st.markdown("""
<style>
    /* Sfondo Gemini */
    [data-testid="stAppViewContainer"] { background-color: #131314; }
    [data-testid="stSidebar"] { background-color: #0b0b0b; border-right: 1px solid #222; }
    
    /* Sidebar Title & Logo */
    .sidebar-title { color: #ffffff; font-size: 20px; font-weight: 600; padding: 10px; }
    
    /* Barra di input personalizzata */
    .stChatInput { background-color: #1f1f1f; border-radius: 24px; }
    
    /* Messaggi */
    .stChatMessage { background-color: transparent !important; }
    
    /* Nascondi header standard per pulizia */
    header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# --- 2. LOGICA E FUNZIONI ---
# (Mantieni la logica precedente per la gestione Groq e PPTX)
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except:
    st.error("⚠️ Chiave API mancante!")
    st.stop()

# --- 3. SIDEBAR (Design Gemini) ---
with st.sidebar:
    st.markdown('<div class="sidebar-title">⚡ Ernello</div>', unsafe_allow_html=True)
    
    if st.button("➕ Nuova chat", use_container_width=True):
        st.session_state.active_chat = "Chat 1"
        st.rerun()
    
    st.write("---")
    st.subheader("Recenti")
    # Qui potresti ciclare le tue chat salvate
    st.text("Chat 1")
    st.text("Progetto Scooter")
    st.text("Coding Python")
    
    st.divider()
    modello = st.selectbox("Motore:", ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"])

# --- 4. MAIN CHAT (Look Gemini) ---
if "all_chats" not in st.session_state: st.session_state.all_chats = {"Chat 1": []}

messages = st.session_state.all_chats["Chat 1"]

for m in messages:
    with st.chat_message(m["role"], avatar="⚡" if m["role"] == "assistant" else None):
        st.markdown(m["content"])

# --- 5. BARRA INPUT GEMINI STYLE ---
# Usiamo i contenitori per mimare la barra di Gemini
col_plus, col_input, col_mic, col_send = st.columns([0.05, 0.8, 0.05, 0.05])

with col_plus:
    if st.button("➕"):
        st.file_uploader("Upload", label_visibility="collapsed")

with col_input:
    testo = st.text_input("Scrivi a Ernello...", label_visibility="collapsed", key="input_gemini")

with col_mic:
    mic = st.button("🎙️")

with col_send:
    send = st.button("⬆️")

# Logica di invio
if send and testo:
    st.session_state.all_chats["Chat 1"].append({"role": "user", "content": testo})
    with st.chat_message("user"): st.markdown(testo)
    
    # Risposta AI (semplificata)
    with st.chat_message("assistant", avatar="⚡"):
        placeholder = st.empty()
        stream = client.chat.completions.create(
            model=modello,
            messages=[{"role": "user", "content": testo}],
            stream=True
        )
        full_response = ""
        for chunk in stream:
            if chunk.choices[0].delta.content:
                full_response += chunk.choices[0].delta.content
                placeholder.markdown(full_response + "▌")
        placeholder.markdown(full_response)
        st.session_state.all_chats["Chat 1"].append({"role": "assistant", "content": full_response})
