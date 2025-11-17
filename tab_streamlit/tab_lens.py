import time

import streamlit as st
import os
import threading
from PIL import Image
from googleLens_executor import GoogleLensExecutor

SERPAPI_KEY = "f29a5635dc6d42b04fcbb686f042710f5a5293f8e42dcbf9fbc7830e4ed7ce51"

def tab_google_lens():
    if 'stop_research' not in st.session_state:
        st.session_state.stop_research = False

    if 'thread' not in st.session_state:
        st.session_state.thread = None

    if "status" not in st.session_state:
        st.session_state.status = 'Not Running'

    st.markdown(
        "Esegui ricerche di immagini tramite **Google Lens**, caricando un file, "
        "fornendo un URL oppure selezionando una directory di immagini. "
        "I risultati verranno poi analizzati tramite un LLM (Ollama)."
    )
    executor = GoogleLensExecutor(api_key=SERPAPI_KEY)

    # Stato per tenere traccia se Google Lens ha terminato
    if "lens_done" not in st.session_state:
        st.session_state.lens_done = False

    tab_file, tab_url, tab_dir = st.tabs(["📸 Da File", "🌐 Da URL", "📂 Da Directory"])

    # ========= 🔹 FILE =========
    with tab_file:
        uploaded_file = st.file_uploader("Carica un'immagine (JPG/PNG)", type=["jpg", "jpeg", "png"])
        st.caption("L'immagine verrà cercata su Google Lens per trovare risultati simili online.")
        disable = True

        if uploaded_file is not None:
            disable = False
            img = Image.open(uploaded_file)
            temp_path = os.path.join("google_lens_results", uploaded_file.name)
            os.makedirs("temp", exist_ok=True)
            img.save(temp_path)

            with st.expander("👁️ Anteprima immagine"):
                img_size_percent = st.slider(
                    "🖼️ Dimensione immagine (%)", 20, 200, 50, step=10, key="slider_file"
                )
                img_width = int(3 * img_size_percent)
                st.image(img, caption="Immagine caricata", width=img_width)
            avvia_research(executor=executor, type='File', params=temp_path, disable=disable)

    # ========= 🔹 URL =========
    with tab_url:
        image_url = st.text_input("Inserisci URL dell'immagine", placeholder="URL", value='https://www.viridea.it/wp-content/uploads/2008/04/Golden-Retriever.jpg')
        st.caption("Inserisci l'indirizzo completo (es. https://esempio.com/foto.jpg).")
        disable = True
        if image_url:
            disable = False
            with st.expander("👁️ Anteprima immagine da URL"):
                img_size_percent = st.slider(
                    "🖼️ Dimensione immagine (%)", 20, 200, 50, step=10, key="slider_URL"
                )
                img_width = int(3 * img_size_percent)
                try:
                    st.image(image_url, caption="Anteprima da URL", width=img_width, )
                except Exception:
                    st.warning("⚠️ Impossibile caricare l'immagine da URL.")
            temp_path = "google_lens_results"
            avvia_research(executor=executor, type='URL', params=temp_path, disable=disable)

    # ========= 🔹 DIRECTORY =========
    with tab_dir:
        dir_path = st.text_input("Inserisci percorso directory locale contenente immagini")
        st.caption("Tutte le immagini .jpg/.jpeg/.png nella directory verranno inviate a Google Lens.")
        disable = True
        if dir_path and os.path.isdir(dir_path):
            images_to_show = executor.extract_images_paths(dir_path)
            if images_to_show:
                disable = False
                st.markdown(f"**Trovate {len(images_to_show)} immagini:**")

                # Mostra le anteprime in un expander
                with st.expander("👁️ Anteprima immagini directory"):
                    img_size_percent = st.slider(
                        "🖼️ Dimensione immagine (%)", 20, 200, 50, step=10, key="slider_DIR"
                    )
                    img_width = int(3 * img_size_percent)
                    cols_per_row = 4
                    cols = st.columns(cols_per_row)
                    for idx, img_path in enumerate(images_to_show):
                        with cols[idx % cols_per_row]:
                            st.image(img_path, caption=os.path.basename(img_path), width=img_width)

                avvia_research(executor=executor, type='Directory', params=dir_path, disable=disable)
            else:
                st.warning("⚠️ Nessuna immagine trovata nella directory specificata.")
        elif dir_path:
            st.error("❌ Percorso non valido. Assicurati che la directory esista.")

    # ========= 🧠 LLM (solo se ricerca completata) =========
    if st.session_state.lens_done:
        st.divider()
        st.markdown("### 🧠 **Analizza con LLM (Ollama)**")
        st.caption("Analizza i file HTML ottenuti da Google Lens per estrarre informazioni rilevanti.")

        analyze_dir = st.text_input("📁 Inserisci directory con i risultati (es. output Google Lens)")
        custom_prompt = st.text_area(
            "✏️ Prompt personalizzato (opzionale)",
            placeholder="[TEXT_IN_FILE] verrà sostituito dal testo estratto."
        )

        if st.button("🧩 Avvia analisi con LLM"):
            if analyze_dir and os.path.isdir(analyze_dir):
                with st.spinner("Analisi dei file HTML in corso... 🧠"):
                    prompt_ready = executor._analyze_dir_with_llm_ollama_ui(
                        analyze_dir, customized_prompt=custom_prompt
                    )
                    st.text_area("📜 Prompt inviato all'LLM:", prompt_ready, height=200)
                st.success("✅ Analisi completata.")
            else:
                st.error("❌ Inserisci una directory valida contenente file HTML da analizzare.")
    else:
        st.info("🔍 Esegui prima una ricerca con Google Lens per abilitare l'analisi LLM.")


def avvia_research(executor, type, params, disable):

    col1, col2, col3 = st.columns(3)
    with col1:
        research = st.button(f"🔍 Avvia ricerca ({type})", key=f'research_{type}', disabled=disable)

    with col2:
        stop = st.button('Stop Research', disabled=st.session_state.thread is None, key=f'stop_{type}')

    with col3:
        col4, col5 = st.columns(2)
        with col4:
            st.warning('Thread is Alive' if st.session_state.thread is not None else 'Thread is not Alive')
        with col5:
            st.warning(st.session_state.thread)

    def run_search(exe, param, tp):
        st.session_state.status = "Inviando immagine a SerpAPI..."
        results = None
        if tp == "Directory":
            results = exe.process_directory(param)
            st.session_state.last_results_dir = "results/dir"
        elif tp == "URL":
            results = exe.process_url(param)
            st.session_state.last_results_dir = "results/url_search"
        elif tp == "File":
            results = exe.process_file(param)
            st.session_state.last_results_dir = os.path.join("results", os.path.basename(param))
        st.session_state.lens_done = True
        st.session_state.results = results
        st.session_state.status = "Completato!"

    if research:
        st.toast(f'{type}')
        st.session_state.thread = threading.Thread(target=run_search, args=(executor, params, type))
        st.session_state.thread.start()
        st.toast("✅ Ricerca avviata in background!")

    if stop:
        if st.session_state.thread is not None:
            st.toast('Thread is alive')
            while st.session_state.thread.is_alive():
                st.session_state.thread.join(1)
                time.sleep(1)
                if not st.session_state.thread.is_alive():
                    st.session_state.thread = None
                    st.toast('Thread is not alive')
                    break
        else:
            st.toast('Thread is not alive')