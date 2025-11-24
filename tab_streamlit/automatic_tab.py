import os
from time import sleep

import pandas as pd
import streamlit as st
from PIL import Image

from social_mapper_automatic import socialMapper_AutomaticExecutor
from tab_streamlit.utils_tab import format_social_sites_icons, _default_imagefolder_if_empty, save_image
from utils.utils import save_history_entry

out_folder = os.path.join(os.getcwd(), "Input-Examples", "imagefolder")

def tab_automatic():

    with st.container():
        st.markdown("**Parametri Face Recognition**")

        c1, c2 = st.columns([1, 1], vertical_alignment="top")

        with c1:
            # --- Face Recognition Mode ---
            mode = st.selectbox(
                "Face Recognition Mode",
                ["fast", "accurate"],
                index=0,
                key="face_mode"
            )

            # Descrizione dinamica
            if mode == "fast":
                st.caption(
                    "⚡ **fast** → Usa un solo modello di face recognition, più veloce ma meno preciso.\n\n**Modello selezionato** -> Facenet")
            else:
                st.caption(
                    "🎯 **accurate** → Usa più modelli di face recognition per maggiore accuratezza (più lento).\n\n**Modelli selezionati** -> Facenet, VGG-Face, ArcFace")

        with c2:
            # --- Threshold ---
            thresholds = ["loose", "standard", "strict", "superstrict"]
            threshold = st.selectbox(
                "Threshold",
                thresholds,
                index=thresholds.index("standard"),
                key="face_threshold"
            )

            threshold_desc = {
                "loose": "🔹 **loose** → Trova più corrispondenze, ma alcune potrebbero essere errate.",
                "standard": "⚖️ **standard** → Buon equilibrio tra sensibilità e precisione.",
                "strict": "🔸 **strict** → Meno risultati ma più affidabili.",
                "superstrict": "🔒 **superstrict** → Solo corrispondenze molto sicure, ma potresti perderne alcune reali."
            }
            st.caption(threshold_desc[threshold])

    with st.container():
        st.markdown("**Task Setup**")
        c1, c2, = st.columns([1, 1], vertical_alignment="top")

        with c1:
            # --- Task Setup ---
            people_to_search = st.selectbox(
                "People to Search",
                [2, 5, 10, 15, 20],
                index=1,
                key="people_to_search"
            )
            st.caption(
                f"👥 Numero di persone considerate per ogni identificazione. "
                f"Un gruppo più grande (**{people_to_search} persone**) aumenta le probabilità "
                f"di trovare il profilo corretto dell'utente target, ma richiede più tempo di elaborazione."
            )

        with c2:
            task_types = ["Candidate Extraction", "Information Extraction", "Full Search"]
            task_type_auto = st.selectbox(
                "Task Type",
                task_types,
                index=0,
                key="task_type_auto"
            )

            task_desc = {
                "Candidate Extraction": "📸 **Candidate Extraction** → Identifica potenziali candidati dai dati iniziali (immagini o CSV).",
                "Information Extraction": "🧾 **Information Extraction** → Estrae dettagli dai profili trovati.",
                "Full Search": "🚀 **Full Search** → Esegue sia estrazione candidati che informazioni in un unico passaggio."
            }
            st.caption(task_desc[task_type_auto])

    with st.container():
        st.markdown("**Formato Input**")
        c1, c2, = st.columns([1, 1], vertical_alignment="top")
        with c1:
            # --- Selettore tipo input ---
            format_options = ["csv", "imagefolder", "company"]
            format_input = st.selectbox(
                "Input Format",
                format_options,
                index=1,
                key="format_input",
            )

            # --- Descrizioni dinamiche per ogni tipo di input ---
            format_desc = {
                "csv": (
                    "📄 **CSV** → Fornisci un file contenente una lista di persone "
                    "da analizzare (es. nomi, ruoli, link ai profili). "
                    "Ideale per ricerche multiple o batch."
                ),
                "imagefolder": (
                    "🖼️ **Image Folder** → Seleziona una cartella contenente immagini "
                    "di riferimento dei soggetti da identificare. "
                    "Ogni immagine rappresenta una persona da confrontare nei social."
                )
            }
            st.caption(format_desc[format_input])

        with c2:
            # --- Gestione dinamica del tipo di input ---
            if format_input == "csv":
                csv_file = st.file_uploader("📄 Carica file CSV", type=["csv"], key="csv_file")
                if csv_file:
                    st.info(f"📄 Hai caricato: {csv_file.name}")

            elif format_input == "imagefolder":
                # Inserisci il path della cartella manualmente
                folder_path = st.text_input("📁 Inserisci il percorso della cartella",
                                            value=os.path.join(os.getcwd(), "Input-Examples", "imagefolder"))

                if folder_path and os.path.isdir(folder_path):
                    st.success(f"📁 Cartella selezionata: {folder_path}")
                    st.session_state.imagefolder = folder_path
                else:
                    st.error('Please select another folder!')
                    folder_path = None

    with st.container():
        # Colonna sinistra: selezione social
        st.markdown("### 📱 Piattaforme Social")
        all_social = st.checkbox("Seleziona Tutti i Social", value=False)

        col1, col2, col3, col4, col5, col6 = st.columns(6)
        with col1:
            linkedin = st.checkbox(f"LinkedIn {format_social_sites_icons(sites={'ln':''}, width_height = 20)}", value=False, disabled=all_social)
        with col2:
            facebook = st.checkbox("Facebook", value=False, disabled=all_social)
        with col3:
            instagram = st.checkbox("Instagram", value=False, disabled=all_social)
        with col4:
            threads = st.checkbox("Threads", value=False, disabled=all_social)
        with col5:
            x_twitter = st.checkbox("X", value=False, disabled=all_social)

    with st.expander("🧑‍🧑‍🧒 Selected Target", expanded=False):
        VALID_EXT = (".jpg", ".jpeg", ".png", ".webp")

        if format_input == "csv":
            if csv_file is not None:
                input_path = os.path.join(os.getcwd(),"Input-Examples","uploaded",'automatic_csv')

                csv_path = _default_imagefolder_if_empty(input_path)
                os.makedirs(csv_path, exist_ok=True)

                df = pd.read_csv(csv_file)
                cols = st.columns(df.shape[0])
                images = []  # per salvare le path scaricate

                for i, row in df.iterrows():
                    name = str(row["name"]).strip()
                    url = str(row["url"]).strip()

                    # Estrai estensione dall'URL
                    ext = os.path.splitext(url.split("?")[0])[1]  # rimuove querystring
                    if ext == "":
                        ext = ".jpg"  # fallback

                    # Path dove salvare immagine
                    local_path = os.path.join(csv_path, f"{name}{ext}")

                    # Scarica immagine se non esiste
                    if not os.path.exists(local_path):
                        save_image(url_image_user=url, local_path_img=local_path)

                    images.append((cols[i], local_path, name))

                # Mostra immagini sulla stessa riga
                for col, img_path, name in images:
                    with col:
                        try:
                            img = Image.open(img_path).resize((150, 150))
                            st.image(img, caption=name)
                        except Exception as e:
                            st.error(f"Errore con {name}: {e}")

        elif st.session_state.imagefolder and os.path.isdir(st.session_state.imagefolder):

            files = [f for f in os.listdir(st.session_state.imagefolder) if f.lower().endswith(VALID_EXT)]

            if not files:
                st.warning("Nessuna immagine trovata nella cartella.")
            else:
                cols = st.columns(len(files))

                for col, file in zip(cols, sorted(files)):
                    img_path = os.path.join(st.session_state.imagefolder, file)
                    img = Image.open(img_path)
                    img = img.resize((150, 150))

                    caption = os.path.splitext(file)[0]

                    with col:
                        st.image(img, caption=caption)

    # Colonna destra: riepilogo input
    with st.container():
        st.markdown("#### ⚙️ Dettagli Selezionati")
        with st.container():
            col_input, col_face, col_task, col_social = st.columns(4)

            # Colonna 1: Input
            with col_input:
                if format_input == "csv":
                    input_detail = f"📄 <b>CSV Caricato:</b> {getattr(st.session_state.get('csv_file'), 'name', 'Nessun file')}"
                elif format_input == "imagefolder":
                    folder_name = st.session_state.get('imagefolder', 'No directory selected').split('\\')[-1]

                    input_detail = f"🖼️ <b>Image Directory:</b> {folder_name}"
                else:
                    input_detail = "N/A"

                st.markdown(
                    f"""
                        <div style="
                            background-color:#373738;
                            padding: 15px;
                            border-radius: 10px;
                            box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
                            line-height: 1.6;
                        ">
                        <p>📂 <b>Formato Input:</b> {format_input}</p>
                        <p>{input_detail}</p>
                        </div>
                        """,
                    unsafe_allow_html=True
                )

            # Colonna 2: Face Recognition
            with col_face:
                st.markdown(
                    f"""
                        <div style="
                            background-color:#373738;
                            padding: 15px;
                            border-radius: 10px;
                            box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
                            line-height: 1.6;
                        ">
                        <p>⚡ <b>Face Recognition Mode:</b> {st.session_state.get('face_mode', 'N/A')}</p>
                        <p>🔹 <b>Threshold:</b> {st.session_state.get('face_threshold', 'N/A')}</p>
                        </div>
                        """,
                    unsafe_allow_html=True
                )

            # Colonna 3: Task Setup
            with col_task:
                st.markdown(
                    f"""
                        <div style="
                            background-color:#373738;
                            padding: 15px;
                            border-radius: 10px;
                            box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
                            line-height: 1.6;
                        ">
                        <p>👥 <b>People to Search:</b> {st.session_state.get('people_to_search', 'N/A')}</p>
                        <p>📌 <b>Task Type:</b> {st.session_state.get('task_type_auto', 'N/A')}</p>
                        </div>
                        """,
                    unsafe_allow_html=True
                )

            # Colonna 4: Social selezionati
            with col_social:
                if all_social:
                    selected_social = {
                        "ln": True,
                        "fb": True,
                        "ig": True,
                        "th": True,
                        "x": True,
                    }
                else:
                    selected_social = [(name, val) for name, val in {
                        "ln": linkedin,
                        "fb": facebook,
                        "ig": instagram,
                        "th": threads,
                        "x": x_twitter
                    }.items() if val]

                icons = format_social_sites_icons(
                    sites=dict(selected_social), width_height = 20) if selected_social else "Choose at least one SN Platform"

                html_block = f"""
                <div style="
                    background-color:#373738;
                    padding: 15px;
                    border-radius: 10px;
                    box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
                    line-height: 1.4;
                ">
                    <p>📱 <b>Social Selezionati:</b></p>
                    <p>{icons}</p>
                </div>
                """

                st.markdown(html_block, unsafe_allow_html=True)

    with st.container(border=False):
        st.markdown('')
        submitted = st.button("▶️ Run SCOPE (Automatica)")

        output_area = st.empty()

    if submitted:
        # --- Controlli input ---
        can_submit = True
        error_messages = []

        # Controllo input
        if format_input == "csv" and not st.session_state.get("csv_file"):
            can_submit = False
            error_messages.append("❌ Carica un file CSV.")

        if format_input == "imagefolder":
            folder = st.session_state.get("imagefolder")
            print('Folder: ', folder)
            print('Format Input: ', format_input)
            if not folder or not os.path.isdir(folder):
                can_submit = False
                error_messages.append("❌ Inserisci un percorso valido per la cartella immagini.")

        if format_input == "company" and not st.session_state.get("company_name"):
            can_submit = False
            error_messages.append("❌ Inserisci il nome della company.")

        if format_input == "csv" and csv_file is not None:
            image_path = csv_path

        elif format_input == 'imagefolder':
            image_path = folder

        else:
            image_path = None

        # Controllo social
        selected_social = [linkedin, facebook, instagram, threads, x_twitter]
        if not all_social and not any(selected_social):
            can_submit = False
            error_messages.append("❌ Seleziona almeno un social o 'Seleziona Tutti i Social'.")

        # Mostra errori se presenti
        if not can_submit:
            for msg in error_messages:
                st.warning(msg)
        else:
            # Tutto ok, esegui SODA
            st.toast("✅ Tutti i controlli superati.")
            st.toast("✅ Avvio di SCOPE")
            # Qui puoi inserire la chiamata alla funzione di ricerca automatica

            # prepare social_sites dict
            social_sites = {}
            if all_social:
                social_sites["all"] = True
            else:
                if linkedin: social_sites["ln"] = True
                if facebook: social_sites["fb"] = True
                if instagram: social_sites["ig"] = True
                if threads: social_sites["th"] = True
                if x_twitter: social_sites["x"] = True

            exec_auto = socialMapper_AutomaticExecutor(
                format_input=format_input,
                image_path=image_path if image_path else None,
                task_type=task_type_auto,
                social_sites=social_sites,
                people_to_search=people_to_search,
                mode=mode,
                threshold=threshold,
            )

            if st.session_state.result_automatic_research is None or len(st.session_state.result_automatic_research) == 0:
                output_area.warning("Torna dopo per i risultati.")

            with st.spinner():
                try:
                    results = exec_auto.run()
                except Exception as e:
                    print(f"[Automatic] Si è verificato un errore durante l'esecuzione: {str(e)}")
                    results = {}
                    
                st.session_state.result_automatic_research = results

            if st.session_state.result_automatic_research is not None and len(st.session_state.result_automatic_research) > 0:
                st.success("I risultati sono disponibili.")
                print('[Automatic] Scrivo st.session_state.result_automatic_research:')
                print('-' * 30)
                print(st.session_state.result_automatic_research)
                print('-'*30)
                sleep(20)
                save_history_entry(
                    'Automatic Research',
                    st.session_state.result_automatic_research,
                    st.session_state.HISTORY_FILE)
            else:
                output_area.error(f"❌ Si è verificato un errore durante l'esecuzione")