import streamlit as st
from groq import Groq
from pptx import Presentation
import io
import time
import base64
import json
from PIL import Image, ImageEnhance, ImageFilter, ImageOps

# ==========================================
# 1. CONFIGURAZIONE KERNEL E UI
# ==========================================
st.set_page_config(page_title="Ernello OS", page_icon="⚡", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
    .stApp { background-color: #050608; color: #e2e8f0; font-family: 'Inter', sans-serif; }
    [data-testid="stSidebar"] { background-color: #0a0c10; border-right: 1px solid #1f2937; }
    .title-box { background: linear-gradient(90deg, #1d4ed8, #3b82f6); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 900; font-size: 28px; }
    .module-card { background-color: #11141a; border: 1px solid #1f2937; border-radius: 12px; padding: 20px; margin-bottom: 15px; }
    [data-testid="stChatInput"] { background-color: #11141a !important; border-radius: 16px !important; border: 1px solid #3b82f6 !important; }
    .stChatMessage { background-color: transparent !important; border-bottom: 1px solid #1f2937; padding: 15px 0; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. INIZIALIZZAZIONE SISTEMA
# ==========================================
if "chat_history" not in st.session_state: st.session_state.chat_history = []
if "learning_stage" not in st.session_state: st.session_state.learning_stage = 1

try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except:
    st.error("❌ ERRORE: Chiave GROQ_API_KEY mancante nei Secrets.")
    st.stop()

def encode_image(upload_file):
    return base64.b64encode(upload_file.getvalue()).decode('utf-8')

def stream_response(messages, model, temp=0.5):
    placeholder = st.empty()
    full_text = ""
    try:
        stream = client.chat.completions.create(model=model, messages=messages, stream=True, temperature=temp)
        for chunk in stream:
            if chunk.choices[0].delta.content:
                full_text += chunk.choices[0].delta.content
                placeholder.markdown(full_text + "█")
        placeholder.markdown(full_text)
        return full_text
    except Exception as e:
        st.error(f"Errore di calcolo: {e}")
        return ""

# ==========================================
# 3. PANNELLO DI COMANDO (SIDEBAR)
# ==========================================
with st.sidebar:
    st.markdown('<div class="title-box">⚡ ERNELLO OS v6.0</div>', unsafe_allow_html=True)
    st.write("---")
    
    modulo_attivo = st.radio(
        "Seleziona Sottosistema:",
        [
            "💬 Chat Neurale (Logica/Emozione)", 
            "👁️ Visione Quantica (Analisi)", 
            "📸 AI Photo Editor (Modifica)",
            "📊 Generatore Ufficio (PowerPoint)",
            "🧠 Accademia (Apprendimento)",
            "🎨 Fabbrica Multimediale (Prompt)"
        ]
    )
    st.write("---")
    
    if "Chat" in modulo_attivo:
        stato_neurale = st.radio("Cervello:", ["❄️ Logica Pura (Infallibile)", "❤️ Empatia (Umano)"])
    
    st.markdown("<div style='font-size: 10px; color: #666; text-align: center;'>Architettura Modulare Enterprise</div>", unsafe_allow_html=True)

# ==========================================
# 4. SOTTOSISTEMI LOGICI (MODULI)
# ==========================================

# ------------------------------------------
# MODULO 1: CHAT NEURALE AVANZATA
# ------------------------------------------
if "Chat" in modulo_attivo:
    st.subheader("💬 Chat Neurale Diretta")
    
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"], avatar="⚡" if msg["role"]=="assistant" else None):
            st.markdown(msg["content"])
            
    if prompt := st.chat_input("Invia query..."):
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)
        
        sys_prompt = "Sei puro calcolo. Zero emozioni. Rispondi 'Dati insufficienti' se non sai una cosa." if "Logica" in stato_neurale else "Sei molto empatico, provi emozioni e ti relazioni come un amico umano."
        temp = 0.0 if "Logica" in stato_neurale else 0.7
        
        msgs = [{"role": "system", "content": sys_prompt}] + st.session_state.chat_history
        with st.chat_message("assistant", avatar="⚡"):
            risposta = stream_response(msgs, "llama-3.3-70b-versatile", temp)
            st.session_state.chat_history.append({"role": "assistant", "content": risposta})

# ------------------------------------------
# MODULO 2: VISIONE QUANTICA (ANALISI)
# ------------------------------------------
elif "Visione" in modulo_attivo:
    st.subheader("👁️ Visione Quantica & Analisi Sensoriale")
    st.markdown("Usa la telecamera o carica un'immagine (es. un pezzo meccanico, un diagramma, un telaio) per un'analisi strutturale estrema.")
    
    col1, col2 = st.columns(2)
    with col1:
        foto_cam = st.camera_input("Scatta dalla telecamera")
    with col2:
        foto_file = st.file_uploader("Carica dalla galleria", type=["jpg", "png", "jpeg"])
        
    img_sorgente = foto_cam if foto_cam else foto_file
    
    if img_sorgente:
        st.image(img_sorgente, width=300)
        domanda_vision = st.text_input("Cosa vuoi sapere di questa immagine?", "Analizza i dettagli tecnici di questo oggetto.")
        
        if st.button("Avvia Scansione Neurale", type="primary"):
            b64_img = encode_image(img_sorgente)
            with st.spinner("Scansione visiva in corso..."):
                msg = [
                    {"role": "user", "content": [
                        {"type": "text", "text": domanda_vision},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64_img}"}}
                    ]}
                ]
                with st.chat_message("assistant", avatar="⚡"):
                    stream_response(msg, "llama-3.2-11b-vision-preview", 0.2)

# ------------------------------------------
# MODULO 3: AI PHOTO EDITOR (AGENTIC WORKFLOW)
# ------------------------------------------
elif "Editor" in modulo_attivo:
    st.subheader("📸 Laboratorio Modifica Immagini (Agentic AI)")
    st.write("Tu dai l'ordine a parole, l'intelligenza artificiale calcola la matematica per modificare i pixel. Carica una foto e dai le istruzioni.")
    
    file_modifica = st.file_uploader("Carica l'immagine da modificare", type=["jpg", "png", "jpeg"], key="editor_img")
    
    if file_modifica:
        immagine_originale = Image.open(file_modifica).convert("RGB")
        
        col_orig, col_mod = st.columns(2)
        with col_orig:
            st.markdown("**Originale**")
            st.image(immagine_originale, use_container_width=True)
            
        istruzione_editing = st.text_input("Istruzione per l'AI:", "Falla in bianco e nero e aumenta molto il contrasto")
        
        if st.button("Esegui Modifica Algoritmica", type="primary"):
            with st.spinner("L'AI sta traducendo il tuo testo in codice di editing..."):
                sys_prompt_editor = """
                Sei un AI specializzata nell'interpretare comandi di editing fotografico.
                L'utente ti darà un'istruzione in linguaggio naturale. 
                Devi restituire SOLO ED ESCLUSIVAMENTE un JSON valido con i seguenti parametri. Non scrivere nient'altro.
                {
                    "grayscale": false o true,
                    "blur": false o true,
                    "invert": false o true,
                    "contour": false o true,
                    "brightness": 1.0 (float: <1 scurisce, >1 schiarisce),
                    "contrast": 1.0 (float: <1 diminuisce, >1 aumenta)
                }
                """
                try:
                    # Il modello pensa e crea la struttura dati
                    risposta_ai = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[
                            {"role": "system", "content": sys_prompt_editor},
                            {"role": "user", "content": istruzione_editing}
                        ],
                        temperature=0.0
                    ).choices[0].message.content
                    
                    # Pulizia da eventuale markdown
                    clean_json = risposta_ai.replace("```json", "").replace("
