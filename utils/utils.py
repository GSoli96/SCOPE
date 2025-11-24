import stat
from tkinter import messagebox

from tqdm import tqdm

from utils.candidate import Candidate
from utils.person import Person

import json
import os
from datetime import datetime
import shutil

def load_json_safe(path_file):
    """
    Carica un JSON in modo sicuro:
    - se il file esiste e il JSON è valido → ritorna il contenuto
    - se il file è corrotto/non valido → crea copia backup e ricrea file vuoto
    - se il file non esiste → ritorna []
    """

    # 🔹 Se il file non esiste → ritorna lista vuota
    if not os.path.exists(path_file):
        return []

    try:
        # 🔹 Prova a leggere e decodificare JSON
        with open(path_file, "r", encoding="utf-8") as f:
            return json.load(f)

    except Exception as e:
        # 🛑 File corrotto → crea backup
        base, ext = os.path.splitext(path_file)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        corrupted_copy = f"{base}_corrotto_{timestamp}{ext}"

        try:
            shutil.copy(path_file, corrupted_copy)
        except:
            pass  # non bloccare l'app se il backup fallisce

        # 🆕 Creiamo un nuovo file JSON vuoto
        with open(path_file, "w", encoding="utf-8") as f:
            json.dump([], f, indent=4)

        # Log utile su Streamlit
        print(
            f"⚠️ Il file `{path_file}` era corrotto.\n"
            f"È stata salvata una copia di backup: `{corrupted_copy}`.\n"
            f"Il file è stato ricreato da zero."
        )

        return []

def save_json_files(peoplelist):
    try:
        with tqdm(total=len(peoplelist), desc="Salvataggio file JSON", unit="file") as pbar:
            for person in peoplelist:
                print(f'Saving user: {person.full_name}')
                file_p = os.path.join(person.potential_path_person, f'{person.full_name}.json')
                person.save_to_json(file_path = file_p)
                pbar.update(1)
                print(f'{person.full_name} saved in {file_p}')

        return True
    except Exception as e:
        print('[Error] Error Save Person into JSON')
        return False

def remove_dir(self):
    path = 'Potential_target'
    if os.path.exists(path):
        try:
            # Cambia i permessi dei file e directory se necessario
            def handle_permission_error(func, path, exc_info):
                # Cambia i permessi per consentire la cancellazione
                os.chmod(path, stat.S_IWRITE)
                func(path)

            # Rimuove ricorsivamente la directory
            shutil.rmtree(path, onerror=handle_permission_error)
            # print(f"Directory {path} rimossa con successo.")
        except Exception as e:
            print(f"Errore nel rimuovere {path}: {e}")
            
            os.chmod('Potential_target' , stat.S_IWRITE)
            shutil.rmtree('Potential_target', onerror=handle_permission_error)
        os.makedirs('Potential_target',exist_ok=True)
    else:
        os.makedirs('Potential_target')

def collect_people_already_searched(image_path):
    
    peoplelist = []
    original_path = 'Potential_target'

    if os.listdir(original_path) != 0:
        def count_json_files(path):
            count = 0
            for dir_user in os.listdir(path):
                for user_file in os.listdir(os.path.join(path, dir_user)):
                    if user_file == f'{dir_user}.json':
                        count += 1
            return count

        with tqdm(total=count_json_files(original_path), desc="Load JSON Files", unit="file") as pbar:
            for dir_user in os.listdir(original_path):
                for user_file in os.listdir(os.path.join(original_path, dir_user)):
                    if user_file == f'{dir_user}.json':
                        peoplelist.append(load_from_json(os.path.join(original_path, dir_user, user_file)))
                        pbar.update(1)
        if(len(peoplelist)!=0):
            return peoplelist
        else:
            return collect_new_people(image_path)
        
    elif os.listdir(original_path) == 0:
        print('Nessuna persona trovata')
        return collect_new_people(image_path)
    
def collect_new_people(image_path):

    peoplelist = []
    files = [f for f in os.listdir(image_path) if f.endswith((".jpg", ".png", ".jpeg"))]
    num_files = len(files)

    for filename in tqdm(files, desc="Elaborazione img", total=num_files, leave=False, disable=True):
        full_name = filename.split(".")[0]
        estensione = filename.split(".")[1]

        first_name = full_name.split(" ")[0]
        last_name = full_name.replace(f'{first_name} ', '')
            
        potential_path_person = make_dir(full_name, os.path.join(image_path, filename),estensione)
        peoplelist.append(Person(
            first_name=first_name, 
            last_name=last_name,
            original_person_image=os.path.join(image_path, filename), 
            potential_path_person=potential_path_person)
            )

    print(f'Loaded {len(peoplelist)} people.')
    for person in peoplelist:
        print(f'- {person.first_name} {person.last_name}')

    return peoplelist

def find_first_key_value(data, key_to_find):
    if isinstance(data, dict):
        for key, value in data.items():
            if key == key_to_find and value:  # Controlla se la chiave corrisponde ed è non vuota
                return value
            # Ricerca ricorsiva se il valore è un dizionario o una lista
            if isinstance(value, (dict, list)):
                result = find_first_key_value(value, key_to_find)
                if result:
                    return result
    elif isinstance(data, list):
        for item in data:
            result = find_first_key_value(item, key_to_find)
            if result:
                return result
    return None

def make_dir(full_name, path_original_image, estensione):
    percorso_cartella = os.path.join(os.getcwd(), 'Potential_target', full_name)

    try:

        os.makedirs(percorso_cartella, exist_ok=True)

        shutil.copy(path_original_image, os.path.join(percorso_cartella, f'{full_name}_origin.{estensione}'))

        return percorso_cartella

    except Exception as e:
        messagebox.showerror("Error", f"Error occurred while copy original image:\n{e}")
        exit(0)

def extract_images_paths(directory, estensioni = ('.jpg', '.jpeg', '.png')):
    """
    Trova tutti i file .jpg, .jpeg e .png in una directory e nelle sue sottodirectory.
    Versione semplificata con endswith().

    Args:
        directory: Il percorso della directory da cercare.

    Returns:
        Una lista di stringhe, dove ogni stringa è il percorso assoluto di un file immagine trovato.
        Restituisce una lista vuota se la directory non esiste o non contiene immagini.
        Solleva un'eccezione OSError se si verifica un errore durante l'accesso al filesystem.
    """
    immagini = []
    try:
        for root, _, filenames in os.walk(directory): # _ ignora dirnames che non ci serve
            for filename in filenames:
                if filename.lower().endswith(estensioni):  # Controllo case-insensitive
                    percorso_assoluto = os.path.join(root, filename)
                    immagini.append(percorso_assoluto)
    except OSError as e:
        print(f"Errore di accesso al filesystem: {e}")
        raise
    return immagini

def load_from_json(file_path = None, data = None):
    """Load a Person object from a JSON file."""

    if file_path is not None and data is None:
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                data = json.load(file)
        except Exception as e:
            print(f"Errore durante la lettura del file JSON: {e}")
            return None

    # Ricostruisci l'oggetto Person
    person = Person(
        first_name=data.get("first_name"),
        last_name=data.get("last_name"),
        original_person_image=data.get("original_person_image"),
        potential_path_person=data.get("potential_path_person")
    )

    # Aggiorna fullname
    person.full_name = data.get("full_name", f"{person.first_name} {person.last_name}")

    # ---------------------------------------
    # 🔄 SOCIAL PROFILES
    # ---------------------------------------
    person.social_profiles = data.get("social_profiles", {})

    # ---------------------------------------
    # 🔄 INFO
    # ---------------------------------------
    person.info_facebook = data.get("info_facebook", {})
    person.info_linkedin = data.get("info_linkedin", {})
    person.info_X = data.get("info_X", {})
    person.info_threads = data.get("info_threads", {})
    person.info_instagram = data.get("info_instagram", {})

    # ---------------------------------------
    # 🔄 LISTE CANDIDATI → ricostruzione oggetti Candidate
    # ---------------------------------------

    def rebuild_candidate_list(list_data):
        result = []
        for d in list_data:
            try:
                c = Candidate(
                    username=d.get("username"),
                    link_image=d.get("link_image"),
                    url_profile=d.get("url_profile"),
                    local_path_img=d.get("local_path_img")
                )
                result.append(c)
            except Exception as e:
                print(f"Errore ricostruendo Candidate: {e}")
        return result

    person.list_candidate_user_found_fb = rebuild_candidate_list(
        data.get("list_candidate_user_found_fb", [])
    )
    person.list_candidate_user_found_linkedin = rebuild_candidate_list(
        data.get("list_candidate_user_found_linkedin", [])
    )
    person.list_candidate_user_found_threads = rebuild_candidate_list(
        data.get("list_candidate_user_found_threads", [])
    )
    person.list_candidate_user_found_X = rebuild_candidate_list(
        data.get("list_candidate_user_found_X", [])
    )
    person.list_candidate_user_found_instagram = rebuild_candidate_list(
        data.get("list_candidate_user_found_instagram", [])
    )

    return person

def remove_unmatched_files(folder_path, target_text):
    """
    Rimuove tutti i file nella cartella specificata i cui nomi non contengono il testo target.

    :param folder_path: Percorso della cartella da processare
    :param target_text: Testo da cercare nei nomi dei file
    """
    # Verifica che il percorso fornito sia una directory
    if not os.path.isdir(folder_path):
        raise ValueError(f"Il percorso {folder_path} non è una directory valida.")

    # Itera su tutti i file nella cartella
    for file_name in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file_name)

        # Controlla se è un file (ignora sottocartelle)
        if os.path.isfile(file_path):
            # Rimuovi il file se il nome non contiene il target_text
            if target_text not in file_name:
                try:
                    os.remove(file_path)
                    print(f"Rimosso: {file_path}")
                except Exception as e:
                    print(f"Errore durante la rimozione di {file_path}: {e}")

def save_history_entry(task, result, path_file):
    """Salva una ricerca nello storico."""
    entry = {
        "task": task,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "result": result,
    }

    # Se il file esiste, caricalo
    if os.path.exists(path_file):
        data = load_json_safe(path_file)
    else:
        data = []

    data.append(entry)

    # Riscrivi il file
    with open(path_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
