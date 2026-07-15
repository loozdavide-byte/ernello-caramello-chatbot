import streamlit as st
from groq import Groq
import urllib.parse
import base64

# 1. Configurazione della pagina web
st.set_page_config(page_title="Il mio AI Super Bot", page_icon="🤖", layout="centered")
st.title("super ai bot di ernello caramello")
st.caption("Creato da il Merluzzo 🚀")

# 2. Connessione sicura alla cassaforte
CHIAVE_API = st.secrets["GROQ_API_KEY"]
client = Groq(api_key=CHIAVE_API)

# 3. Inizializzazione della memoria
if "messages" not in st.session_state:
    st.session_state.messages = []
if "last_processed_file_id" not in st.session_state:
    st.session_state.last_processed_file_id = None

# Definizione della personalità
sistema_ernello = [{"role": "system", "content": "Tu sei un assistente IA super intelligente. Il tuo nome è Ernello. Rispondi sempre in italiano in modo amichevole e personalizzato."}]

def converti_in_base64(file_caricato):
    return base64.b64encode(file_caricato.read()).decode("utf-8")

# 4. Barra laterale
with st.sidebar:
    st.header("⚙️ Pannello di Controllo")
    if st.button("🗑️ Cancella Cronologia Chat"):
        st.session_state.messages = []
        st.session_state.last_processed_file_id = None
        st.rerun()
    st.write("---")
    st.header("📸 Invia una Foto")
    foto_utente = st.file_uploader("Trascina qui un'immagine", type=["png", "jpg", "jpeg"])

# 5. Visualizzazione cronologia
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if message["type"] == "text":
            st.write(message["content"])
        elif message["type"] == "generated_image":
            st.image(message["content"], caption="🎨 Immagine Generata")
        elif message["type"] == "uploaded_image":
            st.image(message["content"], caption="📸 Foto Caricata")

# 6. Input utente
if prompt := st.chat_input("Scrivi qualcosa..."):
    base64_foto = None
    if foto_utente:
        base64_foto = converti_in_base64(foto_utente)
    
    api_messages = []
    for m in st.session_state.messages:
        if m["type"] == "text":
            api_messages.append({"role": m["role"], "content": m["content"]})
        else:
            api_messages.append({"role": m["role"], "content": "Immagine"})

    if foto_utente:
        file_id = f"{foto_utente.name}_{foto_utente.size}"
        if st.session_state.last_processed_file_id != file_id:
            st.session_state.messages.append({"role": "user", "type": "uploaded_image", "content": foto_utente.getvalue()})
            st.session_state.last_processed_file_id = file_id
            with st.chat_message("user"):
                st.image(foto_utente, caption="📸 Foto Caricata")
                
    st.session_state.messages.append({"role": "user", "type": "text", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    # Preparazione messaggi
    if base64_foto is not None:
        api_messages.append({
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_foto}"}}
            ]
        })
    else:
        api_messages.append({"role": "user", "content": prompt})

    # 7. Risposte
    with st.chat_message("assistant"):
        if any(p in prompt.lower() for p in ["disegna", "crea immagine", "foto di"]):
            st.write("🎨 Sto creando...")
            p_pulito = prompt
            url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(p_pulito)}"
            st.image(url)
            st.session_state.messages.append({"role": "assistant", "type": "generated_image", "content": url})
        
        elif base64_foto is not None:
            st.write("👀 Sto guardando...")
            try:
                risposta = client.chat.completions.create(
                    model="llama-3.2-11b-vision-preview",
                    messages=sistema_ernello + api_messages
                )
                testo = risposta.choices[0].message.content
                st.write(testo)
                st.session_state.messages.append({"role": "assistant", "type": "text", "content": testo})
            except Exception as e:
                st.error(f"Errore: {e}")

        else:
            st.write("Pensando...")
            try:
                risposta = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=sistema_ernello + api_messages
                )
                testo = risposta.choices[0].message.content
                st.write(testo)
                st.session_state.messages.append({"role": "assistant", "type": "text", "content": testo})
            except Exception as e:
                st.error(f"Errore: {e}")
