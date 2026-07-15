import streamlit as st
from groq import Groq
import urllib.parse
import base64

# Configurazione stile (Il trucco per farlo sembrare WhatsApp)
st.set_page_config(page_title="Ernello", page_icon="💬", layout="centered")

# --- STILE CSS (Bolle Chat WhatsApp) ---
st.markdown("""
<style>
    /* Colore sfondo generale */
    .stApp { background-color: #f0f2f5; }
    /* Bolle chat personalizzate */
    [data-testid="stChatMessage"] {
        border-radius: 15px !important;
        padding: 10px !important;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
    }
    /* Sidebar più bella */
    [data-testid="stSidebar"] { background-color: #ffffff; }
</style>
""", unsafe_allow_html=True)

# Configurazione Logica
CHIAVE_API = st.secrets["GROQ_API_KEY"]
client = Groq(api_key=CHIAVE_API)
sistema_ernello = [{"role": "system", "content": "Tu sei Ernello. Rispondi in italiano in modo amichevole, conciso come su WhatsApp, e ricorda le conversazioni."}]

# Inizializzazione
if "all_chats" not in st.session_state: st.session_state.all_chats = {"Chat 1": []}
if "active_chat" not in st.session_state: st.session_state.active_chat = "Chat 1"

# Barra Laterale
with st.sidebar:
    st.title("💬 Chat di Ernello")
    chat_scelta = st.selectbox("Seleziona conversazione:", list(st.session_state.all_chats.keys()))
    st.session_state.active_chat = chat_scelta
    if st.button("➕ Nuova Chat"):
        nuovo_nome = f"Chat {len(st.session_state.all_chats) + 1}"
        st.session_state.all_chats[nuovo_nome] = []
        st.session_state.active_chat = nuovo_nome
        st.rerun()
    st.write("---")
    foto_utente = st.file_uploader("📸 Invia foto (o usa fotocamera)", type=["png", "jpg", "jpeg"])

# Visualizzazione
messages = st.session_state.all_chats[st.session_state.active_chat]
for m in messages:
    with st.chat_message(m["role"]): st.write(m["content"])

# Logica Invio
if prompt := st.chat_input("Scrivi a Ernello..."):
    base64_foto = None
    if foto_utente: base64_foto = base64.b64encode(foto_utente.read()).decode("utf-8")
    
    st.session_state.all_chats[st.session_state.active_chat].append({"role": "user", "type": "text", "content": prompt})
    with st.chat_message("user"): st.write(prompt)

    api_messages = sistema_ernello + [{"role": m["role"], "content": m["content"]} for m in messages if m["type"] == "text"]
    
    with st.chat_message("assistant"):
        st.write("...")
        try:
            if base64_foto:
                risposta = client.chat.completions.create(model="llama-3.2-11b-vision-preview", 
                    messages=[{"role": "user", "content": [{"type": "text", "text": prompt}, {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_foto}"}}]}])
            else:
                risposta = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=api_messages)
            
            testo = risposta.choices[0].message.content
            st.write(testo)
            st.session_state.all_chats[st.session_state.active_chat].append({"role": "assistant", "type": "text", "content": testo})
        except Exception as e: st.error(f"Ernello è un po' stanco: {e}")
