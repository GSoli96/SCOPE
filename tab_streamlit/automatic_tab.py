import os
from pathlib import Path
from time import sleep
import streamlit as st
from tenacity import sleep_using_event

from social_mapper_automatic import socialMapper_AutomaticExecutor
from tab_streamlit.utils_tab import get_social_svg, _default_imagefolder_if_empty, _persist_uploaded_file
from utils.utils import save_history_entry

def tab_automatic():

    with st.container():
        st.markdown("**Parametri Face Recognition**")

        c1, c2, = st.columns([1, 1], vertical_alignment="top")

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
                ),
                "company": (
                    "🏢 **Company Name** → Inserisci il nome di un'azienda. "
                    "Il sistema cercherà automaticamente i profili associati a quella realtà "
                    "per individuare potenziali dipendenti o collaboratori."
                ),
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
                                            value=f"{os.getcwd()}/Input-Examples/imagefolder")

                if folder_path and os.path.isdir(folder_path):
                    st.session_state.imagefolder = folder_path

                if "imagefolder" in st.session_state and st.session_state.imagefolder:
                    st.write(f"📁 Cartella selezionata: {st.session_state.imagefolder}")


            elif format_input == "company":
                company = st.text_input("🏢 Insert Company Name", key="company_name")
                if company:
                    st.session_state.company_name = company
                    st.info(f"🏢 Hai inserito: {company}")

    with st.container():
        # Colonna sinistra: selezione social
        st.markdown("### 📱 Piattaforme Social")
        all_social = st.checkbox("Seleziona Tutti i Social", value=False)

        # Colonne interne per i checkbox
        col_sx, col_cx, col_dx = st.columns(3)
        with col_sx:
            linkedin = st.checkbox("LinkedIn", value=False, disabled=all_social)
            facebook = st.checkbox("Facebook", value=False, disabled=all_social)
        with col_cx:
            instagram = st.checkbox("Instagram", value=False, disabled=all_social)
            threads = st.checkbox("Threads", value=False, disabled=all_social)
        with col_dx:
            x_twitter = st.checkbox("X (Twitter)", value=False, disabled=all_social)

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
                    folder_name = st.session_state.get('imagefolder', 'Nessuna cartella selezionata').split('/')[-1]
                    input_detail = f"🖼️ <b>Cartella Immagini:</b> {folder_name}"
                elif format_input == "company":
                    input_detail = f"🏢 <b>Company:</b> {st.session_state.get('company_name', 'N/A')}"
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
                    social_html = "<li>Tutti</li>"
                else:
                    selected_social = [name for name, val in {
                        "LinkedIn": linkedin,
                        "Facebook": facebook,
                        "Instagram": instagram,
                        "Threads": threads,
                        "X (Twitter)": x_twitter
                    }.items() if val]

                    if selected_social:
                        items = []
                        for s in selected_social:
                            canon_name = s.lower().strip()

                            svg = get_social_svg(canon_name)
                            items.append(
                                f'<span style="display:inline-flex;align-items:center;gap:4px;">{svg} {s}</span>')
                        social_html = "&nbsp; ".join(items)
                    else:
                        social_html = "<li>Nessuno</li>"

                st.markdown(
                    f"""
                        <div style="
                            background-color:#373738;
                            padding: 15px;
                            border-radius: 10px;
                            box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
                            line-height: 1.6;
                        ">
                        <p>📱 <b>Social Selezionati:</b></p>
                        <ul style="margin-top:0; padding-left:20px;">
                            {social_html}
                        </ul>
                        </div>
                        """,
                    unsafe_allow_html=True
                )
    st.markdown('###')
    with st.container(border=False):
        submitted = st.button("▶️ Run SODA (Automatica)")

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
            if not folder or not os.path.isdir(folder):
                can_submit = False
                error_messages.append("❌ Inserisci un percorso valido per la cartella immagini.")

        if format_input == "company" and not st.session_state.get("company_name"):
            can_submit = False
            error_messages.append("❌ Inserisci il nome della company.")

        if format_input == "csv" and csv_file is not None:
            dest = Path(os.getcwd()) / "Input-Examples" / "uploaded" / csv_file.name
            saved = _persist_uploaded_file(csv_file, dest)
            input_path = str(saved)

            image_path = _default_imagefolder_if_empty(input_path)

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
            st.success("✅ Tutti i controlli superati, avvio SODA...")
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

            if st.session_state.result_automatic_research is None:
                st.warning("Torna dopo per i risultati.")

            with st.spinner():
                st.session_state.result_automatic_research = exec_auto.run()

            if st.session_state.result_automatic_research is not None:
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