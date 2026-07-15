import streamlit as st
from groq import Groq
from pptx import Presentation
import io

# --- 1. CONFIGURAZIONE PAGINA (Dark & Clean) ---
st.set_page_config(page_title="Ernello MAX", page_icon="⚡", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #000000; color: #e0e0e0; }
    [data-testid="stSidebar"] { background-color: #0a0a0a; border-right: 1px solid #222; }
    .stChatMessage { background-color: transparent !important; padding: 10px 0px; }
    .stChatMessageContent { color: #d1d1d1; font-family: sans-serif; }
    .block-container { padding-top: 2rem; }
</style>
""", unsafe_allow_html=True)

# --- 2. FUNZIONI UTILITY ---
def crea_presentazione(titolo, contenuto):
    prs = Presentation()
    slide = prs.slides.add_slide(prs.slide_layouts[0])
    slide.shapes.title.text = titolo
    slide.placeholders[1].text = contenuto
    bio = io.BytesIO()
    prs.save(bio)
    return bio.getvalue()

try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except:
    st.error("⚠️ Chiave API mancante nei Secrets!")
    st.stop()

# --- 3. BARRA LATERALE (Controllo Totale) ---
with st.sidebar:
    st.title("⚡ Ernello Control")
    modello = st.selectbox("Modello:", ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"])
    system_prompt = st.text_area("Stato d'animo:", "Tu sei un assistente AI preciso, tecnologico e amichevole.")
    
    st.divider()
    st.subheader("💬 Le tue Chat")
    if "all_chats" not in st.session_state: st.session_state.all_chats = {"Chat 1": []}
    
    # Lista chat
    chat_scelta = st.radio("Seleziona:", list(st.session_state.all_chats.keys()))
    st.session_state.active_chat = chat_scelta
    
    if st.button("➕ Nuova Chat"):
        nome = f"Chat {len(st.session_state.all_chats) + 1}"
        st.session_state.all_chats[nome] = []
        st.rerun()
    
    st.divider()
    st.subheader("📊 Presentazioni")
    tema_ppt = st.text_input("Argomento PPT:")
    if st.button("Genera .pptx"):
        dati = crea_presentazione(tema_ppt, f"Presentazione su {tema_ppt}")
        st.download_button("Scarica PPTX", dati, file_name="presentazione.pptx")

# --- 4. MOTORE CHAT ---
messages = st.session_state.all_chats[st.session_state.active_chat]

# Visualizzazione (Senza avatar)
for m in messages:
    with st.chat_message(m["role"], avatar=None):
        st.markdown(m["content"])

# --- 5. AREA INPUT (Audio + Testo vicini) ---
# Usiamo colonne per mettere l'audio vicino all'input
col_audio, col_input = st.columns([0.15, 0.85])

with col_audio:
    audio_utente = st.audio_input("🎙️")

with col_input:
    testo_inviato = st.chat_input("Scrivi un messaggio...")

# Logica di elaborazione
input_finale = None

if audio_utente:
    with st.spinner("Trascrizione in corso..."):
        trascrizione = client.audio.transcriptions.create(
            file=("audio.wav", audio_utente.read()), 
            model="whisper-large-v3", 
            language="it"
        )
        input_finale = trascrizione.text

if testo_inviato:
    input_finale = testo_inviato

if input_finale:
    # Aggiungi e mostra messaggio utente
    st.session_state.all_chats[st.session_state.active_chat].append({"role": "user", "content": input_finale})
    with st.chat_message("user", avatar=None):
        st.markdown(input_finale)
    
    # Risposta assistente
    with st.chat_message("assistant", avatar=None):
        placeholder = st.empty()
        full_response = ""
        stream = client.chat.completions.create(
            model=modello,
            messages=[{"role": "system", "content": system_prompt}] + 
                     [{"role": m["role"], "content": m["content"]} for m in st.session_state.all_chats[st.session_state.active_chat]],
            stream=True
        )
        for chunk in stream:
            if chunk.choices[0].delta.content:
                full_response += chunk.choices[0].delta.content
                placeholder.markdown(full_response + "▌")
        placeholder.markdown(full_response)
        st.session_state.all_chats[st.session_state.active_chat].append({"role": "assistant", "content": full_response})
