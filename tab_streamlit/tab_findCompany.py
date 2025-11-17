from configuration import accounts, configuration
import streamlit as st
import pandas as pd
import os
import json
from time import sleep

import requests
from staffspy import LinkedInAccount, SolverType, DriverType, BrowserType

from configuration.BrowserDriverConfigurations import BrowserDriverConfigurations
from tab_streamlit.tab_results import tab_results_find_user_company
from utils.utils import save_history_entry

social_account = accounts.SocialMediaAccounts().get_account(platform='linkedin')
USERNAME = social_account['username']
PASSWORD = social_account['password']

BASE_PATH = configuration.Configuration.get_instance().get_findcompany_path()

hunter_api = '77bb62dd99275988467975c42ab12429913c5e7c'

import streamlit as st
from pyhunter import PyHunter

def tab_hunter_search():

    hunter = PyHunter(hunter_api)

    # ---- SELEZIONE MODALITÀ ----
    tab_company, tab_search_p = st.tabs(
        ["Ricerca Azienda", "Ricerca Persona in Azienda(Hunter API)"]
    )
    with tab_company:
        st.markdown(
            "Cerca un'azienda su LinkedIn e ottieni informazioni sui dipendenti. "
            "I dati verranno salvati in locale con le foto profilo e i dettagli di ciascun utente."
        )
        # --- Layout a 2x2 colonne ---
        col1, col2 = st.columns(2)
        col3, col4, col5 = st.columns(3)

        with col1:
            company_name = st.text_input("🏢 Nome azienda")
            st.caption("Nome ufficiale dell’azienda da cercare su LinkedIn (es. *OpenAI, Google, Ferrari*).")

        with col2:
            search_term = st.text_input("💼 Ruolo o parola chiave (opzionale)", "")
            st.caption("Puoi filtrare i dipendenti per ruolo (es. *software engineer*, *marketing manager*).")

        with col3:
            location = st.text_input("📍 Località (opzionale)", "")
            st.caption("Filtra per area geografica (es. *London*, *Milan*, *New York*).")

        with col4:
            max_results = st.number_input("📊 Numero massimo risultati", 1, 1000, 5)
            st.caption("Numero di profili da estrarre (massimo 1000).")

        with col5:
            offset = st.number_input(
                "Offset risultati (opzionale)",
                min_value=0,
                max_value=100,
                value=0,
                step=1
            )
            st.caption("➡️ Quanti risultati saltare prima di iniziare a mostrare i contatti")

        if st.button("### 🚀 **Avvia la ricerca**"):
            # Controllo parametri obbligatori
            if not company_name.strip():
                st.error("⚠️ Devi inserire almeno il nome dell’azienda.")
                return
            else:

                with st.spinner("Connessione a LinkedIn e scraping in corso... ⏳"):
                    # ====================================================
                    # 1️⃣ RICERCA AZIENDA (spyStaff)
                    # ====================================================
                    entry_staffSpy = search_staffspy(company_name=company_name.strip(),
                                                     max_results=max_results,
                                                     search_term=search_term,
                                                     location=location)

                    # ====================================================
                    # 1️⃣ RICERCA AZIENDA (Hunter API)
                    # ====================================================
                    entry_hunter = search_hunter(company_name=company_name.strip(),
                                                 max_results=max_results,
                                                 offset=offset)

                    st.session_state.result_find_company = {'hunter' : entry_hunter,
                                                            'staffSpy': entry_staffSpy
                                                            }

                if st.session_state.result_find_company is not None:
                    st.success("✔️ Informazioni trovate!")
                    st.info("Puoi vedere i risultati nella tab **Results**.")
                    print('[Find Company] Scrivo st.session_state.result_find_company:')
                    print('-' * 30)
                    print(st.session_state.result_find_company)
                    print('-' * 30)
                    sleep(20)
                    save_history_entry(task='Find Company',
                                       result=st.session_state.result_find_company,
                                       path_file=st.session_state.HISTORY_FILE
                                       )



    # ====================================================
    # 2️⃣ RICERCA PERSONA IN AZIENDA (Hunter API)
    # ====================================================
    with tab_search_p:
        st.subheader("👤 Ricerca Persona → Email Finder")

        col1, col2 = st.columns(2)
        with col1:
            first = st.text_input("Nome", value='Kevin')
        with col2:
            last = st.text_input("Cognome", value='Systrom')

        company = st.text_input("Dominio aziendale (es: Instagram)", value='instagram')

        if st.button("Cerca Email Persona"):
            if not (first and last and company):
                st.error("Compila tutti i campi!")
            else:
                try:
                    with st.spinner("🔎 Ricerca email in corso..."):
                        person = hunter.email_finder(
                            company=company,
                            full_name=f'{first} {last}',
                            raw=True)

                    # Se è una risposta HTTP, converti in JSON
                    if hasattr(person, "json"):
                        person = person.json()

                    if not person:
                        st.warning("Nessuna email trovata.")
                        return
                    entry = {
                        "company": company.strip(),
                        'full_name': f'{first} {last}',
                        'first_name': f'{first}',
                        'last_name': f'{last}',
                        'data': person.person_to_dict(),
                    }

                    st.session_state.result_find_user_company = entry
                    if st.session_state.result_find_user_company is not None:
                        st.success("✔️ Informazioni trovate!")
                        st.info("Puoi vedere i risultati nella tab **Results**.")
                        print('[Find User in Company(Hunter API)] Scrivo st.session_state.result_find_user_company:')
                        print('-' * 30)
                        print(st.session_state.result_find_user_company)
                        print('-' * 30)
                        sleep(20)

                        save_history_entry(task='Find User in Company(Hunter API)',
                                           result=st.session_state.result_find_user_company ,
                                           path_file=st.session_state.HISTORY_FILE)


                except Exception as ex:
                    st.error(f"Errore nella richiesta: {ex}")

def search_staffspy(company_name: str = None,
                    max_results: int = None,
                    search_term: str = None,
                    location: str = None):
    try:
        # --- Connessione account LinkedIn ---
        account = LinkedInAccount(
            username=USERNAME,
            password=PASSWORD,
            session_file="session.pkl",
            log_level=1
        )

        # --- Parametri opzionali ---
        scrape_kwargs = {
            "company_name": company_name.strip(),
            "extra_profile_data": True,
            "max_results": max_results
        }
        if search_term.strip():
            scrape_kwargs["search_term"] = search_term.strip()
        if location.strip():
            scrape_kwargs["location"] = location.strip()

        # --- Scraping dei profili ---
        staff = account.scrape_staff(**scrape_kwargs)
        df = pd.DataFrame(staff)

        if df.empty:
            st.warning("Nessun risultato trovato. Prova a cambiare i parametri di ricerca.")
            return {
            'Task': 'Find Company(StaffSpy)',
            'company': company_name.strip(),
            'max_results': max_results,
            'data': {},
        }

        term = list(df['search_term'])[0]
        st.success(f"Trovati {len(df)} risultati per **{company_name}** 🔍")
        df.drop(columns=['search_term'], inplace=True)
        st.dataframe(df)

        global BASE_PATH

        BASE_PATH = os.path.join(BASE_PATH, term)
        os.makedirs(BASE_PATH, exist_ok=True)

        # --- Creazione cartelle e salvataggio dati ---
        for idx, row in df.iterrows():
            name = row.get("name", "unknown").replace("/", "_")
            folder_path = os.path.join(BASE_PATH, name, "linkedin")

            os.makedirs(folder_path, exist_ok=True)

            # Salva JSON
            json_path = os.path.join(folder_path, "info.json")
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(row.to_dict(), f, indent=4, ensure_ascii=False)

            # Scarica immagine
            profile_photo = row.get("profile_photo")
            if profile_photo:
                try:
                    img_data = requests.get(profile_photo, timeout=10).content
                    img_path = os.path.join(folder_path, f"{name}_{idx}.jpg")
                    with open(img_path, "wb") as img_file:
                        img_file.write(img_data)
                except Exception as e:
                    st.warning(f"⚠️ Errore nel download dell’immagine per {name}(User {idx}: {e}")

        st.success(f"✅ Dati salvati in **{BASE_PATH}**")
        entry = {
            'Task': 'Find Company(StaffSpy)',
            'company': company_name.strip(),
            'max_results': max_results,
            'data': df.to_dict(orient='records'),
        }

        return entry

    except Exception as e:
        st.error(f"❌ Errore durante l'accesso o lo scraping: {e}")
        return {
            'Task': 'Find Company(StaffSpy)',
            'company': company_name.strip(),
            'max_results': max_results,
            'data': {},
        }

def search_hunter(company_name, max_results, offset):
    hunter = PyHunter(hunter_api)

    data = hunter.domain_search(
        company=company_name,
        limit=max_results,  # <-- ora prende il valore dell'utente
        offset=offset,
        emails_type='personal'
    )

    if not data:
        st.warning("Nessun risultato trovato.")
        return {
        'task': 'Find Company(HunterAPI)',
        "company": company_name.strip(),
        "limit": max_results,
        "offset": offset,
        "emails_type": 'personal',
        "data": {}
    }

    entry = {
        'task': 'Find Company(HunterAPI)',
        "company": company_name.strip(),
        "limit": max_results,
        "offset": offset,
        "emails_type": 'personal',
        "data": data
    }

    return entry


