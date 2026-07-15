import streamlit as st
from groq import Groq
from pptx import Presentation
import io

# --- 1. CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="Ernello Gemini Style", page_icon="⚡", layout="wide")

# --- CSS PER IL LOOK "GEMINI" ---
st.markdown("""
<style>
    /* Sfondo globale scuro */
    .stApp { background-color: #0d0d0d; color: #e0e0e0; }
    
    /* Sidebar scura */
    [data-testid="stSidebar"] { background-color: #050505; border-right: 1px solid #222; }
    
    /* Messaggi chat puliti */
    .stChatMessage { background-color: transparent !important; }
    .stChatMessageContent { color: #e0e0e0; font-family: sans-serif; }
    
    /* Barra input arrotondata stile Gemini */
    .input-container {
        background-color: #1f1f1f;
        border-radius: 30px;
        padding: 5px 20px;
        display: flex;
        align-items: center;
        border: 1px solid #333;
    }
    .block-container { padding-bottom: 5rem; }
</style>
""", unsafe_allow_html=True)

# --- 2. FUNZIONI ---
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
    st.error("⚠️ Configura GROQ_API_KEY nei Secrets!")
    st.stop()

# --- 3. BARRA LATERALE ---
with st.sidebar:
    st.title("⚙️ Controlli")
    modello = st.selectbox("Modello:", ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"])
    system_prompt = st.text_area("Stato d'animo:", "Tu sei Ernello, assistente preciso e professionale.")
    
    st.divider()
    if "all_chats" not in st.session_state: st.session_state.all_chats = {"Chat 1": []}
    st.session_state.active_chat = st.radio("Le tue chat:", list(st.session_state.all_chats.keys()))
    if st.button("➕ Nuova Chat"):
        nome = f"Chat {len(st.session_state.all_chats) + 1}"
        st.session_state.all_chats[nome] = []
        st.rerun()

# --- 4. AREA CHAT ---
messages = st.session_state.all_chats[st.session_state.active_chat]
for m in messages:
    with st.chat_message(m["role"], avatar=None):
        st.markdown(m["content"])

# --- 5. INPUT BAR "GEMINI STYLE" ---
# Creiamo un contenitore fisso in basso
container = st.container()
with container:
    # Divisori per layout: [Mic] [Input] [Send]
    col1, col2, col3 = st.columns([0.1, 0.8, 0.1])
    
    with col1:
        # Il microfono è un tasto che attiva l'audio_input (nascosto o compatto)
        audio_trigger = st.button("🎙️")
    
    with col2:
        testo_input = st.text_input("Scrivi...", label_visibility="collapsed", key="input_text")
    
    with col3:
        send_trigger = st.button("⬆️")

# Logica di invio
final_text = None
if audio_trigger:
    # Qui dovresti gestire l'audio, per semplicità nel layout "Gemini" 
    # usiamo il widget nativo che appare solo se necessario
    audio_val = st.audio_input("Parla...")
    if audio_val:
        # Trascrizione...
        pass

if send_trigger and testo_input:
    final_text = testo_input

if final_text:
    # (Logica di append e risposta identica a prima)
    st.session_state.all_chats[st.session_state.active_chat].append({"role": "user", "content": final_text})
    st.rerun()
