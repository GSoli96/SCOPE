import os

import streamlit as st
from PIL import Image

# ------------------------------------------------
# SVG ICONS FOR SOCIALS
# ------------------------------------------------
def get_social_svg(platform):
    platform = platform.lower().strip()

    icons = {
        "facebook": """<svg width="14" height="14" fill="#1877F2" viewBox="0 0 24 24"><path d="M22 12a10 10 0 1 0-11.5 9.9v-7h-2v-3h2v-2.3c0-2 1.2-3.1 3-3.1.9 0 1.8.1 1.8.1v2h-1c-1 0-1.3.6-1.3 1.2V12h2.2l-.4 3h-1.8v7A10 10 0 0 0 22 12"/></svg>""",
        "linkedin": """<svg width="14" height="14" fill="#0A66C2" viewBox="0 0 24 24"><path d="M20 2H4C3 2 2 3 2 4v16c0 1 .9 2 2 2h16c1 0 2-1 2-2V4c0-1-.9-2-2-2zM8.3 18H5.6v-8h2.7v8zM7 8.7c-.9 0-1.6-.7-1.6-1.6S6.1 5.6 7 5.6s1.6.7 1.6 1.6S7.9 8.7 7 8.7zm11 9.3h-2.7v-4c0-1 0-2.3-1.4-2.3-1.4 0-1.6 1.1-1.6 2.2v4h-2.7v-8h2.6v1.1h.1c.4-.8 1.3-1.4 2.7-1.4 2.9 0 3.4 1.9 3.4 4.3v4z"/></svg>""",
        "instagram": """<svg width="14" height="14" fill="#E4405F" viewBox="0 0 24 24"><path d="M12 2.2c3 0 3.3 0 4.4.1 1 .1 1.7.3 2.3.6.6.4 1.1.8 1.6 1.4.5.5 1 1 1.4 1.6.3.6.5 1.3.6 2.3.1 1 .1 1.4.1 4.4s0 3.3-.1 4.4c-.1 1-.3 1.7-.6 2.3-.4.6-.8 1.1-1.4 1.6-.5.5-1 .9-1.6 1.4-.6.3-1.3.5-2.3.6-1 .1-1.4.1-4.4.1s-3.3 0-4.4-.1c-1-.1-1.7-.3-2.3-.6-.6-.4-1.1-.8-1.6-1.4-.5-.5-1-1-1.4-1.6-.3-.6-.5-1.3-.6-2.3C2.2 15.3 2.2 15 2.2 12s0-3.3.1-4.4c.1-1 .3-1.7.6-2.3.4-.6.8-1.1 1.4-1.6.5-.5 1-.9 1.6-1.4.6-.3 1.3-.5 2.3-.6C8.7 2.2 9 2.2 12 2.2m0 3.3A6.5 6.5 0 1 0 18.5 12 6.47 6.47 0 0 0 12 5.5zm6.8-.9a1.5 1.5 0 1 0 1.5 1.5 1.5 1.5 0 0 0-1.5-1.5zM12 8a4 4 0 1 1-4 4 4 4 0 0 1 4-4z"/></svg>""",
        "x": """<svg width="14" height="14" fill="#fff" viewBox="0 0 24 24"><path d="M18 2h3l-7 8 8 10h-6l-5-6-5 6H0l8-10L1 2h6l4 5 4-5z"/></svg>""",
        "threads": """<svg width="14" height="14" fill="#000" viewBox="0 0 24 24"><path d="M12 0a12 12 0 1 0 12 12A12 12 0 0 0 12 0zm3.67 17.13a5.31 5.31 0 0 1-3.35 1.17 5.48 5.48 0 0 1-5.31-5.64 5.5 5.5 0 0 1 9.29-3.9l1-.94A7 7 0 0 0 7 12.66a7 7 0 0 0 11.13 5.32z"/></svg>""",
    }

    return icons.get(platform, "")

# ------------------------------------------------
# Show thumbnail if exists
# ------------------------------------------------
def render_image(img_path, caption=None):
    if img_path and os.path.exists(img_path):
        img = Image.open(img_path)
        st.image(img, width=120, caption=caption)
    else:
        st.write("<span style='color:gray;'>Nessuna immagine</span>", unsafe_allow_html=True)

if 'result_automatic_research' not in st.session_state:
    st.session_state.result_automatic_research = None

if 'result_manual_research_single' not in st.session_state:
    st.session_state.result_manual_research_single = None

if 'result_manual_research_multi' not in st.session_state:
    st.session_state.result_manual_research_multi = None

if 'result_find_company' not in st.session_state:
    st.session_state.result_find_company = None

if 'result_find_user_company' not in st.session_state:
    st.session_state.result_find_user_company = None

# ------------------------------------------------
# RENDER TAB RISULTATI
# ------------------------------------------------
def tab_show_results():
    import json
    with open('tab_streamlit/peoplelist.json', 'r') as f:
        list_people = json.load(f)
    st.session_state.result_automatic_research = list_people

    # Mapping: Nome tab → (risultato, funzione renderer)
    tab_selection = {
        "Results Ricerca Automatica": (
            st.session_state.result_automatic_research,
            tab_results_automatic
        ),
        "Results Ricerca Manuale Singolo utente": (
            st.session_state.result_manual_research_single,
            tab_results_manual_single
        ),
        "Results Ricerca Manuale Multi utente": (
            st.session_state.result_manual_research_multi,
            tab_results_manual_multi
        ),
        "Results Ricerca Per Azienda": (
            st.session_state.result_find_company,
            tab_results_find_company_hunter_spy
        ),
        "Results Ricerca Per Azienda Utente": (
            st.session_state.result_find_user_company,
            tab_results_find_user_company
        ),
    }

    # 🔹 Filtra tab che hanno risultati validi
    available_tabs = {k: v for k, v in tab_selection.items() if v[0] is not None}

    if not available_tabs:
        st.info("Nessun risultato disponibile.")
        return

    # 🔹 Crea tab dinamiche
    tab_labels = list(available_tabs.keys())
    tabs = st.tabs(tab_labels)

    # 🔹 Disegna la tab corretta
    for (label, (data, renderer)), tab in zip(available_tabs.items(), tabs):
        with tab:
            renderer(data)  # ✨ chiama la funzione corretta

def tab_results_manual_single(result):
    st.write("### 👤 Risultati Ricerca Manuale (Singolo Utente)")

    if result is None:
        st.info("Fai una ricerca per vedere i risultati")
        return
    person = result['person']

    if person:
        with st.expander("Person", expanded=False):
            st.write('All Data')
            st.write(person)

def tab_results_manual_multi(result):
    st.write("### 👥 Risultati Ricerca Manuale (Multi Utente)")

    if result is None:
        st.info("Fai una ricerca per vedere i risultati")
        return

    people = result['people']

    for idx in range(people):
        person = people[idx]
        with st.expander(f"{idx}. Person", expanded=True if idx == 0 else False):
            st.write(person)

import streamlit as st
from typing import Any, Dict, List

import streamlit as st
import pandas as pd
from typing import Any, Dict, List

def tab_results_automatic(result: Dict[str, Any]):
    st.write("### 🔎 Risultati Ricerca Automatica")

    if result is None:
        st.info("Fai una ricerca per vedere i risultati")
        return

    # ========== Helper ==========
    def is_empty(v: Any) -> bool:
        if v is None:
            return True
        if isinstance(v, str):
            return v.strip() == ""
        if isinstance(v, (list, dict, set, tuple)):
            return len(v) == 0
        return False

    def dict_to_dataframe(d: Dict[str, Any]) -> pd.DataFrame:
        clean_items = [(str(k), str(v)) for k, v in d.items() if not is_empty(v)]
        if not clean_items:
            return pd.DataFrame(columns=["Campo", "Valore"])
        df = pd.DataFrame(clean_items, columns=["Campo", "Valore"])
        return df

    def format_social_sites(sites: Any) -> str:
        if not isinstance(sites, dict) or not sites:
            return "Nessun social specificato"
        labels = []
        for k, v in sites.items():
            if not v:
                continue
            name_map = {
                "x": "X / Twitter",
                "facebook": "Facebook",
                "linkedin": "LinkedIn",
                "instagram": "Instagram",
                "threads": "Threads",
            }
            label = name_map.get(str(k).lower(), str(k))
            labels.append(label)
        if not labels:
            return "Nessun social attivo"
        return ", ".join(labels)

    # ================= TITOLI GENERALI =================
    with st.container(border=True):
        st.subheader("📌 Info Generali")

        # estrai info generali note
        image_path    = result.get("image_path")
        format_input  = result.get("format_input")
        mode          = result.get("mode")
        social_sites  = result.get("social_sites", {})
        people_to_search = result.get("people_to_search", [])
        threshold     = result.get("threshold")
        task_type     = result.get("task_type")
        show_browser  = result.get("show_browser")

        colA, colB = st.columns(2)

        with colA:
            st.write("🎯 Parametri principali")
            if not is_empty(format_input):
                st.markdown(f"**Formato input:** `{format_input}`")
            if not is_empty(mode):
                st.markdown(f"**Modalità:** `{mode}`")
            if not is_empty(task_type):
                st.markdown(f"**Task type:** `{task_type}`")
            if threshold is not None and threshold != "":
                st.markdown(f"**Soglia Face Recognition:** `{threshold}`")
            if show_browser is not None:
                st.markdown(f"**Mostra browser:** `{show_browser}`")

        with colB:
            st.markdown(" ")
            st.markdown(f"**Siti social selezionati:** {format_social_sites(social_sites)}")
            if not is_empty(people_to_search):
                try:
                    n_people = len(people_to_search)
                except TypeError:
                    n_people = 1
                st.markdown(f"**Persone da cercare:** {n_people}")
                # Lista nomi (limitata)
                if isinstance(people_to_search, (list, tuple)):
                    preview = ", ".join(map(str, people_to_search[:5]))
                    if n_people > 5:
                        preview += f" ... (+{n_people-5})"
                    st.markdown(f"`{preview}`")
            if not is_empty(image_path):
                st.markdown("**Cartella immagini input:**")
                import os

                relative_path = str(image_path).replace(os.getcwd(), '')
                relative_path = relative_path.lstrip('/\\')  # rimuove sia '/' che '\'
                st.code(relative_path)

    # ================= PERSONE ANALIZZATE =================
    st.header("🧑‍🧑‍🧒 Persone Analizzate")

    peoplelist: List[Dict[str, Any]] = result.get("peoplelist", []) or []
    if len(peoplelist) == 0:
        st.info("Nessuna persona analizzata.")
        return

    col1, col2 = st.columns(2)
    with col1:
        # ----- FILTRI -----
        filter_name = st.text_input("🔍 Filtra per nome / username", "")

    with col2:
        all_socials = ["Facebook", "LinkedIn", "Instagram", "Threads", "X"]
        filter_social = st.multiselect(
            "🌐 Filtra per social",
            options=all_socials,
            default=[]
        )

    def person_matches_filters(p: Dict[str, Any]) -> bool:
        # filtro per nome
        if filter_name:
            target = filter_name.lower().strip()
            full_name = f"{p.get('first_name','')} {p.get('last_name','')} {p.get('full_name','')}".lower()
            if target not in full_name:
                # cerca anche nei candidati username
                found_in_candidates = False
                cand_keys = [
                    "list_candidate_user_found_fb",
                    "list_candidate_user_found_linkedin",
                    "list_candidate_user_found_threads",
                    "list_candidate_user_found_X",
                    "list_candidate_user_found_instagram",
                ]
                for ck in cand_keys:
                    for cand in p.get(ck, []) or []:
                        uname = str(cand.get("username", "")).lower()
                        if target in uname:
                            found_in_candidates = True
                            break
                    if found_in_candidates:
                        break
                if not found_in_candidates:
                    return False

        # filtro per social
        if filter_social:
            social_profiles = p.get("social_profiles", {}) or {}
            map_label_key = {
                "Facebook": "facebook",
                "LinkedIn": "linkedin",
                "Instagram": "instagram",
                "Threads": "threads",
                "X": "X",
            }
            ok = False
            for label in filter_social:
                skey = map_label_key.get(label)
                prof = social_profiles.get(skey, {}) if skey else {}
                if prof and any(not is_empty(v) for v in prof.values()):
                    ok = True
                    break
            if not ok:
                return False

        return True

    filtered_people = [p for p in peoplelist if person_matches_filters(p)]

    st.markdown(
        f"**Totale persone:** {len(peoplelist)} &nbsp;&nbsp;|&nbsp;&nbsp; "
        f"**Mostrate:** {len(filtered_people)}"
    )

    # ========= MAPPING SOCIAL =========
    PLATFORM_MAP = [
        ("Facebook", "facebook"),
        ("LinkedIn", "linkedin"),
        ("Instagram", "instagram"),
        ("Threads", "threads"),
        ("X", "X"),
    ]
    CAND_KEY_MAP = {
        "Facebook": "list_candidate_user_found_fb",
        "LinkedIn": "list_candidate_user_found_linkedin",
        "Threads": "list_candidate_user_found_threads",
        "X": "list_candidate_user_found_X",
        "Instagram": "list_candidate_user_found_instagram",
    }

    # ========== LOOP PERSONE ==========
    for p in filtered_people:
        full_name = p.get("full_name") or f"{p.get('first_name','')} {p.get('last_name','')}"
        full_name = (full_name or "").strip() or "Utente sconosciuto"

        with st.expander(f"👤 {full_name}", expanded=False):

            # ====== INFO DI BASE ======
            st.write("📄 Info di base")

            base_container = st.container()
            with base_container:
                col1, col2, col3 = st.columns([4, 2, 2])

                with col1:
                    first_name = p.get("first_name", "")
                    last_name = p.get("last_name", "")
                    import os

                    pot_path = str(p.get("potential_path_person")).replace(os.getcwd(), '').lstrip('/\\')  # rimuove sia '/' che '\'

                    name_card = f"""
                                        <div style="
                                            background-color:#2b2b2b;
                                            padding: 12px;
                                            border-radius: 10px;
                                            line-height: 1.6;
                                        ">
                                            <p><b>Nome completo:</b> {full_name}</p>
                                            <p><b>File sorgente:</b> {pot_path}</p>
                                        </div>
                                        """
                    st.markdown(name_card, unsafe_allow_html=True)

                    # altri campi semplici
                    skip_keys = {
                        "first_name",
                        "last_name",
                        "full_name",
                        "original_person_image",
                        "potential_path_person",
                        "social_profiles",
                        "info_facebook",
                        "info_linkedin",
                        "info_X",
                        "info_threads",
                        "info_instagram",
                        "list_candidate_user_found_fb",
                        "list_candidate_user_found_linkedin",
                        "list_candidate_user_found_threads",
                        "list_candidate_user_found_X",
                        "list_candidate_user_found_instagram",
                    }
                    extra_simple = {}
                    for k, v in p.items():
                        if k in skip_keys:
                            continue
                        if isinstance(v, (dict, list, tuple, set)):
                            continue
                        if is_empty(v):
                            continue
                        extra_simple[k] = v

                    if extra_simple:
                        st.markdown("**Altri campi utente**")
                        df_extra = dict_to_dataframe(extra_simple)
                        st.dataframe(df_extra, width='stretch', hide_index=True)

                with col2:
                    img_path = p.get("original_person_image")
                    if not is_empty(img_path):
                        render_image(img_path, caption=full_name)
                    else:
                        st.write("Nessuna immagine di base.")


            # ========= PROFILI SOCIAL =========
            st.markdown("### 🔗 Profili social")

            social_profiles = p.get("social_profiles", {}) or {}

            for label, key in PLATFORM_MAP:
                profile = social_profiles.get(key, {}) or {}

                # info specifiche (facebook, linkedin, X, threads, instagram)
                if label == "Facebook":
                    info_block = p.get("info_facebook", {}) or {}
                elif label == "LinkedIn":
                    info_block = p.get("info_linkedin", {}) or {}
                elif label == "X":
                    info_block = p.get("info_X", {}) or {}
                elif label == "Threads":
                    info_block = p.get("info_threads", {}) or {}
                elif label == "Instagram":
                    info_block = p.get("info_instagram", {}) or {}
                else:
                    info_block = {}

                candidate_key = CAND_KEY_MAP.get(label)
                candidates = p.get(candidate_key, []) or []

                # Controlla se c'è qualcosa da mostrare
                has_profile = profile and any(not is_empty(v) for v in profile.values())
                has_info = isinstance(info_block, dict) and any(not is_empty(v) for v in info_block.values())
                has_candidates = len(candidates) > 0

                # per X controlliamo anche i tweets
                if label == "X" and isinstance(info_block, dict):
                    tweets = info_block.get("tweets", {}) or {}
                    if tweets:
                        has_info = True

                if not (has_profile or has_info or has_candidates):
                    continue
                canon = label.lower().strip()
                svg_icon = get_social_svg(canon)

                with st.expander(f"{label}", expanded=True):
                    prof_col1, prof_col2 = st.columns([1, 3])

                    with prof_col1:
                        img_path_social = profile.get("image")
                        if not is_empty(img_path_social):
                            render_image(img_path_social, caption=profile.get("username") or label)
                        else:
                            st.write("Nessuna immagine profilo.")

                    def pretty_url(url: str) -> str:
                        from urllib.parse import urlparse
                        p = urlparse(url)
                        # se manca lo schema (es. "example.com/..."), aggiungilo al volo
                        if not p.netloc:
                            p = urlparse("https://" + url)

                        display = p.netloc + p.path  # dominio + path, senza query/fragment
                        if display.startswith("www."):
                            display = display[4:]  # togli "www."
                        return display.rstrip("/")  # togli eventuale "/" finale

                    with prof_col2:
                        other = info_block.get('other_info')
                        # st.write(other.keys())
                        if has_profile:
                            col1, col2 = st.columns([3,2])
                            username = info_block.get('username')
                            full_n = info_block['other_info'].get('full_name')
                            profile = info_block['other_info'].get('url_profile')
                            with col1:
                                st.markdown('**Username**: {}'.format(username))
                                st.caption(pretty_url(profile))
                            with col2:
                                st.markdown('**Full Name**: {}'.format(full_n))
                                st.link_button("**Apri profilo**", profile)

                    # --- Info generali del social (tabella) ---
                    if label != "X":
                        if has_info:
                            st.markdown("**📚 Info estratte dal profilo**")

                            df_info = dict_to_dataframe(info_block)
                            if not df_info.empty:
                                st.dataframe(df_info, width='stretch', hide_index=True)
                    else:
                        # ====== BLOCCO SPECIFICO X / TWITTER ======
                        if isinstance(info_block, dict):
                            path_tweets = info_block.get("path_tweets")
                            other_info = info_block.get("other_info", {}) or {}
                            tweets = info_block.get("tweets", {}) or {}

                            # Riepilogo numerico X
                            if tweets:
                                total_tweets = len(tweets)

                                posted_times = []
                                for _, tw in tweets.items():
                                    pt = tw.get("posted_time") or tw.get("date") or tw.get("datetime")
                                    if pt:
                                        posted_times.append(str(pt))

                                if posted_times:
                                    min_time = min(posted_times)
                                    max_time = max(posted_times)
                                else:
                                    min_time = max_time = None

                                def fmt(dt_str):
                                    from datetime import datetime
                                    dt = datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
                                    return dt.strftime("%d-%m-%Y")

                                def fmh(dt_str):
                                    from datetime import datetime
                                    dt = datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
                                    return dt.strftime("%H:%M:%S")

                                summary_html_parts = [f"<p><b>Numero totale di tweet:</b> {total_tweets}</p>"]
                                if min_time and max_time:
                                    min_fmt = fmt(min_time)
                                    max_fmt = fmt(max_time)
                                    summary_html_parts.append(
                                        f"<p><b>Intervallo temporale:</b> {min_fmt}  →  {max_fmt}</p>"
                                    )

                                summary_html = """
                                <div style="
                                    background-color:#262626;
                                    padding: 10px 12px;
                                    border-radius: 8px;
                                    margin-top: 10px;
                                    margin-bottom: 10px;
                                    line-height: 1.6;
                                ">
                                """ + "".join(summary_html_parts) + "</div>"

                                # Info generali X (path, altre info)
                                if not is_empty(path_tweets) or (
                                        other_info and any(not is_empty(v) for v in other_info.values())):
                                    with st.expander("📁 Altre info", expanded=False):
                                        if other_info:
                                            df_other = dict_to_dataframe(other_info)
                                            if not df_other.empty:
                                                st.dataframe(df_other, width='stretch', hide_index=True)



                            # ---- BOX TWEET ----
                            if tweets:
                                st.markdown("### 🐦 Tweet estratti")
                                st.markdown(summary_html, unsafe_allow_html=True)

                                tweet_items = list(tweets.items())

                                def sort_key(item):
                                    _tid, tw = item
                                    pt = tw.get("posted_time") or tw.get("date") or ""
                                    return str(pt)

                                tweet_items.sort(key=sort_key, reverse=True)

                                total = len(tweet_items)
                                with st.expander(f"Mostra tutti i tweet ({total})", expanded=False):
                                    from urllib.parse import urlparse

                                    def clean_url(url):
                                        p = urlparse(url)
                                        if not p.netloc:
                                            p = urlparse("https://" + url)
                                        d = p.netloc.replace("www.", "") + p.path
                                        return d.rstrip("/")

                                    chunk_size = 5
                                    for start in range(0, total, chunk_size):
                                        end = min(start + chunk_size, total)
                                        with st.expander(f"Tweet {start+1}–{end}", expanded=False):
                                            for _tweet_id, tw in tweet_items[start:end]:

                                                text_fields = ["tweet_text", "text", "content"]
                                                date_fields = ["posted_time", "date", "datetime"]
                                                url_fields = ["tweet_url", "link", "retweet_link"]

                                                tweet_text = next(
                                                    (tw.get(f) for f in text_fields if not is_empty(tw.get(f))), "")
                                                tweet_date = next(
                                                    (tw.get(f) for f in date_fields if not is_empty(tw.get(f))), "")
                                                tweet_url = next(
                                                    (tw.get(f) for f in url_fields if not is_empty(tw.get(f))), "")

                                                images = tw.get("images", []) or []
                                                videos = tw.get("videos", []) or []

                                                # contenitore principale
                                                st.markdown("### 📄 Informazioni principali")

                                                if tweet_date:
                                                    col1, col2 = st.columns(2)
                                                    with col1:
                                                        st.markdown(f"**Data:** {fmt(tweet_date)}")
                                                    with col2:
                                                        st.markdown(f"**Ora:** {fmh(tweet_date)}")

                                                if tweet_text:
                                                    st.markdown(f"{tweet_text}")

                                                if tweet_url:
                                                    st.link_button("Apri tweet", tweet_url, type="primary")

                                                #
                                                # ---------------------------------------------------------
                                                # 🔹 EXPANDER → dettagli secondari
                                                # ---------------------------------------------------------
                                                with st.expander("Mostra dettagli completi"):

                                                    col1, col2 = st.columns(2)

                                                    # alterna le colonne
                                                    toggle = True
                                                    for k, v in tw.items():
                                                        if k in text_fields + date_fields + url_fields + ["images",
                                                                                                          "videos"]:
                                                            continue
                                                        if is_empty(v):
                                                            continue
                                                        if k in ["username", "name", "profile_picture"]:
                                                            continue

                                                        target_col = col1 if toggle else col2
                                                        target_col.markdown(f"**{k}:** {v}")

                                                        toggle = not toggle

                                                    # immagini
                                                    if images:
                                                        st.markdown("### 🖼️ Immagini")
                                                        for i, url in enumerate(images):
                                                            st.markdown(f"- [Immagine {i + 1}]({url})")

                                                    # video
                                                    if videos:
                                                        st.markdown("### 🎥 Video")
                                                        for i, url in enumerate(videos):
                                                            st.markdown(f"- [Video {i + 1}]({url})")

                                                st.markdown("---")
                    # --- CANDIDATI TROVATI PER SOCIAL ---
                    if has_candidates:
                        st.markdown("### 🧩 Candidati trovati")

                        for cand in candidates:
                            st.markdown(
                                """
                                <div style="
                                    background-color:#2b2b2b;
                                    padding:15px;
                                    border-radius:10px;
                                    margin-bottom:12px;
                                    box-shadow:0 0 8px rgba(0,0,0,0.3);
                                ">
                                """,
                                unsafe_allow_html=True,
                            )

                            c1, c2 = st.columns([1, 3])

                            with c1:
                                img_cand = cand.get("local_path_img") or cand.get("image")
                                if not is_empty(img_cand):
                                    render_image(img_cand, caption=cand.get("username", "candidato"))
                                else:
                                    st.write("Nessuna immagine candidato.")

                            with c2:
                                df_cand = dict_to_dataframe(cand)
                                if not df_cand.empty:
                                    st.dataframe(df_cand, width='stretch', hide_index=True)

                            st.markdown("</div>", unsafe_allow_html=True)

                    # chiusura box social
                    st.markdown("</div>", unsafe_allow_html=True)

def tab_results_find_user_company(result):
    import pyperclip

    company = result.get('company', 'N/A')
    full_name = result.get('full_name', 'N/A')
    person = result.get('data', {})
    data = person.get("data", person)

    email = data.get("email", "Non trovata")
    score = data.get("score", 0)
    position = data.get("position", "N/A")
    domain = data.get("domain", "N/A")
    accept_all = data.get("accept_all", False)
    verification = data.get("verification", {})
    sources = data.get("sources", [])

    # ============================
    # HEADER
    # ============================
    st.header(f"👤 {full_name}")
    st.subheader(f"🏢 Azienda: **{company}**")

    # ============================
    # CARD INFORMAZIONI PERSONA
    # ============================
    with st.container(border=True):
        st.subheader("📧 Email trovata")

        col1_e, col2_e = st.columns(2)
        with col1_e:
            st.markdown(f"### **{email}**")
        with col2_e:
            if st.button("📋 Copia email", key=f"copy_{email}"):
                try:
                    pyperclip.copy(email)
                    st.success("Email copiata!")
                except:
                    st.warning("Non posso copiare negli appunti.")

        # Badge confidenza
        if score >= 90:
            badge = "🟩 Alta"
        elif score >= 70:
            badge = "🟨 Media"
        else:
            badge = "🟧 Bassa"

        col1, col2, col3 = st.columns(3)

        with col1:
            st.write(f"**Confidence:** {badge} ({score}%)")
            st.write(f"🔐 **Accept-All:** {'🟢 Sì' if accept_all else '🔴 No'}")

        with col2:
            st.write(f"📌 **Ruolo:** {position}")
            st.write(
                f"🔍 **Verifica:** {verification.get('status', 'N/A')} "
                f"({verification.get('date', 'N/A')})"
            )

        with col3:
            st.write(f"🌐 **Dominio email:** `{domain}`")

    # ============================
    # FONTI — BOX COMPATTI
    # ============================
    st.subheader(f"🔗 {len(sources)} Fonti trovate")

    if not sources:
        st.info("Nessuna fonte disponibile.")
        return

    for i, src in enumerate(sources):
        dom = src.get("domain", "N/A")
        uri = src.get("uri", "")
        extracted = src.get("extracted_on", "N/A")
        still = src.get("still_on_page", False)

        with st.expander(f"{i + 1}. 🌐{dom}", expanded=True if i == 0 else False):
            with st.container(border=False):
                col1, col2, col3 = st.columns(3)
                with col1:
                    # Estratto il
                    st.markdown(
                        f"📅 Estratto il: **{extracted}**",
                        unsafe_allow_html=True
                    )

                with col2:
                    # Stato online/offline
                    st.markdown(
                        f"{'🟢 Online' if still else '🔴 Offline'}",
                        unsafe_allow_html=True
                    )

                with col3:
                    # Link nascosto dietro pulsante
                    st.link_button(
                        "🔗 Apri Sorgente",
                        uri
                    )

def tab_results_find_company_hunter(result):
    if result is None:
        st.info("Fai una ricerca per vedere i risultati")
        return



    data = result['data']
    st.subheader(f"🏢 Company: {data.get('organization', 'Azienda sconosciuta')}")

    # ====================================================
    # 📌 INFO PRINCIPALI DOMINIO
    # ====================================================
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Dominio", data.get("domain"))
    with col2:
        st.metric("Pattern Email", data.get("pattern", "N/A"))
    with col3:
        st.metric("Accept All", "✔️" if data.get("accept_all") else "❌")

    # ====================================================
    # 📨 EMAIL TROVATE
    # ====================================================
    emails = data.get("emails", [])
    if not emails:
        st.info("Nessuna email trovata.")
        return

    st.markdown(f"### Found {len(emails)} Employee")


    for idx, email in enumerate(emails):

        with st.expander(f"{idx+1}. {email.get('first_name', '')} {email.get('last_name', '')} - {email.get('position', 'N/A')}",expanded=True if idx == 0 else False):

            # INFO PRINCIPALI
            c1, c2, c3 = st.columns(3)
            with c1:
                st.write("**👤 Persona**")
                st.write(f"{email.get('first_name', '')} {email.get('last_name', '')}")

            with c2:
                st.write("**🏢 Ruolo**")
                st.write(email.get("position", "N/A"))

            with c3:
                st.write("**📊 Confidence**")
                st.write(f"{email.get('confidence')}%")

            details_col1, details_col2, details_col3 = st.columns(3)
            with details_col1:
                st.write("👔 **Seniority**")
                st.write(email.get("seniority", "N/A"))

            with details_col2:
                st.write("🏛️ **Department**")
                st.write(email.get("department", "N/A"))

            with details_col3:
                st.write("🌐 **LinkedIn**")
                if email.get("linkedin"):
                    st.link_button("Profilo", email["linkedin"])
                else:
                    st.write("—")

            # VERIFICA EMAIL
            ver = email.get("verification", {})
            st.markdown("##### ✔️ Verifica email")

            col1, col2, col3 = st.columns(3)
            with col1:
                # HEADER EMAIL
                st.write(
                    f"✉️ {email.get('value')}"
                )
            with col2:
                st.write(f"📅 **Data verifica:** {ver.get('date', 'N/A')}")

            with col3:
                status = ver.get("status", "unknown")
                icon = "✔️" if status == "valid" else "❌" if status == "invalid" else "⚠️"

                st.write(f"{icon} **Status:** {status}")

            # FONTI
            st.markdown("##### 🔗 Fonti")
            if email.get("sources"):
                for src in email["sources"]:
                    with st.expander(f"🌍 {src.get('domain')}"):
                        st.write(f"**URL:** {src.get('uri')}")
                        col_1, col_2, col_3 = st.columns(3)
                        with col_1:
                            st.write(f"⏱️ Last Seen: {src.get('last_seen_on')}")
                        with col_2:
                            st.write(f"📅 Extracted: {src.get('extracted_on')}")
                        with col_3:
                            st.write(f"🟢 On page: {src.get('still_on_page')}")
            else:
                st.write("Nessuna fonte disponibile.")

def tab_result_find_company_spy(result: dict):

    st.header("🏢 Risultati Ricerca Aziendale (SpyStaff)")

    if not result:
        st.info("Nessun risultato disponibile. Esegui prima una ricerca.")
        return

    company = result.get("company", "N/A")
    max_results = result.get("max_results", "N/A")
    data = result.get("data", [])

    # ==========================
    # HEADER RIASSUNTIVO
    # ==========================
    st.markdown(f"""
        ### 🔎 Azienda: **{company}**
        **Numero massimo risultati richiesti:** {max_results}
        ---
    """)

    if not data:
        st.warning("Nessun risultato trovato per questa ricerca.")
        return

    # ==========================
    # RENDER RISULTATI
    # ==========================
    st.subheader(f"👤 Risultati trovati: {len(data)}")

    for idx, person in enumerate(data, start=1):
        st.markdown(f"## 👤 Risultato {idx}")

        with st.expander(f"{idx}. {person.get('name', 'N/A')}", expanded=True if idx == 1 else False):
            with st.container(border=True):

                # ==========================
                # NUOVO LAYOUT TRE COLONNE
                # ==========================

                col_left, col_mid, col_right = st.columns([1, 1, 1])

                # =========================================
                # 📌 COLONNA 1 — INFO BASE
                # =========================================
                with col_left:
                    st.markdown("### 📌 Info Base")
                    with st.container(border=True):
                        st.write(f"**Nome:** {person.get('name', 'N/A')}")
                        st.write(f"**Ruolo:** {person.get('job_title', 'N/A')}")
                        st.write(f"**Località:** {person.get('location', 'N/A')}")
                        st.write(f"**Email:** {person.get('email', 'N/A')}")

                        score = person.get("score")
                        if score is not None:
                            st.write(f"**Confidence Score:** {score}%")

                    # SOCIAL LINKS
                    st.markdown("### 🔗 Social")
                    with st.container(border=True):
                        links = person.get("links", {})
                        if links:
                            for platform, url in links.items():
                                st.write(f"- [{platform.capitalize()}]({url})")
                        else:
                            st.caption("Nessun link social disponibile.")

                # =========================================
                # 🧭 COLONNA 2 — INFO AGGIUNTIVE
                # =========================================
                with col_mid:
                    st.markdown("### 🧭 Informazioni Aggiuntive")
                    with st.container(border=True):
                        st.write(f"**Dominio:** {person.get('domain', 'N/A')}")
                        st.write(f"**Azienda rilevata:** {person.get('company', 'N/A')}")
                        st.write(f"**Seniority:** {person.get('seniority', 'N/A')}")
                        st.write(f"**Dipartimento:** {person.get('department', 'N/A')}")

                    # VERIFICHE
                    ver = person.get("verification", {})
                    if ver:
                        st.markdown("### ✔️ Verifica Email")
                        with st.container(border=True):
                            st.write(f"**Data verifica:** {ver.get('date', 'N/A')}")
                            st.write(f"**Stato:** {ver.get('status', 'N/A')}")
                    else:
                        st.caption("Nessuna verifica disponibile.")

                # =========================================
                # 🌍 COLONNA 3 — FONTI
                # =========================================
                with col_right:
                    sources = person.get("sources", [])
                    st.markdown(f"### 🌍 Fonti ({len(sources)})")

                    if sources:
                        for src in sources:
                            dom = src.get("domain", "N/A")
                            uri = src.get("uri", "#")
                            extracted = src.get("extracted_on", "N/A")
                            still = src.get("still_on_page")

                            icon = "🟢 Online" if still else "🔴 Offline"

                            with st.container(border=True):
                                st.write(f"**Dominio:** {dom}")
                                st.write(f"**Estratto il:** {extracted}")
                                st.markdown(f"[🔗 Visita la pagina]({uri})")
                                st.caption(icon)
                    else:
                        st.caption("Nessuna fonte disponibile.")

def tab_results_find_company_hunter_spy(result):
    if result is None:
        st.info("Fai una ricerca per vedere i risultati")
        return

    tab_hunter, tab_staffSpy = st.tabs([
        'Results from Hunter',
        'Results from StaffSpy',
    ])

    with tab_hunter:
        entry_hunter = result.get("hunter", {})
        if len(entry_hunter['data']) != 0:
            tab_results_find_company_hunter(entry_hunter)
        else:
            st.info("Nessun risultato per hunter")

    with tab_staffSpy:
        entry_staffSpy = result.get("staffSpy", {})
        if len(entry_staffSpy['data']) != 0:
            tab_result_find_company_spy(entry_staffSpy)
        else:
            st.info("Nessun risultato per staffSpy")
