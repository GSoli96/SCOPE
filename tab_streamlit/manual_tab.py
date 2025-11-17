import os
from pathlib import Path

import streamlit as st

from social_mapper_manual import socialMapper_ManualExecutor
from social_mapper_manual_multy import socialMapper_ManualExecutor_multiple
from tab_streamlit.utils_tab import get_social_svg, _persist_uploaded_file, _capture_run, _default_imagefolder_if_empty
from utils.utils import save_history_entry
from time import sleep

def manual_tab_csv():

    up = st.file_uploader("Oppure carica CSV", type=["csv"], key="csv_multi")

    submitted_c = st.button("▶️ Run SODA (Manual CSV)")

    if submitted_c:
        if up is not None:
            dest = Path(os.getcwd()) / "Input-Examples" / "uploaded" / up.name
            saved = _persist_uploaded_file(up, dest)
            csv_path = str(saved)

            st.success("✅ Tutti i controlli superati, avvio SODA...")
            if st.session_state.result_manual_research_multi is None:
                st.warning("Torna dopo per i risultati.")

            exec_multi = socialMapper_ManualExecutor_multiple(path_accounts_users=csv_path)
            with st.spinner():
                results = exec_multi.run()

                entry = {}
                entry["people"] = []
                for idx, person in enumerate(results):
                    entry["people"].append({
                        f"{idx}" : person.person_to_dict()
                    })
                st.session_state.result_manual_research_multi = entry

            if st.session_state.result_manual_research_multi is not None:
                st.success("I risultati sono disponibili.")
                print('[Manual Multy] Scrivo st.session_state.result_manual_research_multi:')
                print('-' * 30)
                print(st.session_state.result_manual_research_multi)
                print('-'*30)
                sleep(20)
                save_history_entry(
                    'Manual Research Multy',
                    st.session_state.result_manual_research_multi,
                    st.session_state.HISTORY_FILE)
        else:
            st.error("Specificare il file CSV.")




def manual_tab():
    """
    Tab: Ricerca Manuale (singolo utente) - versione migliorata
    - 3 colonne per riga con card per ogni social.
    - Validazione e riassegnazione intelligente degli URL messi nel campo sbagliato.
    - Upload multiplo immagini per impostare automaticamente image_path.
    - Opzioni avanzate (facoltative) per mode/people/task_type.
    """
    import os
    import time
    from pathlib import Path
    from urllib.parse import urlparse, quote
    import streamlit as st

    # Fallback icon nel caso get_social_svg non sia stata definita altrove
    def _fallback_svg(name: str) -> str:
        base = (name or "").strip().lower()[:2] or "?"
        svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 22 22" role="img" aria-label="{name}">
  <circle cx="11" cy="11" r="10" fill="#666"/>
  <text x="11" y="14" text-anchor="middle" font-size="10" font-family="Inter, Arial, sans-serif" fill="#FFFFFF">{base.upper()}</text>
</svg>'''
        return svg

    def _svg_uri(name: str) -> str:
        try:
            svg = get_social_svg(name)  # usa la funzione globale se presente
        except Exception:
            svg = _fallback_svg(name)
        return f"data:image/svg+xml;utf8,{quote(svg)}"

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

    # Session-state: chiavi per i campi così possiamo fare "Carica esempi"
    keys = {
        "ln": "manual_ln",
        "fb": "manual_fb",
        "ig": "manual_ig",
        "th": "manual_th",
        "x":  "manual_xt",
        "image": "manual_image_path",
        "use_adv": "manual_use_advanced",
        "mode": "manual_mode",
        "pts": "manual_people_to_search",
        "task": "manual_task_type",
    }

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
            svg_uri = _svg_uri(CANON_FULL[code])
            with col.container():
                st.markdown(
                    f'<div style="display:flex;align-items:center;gap:8px;">'
                    f'<img src="{svg_uri}" width="22" height="22"/>'
                    f'<h4 style="margin:0;">{label}</h4>'
                    f'</div>',
                    unsafe_allow_html=True
                )
                st.text_input(
                    "URL o username",
                    key=keys[code],
                    placeholder=placeholder,
                )
                st.markdown("---")

        render_card(row1[0], "ln", "LinkedIn", "es. https://www.linkedin.com/in/<utente>")
        render_card(row1[1], "fb", "Facebook", "es. https://www.facebook.com/<utente>")
        render_card(row1[2], "ig", "Instagram", "es. https://www.instagram.com/<utente>")

        render_card(row2[0], "th", "Threads", "es. https://www.threads.net/@<utente>")
        render_card(row2[1], "x",  "X (Twitter)", "es. https://x.com/<utente>")
        # segnaposto per allineamento a 3 colonne
        with row2[2].container():
            st.markdown("&nbsp;", unsafe_allow_html=True)

        with st.expander('Opzioni avanzate (facoltative)'):
            st.selectbox("Task Type", ["Candidate Extraction", "Information Extraction", "Full Search"], index=2, key=keys["task"])

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
            task = st.session_state.get(keys["task"], "Candidate Extraction")
            exec_man = socialMapper_ManualExecutor(
                social_sites=social_sites,
                task_type=task,
            )

            st.success("✅ Tutti i controlli superati, avvio SODA...")

            if st.session_state.result_manual_research_single is None:
                st.warning("Torna dopo per i risultati.")

            with st.spinner():
                person = exec_man.run()
                st.session_state.result_manual_research_single = person.person_to_dict()

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
