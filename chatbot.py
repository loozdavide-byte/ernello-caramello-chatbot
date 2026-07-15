import streamlit as st
from groq import Groq
import base64
import os

# --- 1. CONFIGURAZIONE PAGINA E DESIGN ---
st.set_page_config(page_title="Ernello PRO", page_icon="⚡", layout="wide")

def applica_stile_e_sfondo(nome_file):
    if os.path.exists(nome_file):
        with open(nome_file, "rb") as f:
            b64_immagine = base64.b64encode(f.read()).decode()
        
        # IL TRUCCO È QUI: Nessuno spazio prima di <style>
        st.markdown(f"""
<style>
.stChatMessage {{
    background-color: rgba(255, 255, 255, 0.90) !important;
    border-radius: 15px;
    padding: 15px;
    box-shadow: 0px 4px 6px rgba(0,0,0,0.1);
    margin-bottom: 10px;
    color: black;
}}
.block-container {{ 
    background-color: transparent !important; 
    padding-top: 2rem; 
}}
.stApp {{
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
}}
</style>
""", unsafe_allow_html=True)
    else:
        st.markdown(f"""
<style>
.stChatMessage {{
    background-color: rgba(255, 255, 255, 0.90) !important;
    border-radius: 15px;
    padding: 15px;
    box-shadow: 0px 4px 6px rgba(0,0,0,0.1);
    margin-bottom: 10px;
}}
.stApp {{ background-color: #f0f2f6; }}
</style>
""", unsafe_allow_html=True)

applica_stile_e_sfondo("sfondo.jpg")

# --- 2. CONFIGURAZIONE API GROQ ---
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except:
    st.error("⚠️ Manca la chiave API nei Secrets!")
    st.stop()

# --- 3. BARRA LATERALE: I SUPERPOTERI ---
with st.sidebar:
    st.title("⚙️ Pannello di Controllo")
    
    st.subheader("🧠 Scegli il Modello")
    modello_scelto = st.selectbox(
        "Motore AI:",
        ["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "mixtral-8x7b-32768"],
        help="70b = Più intelligente. 8b = Più veloce. Mixtral = Ottimo per codice."
    )
    
    st.subheader("🎭 Personalità")
    system_prompt = st.text_area("Come deve comportarsi Ernello?", "Tu sei Ernello, un assistente AI super intelligente, esperto di informatica, motori e matematica. Rispondi in italiano, in modo amichevole e preciso.")
    
    st.divider()
    
    st.subheader("💬 Le tue Chat")
    if "all_chats" not in st.session_state: st.session_state.all_chats = {"Chat 1": []}
    if "active_chat" not in st.session_state: st.session_state.active_chat = "Chat 1"
    
    chat_scelta = st.radio("Seleziona:", list(st.session_state.all_chats.keys()))
    st.session_state.active_chat = chat_scelta
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("➕ Nuova"):
            nome = f"Chat {len(st.session_state.all_chats) + 1}"
            st.session_state.all_chats[nome] = []
            st.session_state.active_chat = nome
            st.rerun()
    with col2:
        if st.button("🗑️ Pulisci"):
            st.session_state.all_chats[st.session_state.active_chat] = []
            st.rerun()
            
    st.divider()
    
    st.subheader("📎 Invia File")
    foto_utente = st.file_uploader("📸 Analizza una foto", type=["png", "jpg", "jpeg"])
    audio_utente = st.audio_input("🎙️ Parlami a voce")

# --- 4. MOTORE DELLA CHAT PRINCIPALE ---
messages = st.session_state.all_chats[st.session_state.active_chat]

for m in messages:
    with st.chat_message(m["role"]):
        if m["type"] == "text":
            st.markdown(m["content"])
        elif m["type"] == "image":
            st.image(m["content"])

# --- 5. LOGICA DI RICEZIONE MESSAGGI ---
testo_inviato = st.chat_input("Scrivi un messaggio...")

if audio_utente:
    with st.spinner("Sto ascoltando..."):
        trascrizione = client.audio.transcriptions.create(
            file=("audio.wav", audio_utente.read()),
            model="whisper-large-v3",
            language="it"
        )
        testo_inviato = trascrizione.text

if testo_inviato:
    st.session_state.all_chats[st.session_state.active_chat].append({"role": "user", "type": "text", "content": testo_inviato})
    with st.chat_message("user"):
        st.markdown(testo_inviato)

    api_messages = [{"role": "system", "content": system_prompt}]
    for m in st.session_state.all_chats[st.session_state.active_chat]:
        if m["type"] == "text":
            api_messages.append({"role": m["role"], "content": m["content"]})
            
    with st.chat_message("assistant"):
        placeholder_risposta = st.empty()
        
        try:
            if foto_utente:
                base64_foto = base64.b64encode(foto_utente.read()).decode("utf-8")
                risposta = client.chat.completions.create(
                    model="llama-3.2-11b-vision-preview", 
                    messages=[{"role": "user", "content": [
                        {"type": "text", "text": testo_inviato}, 
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_foto}"}}
                    ]}]
                )
                testo_finale = risposta.choices[0].message.content
                placeholder_risposta.markdown(testo_finale)
                
            else:
                stream = client.chat.completions.create(
                    model=modello_scelto,
                    messages=api_messages,
                    stream=True 
                )
                testo_finale = ""
                for chunk in stream:
                    if chunk.choices[0].delta.content is not None:
                        testo_finale += chunk.choices[0].delta.content
                        placeholder_risposta.markdown(testo_finale + "▌")
                placeholder_risposta.markdown(testo_finale)

            st.session_state.all_chats[st.session_state.active_chat].append({"role": "assistant", "type": "text", "content": testo_finale})
            
        except Exception as e:
            st.error(f"Errore di sistema: {e}")
