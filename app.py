import os
import sys
import threading
import time
from pathlib import Path

import streamlit as st

from tab_streamlit.automatic_tab import tab_automatic
from tab_streamlit.manage_account_tab import account_manager_tab
from tab_streamlit.manual_tab import manual_tab, manual_tab_csv
from tab_streamlit.tab_findCompany import tab_hunter_search
from tab_streamlit.tab_hystory import show_tab_history
from tab_streamlit.tab_lens import tab_google_lens
from tab_streamlit.tab_results import tab_show_results
from tab_streamlit.tab_verba import verba_rag_tab
from tab_streamlit.utils_tab import _patch_messagebox

# Ricezione del messaggio JS

# Ensure we can import the project package
ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Import project modules (unchanged business logic)

label_map = {
    "linkedin": "LinkedIn",
    "facebook": "Facebook",
    "instagram": "Instagram",
    "threads": "Threads",
    "x": "X (Twitter)",
}
HISTORY_FILE = "history\history.json"

def thread_monitor():
    while True:
        if 'threads' not in st.session_state:
            st.session_state['threads'] = {}
        threads = st.session_state.threads

        if not threads:
            print("[Monitor] Nessun thread attivo, attendo...")
            time.sleep(10)  # attesa ridotta
            continue

        print("\n[Monitor] Stato thread:")
        to_remove = []

        for name, managed in threads.items():
            alive = managed.is_alive()
            elapsed = managed.elapsed()

            print(f" - {name}: alive={alive}, elapsed={elapsed:.1f}s")

            if elapsed > 240:  # più di 4 minuti
                print(f"   ⚠️ Thread {name} è bloccato (>120s)!")
                managed.status = "timeout"
                to_remove.append(name)

            if not alive:
                print(f"   ✔️ Thread {name} è terminato.")
                to_remove.append(name)

        # pulizia thread completati o bloccati
        for name in to_remove:
            del st.session_state["threads"][name]

        time.sleep(10)  # controllo ogni 10 secondi


def inizialize():
    # st.session_state.setdefault("Face_Recognition_Mode", 'fast')
    # st.session_state.setdefault("Threshold", 'standard')
    st.session_state.imagefolder = ""
    st.session_state.status = 'Not Running'
    st.session_state.stop_research = False

    #Result of Automatic
    st.session_state.result_automatic_research = None

    #Result of Manual Single
    st.session_state.result_manual_research_single = None

    #Result of Manual Multy
    st.session_state.result_manual_research_multi = None

    #Result of find company (Hunter - Spy)
    st.session_state.result_find_company = None

    #Results of research user (Hunter)
    st.session_state.result_find_user_company = None

    #Path history file
    st.session_state.HISTORY_FILE= HISTORY_FILE

    #controllo thread
    st.session_state.threads = {}

    if "monitor_started" not in st.session_state:
        st.session_state.monitor_started = True

        monitor = threading.Thread(target=thread_monitor, daemon=True)
        monitor.start()

inizialize()

_patch_messagebox()

# ---- UI ----
st.set_page_config(page_title="SODA United — Streamlit UI", layout="wide")
st.title("SODA United")
st.markdown("""
    <style>
    /* Selettore per la barra delle tab */
    div[data-baseweb="tab-list"] {
        justify-content: space-between;
    }

    /* Seleziona i singoli tab e cambia ordine */
    div[data-baseweb="tab-list"] button:nth-child(1) { order: 1; }  /* LLM 1 */
    div[data-baseweb="tab-list"] button:nth-child(2) { order: 2; }  /* LLM 2 */
    div[data-baseweb="tab-list"] button:nth-child(3) { order: 3; }  /* LLM 3 */
    div[data-baseweb="tab-list"] button:nth-child(4) { order: 4; }  /* LLM 3 */
    div[data-baseweb="tab-list"] button:nth-child(5) { order: 5; }  /* LLM 3 */
    div[data-baseweb="tab-list"] button:nth-child(6) { order: 6; }  /* LLM 3 */
    div[data-baseweb="tab-list"] button:nth-child(7) { order: 7; }  /* LLM 3 */
    </style>
""", unsafe_allow_html=True)
# st.caption("Interfaccia Streamlit per le funzioni esistenti (nessuna modifica alla logica).")
# st.write(f"**Working directory:** `{os.getcwd()}`")
# st.divider()

# tab_auto, tab_manual, tab_company, tab_results, tab_lens, tab_verba, tab_hystory, tab_accounts = st.tabs(
#     ["🔎 Ricerca Automatica", "🧭 Ricerca Manuale", "🏢 Find Company", "Result",
#      "📷 Google Lens", "💬 Verba", "Hystory" ,"🔐 Account Social"]
# )
tab_auto, tab_manual, tab_company, tab_results, tab_verba, tab_hystory, tab_accounts = st.tabs([
            "🔎 Ricerca Automatica",
            "🧭 Ricerca Manuale",
            "🏢 Find Company",
            "📊 Risultati",
            "💬 Verba",
            "📚 History",
            "🔐 Account Social"
        ]
    )

# ==============================
# TAB: Ricerca Automatica
# ==============================
with tab_auto:
    st.subheader('🕵️‍♂️ Automatic Search')
    tab_automatic()

# ==============================
# TAB: Ricerca Manuale
# ==============================
with tab_manual:
    st.subheader(' 📝Manual Search')
    tab1, tab2 = st.tabs(
        ['👤 Ricerca Manuale (singolo utente)',
         '📄 Ricerca Manuale — più utenti via CSV'])

    # ==============================
    # TAB: Ricerca Manuale
    # ==============================
    with tab1:
        # st.subheader("✏️ Ricerca Manuale — singolo utente")
        manual_tab()

    # ==============================
    # TAB: Ricerca Manuale (CSV)
    # ==============================
    with tab2:
        st.subheader("📑 Ricerca Manuale — più utenti via CSV")
        manual_tab_csv()

# # ==============================
# # TAB: Find Company
# # ==============================
with tab_company:
    st.subheader("🏙️ Find Company")
    tab_hunter_search()

# ==============================
# TAB: Result
# ==============================
with tab_results:
    st.subheader("📈 Results")
    tab_show_results()

# ==============================
# TAB: Verba RAG
# ==============================
with tab_verba:
    st.subheader("🧠 Verba RAG — GoldenVerba")
    verba_rag_tab()

# ==============================
# TAB: Hystory
# ==============================
with tab_hystory:
    st.subheader("🗂️ Cronologia Ricerche")
    show_tab_history()

# ==============================
# TAB: Account Social
# ==============================
with tab_accounts:
    st.subheader("🛡️ Gestione account")
    account_manager_tab()
