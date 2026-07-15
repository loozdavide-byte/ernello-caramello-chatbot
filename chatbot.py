import streamlit as st
from groq import Groq
import urllib.parse
import base64  # Necessario per convertire la foto e farla vedere all'IA

# Configurazione della pagina web
st.set_page_config(page_title="Il mio AI Super Bot", page_icon="🤖", layout="centered")
st.title("🤖 Il mio AI Super Bot")
st.caption("Creato da il Merluzzo 🚀")
st.write("Chiedimi di disegnare qualcosa, carica una foto o facciamo due chiacchiere!")

# Recupera la chiave dalle impostazioni segrete (cassaforte) di Streamlit
CHIAVE_API = st.secrets["GROQ_API_KEY"]

# Inizializziamo il client Groq
client = Groq(api_key=CHIAVE_API)

# Crea la memoria della chat se non esiste
if "messages" not in st.session_state:
    st.session_state.messages = []

# Mostra i messaggi precedenti nella cronologia
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if message.get("is_image"):
            st.image(message["content"], caption="Immagine")
        else:
            st.write(message["content"])

# Funzione tecnica per tradurre l'immagine in un formato leggibile dall'IA
def converti_in_base64(file_caricato):
    return base64.b64encode(file_caricato.read()).decode("utf-8")

# --- NUOVA BARRA LATERALE PER CARICARE LE FOTO ---
with st.sidebar:
    st.header("📸 Invia una Foto")
    foto_utente = st.file_uploader("Carica un'immagine dal tuo dispositivo", type=["png", "jpg", "jpeg"])
    if foto_utente:
        st.image(foto_utente, caption="Foto pronta per essere analizzata!")

# Input di testo dell'utente
if prompt := st.chat_input("Scrivi qui... (es. 'Cosa ne pensi di questa foto?' o 'Disegna un drago')"):
    
    # Mostra il messaggio di testo dell'utente
    with st.chat_message("user"):
        st.write(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Se c'è una foto caricata, la salviamo e la mostriamo nella cronologia della chat
    base64_foto = None
    if foto_utente:
        base64_foto = converti_in_base64(foto_utente)
        with st.chat_message("user"):
            st.image(foto_utente, caption="Foto inviata")
        st.session_state.messages.append({"role": "user", "content": foto_utente.getvalue(), "is_image": True})

    # Parole chiave per capire se l'utente vuole GENERARE un disegno da zero
    parole_immagine = ["disegna", "crea immagine", "creami un'immagine", "genera immagine", "foto di", "immagine di", "/immagine"]
    parole_video = ["crea video", "genera video", "fai un video", "creami un video", "video di"]

    with st.chat_message("assistant"):
        
        # CASO 1: L'utente chiede un VIDEO
        if any(parola in prompt.lower() for parola in parole_video):
            risposta_video = "🎥 **Generatore Video:** Per creare video reali serve una configurazione a pagamento con chiavi Replicate.com!"
            st.write(risposta_video)
            st.session_state.messages.append({"role": "assistant", "content": risposta_video})
            
        # CASO 2: L'utente vuole GENERARE un'immagine (Pollinations)
        elif any(parola in prompt.lower() for parola in parole_immagine):
            st.write("🎨 Sto creando la tua immagine, un attimo di pazienza...")
            prompt_pulito = prompt
            for parola in parole_immagine:
                prompt_pulito = prompt_pulito.lower().replace(parola, "").strip()
            if not prompt_pulito:
                prompt_pulito = "un disegno astratto"
            prompt_codificato = urllib.parse.quote(prompt_pulito)
            url_immagine = f"https://image.pollinations.ai/prompt/{prompt_codificato}?width=1024&height=1024&nologo=true"
            st.image(url_immagine, caption=f"Risultato per: {prompt_pulito}")
            st.session_state.messages.append({"role": "assistant", "content": url_immagine, "is_image": True})
            
        # CASO 3: L'utente ha CARICATO una FOTO (Attiviamo il modello Vision!)
        elif base64_foto is not None:
            st.write("👀 Sto esaminando l'immagine che mi hai caricato...")
            try:
                risposta = client.chat.completions.create(
                    model="llama-3.2-11b-vision-preview", # <-- Modello speciale con gli occhi!
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": prompt},
                                {
                                    "type": "image_url",
                                    "image_url": {"url": f"data:image/jpeg;base64,{base64_foto}"}
                                }
                            ]
                        }
                    ]
                )
                testo_risposta = risposta.choices[0].message.content
                st.write(testo_risposta)
                st.session_state.messages.append({"role": "assistant", "content": testo_risposta})
            except Exception as errore:
                st.error(f"Errore durante l'analisi della foto: {errore}")

        # CASO 4: Chat normale a parole (Modello Llama 3.3 Super Intelligente!)
        else:
            st.write("Pensando...")
            try:
                risposta = client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model="llama-3.3-70b-specdec", # <-- Il super cervello ultra colto!
                )
                testo_risposta = risposta.choices[0].message.content
                st.write(testo_risposta)
                st.session_state.messages.append({"role": "assistant", "content": testo_risposta})
            except Exception as errore:
                st.error(f"Errore di connessione: {errore}")
