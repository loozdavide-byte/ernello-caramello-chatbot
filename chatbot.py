import streamlit as st
from groq import Groq
import urllib.parse

# Configurazione della pagina web
st.set_page_config(page_title="Il mio AI Super Bot", page_icon="🤖", layout="centered")
st.title("super ai bot di ernello caramello")
st.caption("Creato da il Merluzzo")
st.write("Chiedimi di disegnare qualcosa o semplicemente di fare due chiacchiere!")

# INCOLLA QUI LA TUA CHIAVE API DI GROQ (inizia con gsk_) TRA LE VIRGOLETTE
CHIAVE_API = st.secrets["GROQ_API_KEY"]

# Inizializziamo il client Groq
client = Groq(api_key=CHIAVE_API)

# Crea la memoria della chat
if "messages" not in st.session_state:
    st.session_state.messages = []

# Mostra i messaggi precedenti
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if message.get("is_image"):
            st.image(message["content"], caption="Immagine Generata")
        else:
            st.write(message["content"])

# Input dell'utente
if prompt := st.chat_input("Scrivi qui... (es. 'disegna un drago rosso' oppure 'ciao, come stai?')"):
    
    # Mostra il messaggio dell'utente
    with st.chat_message("user"):
        st.write(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Parole chiave per capire cosa vuole l'utente
    parole_immagine = ["disegna", "crea immagine", "creami un'immagine", "genera immagine", "foto di", "immagine di", "/immagine"]
    parole_video = ["crea video", "genera video", "fai un video", "creami un video", "video di"]

    with st.chat_message("assistant"):
        
        # CASO 1: L'utente chiede un VIDEO
        if any(parola in prompt.lower() for parola in parole_video):
            risposta_video = (
                "🎥 **Generatore Video:** Per creare video reali serve una potenza di calcolo enorme. "
                "Non esistono servizi professionali gratuiti senza registrazione. "
                "Per sbloccarli sul serio, dobbiamo collegare questo bot a un servizio come **Replicate.com** "
                "(che costa circa 2-5 centesimi a video). Se decidi di farti un account lì, ti scriverò il codice per collegarlo!"
            )
            st.write(risposta_video)
            st.session_state.messages.append({"role": "assistant", "content": risposta_video})
            
        # CASO 2: L'utente chiede un'IMMAGINE (Rilevamento Automatico!)
        elif any(parola in prompt.lower() for parola in parole_immagine):
            st.write("🎨 Sto creando la tua immagine, un attimo di pazienza...")
            
            # Puliamo il testo eliminando la parola d'ordine (es. "disegna") per dare all'IA solo il soggetto
            prompt_pulito = prompt
            for parola in parole_immagine:
                prompt_pulito = prompt_pulito.lower().replace(parola, "").strip()
            
            if not prompt_pulito:
                prompt_pulito = "un disegno astratto e colorato"
                
            # Codifichiamo il testo per il link web
            prompt_codificato = urllib.parse.quote(prompt_pulito)
            url_immagine = f"https://image.pollinations.ai/prompt/{prompt_codificato}?width=1024&height=1024&nologo=true"
            
            # Mostriamo l'immagine
            st.image(url_immagine, caption=f"Risultato per: {prompt_pulito}")
            st.session_state.messages.append({"role": "assistant", "content": url_immagine, "is_image": True})
            
        # CASO 3: Chat normale con Groq
        else:
            st.write("Pensando...")
            try:
                risposta = client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model="llama-3.3-70b-specdec",
                )
                testo_risposta = risposta.choices[0].message.content
                st.write(testo_risposta)
                st.session_state.messages.append({"role": "assistant", "content": testo_risposta})
            except Exception as errore:
                st.error(f"Errore di connessione: {errore}")
