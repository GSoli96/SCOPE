#
# Metodo che estrapola le infomazioni sul social Instagram
#
# @param peoplelist Lista di persone identificate di cui recuperare le informazioni
# @return peoplelist Lista di persone aggioranata con le informazioni estrapolate
#
from configuration import accounts
from finders_modules import instagramfinder
from tqdm import tqdm
import requests
import json
import instaloader
from instaloader import Profile
import os

class InstaloaderConnector():
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.check_session_loaded = False

    def __init__(self):
        social_account = accounts.SocialMediaAccounts().get_account(platform='instagram')
        self.username = social_account['username']
        self.password = social_account['password']
        self.check_session_loaded = False

    def login_with_session(self,
                           storing_dir_path,
                           directory_file_path = ".\\configuration\\InstaloaderSession\\",
                           session_file_path=None):
        """
        Gestisce una sessione di Instaloader:
        - Carica una sessione esistente, se disponibile.
        - Altrimenti, crea una nuova sessione effettuando il login.

        Args:
            username (str): Il nome utente Instagram.
            password (str): La password dell'utente (necessaria se si crea una nuova sessione).
            session_file_path (str): Percorso personalizzato per salvare/caricare il file di sessione.

        Returns:
            instaloader.Instaloader: L'oggetto Instaloader con sessione gestita.
        """
        # Inizializza Instaloader
        if self.check_session_loaded:
            self.loader.dirname_pattern = storing_dir_path
        else:
            self.loader = instaloader.Instaloader(dirname_pattern=storing_dir_path)

            self.check_session_loaded = True

            # Percorso del file di sessione (default nella directory corrente)
            session_file_path = session_file_path or f"{self.username}-session"
            session_file_path = os.path.join(directory_file_path, session_file_path)
            try:
                # Controlla se esiste una sessione salvata
                if os.path.exists(session_file_path):
                    print(f"[Instaloader] Caricamento della sessione salvata da '{session_file_path}'...")
                    self.loader.load_session_from_file(self.username, filename=session_file_path)
                    print("[Instaloader] Sessione caricata con successo.")
                else:
                    print("[Instaloader] File di sessione non trovato. Creazione di una nuova sessione...")
                    if not self.password:
                        raise ValueError("[Instaloader] La password è necessaria per creare una nuova sessione.")
                    self.loader.login(self.username, self.password)
                    self.loader.save_session_to_file(filename=session_file_path)
                    print(f"[Instaloader] Nuova sessione salvata in '{session_file_path}'.")
            except Exception as e:
                print(f"[Instaloader] Errore nella gestione della sessione: {e}")
                self.loader.login(self.username, self.password)
                self.loader.save_session_to_file(filename=session_file_path)
                print(f"[Instaloader] Nuova sessione salvata in '{session_file_path}'.")

        return self.loader

    def download_profile(self, username_profile_to_download):
        profile = Profile.from_username(self.loader.context, username_profile_to_download)
        self.loader.download_profile(profile, profile_pic=True)
        print("[Instaloader] Profile downloading complete!")

class fill_instagram():
    def __init__(self, peoplelist, people_to_search, show_browser=False):
        self.peoplelist = peoplelist
        self.show_browser = show_browser
        self.people_to_search = people_to_search

        social_account = accounts.SocialMediaAccounts().get_account(platform='instagram')

        self.username = social_account['username']
        self.password = social_account['password']
        self.InstagramfinderObject = None

        print('[Instagram] Peoplelist',self.peoplelist)
        print('[Instagram] People_to_search',self.people_to_search)

    def login(self):
        self.InstagramfinderObject = instagramfinder.Instagramfinder(self.show_browser, self.username, self.password)
        self.InstagramfinderObject.doLogin()

    def pre_processing(self):
        amount = len(self.peoplelist)
        counter = 0
        for person in tqdm(self.peoplelist, desc="[Instagram] Elaborazione User", total=amount, ncols=80):
            self.picturelist = []
            instagra_path = os.path.join(person.potential_path_person, 'Instagram')
            os.makedirs(instagra_path, exist_ok=True)

            print("[Instagram] Searching for", person.first_name, person.last_name)
            profile_and_pictures = self.InstagramfinderObject.getInstagramProfiles(person.first_name,
                                                                                   person.last_name, counter)
            if counter == 0: counter += 1
            #Dopo la ricerca, assegno ad ogni persona la lista dei potenziali user candidati
            person.list_usr_profiel_ig = profile_and_pictures

            #Salvo i link ottenuti dalla persona analizzata in un json
            with open(os.path.join(instagra_path,"potential_users.json"), "w") as outfile:
                json.dump(profile_and_pictures, outfile)

            # Loop su ogni profilo e immagine
            set_username = []
            for profile, image_url in profile_and_pictures.items():
                #print('[Instagram] Storing: {} -> img: {}'.format(profile, image_url))
                print('[Instagram] Storing image for: {}'.format(profile))
                try:
                    # Creazione della directory se non esiste
                    username = profile.replace("https://www.instagram.com/", "").replace("/", "").replace("?hl=en", "")

                    if username not in set_username:
                        set_username.append(username)
                        os.makedirs(os.path.join(instagra_path, username), exist_ok=True)

                        # Ottieni il contenuto dell'immagine
                        response = requests.get(image_url)
                        response.raise_for_status()  # Verifica se la richiesta è andata a buon fine

                        # Estrai il nome file dall'URL
                        file_name = image_url.split("/")[-1].split("?")[0]  # Rimuovi i parametri GET
                        file_path = os.path.join(instagra_path, username, file_name)

                        # Salva l'immagine nel file
                        with open(file_path, "wb") as file:
                            file.write(response.content)
                        self.picturelist.append((username, profile, image_url, file_path))
                except requests.exceptions.RequestException as e:
                    print(f"[Instagram] Error while downloading {image_url} for {profile}: {e}")
                person.list_usr_profile_instagram = self.picturelist
        return self.peoplelist

