import os
from pathlib import Path

import pandas as pd
import streamlit as st

from social_mapper_manual import socialMapper_ManualExecutor
from social_mapper_manual_multy import socialMapper_ManualExecutor_multiple
from tab_streamlit.utils_tab import get_social_svg, _capture_run, _default_imagefolder_if_empty, \
    format_social_sites_icons, single_social_icon, extract_username, clean_dict
from utils.utils import save_history_entry
from time import sleep
import os
import time
from pathlib import Path
from urllib.parse import urlparse, quote
import streamlit as st
from itertools import count

count = count()
content = None

# Session-state: chiavi per i campi così possiamo fare "Carica esempi"
keys = {
    "ln": "manual_ln",
    "fb": "manual_fb",
    "ig": "manual_ig",
    "th": "manual_th",
    "x": "manual_xt",
    "image": "manual_image_path",
    "use_adv": "manual_use_advanced",
    "mode": "manual_mode",
    "pts": "manual_people_to_search",
    "task": ["manual_single_task_type", "manual_multi_task_type"],
}

def user_card(row, single_social_icon, idx):
    platforms = {
        "ln": ("LinkedIn", row.get("LinkedIn")),
        "fb": ("Facebook", row.get("Facebook")),
        "ig": ("Instagram", row.get("Instagram")),
        "th": ("Threads", row.get("Threads")),
        "x":  ("X", row.get("X")),
    }

    html = f"""<div style="background:#2e2e2e;padding:18px;margin:15px 0;border-radius:12px;
    box-shadow:0 2px 5px rgba(0,0,0,0.4);">
    <h4 style="color:white;margin-top:0;">👤 User {idx}</h4>
    """

    for code, (label, url) in platforms.items():
        if url and isinstance(url, str) and url.strip():
            username = extract_username(url)
            icon = single_social_icon(code, 20)

            html += (
                "<div style='display:flex;align-items:center;justify-content:space-between;margin:10px 0;'>"
                "<div style='display:flex;align-items:center;gap:10px;'>"
                f"{icon}"
                f"<span style='font-size:15px;color:#ddd;'>{label}:</span>"
                f"<b style='color:white;'>{username}</b>"
                "</div>"
                f"<a href='{url}' target='_blank'>"
                "<button style='padding:5px 12px;border-radius:6px;background:#444;border:1px solid #666;color:white;cursor:pointer;'>"
                "🌐 Apri"
                "</button>"
                "</a>"
                "</div>"
            )
        else:
            icon = single_social_icon(code, 20)
            html += (
                "<div style='display:flex;align-items:center;justify-content:space-between;margin:10px 0;'>"
                "<div style='display:flex;align-items:center;gap:10px;'>"
                f"{icon}"
                f"<span style='font-size:15px;color:#ddd;'>{label}</span>"
                f"<b style='color:white;'></b>"
                "</div>"
                f"<a href='' target='_blank'>"
                "<button disabled style='padding:5px 12px;border-radius:6px;background:#444;border:1px solid #666;color:#888;cursor:not-allowed;opacity:0.6;'>"
                "🌐 Apri"
                "</button>"
                "</a>"
                "</div>"
            )


    html += "</div>"

    st.markdown(html, unsafe_allow_html=True)
    return {
        "ln":  row.get("LinkedIn"),
        "fb":  row.get("Facebook"),
        "ig":  row.get("Instagram"),
        "th":  row.get("Threads"),
        "x":  row.get("X"),
    }

def show_cards_in_columns(df, single_social_icon, cards_per_row=3):

    rows = df.to_dict(orient="records")   # lista di dict, 1 per riga
    cols = st.columns(cards_per_row)

    idx = 0
    social_sites = {}
    for row in rows:
        col = cols[idx % cards_per_row]
        with col:
            platforms = user_card(row, single_social_icon, idx)
            social_sites['User_{}'.format(idx)] = platforms
        idx += 1

    return social_sites

# ---- tab principale ----
def manual_tab_csv():

    # INIT
    if "csv_content" not in st.session_state:
        st.session_state.csv_content = None
    if "csv_sep" not in st.session_state:
        st.session_state.csv_sep = ","

    col1, col2, col3 = st.columns([8,2,1])

    with col1:
        st.subheader("📑 Ricerca Manuale — più utenti via CSV")

    with col2:
        if st.button("📥 Carica esempio"):
            st.session_state.csv_content = "Input-Examples/users_manual.csv"

    with col3:
        if st.button("Reset"):
            st.session_state.csv_content = None

    # -----------------------------
    # SEPARATORE + FILE UPLOADER
    # -----------------------------
    r1c1, r1c2 = st.columns([6, 2])

    with r1c2:
        if st.session_state.csv_content is None:
            st.session_state.csv_sep = st.selectbox(
                "Separatore", [",", ";", "|", "\t"], index=0
            )
        else:
            st.selectbox(
                "Separatore", [",", ";", "|", "\t"], index=0, disabled=True
            )

    with r1c1:
        if st.session_state.csv_content is None:
            csv_file = st.file_uploader(
                "Oppure carica CSV",
                type=["csv"],
                key="csv_multi_upload"
            )
            if csv_file:
                st.session_state.csv_content = csv_file
        else:
            st.file_uploader(
                "Oppure carica CSV",
                type=["csv"],
                key="tmp_", disabled=True
            )

    # -----------------------------
    # PREVIEW & CARDS
    # -----------------------------
    if st.session_state.csv_content:

        # Leggi CSV
        if isinstance(st.session_state.csv_content, str):
            csv = pd.read_csv(st.session_state.csv_content, sep=st.session_state.csv_sep)
        else:
            csv = pd.read_csv(st.session_state.csv_content, sep=st.session_state.csv_sep)

        st.markdown("### 👀 Preview user found")

        # --- Cards per ogni utente ---
        social_sites = show_cards_in_columns(csv, single_social_icon, cards_per_row=3)

    with st.expander('Opzioni avanzate (facoltative)'):
        st.selectbox("Task Type", ["Candidate Extraction", "Information Extraction", "Full Search"], index=2,
                     key=keys["task"][1])

    submitted_c = st.button("▶️ Run SODA (Manual CSV)")
    if submitted_c:
        st.toast("✅ Tutti i controlli superati.")
        st.toast("✅ Avvio di SCOPE")

        social_sites = {user: clean_dict(data) for user, data in social_sites.items()}
        task = st.session_state.get(keys["task"][1], "Candidate Extraction")
        result_multy = {}
        with st.spinner():
            for key, social_site in social_sites.items():
                st.toast(f"✅ {key} Start!")
                exec_man = socialMapper_ManualExecutor(
                            social_sites=social_site,
                            task_type=task,
                        )
                person = exec_man.run()
                result_multy['people'].append(person['person'].person_to_dict())
                st.toast(f"✅ {key} Done!")
            st.session_state.result_manual_research_multi = result_multy

    if st.session_state.result_manual_research_multi is None:
        st.warning("Torna dopo per i risultati.")
    elif st.session_state.result_manual_research_multi is not None:
        st.success("I risultati sono disponibili.")
        print('[Manual multy] Scrivo st.session_state.result_manual_research_single:')
        print('-' * 30)
        print(st.session_state.result_manual_research_multi)
        print('-' * 30)
        sleep(20)
        save_history_entry(
            'Manual Research Multy',
            st.session_state.result_manual_research_multi,
            st.session_state.HISTORY_FILE)

def manual_tab():
    """
    Tab: Ricerca Manuale (singolo utente) - versione migliorata
    - 3 colonne per riga con card per ogni social.
    - Validazione e riassegnazione intelligente degli URL messi nel campo sbagliato.
    - Upload multiplo immagini per impostare automaticamente image_path.
    - Opzioni avanzate (facoltative) per mode/people/task_type.
    """

    # Heuristics: riconosce piattaforma da un testo (URL o username) per avvisi/riassegnazioni
    DOMAIN_MAP = {
        "linkedin.com": "ln",
        "facebook.com": "fb",
        "instagram.com": "ig",
        "threads.net": "th",
        "x.com": "x",
        "twitter.com": "x",
    }
    CANON_ORDER = [("ln", "LinkedIn"), ("fb", "Facebook"), ("ig", "Instagram"), ("th", "Threads"), ("x", "X (Twitter)")]
    CANON_FULL = {"ln": "linkedin", "fb": "facebook", "ig": "instagram", "th": "threads", "x": "x"}

    def detect_platform(text: str) -> str | None:
        if not text:
            return None
        txt = text.strip()
        # Se è URL, controlla dominio
        if txt.startswith("http://") or txt.startswith("https://"):
            try:
                netloc = urlparse(txt).netloc.lower()
                # normalizza netloc togliendo 'www.'
                if netloc.startswith("www."):
                    netloc = netloc[4:]
                for dom, code in DOMAIN_MAP.items():
                    if dom in netloc:
                        return code
            except Exception:
                pass
        # euristica: prefisso @ per IG/Threads/X (vale poco ma è utile come hint)
        if txt.startswith("@"):
            return None  # non assertivo
        return None

    col1, col2, col3 = st.columns([8,2,1])
    with col1:
        st.subheader("✏️ Ricerca Manuale — singolo utente")
    with col2:
        load_ex = st.button("📥 Carica esempi")

        if load_ex:
            st.session_state[keys["ln"]] = "https://www.linkedin.com/in/stcirillo"
            st.session_state[keys["fb"]] = "https://www.facebook.com/ste.cirillo"
            st.session_state[keys["ig"]] = "https://www.instagram.com/ste_cirillo"
            st.session_state[keys["th"]] = "https://www.threads.net/@ste_cirillo"
            st.session_state[keys["x"]] = "https://x.com/cciro94"

    with col3:
        reset_ex = st.button("Reset all")

    if reset_ex:
        st.session_state[keys["ln"]] = ""
        st.session_state[keys["fb"]] = ""
        st.session_state[keys["ig"]] = ""
        st.session_state[keys["th"]] = ""
        st.session_state[keys["x"]] = ""
        st.session_state[keys["image"]] = ""

    with st.form("manual_form", clear_on_submit=False):
        # ----- CARD SOCIAL: 3 colonne per riga -----
        row1 = st.columns(3)
        row2 = st.columns(3)

        # Helpers per rendere una card social
        def render_card(col, code: str, label: str, placeholder: str):
            icons = single_social_icon(code)
            # svg_uri = _svg_uri(CANON_FULL[code])
            with col.container():
                if code in ['x', 'X']:
                    st.markdown(
                        f'<div style="display:flex;align-items:center;gap:8px;">'
                        f'{icons}'
                        f'<h4 style="margin:0;"> </h4>'
                        f'</div>',
                        unsafe_allow_html=True
                    )
                else:
                    st.markdown(
                        f'<div style="display:flex;align-items:center;gap:8px;">'
                        f'{icons}'
                        f'<h4 style="margin:0;">{label}</h4>'
                        f'</div>',
                        unsafe_allow_html=True
                    )
                st.text_input(
                    "URL or username",
                    key=keys[code],
                    placeholder=placeholder,
                )

        render_card(row1[0], "ln", "LinkedIn", "es. https://www.linkedin.com/in/<username>")
        render_card(row1[1], "fb", "Facebook", "es. https://www.facebook.com/<username>")
        render_card(row1[2], "ig", "Instagram", "es. https://www.instagram.com/<username>")

        render_card(row2[0], "th", "Threads", "es. https://www.threads.net/@<username>")
        render_card(row2[1], "x",  "X", "es. https://x.com/<username>")

        # segnaposto per allineamento a 3 colonne
        with row2[2].container():
            st.markdown("&nbsp;", unsafe_allow_html=True)

        with st.expander('Opzioni avanzate (facoltative)'):
            st.selectbox("Task Type", ["Candidate Extraction", "Information Extraction", "Full Search"], index=2, key=keys["task"][0])

        # Riepilogo dinamico
        def _val(k): return (st.session_state.get(k) or "").strip()
        preview_vals = {code: _val(keys[code]) for code, _ in CANON_ORDER}
        filled = [lbl for (code, lbl) in CANON_ORDER if preview_vals[code]]
        st.info("Piattaforme compilate: " + (", ".join(filled) if filled else "nessuna"))

        submitted_m = st.form_submit_button("▶️ Run SODA (Manuale)")

    if submitted_m:
        # --- Costruzione e sanitizzazione social_sites ---
        raw_inputs = {code: (st.session_state.get(keys[code]) or "").strip() for code, _ in CANON_ORDER}
        # Valori non vuoti
        non_empty = {code: v for code, v in raw_inputs.items() if v}

        if not non_empty:
            st.error("Inserisci almeno un profilo (URL o username).")
            return

        # Avvisi e riassegnazioni: se un campo contiene URL del social sbagliato, sposta dove corretto (se vuoto)
        warnings = []
        corrected = dict(non_empty)  # copia mutabile
        for code, text in list(non_empty.items()):
            det = detect_platform(text)
            if det and det != code:
                # c'è un mismatch
                target_label = dict(CANON_ORDER)[det]
                src_label = dict(CANON_ORDER)[code]
                # Se il campo target è vuoto o non presente, sposta
                if det not in corrected or not corrected[det]:
                    corrected[det] = text
                    del corrected[code]
                    warnings.append(f"Rilevato URL di **{target_label}** nel campo **{src_label}**: spostato automaticamente.")
                else:
                    # non sovrascrivo: solo warning
                    warnings.append(f"Rilevato URL di **{target_label}** nel campo **{src_label}** (non spostato per evitare sovrascritture).")

        for w in warnings:
            st.warning(w)

        # Mappa finale per executor
        social_sites = {}
        if corrected.get("ln"): social_sites["ln"] = corrected["ln"]
        if corrected.get("fb"): social_sites["fb"] = corrected["fb"]
        if corrected.get("ig"): social_sites["ig"] = corrected["ig"]
        if corrected.get("th"): social_sites["th"] = corrected["th"]
        if corrected.get("x"):  social_sites["x"]  = corrected["x"]

        # --- Esecuzione executor ---
        # Opzioni avanzate (facoltative)
        try:
            task = st.session_state.get(keys["task"][0], "Candidate Extraction")
            exec_man = socialMapper_ManualExecutor(
                social_sites=social_sites,
                task_type=task,
            )

            st.success("✅ Tutti i controlli superati, avvio SODA...")

            if st.session_state.result_manual_research_single is None:
                st.warning("Torna dopo per i risultati.")

            with st.spinner():
                person = exec_man.run()
                st.session_state.result_manual_research_single['person'] = person['person'].person_to_dict()

            if st.session_state.result_manual_research_single is not None:
                st.success("I risultati sono disponibili.")
                print('[Manual Single] Scrivo st.session_state.result_manual_research_single:')
                print('-' * 30)
                print(st.session_state.result_manual_research_single)
                print('-'*30)
                sleep(20)
                save_history_entry(
                    'Manual Research Single',
                    st.session_state.result_manual_research_single,
                    st.session_state.HISTORY_FILE)

        except Exception as e:
            st.error(f"Errore durante l'esecuzione: {e}")
