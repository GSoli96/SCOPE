import os
import platform
import subprocess
import time

import streamlit as st
import streamlit.components.v1 as components

def copy_box(label, value, key):
    st.write(f"**{label}**")
    st.code(value, language="text")

def verba_rag_tab():
    st.caption(
        "Questa tab incorpora l'interfaccia web di Verba RAG "
        "in modo da poterla usare direttamente dentro SODA United."
    )

    if st.session_state.services_started is False:

        # Avvia Verba una sola volta
        while True:
            out = avvia_verba()
            if out is True:
                break
            time.sleep(1)
        st.toast("Verba avviato!", icon="✔️")

        # Avvia Ollama una sola volta
        while True:
            out = avvia_ollama()
            if out is True:
                break
            time.sleep(1)
        st.toast("Ollama avviato!", icon="✔️")

        st.session_state.services_started = True
        print('TRUE')

    with st.container(border=True):
        col1, col2 = st.columns([2,2])
        with col1:
            # URL dell'interfaccia Verba (modifica il default come preferisci)
            verba_url = st.text_input(
                "URL dell'interfaccia Verba RAG",
                value=st.session_state.verba_localhost,
                help="Inserisci l'URL dove è esposto il frontend di GoldenVerba/Verba RAG."
            )

            copy_box("Weaviate URL", st.session_state.weaviate_url, "weaviate_url")


        with col2:
            height = st.slider(
                "Altezza finestra",
                min_value=400,
                max_value=1200,
                value=500,
                step=50,
                help="Regola l'altezza dell'iframe che contiene Verba."
            )
            copy_box("Weaviate API Key", st.session_state.weaviate_api, "weaviate_key")
    # st.divider()

    if not verba_url.strip():
        st.warning("Inserisci un URL valido per Verba RAG.")
        return

    # 🎯 IFRAME SEMPLICE, ZERO CSS
    components.iframe(
        src=verba_url,
        height=height,
    )

    st.link_button("🔗 Apri Verba in una nuova tab", verba_url)

    st.caption("Se non vedi nulla, verifica che il server Verba RAG sia in esecuzione all'URL indicato.")

# -----------------------------------
# AVVIO SERVIZI
# -----------------------------------
def avvia_verba():
    system = platform.system()
    try:
        if system == "Windows":
            subprocess.Popen("verba start", creationflags=subprocess.CREATE_NEW_CONSOLE, shell=True)
        else:
            subprocess.Popen(["verba", "start"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, preexec_fn=os.setpgrp)
        return True
    except Exception as e:
        return f"Errore: {e}"

def avvia_ollama():
    system = platform.system()
    try:
        if system == "Windows":
            subprocess.Popen("ollama serve", creationflags=subprocess.CREATE_NEW_CONSOLE, shell=True)
        else:
            subprocess.Popen(["ollama", "serve"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, preexec_fn=os.setpgrp)
        return True
    except Exception as e:
        return f"Errore: {e}"