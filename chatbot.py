import streamlit as st
from groq import Groq

# --- 1. CONFIGURAZIONE PAGINA (Layout Minimalista) ---
st.set_page_config(page_title="Ernello AI", page_icon="⚡", layout="centered")

# --- CSS STILE "CLEAN & DARK" ---
st.markdown("""
<style>
    /* Sfondo nero assoluto */
    .stApp {
        background-color: #000000;
        color: #e0e0e0;
    }
    
    /* Pulizia sidebar */
    [data-testid="stSidebar"] {
        background-color: #0a0a0a;
        border-right: 1px solid #222;
    }
    
    /* Messaggi chat: design pulito, senza bordi pesanti */
    .stChatMessage {
        background-color: transparent !important;
        padding: 10px 0px;
        border-bottom: 0px;
    }
    
    /* Colore testo messaggi */
    .stChatMessageContent {
        color: #d1d1d1;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    /* Input box */
    [data-testid="stChatInput"] {
        background-color: #1a1a1a;
        border: 1px solid #333;
        border-radius: 8px;
    }
    
    /* Rimuove spazi extra */
    .block-container {
        padding-top: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# --- 2. CONFIGURAZIONE API ---
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except:
    st.error("⚠️ Configura la chiave API in st.secrets!")
    st.stop()

# --- 3. BARRA LATERALE ---
with st.sidebar:
    st.title("⚙️ Configurazione")
    modello = st.selectbox("Modello:", ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"])
    st.divider()
    if "all_chats" not in st.session_state: st.session_state.all_chats = {"Chat 1": []}
    st.session_state.active_chat = st.radio("Le tue chat:", list(st.session_state.all_chats.keys()))
    if st.button("➕ Nuova Chat"):
        nome = f"Chat {len(st.session_state.all_chats) + 1}"
        st.session_state.all_chats[nome] = []
        st.rerun()

# --- 4. MOTORE CHAT ---
messages = st.session_state.all_chats[st.session_state.active_chat]

# Visualizzazione messaggi esistenti
for m in messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# Input utente
if prompt := st.chat_input("Scrivi a Ernello..."):
    # Messaggio utente
    st.session_state.all_chats[st.session_state.active_chat].append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Preparazione contesto
    api_messages = [{"role": m["role"], "content": m["content"]} for m in st.session_state.all_chats[st.session_state.active_chat]]
    
    # Risposta AI
    with st.chat_message("assistant"):
        placeholder = st.empty()
        full_response = ""
        stream = client.chat.completions.create(
            model=modello,
            messages=[{"role": "system", "content": "Tu sei un assistente AI preciso e ordinato."}] + api_messages,
            stream=True
        )
        
        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                full_response += chunk.choices[0].delta.content
                placeholder.markdown(full_response + "▌")
        
        placeholder.markdown(full_response)
        st.session_state.all_chats[st.session_state.active_chat].append({"role": "assistant", "content": full_response})
    
