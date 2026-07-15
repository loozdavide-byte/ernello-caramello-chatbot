import streamlit as st
from groq import Groq
import base64
from pptx import Presentation
import io

# --- 1. CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="Ernello MAX", page_icon="⚡", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #000000; color: #e0e0e0; }
    [data-testid="stSidebar"] { background-color: #0a0a0a; border-right: 1px solid #222; }
    .stChatMessage { background-color: transparent !important; padding: 10px 0px; }
    .stChatMessageContent { color: #d1d1d1; font-family: sans-serif; }
    [data-testid="stChatInput"] { background-color: #1a1a1a; border: 1px solid #333; border-radius: 8px; }
    .block-container { padding-top: 2rem; }
</style>
""", unsafe_allow_html=True)

# --- 2. LOGICA GENERAZIONE PPTX ---
def crea_presentazione(titolo, contenuto):
    prs = Presentation()
    slide = prs.slides.add_slide(prs.slide_layouts[0])
    slide.shapes.title.text = titolo
    slide.placeholders[1].text = contenuto
    
    bio = io.BytesIO()
    prs.save(bio)
    return bio.getvalue()

# --- 3. CONFIGURAZIONE API ---
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception as e:
    st.error(f"⚠️ Errore API: {e}")
    st.stop()

# --- 4. BARRA LATERALE ---
with st.sidebar:
    st.title("⚡ Ernello MAX")
    modello = st.selectbox("Modello:", ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"])
    
    st.subheader("🎭 Personalità")
    system_prompt = st.text_area("Stato d'animo AI:", "Tu sei Ernello, un assistente ultra-tecnologico, preciso e amichevole.")
    
    st.divider()
    st.subheader("📊 Genera Presentazione")
    tema_ppt = st.text_input("Di cosa deve parlare la PPT?")
    if st.button("Genera .pptx"):
        dati_ppt = crea_presentazione(tema_ppt, f"Presentazione generata da Ernello su: {tema_ppt}")
        st.download_button("Scarica PPTX", dati_ppt, file_name="presentazione.pptx")

# --- 5. GESTIONE STATO CHAT ---
if "all_chats" not in st.session_state:
    st.session_state.all_chats = {"Chat 1": []}

st.session_state.active_chat = st.sidebar.radio("Le tue chat:", list(st.session_state.all_chats.keys()))

# --- 6. MOTORE CHAT ---
messages = st.session_state.all_chats[st.session_state.active_chat]

for m in messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# Gestione input vocale e testo
audio_utente = st.audio_input("🎙️")
testo_inviato = st.chat_input("Scrivi...")

if audio_utente:
    with st.spinner("Trascrizione in corso..."):
        trascrizione = client.audio.transcriptions.create(
            file=("audio.wav", audio_utente.read()), 
            model="whisper-large-v3", 
            language="it"
        )
        testo_inviato = trascrizione.text

if testo_inviato:
    st.session_state.all_chats[st.session_state.active_chat].append({"role": "user", "content": testo_inviato})
    with st.chat_message("user"):
        st.markdown(testo_inviato)
    
    with st.chat_message("assistant"):
        placeholder = st.empty()
        full_response = ""
        stream = client.chat.completions.create(
            model=modello,
            messages=[{"role": "system", "content": system_prompt}] + messages,
            stream=True
        )
        for chunk in stream:
            if chunk.choices[0].delta.content:
                full_response += chunk.choices[0].delta.content
                placeholder.markdown(full_response + "▌")
        placeholder.markdown(full_response)
        st.session_state.all_chats[st.session_state.active_chat].append({"role": "assistant", "content": full_response})
