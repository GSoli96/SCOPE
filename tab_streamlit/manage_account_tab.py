import json
from pathlib import Path
from urllib.parse import quote
import streamlit as st
from configuration.configuration import Configuration
from tab_streamlit.utils_tab import get_social_svg


def _load_accounts_json(cfg):
    path = Path(cfg.get_account_data_path())
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8")), path
        except Exception:
            return {}, path
    return {}, path

def _save_accounts_json(cfg,data):
    path = Path(cfg.get_account_data_path())
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    return path

def account_manager_tab():
    """
    Tab: Account Social
    - Mostra card a 3 per riga per ciascun account.
    - Evita duplicazioni (es. 'X' vs 'x' vs 'twitter').
    - Non mostra il JSON: si editano 'Account' e 'Password' per ogni social.
    - Usa _load_accounts_json(config) e _save_accounts_json(config, data).
    """
    import json



    config = Configuration.get_instance()
    data, path = _load_accounts_json(config)
    st.caption(f"File: `{path}`")

    # --- Normalizzazione nomi social (per evitare duplicati "X"/"x"/"twitter") ---
    CANONICALS = ["linkedin", "facebook", "instagram", "threads", "x"]
    SYNONYMS = {
        "linkedin":  {"linkedin", "ln", "linkedIn".lower()},
        "facebook":  {"facebook", "fb"},
        "instagram": {"instagram", "ig", "insta"},
        "threads":   {"threads", "thread"},
        "x":         {"x", "twitter", "tw", "x (twitter)", "X"},
    }

    def canonicalize_key(k: str) -> str:
        if not isinstance(k, str):
            return ""
        kl = k.strip()
        # match case-insensitive su ogni gruppo
        kl_cf = kl.casefold()
        for canon, syns in SYNONYMS.items():
            if kl_cf in {s.casefold() for s in syns}:
                return canon
        return kl_cf  # chiave "altra"

    # Helper estrazione username/password con tolleranza
    def get_username(d: dict) -> str:
        if not isinstance(d, dict):
            return ""
        return d.get("username") or d.get("user") or d.get("email") or ""

    def get_password(d: dict) -> str:
        if not isinstance(d, dict):
            return ""
        return d.get("password", "")

    # Determina, per ogni canonico standard, quale chiave "originale" usare come primaria
    used_original_keys = set()
    primary_key_for_canon = {}
    values_for_canon = {}

    if isinstance(data, dict):
        # Scansiona data una volta per trovare assoc. migliori per i canonici
        for canon in CANONICALS:
            best_key = None
            best_val = {"username": "", "password": ""}
            for orig_key, acc in data.items():
                if canonicalize_key(orig_key) == canon:
                    u = get_username(acc)
                    p = get_password(acc)
                    # preferisci una con contenuto
                    if best_key is None or (u or p):
                        best_key = orig_key
                        best_val = {"username": u, "password": p}
                        # se ha contenuto, fermati subito
                        if u or p:
                            break
            if best_key is not None:
                primary_key_for_canon[canon] = best_key
                values_for_canon[canon] = best_val
                used_original_keys.add(best_key)
            else:
                # non presente nei dati → inizializza vuoto
                primary_key_for_canon[canon] = canon
                values_for_canon[canon] = {"username": "", "password": ""}

    # Altri account (non canonici) senza duplicati
    other_entries = []
    if isinstance(data, dict):
        for orig_key, acc in data.items():
            if orig_key in used_original_keys:
                continue
            if canonicalize_key(orig_key) in CANONICALS:
                # è sinonimo di un canonico già usato → salta (evita duplicati)
                continue
            # account "altro"
            other_entries.append((
                orig_key,  # chiave da salvare
                {"username": get_username(acc), "password": get_password(acc)}
            ))

    # --- UI state ---
    col_top_l, col_top_r = st.columns([3, 1])
    with col_top_l:
        st.markdown("Compila le credenziali per ciascun account (3 card per riga).")
    with col_top_r:
        show_password = st.checkbox("Mostra password", value=False, help="Visualizza in chiaro i campi password.")
    pwd_type = "default" if show_password else "password"

    # --- Form di editing atomico ---
    with st.form("accounts_form", clear_on_submit=False):
        # 1) Canonici in ordine definito
        tiles = []
        label_map = {
            "linkedin":  "LinkedIn",
            "facebook":  "Facebook",
            "instagram": "Instagram",
            "threads":   "Threads",
            "x":         "X (Twitter)",
        }
        for canon in CANONICALS:
            label = label_map[canon]
            svg = get_social_svg(canon)
            svg_uri = f"data:image/svg+xml;utf8,{quote(svg)}"
            prim_key = primary_key_for_canon.get(canon, canon)
            val = values_for_canon.get(canon, {"username": "", "password": ""})
            tiles.append( (canon, label, svg_uri, prim_key, val) )

        # 2) Altri account (ordinati alfabeticamente per stabilità)
        for orig_key, val in sorted(other_entries, key=lambda x: x[0].casefold()):
            svg = get_social_svg(orig_key)  # badge generico col nome
            svg_uri = f"data:image/svg+xml;utf8,{quote(svg)}"
            tiles.append( (orig_key, orig_key, svg_uri, orig_key, val) )

        # Render a griglia 3 per riga
        new_values = {}   # mappa: chiave_di_salvataggio -> {"username":..., "password":...}
        for i in range(0, len(tiles), 3):
            row = tiles[i:i+3]
            cols = st.columns(3)
            for (name, label, svg_uri, save_key, val), col in zip(row, cols):
                with col.container():
                    st.markdown(
                        f'<div style="display:flex;align-items:center;gap:8px;">'
                        f'<img src="{svg_uri}" width="22" height="22"/>'
                        f'<h4 style="margin:0;">{label}</h4>'
                        f'</div>',
                        unsafe_allow_html=True
                    )
                    u = st.text_input(
                        "Account",
                        value=val.get("username", ""),
                        placeholder="username o email",
                        key=f"acc_{save_key}_username",
                    )
                    p = st.text_input(
                        "Password",
                        value=val.get("password", ""),
                        type=pwd_type,
                        key=f"acc_{save_key}_password",
                    )
                    st.markdown("---")
                    new_values[save_key] = {"username": u, "password": p}

        # Azioni
        col_a1, col_a2 = st.columns([1, 1])
        with col_a1:
            save_clicked = st.form_submit_button("💾 Salva")
        with col_a2:
            reload_clicked = st.form_submit_button("🔄 Ricarica")

    # --- Post-azioni ---
    if 'save_clicked' in locals() and save_clicked:
        try:
            # Merge non distruttivo: parti dai dati originali e aggiorna solo le chiavi mostrate
            merged = dict(data) if isinstance(data, dict) else {}
            # Per i canonici: potremmo aver usato chiavi non esistenti prima (es. 'x' al posto di 'X')
            # Applichiamo: aggiorna la chiave primaria usata a video e, se esistono sinonimi duplicati, opzionalmente rimuovili.
            # Per non essere invasivi, ci limitiamo ad aggiornare la chiave mostrata.
            for k, creds in new_values.items():
                if not isinstance(merged.get(k), dict):
                    merged[k] = {}
                merged[k]["username"] = creds.get("username", "")
                merged[k]["password"] = creds.get("password", "")
            _save_accounts_json(config, merged)
            st.success("Credenziali salvate.")
        except Exception as e:
            st.error(f"Errore durante il salvataggio: {e}")

    if 'reload_clicked' in locals() and reload_clicked:
        st.rerun()

    st.markdown("---")
    st.markdown("Le funzioni esistenti leggono automaticamente questo file tramite `Configuration.get_account_data_path()`.")
