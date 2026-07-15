import streamlit as st
from groq import Groq
import urllib.parse
import base64

# 1. Configurazione iniziale della pagina web
st.set_page_config(page_title="Il mio AI Super Bot", page_icon="🤖", layout="centered")
st.title("super ai bot di ernello caramello")
st.caption("Creato da il Merluzzo 🚀")
st.write("Benvenuto! Chiedimi di disegnare, analizzare una foto o parliamo del più e del meno.")

# 2. Connessione sicura alla cassaforte delle chiavi API
CHIAVE_API = st.secrets["GROQ_API_KEY"]
client = Groq(api_key=CHIAVE_API)

# 3. Inizializzazione della memoria del Bot (se è vuota)
if "messages" not in st.session_state:
    st.session_state.messages = []
if "last_processed_file_id" not in st.session_state:
    st.session_state.last_processed_file_id = None

# 4. Funzione tecnica per convertire le immagini per l'I.A.
def converti_in_base64(file_caricato):
    return base64.b64encode(file_caricato.read()).decode("utf-8")

# 5. Costruzione della barra laterale (Sidebar)
with st.sidebar:
    st.header("⚙️ Pannello di Controllo")
    
    # Tasto magico per cancellare la memoria del bot
    if st.button("🗑️ Cancella Cronologia Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.last_processed_file_id = None
        st.rerun()
        
    st.write("---")
    st.header("📸 Invia una Foto")
    foto_utente = st.file_uploader("Trascina qui un'immagine", type=["png", "jpg", "jpeg"])
    if foto_utente:
        st.image(foto_utente, caption="Foto pronta in memoria!")

# 6. Mostra la cronologia passata sullo schermo con il look corretto
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if message["type"] == "text":
            st.write(message["content"])
        elif message["type"] == "generated_image":
            st.image(message["content"], caption="🎨 Immagine Generata")
        elif message["type"] == "uploaded_image":
            st.image(message["content"], caption="📸 Foto Caricata")

# 7. Gestione dell'input dell'utente (Quando invia un messaggio)
if prompt := st.chat_input("Scrivi qui un messaggio o un comando (es. 'disegna un drago')..."):
    
    # Convertiamo la foto se presente
    base64_foto = None
    if foto_utente:
        base64_foto = converti_in_base64(foto_utente)
    
    # A. COSTRUIAMO LA CRONOLOGIA DA MANDARE A GROQ (Così l'I.A. ha memoria!)
    api_messages = []
    for m in st.session_state.messages:
        if m["type"] == "text":
            api_messages.append({"role": m["role"], "content": m["content"]})
        else:
            # Sostituto testuale per non far crashare i modelli con vecchie immagini storiche
            etichetta = "🎨 [Immagine Generata]" if m["type"] == "generated_image" else "📸 [Foto Caricata]"
            api_messages.append({"role": m["role"], "content": etichetta})

    # B. MOSTRIAMO I NUOVI INPUT SULLO SCHERMO E IN CODA ALLA MEMORIA
    if foto_utente:
        file_id = f"{foto_utente.name}_{foto_utente.size}"
        # Mostra la foto nella chat solo se è una NUOVA foto appena caricata
        if st.session_state.last_processed_file_id != file_id:
            st.session_state.messages.append({"role": "user", "type": "uploaded_image", "content": foto_utente.getvalue()})
            st.session_state.last_processed_file_id = file_id
            with st.chat_message("user"):
                st.image(foto_utente, caption="📸 Foto Caricata")
                
    # Mostriamo il testo dell'utente
    st.session_state.messages.append({"role": "user", "type": "text", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    # C. PREPARIAMO IL PACCHETTO DATI FINALE DA SPEDIRE AL CERVELLO DELL'I.A.
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

    # D. ELABORAZIONE DELLA RISPOSTA DELL'ASSISTENTE
    with st.chat_message("assistant"):
        parole_immagine = ["disegna", "crea immagine", "creami un'immagine", "genera immagine", "foto di", "immagine di", "/immagine"]
        parole_video = ["crea video", "genera video", "fai un video", "creami un video", "video di"]

        # CASO 1: Richiesta Video
        if any(parola in prompt.lower() for parola in parole_video):
            risposta_video = "🎥 **Generatore Video:** Per creare video reali serve una configurazione avanzata a pagamento con Replicate.com!"
            st.write(risposta_video)
            st.session_state.messages.append({"role": "assistant", "type": "text", "content": risposta_video})
            
        # CASO 2: Generazione Immagine (Disegno da zero)
        elif any(parola in prompt.lower() for parola in parole_immagine):
            st.write("🎨 Sto dipingendo la tua idea, un attimo...")
            prompt_pulito = prompt
            for parola in parole_immagine:
                prompt_pulito = prompt_pulito.lower().replace(parola, "").strip()
            if not prompt_pulito:
                prompt_pulito = "un paesaggio incredibile"
            
            prompt_codificato = urllib.parse.quote(prompt_pulito)
            url_immagine = f"https://image.pollinations.ai/prompt/{prompt_codificato}?width=1024&height=1024&nologo=true"
            
            st.image(url_immagine, caption=f"Ecco: {prompt_pulito}")
            st.session_state.messages.append({"role": "assistant", "type": "generated_image", "content": url_immagine})
            
        # CASO 3: Analisi di una foto caricata (Visione Artificiale)
        elif base64_foto is not None:
            st.write("👀 Sto guardando la foto...")
            try:
                risposta = client.chat.completions.create(
                    model="llama-3.2-11b-vision-preview",
                    messages=api_messages
                )
                testo_risposta = risposta.choices[0].message.content
                st.write(testo_risposta)
                st.session_state.messages.append({"role": "assistant", "type": "text", "content": testo_risposta})
            except Exception as errore:
                st.error(f"Errore Visione: {errore}")

        # CASO 4: Chat normale testuale (Modello Gigante Ultra-Intelligente)
        else:
            st.write("Pensando...")
            try:
                risposta = client.chat.completions.create(
                   model="llama-3.3-70b-versatile",
                    messages=api_messages
                )
                testo_risposta = risposta.choices[0].message.content
                st.write(testo_risposta)
                st.session_state.messages.append({"role": "assistant", "type": "text", "content": testo_risposta})
            except Exception as errore:
                st.error(f"Errore Connessione: {errore}")
