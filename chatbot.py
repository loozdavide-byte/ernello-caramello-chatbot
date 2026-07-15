import streamlit as st
from groq import Groq
import urllib.parse
import base64

# Configurazione
st.set_page_config(page_title="Ernello MultiChat", page_icon="🤖", layout="centered")
st.title("🤖 Ernello: Multi-Chat")
CHIAVE_API = st.secrets["GROQ_API_KEY"]
client = Groq(api_key=CHIAVE_API)

# Inizializzazione archivio chat
if "all_chats" not in st.session_state:
    st.session_state.all_chats = {"Chat 1": []}
if "active_chat" not in st.session_state:
    st.session_state.active_chat = "Chat 1"

sistema_ernello = [{"role": "system", "content": "Tu sei Ernello. Rispondi in italiano in modo amichevole. Ricorda sempre i dettagli delle conversazioni precedenti."}]

# Barra Laterale per gestire le chat
with st.sidebar:
    st.header("📂 Archivio Chat")
    # Menu per scegliere la chat
    chat_scelta = st.selectbox("Seleziona Chat", list(st.session_state.all_chats.keys()))
    st.session_state.active_chat = chat_scelta
    
    # Crea nuova chat
    if st.button("➕ Nuova Chat"):
        nuovo_nome = f"Chat {len(st.session_state.all_chats) + 1}"
        st.session_state.all_chats[nuovo_nome] = []
        st.session_state.active_chat = nuovo_nome
        st.rerun()

    st.write("---")
    st.header("📸 Foto")
    foto_utente = st.file_uploader("Carica immagine", type=["png", "jpg", "jpeg"])

# Visualizzazione Chat Attiva
messages = st.session_state.all_chats[st.session_state.active_chat]

for m in messages:
    with st.chat_message(m["role"]):
        if m["type"] == "text": st.write(m["content"])
        else: st.image(m["content"])

# Input
if prompt := st.chat_input("Scrivi a Ernello..."):
    # Caricamento foto
    base64_foto = None
    if foto_utente:
        base64_foto = base64.b64encode(foto_utente.read()).decode("utf-8")
    
    # Aggiungi messaggio utente
    st.session_state.all_chats[st.session_state.active_chat].append({"role": "user", "type": "text", "content": prompt})
    with st.chat_message("user"): st.write(prompt)

    # Preparazione per l'IA
    api_messages = sistema_ernello + [{"role": "user", "content": m["content"]} for m in messages if m["type"] == "text"]
    
    with st.chat_message("assistant"):
        st.write("Pensando...")
        try:
            if base64_foto:
                risposta = client.chat.completions.create(
                    model="llama-3.2-11b-vision-preview",
                    messages=[{"role": "user", "content": [{"type": "text", "text": prompt}, {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_foto}"}}]}]
                )
            else:
                risposta = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=api_messages
                )
            testo = risposta.choices[0].message.content
            st.write(testo)
            st.session_state.all_chats[st.session_state.active_chat].append({"role": "assistant", "type": "text", "content": testo})
        except Exception as e:
            st.error(f"Errore: {e}")
