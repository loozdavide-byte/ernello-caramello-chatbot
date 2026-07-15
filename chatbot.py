import streamlit as st
from groq import Groq
import io

# --- 1. CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="Ernello", page_icon="⚡", layout="wide")

# --- CSS "IDENTICO A GEMINI" ---
# Questo CSS forza l'input a stare in basso e arrotonda tutto
st.markdown("""
<style>
    /* Sfondo Gemini */
    .stApp { background-color: #131314; color: #e3e3e3; }
    [data-testid="stSidebar"] { background-color: #0b0b0b; border-right: 1px solid #222; }
    
    /* Input Box Stile Gemini */
    [data-testid="stChatInput"] { 
        background-color: #1f1f1f !important; 
        border-radius: 24px !important; 
        border: 1px solid #333 !important;
        padding: 5px !important;
    }
    
    /* Pulizia messaggi */
    .stChatMessage { background-color: transparent !important; }
    
    /* Sidebar */
    .stButton>button { border-radius: 20px; background: transparent; border: 1px solid #333; }
</style>
""", unsafe_allow_html=True)

# --- 2. LOGICA API ---
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except:
    st.error("⚠️ Configura GROQ_API_KEY nei Secrets!")
    st.stop()

# --- 3. SIDEBAR (Cronologia) ---
with st.sidebar:
    st.markdown("## ⚡ Ernello")
    if st.button("➕ Nuova chat", use_container_width=True):
        st.session_state.active_chat = f"Chat {len(st.session_state.all_chats)+1}"
        st.session_state.all_chats[st.session_state.active_chat] = []
        st.rerun()
    
    st.write("---")
    st.subheader("Recenti")
    if "all_chats" not in st.session_state: st.session_state.all_chats = {"Chat 1": []}
    
    for chat_name in st.session_state.all_chats.keys():
        if st.button(chat_name, use_container_width=True):
            st.session_state.active_chat = chat_name
            st.rerun()

# --- 4. MOTORE CHAT (Input in basso come Gemini) ---
if "active_chat" not in st.session_state: st.session_state.active_chat = "Chat 1"

# Visualizzazione
for m in st.session_state.all_chats[st.session_state.active_chat]:
    with st.chat_message(m["role"], avatar="⚡" if m["role"] == "assistant" else None):
        st.markdown(m["content"])

# Input - st.chat_input è l'unico che rimane fissato in basso come Gemini
if prompt := st.chat_input("Scrivi a Ernello..."):
    # Messaggio Utente
    st.session_state.all_chats[st.session_state.active_chat].append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)
    
    # Risposta AI
    with st.chat_message("assistant", avatar="⚡"):
        placeholder = st.empty()
        full_response = ""
        stream = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.all_chats[st.session_state.active_chat]],
            stream=True
        )
        for chunk in stream:
            if chunk.choices[0].delta.content:
                full_response += chunk.choices[0].delta.content
                placeholder.markdown(full_response + "▌")
        placeholder.markdown(full_response)
        st.session_state.all_chats[st.session_state.active_chat].append({"role": "assistant", "content": full_response})
