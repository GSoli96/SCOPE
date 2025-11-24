import shutil
import traceback

from configuration.configuration import Configuration
from tqdm import tqdm
from utils import utils
from tkinter import messagebox
from Fill_modules import fill_fb
from Fill_modules import fill_Linkedin
from Fill_modules import fill_insta
# from Fill_modules import fill_twitter
from Fill_modules.fill_threads import ThreadsInterface
from utils.deep_face_model import download_deepface_models
from utils.face_Recognition import face_Recognition
import os
import time
import gdown
import sys
from threading import Thread

from utils.utils import load_from_json
import streamlit as st
from utils.ManagedThread import ManagedThread

class socialMapper_AutomaticExecutor:

    def __init__(self, 
                 social_sites=None, 
                 image_path=None,
                 format_input = 'imagefolder',
                 mode='fast',
                people_to_search=10,
                task_type = 'Candidate Extraction',
                threshold = 0.6
                ):
        
        self.config = Configuration.get_instance()
        self.social_sites = social_sites
        self.image_path = image_path
        self.format_input = format_input
        self.mode = mode
        self.show_browser = False
        self.peoplelist = []
        self.people_to_search = people_to_search
        self.task_type = task_type
        self.download_model = False
        self.download_model_th = None
        self.threshold = threshold
    
    def run(self):
        # Start processing
        print(f"Running Social Mapper with: \n - Format: {self.format_input},\n "
              f"- Path Images: {(self.image_path).replace(os.getcwd(), '')},\n "
              f"- Mode: {self.mode}")

        print(f"\nSocial Networks: {self.social_sites}")
        
        print("Initializing modules...")

        self.download_model_th = Thread(target=download_deepface_models)
        self.download_model_th.start()
        print("Downloading Face Recognition Models...")

        match self.format_input:
            case 'imagefolder':
                print('Formato {}'.format(self.format_input))

                match self.task_type:
                    case 'Candidate Extraction':
                        print("Modality: {}".format(self.task_type))

                        print("Loading People to search...")

                        self.peoplelist = utils.collect_new_people(image_path= self.image_path)

                    case 'Information Extraction':
                        print("Modality: {}".format(self.task_type))

                        print("Upload People to search...")

                        self.peoplelist = utils.collect_people_already_searched(image_path=self.image_path)

                    case 'Full Search':
                        print("Modality: {}".format(self.task_type))

                        print("Loading People to search...")

                        self.peoplelist = utils.collect_new_people(image_path=self.image_path)

            case 'csv':
                print('Formato {}'.format(self.format_input))

        print("End initialization...")
        try: 
            self._execute_social_mapper_logic()
        except Exception as e:
            traceback.print_exc()
            print(e)
            raise Exception('Execution Error!')

        utils.save_json_files(self.peoplelist)

        return self.to_dict()

    def to_dict(self):
        return {
            "social_sites": self.social_sites,
            "image_path": self.image_path,
            "format_input": self.format_input,
            "mode": self.mode,
            "show_browser": self.show_browser,
            "peoplelist": [person.person_to_dict() for person in self.peoplelist],
            "people_to_search": self.people_to_search,
            "task_type": self.task_type,
            "download_model": self.download_model,
            "threshold": self.threshold,
        }

    def _execute_social_mapper_logic(self):
        if self.social_sites.get('a'):
                self._process_facebook()
                self._process_instagram()
                self._process_linkedin()
                self._process_threads()
                self._process_X()
        else:
            if self.social_sites.get('fb'): #Facebook
                self._process_facebook()
            if self.social_sites.get('ig'): #Instagram
                self._process_instagram() 
            if self.social_sites.get('ln'): #Linkedin
                self._process_linkedin()
            if self.social_sites.get('th'): #Threads
                self._process_instagram()
                # self._process_threads()
            if self.social_sites.get('x'): #X (Twitter)
                self._process_X()
        
    def _process_facebook(self):
        # Facebook specific logic
        print(f"[Facebook] Processing Facebook...")

        fb = fill_fb.fill_facebook(
            peoplelist=self.peoplelist,
            show_browser=self.show_browser,
            people_to_search=self.people_to_search)
        
        if fb.login():
            print("[Facebook] {}...".format(self.task_type))

            if self.task_type == 'Candidate Extraction' or self.task_type == 'Full Search':
                self.face_recognition_check()

                self.peoplelist = fb.pre_processing()

                fb_face_recogn = face_Recognition(
                        threshold= self.threshold, 
                        peoplelist= self.peoplelist, 
                        platform='facebook', 
                        mode=self.mode
                        )
                
                self.peoplelist = fb_face_recogn.get_face_recognition_results()

                if self.task_type == 'Full Search':
                    self.peoplelist = fb.collect_information(self.peoplelist)

            elif self.task_type == 'Information Extraction':

                self.peoplelist = fb.collect_information(self.peoplelist)

            print("[Facebook] End {} Facebook...".format(self.task_type))

        else:
            messagebox.showerror('FB Login Error', 'Error in the Facebook Login')
            
    def face_recognition_check(self):
        from utils.deep_face_model import downloaded_models

        if len(downloaded_models) == 0 and not self.download_model_th.is_alive():
            self.download_model_th = Thread(target=download_deepface_models)
            self.download_model_th.start()
        elif self.download_model_th.is_alive():
            while self.download_model_th.is_alive():
                print('Model are not yet downloaded. Please Wait...', flush=True)
                time.sleep(5)
                if not self.download_model_th.is_alive():
                    if len(downloaded_models) > 0:
                        print('Model downloaded successfully.')
                        self.download_model = True
                        break
                    else:
                        print('Model are not downloaded. Please try again.')
                        self.download_model = False
                        break           
        elif len(downloaded_models) > 0 and not self.download_model_th.is_alive():
            print('Model downloaded successfully.')
            self.download_model = True
        else:
            print('Model are not downloaded. Please try again.')
            self.download_model = False

    def _process_instagram(self):
        # Instagram specific logic
        print("[Instagram]","Processing Instagram...")
        platform = 'instagram'
        ig = (fill_insta.fill_instagram(peoplelist=self.peoplelist, show_browser=self.show_browser, people_to_search=self.people_to_search))
        ig.login()

        ### Applico il modulo di face_recognition sugli utenti che sto analizzando
        # self.peoplelist = (face_Recognition(threshold= self.threshold, peoplelist= ig.pre_processing(), platform=platform, mode=self.mode)).user_face_recognition_new()
        self.peoplelist = ig.pre_processing()

        face_r = face_Recognition(
            threshold = self.threshold, 
            peoplelist = self.peoplelist, 
            platform = platform, 
            mode = self.mode)
        
        self.face_recognition_check()
        
        self.peoplelist = face_r.user_face_recognition_new()

        #Download informazioni da instaloader dei profili candidati in output dalla face recognition
        instaloader = fill_insta.InstaloaderConnector()
        #storing_dir_path = "./Potential_target/"
        storing_dir_path = self.config.get_potential_path()
        # print("[Instagram]",storing_dir_path)
        instaloader.login_with_session(storing_dir_path)

        #Risultati dalla Face Recognition
        username_candidate = ""

        for person in tqdm(self.peoplelist, desc="Instaloader Processing", total=len(self.peoplelist), ncols=80):
            try:
                #storing_dir_path = "{}{}/instaloader/".format(storing_dir_path,person.full_name)
                storing_dir_path = os.path.join(self.config.get_potential_path(), person.full_name, "instaloader")

                instaloader.login_with_session(storing_dir_path)
                username_candidate = person.social_profiles[platform]['username']
                print('\n[Instaloader] Candidate: {}...\n'.format(username_candidate))
                # match_score = person.social_profiles[platform]['Face_Recognition_Result']
                # print("[Instagram] username_match: ",username_candidate," match_score: ",match_score)
                # print("\n[Instagram] Storing ",username_candidate, "\n")

                instaloader.download_profile(username_candidate)
                #person.social_profiles[platform]['instaloader_data'] = ""
            except Exception as e:
                # print(f"[Instagram] [Error] Failed to retrieve user_id with instaloader: {e}")
                print(f"[Instagram] [Error] Failed to retrieve user_id of {username_candidate} with instaloader")
                pass


        #Identifico la persona con score massimo
        #estraggo l'username e la cerco su thread
        print("[Instagram] Execute Research on Threads of",username_candidate,"...")
        self._process_threads(username_candidate,username_candidate)

        '''
        for username in tqdm(candidate_users_from_facerecognition, desc="Instaloader Processing", total=len(self.peoplelist), ncols=80):
            instaloader.download_profile(username)
        '''

    def _process_threads(self, user_to_find, username_candidate):
        th = ThreadsInterface()
        #base_path = "/Users/stefanocirillo/Desktop/Soda_United/Potential_target/Gino Valentino/threads"
        #base_path = base_path.replace("instaloader","threads")
        base_path = os.path.join(self.config.get_potential_path(), username_candidate, "threads")

        check_user_found = False
        try:
            user_id = th.retrieve_user_id(user_to_find)
            print(f"[Threads] user_id for {user_to_find}: {user_id}")
            check_user_found = True
        except Exception as e:
            print(f"[Threads] [Error] Failed to retrieve user_id for {user_to_find}: {e}")

        if check_user_found:
            try:
                user = th.retrieve_user(user_id)
                print(f"[Threads] user {user_id} information extracted!")
                json_th_path = os.path.join(base_path,'user_info.json')
                th.save_data_to_json(user, json_th_path)
            except Exception as e:
                print(f"[Threads] [Error] Failed to retrieve or save user information for {user_id}: {e}")

            try:
                threads = th.retrieve_user_threads(user_id)
                print("[Threads] User Threads Extracted.")
                th.save_data_to_json(threads, '{}/user_{}_threads.json'.format(base_path, user_to_find))

                for i, post in enumerate(threads["data"]["mediaData"]['threads']):
                    thread_id = post['id']
                    print(i, post['id'])

                    thread_content = th.retrieve_thread(thread_id)
                    print("[Threads] Content of {} Extracted.".format(thread_id))
                    path_2 = os.path.join(base_path,
                                "threads_info", '{}_{}_thread_content.json'.format(thread_id, user_to_find))
                    th.save_data_to_json(thread_content, path_2)

                    thread_likers = th.retrieve_thread_likers(thread_id)
                    print("[Threads] Likers for {} Extracted.".format(thread_id))
                    path_3 = os.path.join(base_path, "threads_info", '{}_thread_likers.json'.format(thread_id))
                    th.save_data_to_json(thread_likers, path_3)

            except Exception as e:
                print(f"[Threads] [Error] Failed to retrieve or save user threads for {user_id}: {e}")

            try:
                replies = th.retrieve_user_replies(user_id)
                print("[Threads] User Replies Extracted.")
                path_4 = os.path.join(base_path, "threads_info", 'user_{}_replies.json'.format(user_to_find))
                th.save_data_to_json(replies, path_4)
            except Exception as e:
                print(f"[Threads] [Error] Failed to retrieve or save user replies for {user_id}: {e}")

    def _process_linkedin_candidate_extraction(self):
        # LinkedIn specific logic
        # print("[Linkedin]","Processing Linkedin...")
        ln = fill_Linkedin.fill_linkedin(peoplelist=self.peoplelist, show_browser=self.show_browser, people_to_search=self.people_to_search)
        ln.login()
        self.peoplelist_linkedin = ln.pre_processing(limit=self.people_to_search)

        # print("[Linkedin]",self.peoplelist_linkedin)
        print("\nEnd Processing Linkedin...")

        return ln

    def _process_linkedin_candidate_information_extraction(self,ln):
        platform = 'linkedin'
        self.face_recognition_check()
        self.peoplelist = (face_Recognition(threshold= self.threshold, peoplelist= self.peoplelist, platform=platform, mode=self.mode)).user_face_recognition_new()

        #dopo aver fatto recognition, per ogni persona ed ogni risultato scarico le info
        for person in self.peoplelist:
            username_match = person.social_profiles[platform]['username']
            print("[Linkedin] username_match:",username_match)

            # Recupero l'informazione dell'utente che matcha dai dati che ho gia tirato fuori in precedenza
            # e che sono presenti nei candidati
            user_candidate_data = person.list_candidate_user_found_linkedin[username_match]
            #print("[Linkedin] user_candidate_data:",user_candidate_data)

            #storage_dir_path_local = "./Potential_target/{}/linkedin/profile_candidates/".format(person.full_name)
            #storage_dir_path_local = "{}/{}/linkedin/profile_candidates/".format(self.config.get_potential_path(), person.full_name)
            storage_dir_path_local = os.path.join(self.config.get_potential_path(), person.full_name, "linkedin", "profile_candidates")

            contact_info = ln.extract_network_and_contact_information(username_match, storage_dir_path_local)
            tmp = person.social_profiles[platform]
            tmp = dict(tmp, **contact_info)
            tmp = dict(tmp, **user_candidate_data)
            person.social_profiles[platform] = tmp

            print("[Linkedin] person updated:",person)

            #rimuovo tutti i file inutili
            #print("[Linkedin] Cleaning results for username...")
            #self.remove_unmatched_files(storage_dir_path_local,username_match)

    def _process_linkedin(self):
        # LinkedIn specific logic
        print("[Linkedin] Processing Linkedin...")
        platform = 'linkedin'
        ln = fill_Linkedin.fill_linkedin(peoplelist=self.peoplelist, show_browser=self.show_browser, people_to_search=self.people_to_search)
        ln.login()
        self.peoplelist = ln.pre_processing(limit=5)

        print("[Linkedin] peoplelist ",self.peoplelist)
        print("[Linkedin] End Processing Linkedin...")
        self.face_recognition_check()
        self.peoplelist = (face_Recognition(threshold= self.threshold, peoplelist= self.peoplelist, platform=platform, mode=self.mode)).user_face_recognition_new()

        #dopo aver fatto recognition, per ogni persona ed ogni risultato scarico le info
        for person in self.peoplelist:
            username_match = person.social_profiles[platform]['username']
            match_score = person.social_profiles[platform]['Face_Recognition_Result']
            print("[Linkedin] username_match:",username_match,"match_score:",match_score)

            # Recupero l'informazione dell'utente che matcha dai dati che ho gia tirato fuori in precedenza
            # e che sono presenti nei candidati
            user_candidate_data = person.list_candidate_user_found_linkedin[username_match]
            #print("[Linkedin] user_candidate_data:",user_candidate_data)

            #storage_dir_path_local = "./Potential_target/{}/linkedin/profile_candidates/".format(person.full_name)
            #storage_dir_path_local = "{}/{}/linkedin/profile_candidates/".format(self.config.get_potential_path(), person.full_name)
            storage_dir_path_local = os.path.join(self.config.get_potential_path(), person.full_name, "linkedin", "profile_candidates")

            contact_info = ln.extract_network_and_contact_information(username_match, storage_dir_path_local)
            tmp = person.social_profiles[platform]
            tmp = dict(tmp, **contact_info)
            tmp = dict(tmp, **user_candidate_data)
            person.social_profiles[platform] = tmp

            print("[Linkedin] person updated:",person)

    def _process_X(self):
        print("[X (Twitter)]", " Automatic.")
        path_base = 'Fill_modules/People_dir/twitter/automatic'
        path = 'Fill_modules/peoplelist.json'
        path_res = 'Fill_modules/peoplelist_result.json'

        def start_tweeter():
            try:
                import subprocess, json

                python_env_b = r"C:\Users\giand\anaconda3\envs\twitter_env\python.exe"

                json_people = {}
                for idx, person in enumerate(self.peoplelist):
                    json_people[idx] = person.person_to_dict()


                with open(path, 'w') as f:
                    json.dump(json_people, f)
                print('[X] File di appoggio salvato!')

                result = subprocess.run([
                    python_env_b,
                    "Fill_modules/fill_twitter.py",
                    "--people_to_search", str(self.people_to_search),
                    "--peoplelist", path,
                    "--task", 'Automatic'
                ], capture_output=True, text=True)

            except Exception as e:
                print('-' * 30)
                traceback.print_exc()
                print('-' * 30)



        name = f"tweeter_automatic_{len(st.session_state.threads)}"
        mt = ManagedThread(target=start_tweeter, name=name)
        st.session_state.threads[name] = mt
        mt.start()

        print('[X (Twitter)] Processo partito!')

        import os, json
        while True:
            if os.path.exists(path_res):
                time.sleep(3)
                break

        with open(path_res, 'r') as f:
            data = json.load(f)

        people = []
        for idx, p_data in data.items():
            person = load_from_json(data=p_data)
            username_x = person.social_profiles['X']['username']
            path_user = os.path.join(path_base, username_x)

            if person.full_name is not None and person.full_name != "" and person.full_name != " ":
                path_potential = f'Potential_target/{person.full_name}/twitter/'
                print(f'Full Name: {path_potential}')
            else:
                path_potential = f'Potential_target/{username_x}/twitter/'
                print(f'username_x: {path_potential}')

            if not os.path.exists(path_potential):
                os.makedirs(path_potential, exist_ok=True)

            if os.path.exists(path_user):
                for list_file in os.listdir(path_user):
                    path_potential_user = os.path.join(path_potential, list_file)
                    print('Potential:', path_potential_user)
                    path_fill = os.path.join(path_user, list_file)
                    print('Fill:', path_fill)

                    if list_file.endswith(".json") and list_file == f'{username_x}_tweets_tw.json':
                        print('Open: ', path_fill)
                        with open(path_fill, 'r') as f:
                            data_tweets = json.load(f)
                        print('Data loaded.')
                        person.info_X['tweets'] = data_tweets

                        print(f'Copying\nfrom {path_fill}\nto {path_potential_user}')
                        shutil.copy(path_fill, path_potential_user)
                        print('Copy Done.')

                    if list_file.endswith(".json") and list_file == f'{username_x}_person_tw.json':
                        print('Open: ', path_fill)
                        with open(path_fill, 'r') as f:
                            data_person = json.load(f)
                        print('Data loaded.')
                        person_loaded = load_from_json(data=data_person)
                        print('Person loaded.')

                        person.social_profiles['X'] = person_loaded.social_profiles['X']
                        person.info_X = person_loaded.info_X
                        if person.info_X['tweets'] == {} or person.info_X['tweets'] is None:
                            person.info_X['tweets'] = data_tweets

                        def is_empty(value):
                            return value is None or value.strip() == ""

                        def is_valid(value, username):
                            return not is_empty(value) and value != username

                        # --- FIRST NAME ---
                        if is_empty(person.first_name) or person.first_name == username_x:
                            if is_valid(person_loaded.first_name, username_x):
                                person.first_name = person_loaded.first_name

                        # --- LAST NAME ---
                        if is_empty(person.last_name) or person.last_name == username_x:
                            if is_valid(person_loaded.last_name, username_x):
                                person.last_name = person_loaded.last_name

                        print(f'Copying\nfrom {path_fill}\nto {path_potential_user}')
                        shutil.copy(path_fill, path_potential_user)
                        print('Copy Done.')

                    if list_file.endswith(".jpg") and list_file == f'{username_x}_tw.jpg' and person.original_person_image is None or person.original_person_image == "":
                        person.original_person_image = path_fill

                        print(f'Copying\nfrom {path_fill}\nto {path_potential_user}')
                        shutil.copy(path_fill, path_potential_user)
                        person.social_profiles['X']['image'] = path_potential_user
                        print('Copy Done.')

            people.append(person)
            shutil.rmtree(path_base, ignore_errors=True)

        self.peoplelist = people

        shutil.rmtree(path, ignore_errors=True)
        shutil.rmtree(path_res, ignore_errors=True)

        print("[X (Twitter)] Extraction Done!")