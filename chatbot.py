import streamlit as st
from groq import Groq
import base64

# Configurazione Pagina
st.set_page_config(page_title="Ernello", page_icon="💬", layout="centered")

# --- CSS GLOBALE: Sfondo WhatsApp ---
st.markdown("""
<style>
    .stApp { background-color: #efeae2; } /* Colore sfondo esatto di WhatsApp */
    /* Rimuoviamo il padding predefinito per renderlo più compatto */
    .block-container { padding-top: 2rem; padding-bottom: 2rem; }
</style>
""", unsafe_allow_html=True)

CHIAVE_API = st.secrets["GROQ_API_KEY"]
client = Groq(api_key=CHIAVE_API)
sistema_ernello = [{"role": "system", "content": "Tu sei Ernello. Rispondi in italiano in modo amichevole, conciso come su WhatsApp."}]

# Inizializzazione Chat
if "all_chats" not in st.session_state: st.session_state.all_chats = {"Chat 1": []}
if "active_chat" not in st.session_state: st.session_state.active_chat = "Chat 1"

# Sidebar
with st.sidebar:
    st.title("💬 Chat di Ernello")
    chat_scelta = st.selectbox("Seleziona:", list(st.session_state.all_chats.keys()))
    st.session_state.active_chat = chat_scelta
    if st.button("➕ Nuova Chat"):
        nome = f"Chat {len(st.session_state.all_chats) + 1}"
        st.session_state.all_chats[nome] = []
        st.session_state.active_chat = nome
        st.rerun()
    st.write("---")
    foto_utente = st.file_uploader("📸 Invia foto", type=["png", "jpg", "jpeg"])

messages = st.session_state.all_chats[st.session_state.active_chat]

# --- IL NUOVO MOTORE IN PURO HTML ---
for m in messages:
    if m["type"] == "text":
        if m["role"] == "user":
            # TUO MESSAGGIO: Spinto a destra (flex-end), verde WhatsApp, coda in alto a destra
            st.markdown(f"""
            <div style='display: flex; justify-content: flex-end; margin-bottom: 10px;'>
                <div style='background-color: #dcf8c6; color: black; padding: 10px 15px; border-radius: 15px 0px 15px 15px; max-width: 75%; box-shadow: 1px 1px 2px rgba(0,0,0,0.1); font-family: Arial, sans-serif; font-size: 15px;'>
                    {m["content"]}
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            # MESSAGGIO ERNELLO: Spinto a sinistra (flex-start), bianco, coda in alto a sinistra
            st.markdown(f"""
            <div style='display: flex; justify-content: flex-start; margin-bottom: 10px;'>
                <div style='background-color: #ffffff; color: black; padding: 10px 15px; border-radius: 0px 15px 15px 15px; max-width: 75%; box-shadow: 1px 1px 2px rgba(0,0,0,0.1); font-family: Arial, sans-serif; font-size: 15px;'>
                    {m["content"]}
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        # Se è un'immagine, la mostriamo normalmente
        st.image(m["content"])

# --- INVIO NUOVO MESSAGGIO ---
if prompt := st.chat_input("Scrivi a Ernello..."):
    base64_foto = None
    if foto_utente: base64_foto = base64.b64encode(foto_utente.read()).decode("utf-8")
    
    # Salviamo il tuo messaggio
    st.session_state.all_chats[st.session_state.active_chat].append({"role": "user", "type": "text", "content": prompt})
    
    # Mostriamo subito il tuo messaggio in verde a destra
    st.markdown(f"""
    <div style='display: flex; justify-content: flex-end; margin-bottom: 10px;'>
        <div style='background-color: #dcf8c6; color: black; padding: 10px 15px; border-radius: 15px 0px 15px 15px; max-width: 75%; box-shadow: 1px 1px 2px rgba(0,0,0,0.1); font-family: Arial, sans-serif; font-size: 15px;'>
            {prompt}
        </div>
    </div>
    """, unsafe_allow_html=True)

    api_messages = sistema_ernello + [{"role": m["role"], "content": m["content"]} for m in messages if m["type"] == "text"]
    
    # Generazione e stampa della risposta
    try:
        if base64_foto:
            risposta = client.chat.completions.create(model="llama-3.2-11b-vision-preview", 
                messages=[{"role": "user", "content": [{"type": "text", "text": prompt}, {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_foto}"}}]}])
        else:
            risposta = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=api_messages)
        
        testo = risposta.choices[0].message.content
        
        # Mostriamo la risposta di Ernello in bianco a sinistra
        st.markdown(f"""
        <div style='display: flex; justify-content: flex-start; margin-bottom: 10px;'>
            <div style='background-color: #ffffff; color: black; padding: 10px 15px; border-radius: 0px 15px 15px 15px; max-width: 75%; box-shadow: 1px 1px 2px rgba(0,0,0,0.1); font-family: Arial, sans-serif; font-size: 15px;'>
                {testo}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.session_state.all_chats[st.session_state.active_chat].append({"role": "assistant", "type": "text", "content": testo})
    except Exception as e:
        st.error(f"Errore di connessione: {e}")
