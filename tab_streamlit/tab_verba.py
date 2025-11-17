import time

import streamlit as st
import requests
import subprocess
import platform
import os
import json

VERBA_PORT = 8000
BASE_URL = f"http://localhost:{VERBA_PORT}"
WEAVIATE_URL = "https://mmljrocuqaechcclhmht6a.c0.europe-west3.gcp.weaviate.cloud"
WEAVIATE_API_KEY = "cE9ZUzltVEtXS0dNcUdiRF9FVW1iK3lJMThsZTdHNlVya2IyRnUvZWhYbGIzN2U3ektvM1kxVHZXcTQ0PV92MjAw"

HEADERS = {"Origin": "http://localhost:8000"}

import streamlit as st
import streamlit.components.v1 as components

import streamlit as st
import streamlit.components.v1 as components

done = False

def copy_box(label, value, key):
    st.write(f"**{label}**")
    st.code(value, language="text")

def verba_rag_tab():
    st.caption(
        "Questa tab incorpora l'interfaccia web di Verba RAG "
        "in modo da poterla usare direttamente dentro SODA United."
    )

    global done
    if not done:
        while True:
            out = avvia_verba()
            if out is True:
                break
            else:
                time.sleep(1)

        st.toast("Verba avviato!" if out is True else out,icon="✔️")

        while True:
            out = avvia_ollama()
            if out is True:
                break
            else:
                time.sleep(1)

        st.toast("Ollama avviato!" if out is True else out, icon="✔️")
        done = True

    with st.container(border=True):
        col1, col2 = st.columns([2,2])
        with col1:
            # URL dell'interfaccia Verba (modifica il default come preferisci)
            verba_url = st.text_input(
                "URL dell'interfaccia Verba RAG",
                value="http://localhost:8000",
                help="Inserisci l'URL dove è esposto il frontend di GoldenVerba/Verba RAG."
            )

            copy_box("Weaviate URL", WEAVIATE_URL, "weaviate_url")


        with col2:
            height = st.slider(
                "Altezza finestra",
                min_value=400,
                max_value=1200,
                value=500,
                step=50,
                help="Regola l'altezza dell'iframe che contiene Verba."
            )
            copy_box("Weaviate API Key", WEAVIATE_API_KEY, "weaviate_key")
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