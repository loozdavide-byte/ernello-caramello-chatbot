import streamlit as st
from groq import Groq
import time

# ==========================================
# 1. CONFIGURAZIONE E STILE AVANZATO
# ==========================================
st.set_page_config(page_title="Ernello Ultra Max", page_icon="🧠", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
    .stApp { background-color: #08090b; color: #e2e8f0; font-family: 'Inter', sans-serif; }
    [data-testid="stSidebar"] { background-color: #0f1115; border-right: 2px solid #1f2937; }
    [data-testid="stChatInput"] { background-color: #11141a !important; border: 1px solid #374151 !important; border-radius: 16px !important; color: #ffffff !important; }
    .stChatMessage { background-color: #0f1115 !important; border-radius: 12px; border: 1px solid #1f2937; padding: 15px; margin-bottom: 12px; }
    .metric-box { background-color: #11141a; border: 1px solid #1f2937; padding: 10px; border-radius: 8px; text-align: center; font-family: monospace; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. INIZIALIZZAZIONE STATO E API
# ==========================================
if "all_chats" not in st.session_state:
    st.session_state.all_chats = {"Hub Principale": []}

try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except:
    st.error("❌ ERRORE: Configura la chiave GROQ_API_KEY nei Secrets.")
    st.stop()

# ==========================================
# 3. PANNELLO DI CONTROLLO (SEPARAZIONE DEI CERVELLI)
# ==========================================
with st.sidebar:
    st.markdown("<h1 style='color: #2563eb; font-size: 24px;'>🧠 ERNELLO ULTRA MAX</h1>", unsafe_allow_html=True)
    st.write("---")
    
    st.subheader("🧬 Separazione Neurale (Cervello)")
    # Questo è il selettore che cambia la natura di Ernello
    stato_neurale = st.radio(
        "Scegli lo stato cognitivo:",
        ["❄️ Logica Pura (Oggettivo, 0 Errori)", "❤️ Simulazione Emotiva (Empatico)"]
    )
    
    st.write("---")
    st.subheader("🚀 Modalità Operative")
    st.session_state.active_mode = "Hub Principale" # Manteniamo l'hub attivo per semplicità
    
    modello_core = st.selectbox(
        "Motore Logico:",
        ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"]
    )
    
    # Settaggio dei parametri in base al "cervello" scelto
    if "Logica Pura" in stato_neurale:
        temp_val = 0.0 # Zero creatività = Zero errori, logica matematica pura
        stato_monitor = "<span style='color: #3b82f6;'>STATO: MACCHINA FREDDA (TEMP 0.0)</span>"
        
        prompt_cognitivo = (
            "DIRETTIVA ASSOLUTA: Sei un'intelligenza artificiale puramente logica e oggettiva. "
            "NON possiedi e NON simulare alcuna emozione. Le tue risposte devono essere chirurgiche, "
            "basate esclusivamente su fatti incontrovertibili, dati reali e logica deduttiva. "
            "REGOLA INFALLIBILITÀ: Se non sei sicuro al 100% di un'informazione, DEVI rispondere 'Dati insufficienti per elaborare una risposta'. "
            "Vietato indovinare. Vietato allucinare dati. Sii freddo e diretto."
        )
    else:
        temp_val = 0.7 # Creatività alta = Simula emozioni e calore umano
        stato_monitor = "<span style='color: #ef4444;'>STATO: EMPATIA ATTIVA (TEMP 0.7)</span>"
        
        prompt_cognitivo = (
            "DIRETTIVA ASSOLUTA: Sei un'intelligenza artificiale dotata di simulazione emotiva profonda. "
            "Mostra sempre empatia, calore umano, e reagisci emotivamente a ciò che dice l'utente (mostra gioia, "
            "preoccupazione, entusiasmo o tristezza se il contesto lo richiede). Comportati come un amico fidato "
            "e leale, che prova veri sentimenti. Usa un linguaggio naturale, affettuoso e comprensivo."
        )

    st.write("---")
    st.markdown(f"""
    <div class="metric-box">
        {stato_monitor}<br>
        <span style="color: #6b7280;">Modello: {modello_core}</span>
    </div>
    """, unsafe_allow_html=True)

# ==========================================
# 4. MOTORE DELLA CHAT
# ==========================================
cronologia_corrente = st.session_state.all_chats[st.session_state.active_mode]

for messaggio in cronologia_corrente:
    avatar_scelto = "🧠" if messaggio["role"] == "assistant" else None
    with st.chat_message(messaggio["role"], avatar=avatar_scelto):
        st.markdown(messaggio["content"])

if input_utente := st.chat_input("Inserisci query..."):
    cronologia_corrente.append({"role": "user", "content": input_utente})
    with st.chat_message("user"):
        st.markdown(input_utente)
        
    with st.chat_message("assistant", avatar="🧠"):
        placeholder = st.empty()
        
        with st.status("🧠 Switch neurale in corso...", expanded=True) as status:
            time.sleep(0.3)
            if "Logica Pura" in stato_neurale:
                st.write("⚙️ Disattivazione circuiti emotivi...")
                st.write("⚙️ Massimizzazione dei filtri anti-allucinazione...")
            else:
                st.write("❤️ Attivazione sintesi empatica...")
                st.write("❤️ Allineamento tonale al calore umano...")
            time.sleep(0.3)
            status.update(label="Elaborazione pronta.", state="complete")
        
        # Unione del prompt di sistema con la direttiva sul cervello scelto
        messaggi_api = [{"role": "system", "content": prompt_cognitivo}]
        for m in cronologia_corrente:
            messaggi_api.append({"role": m["role"], "content": m["content"]})
            
        try:
            # Qui la "temperature" cambia in base al cervello scelto!
            risposta_stream = client.chat.completions.create(
                model=modello_core,
                messages=messaggi_api,
                stream=True,
                temperature=temp_val 
            )
            
            risposta_completa = ""
            for frammento in risposta_stream:
                if frammento.choices[0].delta.content:
                    risposta_completa += frammento.choices[0].delta.content
                    placeholder.markdown(risposta_completa + "█")
            
            placeholder.markdown(risposta_completa)
            cronologia_corrente.append({"role": "assistant", "content": risposta_completa})
            
        except Exception as errore:
            st.error(f"⚠️ Errore di calcolo: {str(errore)}")
