import threading
import time
import traceback

from tqdm import tqdm
from configuration.configuration import Configuration
import os
import pandas as pd
from Fill_modules import fill_insta
from Fill_modules import fill_Linkedin
from Fill_modules import fill_fb
from Fill_modules.fill_threads import ThreadsInterface
from utils.person import Person
from utils.utils import load_from_json
import streamlit as st
from utils.ManagedThread import ManagedThread

if "threads" not in st.session_state:
    st.session_state.threads = {}

class socialMapper_ManualExecutor:
    def __init__(self,
                 social_sites=None,
                  task_type = 'Candidate Extraction',
                 show_browser = False):
        
        self.config = Configuration.get_instance()
        self.social_sites = social_sites
        self.show_browser = show_browser
        self.person = Person()
        self.task_type = task_type
    
    def run(self):
        # Start processing
        print(f"Running Manual Social Mapper with: \n "
              f"- task_type: {self.task_type}")
        
        print(f"\nSocial Networks: {self.social_sites}")

        print("\nInitializing modules...\n")

        for key, value in self.social_sites.items():
            if ('fb' in key) and (len(value) > 0): self._process_facebook_manual()  # Facebook
            if ('th' in key) and (len(value) > 0): self._process_threads_manual() #Threads
            if ('ig' in key) and (len(value) > 0): self._process_instagram_manual() #instagram
            if ('ln' in key) and (len(value) > 0): self._process_linkedin_manual() #Linkedin
            if ('x' in key) and (len(value) > 0): self._process_X_manual() #X
        
        print("\nEnd initialization...\n")

        return {'person' :self.person}

    def _process_X_manual(self):
        path_base = 'Fill_modules/People_dir/twitter/manual'
        url = self.social_sites['x']
        x_username = (url.split('x.com/')[-1])
        path_base_usr = os.path.join(path_base, x_username)

        print("[X (Twitter)]", "Processing X (Twitter) Manual...")

        def start_tweeter():
            import subprocess

            python_env_b = r"C:\Users\giand\anaconda3\envs\twitter_env\python.exe"

            result = subprocess.run([
                python_env_b,
                "Fill_modules/fill_twitter.py",
                "--url", url,
                "--task", 'Manual_S',
            ],capture_output=True, text=True)

            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)





        name = f"tweeter_manual_{len(st.session_state.threads)}"
        mt = ManagedThread(target=start_tweeter, name=name)
        st.session_state.threads[name] = mt
        mt.start()

        print('[X (Twitter)] Processo partito!')

        tentativi = 0
        while True:
            if os.path.exists(f"{path_base_usr}"):
                if len(os.listdir(f"{path_base_usr}")) == 3:
                    break
                elif len(os.listdir(f"{path_base_usr}")) == 2:
                    tentativi += 1
                    time.sleep(5)
                elif tentativi == 5:
                    break
            else:
                time.sleep(5)

        if (self.person.full_name is not None and
                self.person.full_name != "" and
                    self.person.full_name != " "):
            path_potential = f'Potential_target/manual/twitter/{self.person.full_name}'
            print(f'Full Name: {path_potential}')
        else:
            path_potential = f'Potential_target/manual/twitter/{x_username}'
            print(f'x_username: {path_potential}')

        if not os.path.exists(path_potential):
            os.makedirs(path_potential, exist_ok=True)

        import json, shutil

        if os.path.exists(f"{path_base_usr}"):
            for list_file in os.listdir(f"{path_base_usr}"):
                path_potential_user = os.path.join(path_potential, list_file)
                print('Potential:', path_potential_user)
                path_fill = os.path.join(path_base_usr, list_file)
                print('path_base_usr:', path_fill)

                if list_file.endswith(".json") and list_file == f'{x_username}_tweets_tw.json':
                    print('Open: ', path_fill)
                    with open(path_fill, 'r') as f:
                        data_tweets = json.load(f)
                    print('Data loaded.')
                    self.person.info_X['tweets'] = data_tweets

                    print(f'Copying\nfrom {path_fill}\nto {path_potential_user}')
                    shutil.copy(path_fill, path_potential_user)
                    print('Copy Done.')

                if list_file.endswith(".json") and list_file == f'{x_username}_person_tw.json':
                    print('Open: ', path_fill)
                    with open(path_fill, 'r') as f:
                        data_person = json.load(f)
                    print('Data loaded.')
                    person_loaded = load_from_json(data=data_person)
                    print('Person loaded.')

                    self.person.social_profiles['X'] = person_loaded.social_profiles['X']
                    self.person.info_X = person_loaded.info_X
                    if self.person.info_X['tweets'] == {} or self.person.info_X['tweets'] is None:
                        self.person.info_X['tweets'] = data_tweets

                    def is_empty(value):
                        return value is None or value.strip() == ""

                    def is_valid(value, username):
                        return not is_empty(value) and value != username

                    # --- FIRST NAME ---
                    if is_empty(self.person.first_name) or self.person.first_name == x_username:
                        if is_valid(person_loaded.first_name, x_username):
                            self.person.first_name = person_loaded.first_name

                    # --- LAST NAME ---
                    if is_empty(self.person.last_name) or self.person.last_name == x_username:
                        if is_valid(person_loaded.last_name, x_username):
                            self.person.last_name = person_loaded.last_name

                    print(f'Copying\nfrom {path_fill}\nto {path_potential_user}')
                    shutil.copy(path_fill, path_potential_user)
                    print('Copy Done.')

                if list_file.endswith(".jpg") and list_file == f'{x_username}_tw.jpg':
                    self.person.social_profiles['X']['image'] = path_potential_user

                    print(f'Copying\nfrom {path_fill}\nto {path_potential_user}')
                    shutil.copy(path_fill, path_potential_user)
                    print('Copy Done.')

        print(f'[X (Twitter) Manual] User {x_username} Extracted!')

    def _process_linkedin_manual(self):

        print("[Linkedin]","Processing Linkedin Manual...")
        ln = fill_Linkedin.fill_linkedin(peoplelist=[], people_to_search=[])
        username_candidate = self.social_sites['ln'].split("/")[-1].replace("@", "")
        print("[Linkedin] username ID:",username_candidate)
        storing_dir_path = os.path.join(self.config.get_output_manual_path(), username_candidate, "linkedin")

        if ln.login():
            print("[Linkedin] Execute Research of",username_candidate,"...")
            self.person = ln.manual_search(person=self.person, username_candidate=username_candidate, storage_dir_path_local=storing_dir_path, link_to_user=self.social_sites['ln'])

            print(f'[Linkedin Manual] User {self.person.full_name} Extracted!')

    def _process_facebook_manual(self):
        print("[Facebook]","Processing Facebook Manual...")
        fb = fill_fb.fill_facebook(show_browser=self.show_browser)

        username_candidate = self.social_sites['fb'].split("/")[-1]
        print("[Facebook] username ID:",username_candidate)

        storing_dir_path = os.path.join(self.config.get_output_manual_path(), username_candidate, "facebook")

        print("[Facebook] Execute Research of ",username_candidate,"...")

        if fb.login():
            self.person, flag = fb.manual_search(
                url_profile = self.social_sites['fb'],
                storing_dir_path=storing_dir_path,
                person = self.person)
            if flag:
                print(f'[Facebook Manual] User {self.person.full_name} Extracted!')

    def _process_instagram_manual(self):
        # Instagram specific logic
        print("[Instagram]","Processing Instagram...")
        username_candidate = self.social_sites['ig'].split("/")[-1]
        print("[Instagram] username ID:",username_candidate)

        instaloader = fill_insta.InstaloaderConnector()
        storing_dir_path = None
        try:
            storing_dir_path = os.path.join(self.config.get_output_manual_path(), username_candidate, "instaloader")

            instaloader.login_with_session(storing_dir_path)
            print("[Instagram] storing_dir_path:",storing_dir_path)
            instaloader.download_profile(username_candidate)
        except Exception as e:
            print(f"[Instagram] [Error] Failed to retrieve user_id with instaloader: {e}")

        if storing_dir_path:
            self.person.info_instagram['Path_profile'] = storing_dir_path

    def _process_threads_manual(self):
        # estraggo l'username e la cerco su thread
        username_candidate = self.social_sites['th'].split("/")[-1].replace("@", "")
        print("[Threads] username ID:", username_candidate)
        # storing_dir_path = ".\\Potential_target\\manual\\{}\\threads\\".format(username_candidate)
        # storing_dir_path = "{}\\manual\\{}\\threads\\".format(self.config.get_potential_path(), username_candidate)
        storing_dir_path = os.path.join(self.config.get_output_manual_path(), username_candidate, "threads")

        print("[Threads] Execute Research of", username_candidate, "...")
        self._process_threads(username_candidate, storing_dir_path)

    def _process_threads(self, user_to_find, base_path):
        th = ThreadsInterface()

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
                self.person.social_profiles['threads']['username'] = user
                self.person.social_profiles['threads']['user_id'] = user_id

                print(f"[Threads] user {user_id} information extracted!")
                path_1 = os.path.join(base_path, 'user_info.json')
                # th.save_data_to_json(user, '{}\\user_info.json'.format(base_path))
                th.save_data_to_json(user, path_1)
            except Exception as e:
                print(f"[Threads] [Error] Failed to retrieve or save user information for {user_id}: {e}")

            try:
                threads = th.retrieve_user_threads(user_id)
                print("[Threads] User Threads Extracted.")
                path_2 = os.path.join(base_path, 'user_{}_threads.json'.format(user_to_find))
                # th.save_data_to_json(threads, '{}\\user_{}_threads.json'.format(base_path, user_to_find))
                th.save_data_to_json(threads, path_2)
                self.person.info_threads['user_threads'] = {'path' :path_2,
                                                              'res' : threads}

                res = []
                for i, post in enumerate(threads["data"]["mediaData"]['threads']):
                    thread_id = post['id']
                    print(i, post['id'])

                    thread_content = th.retrieve_thread(thread_id)
                    print("[Threads] Content of {} Extracted.".format(thread_id))
                    path_2 = os.path.join(base_path, "threads_info",
                                          '{}_{}_thread_content.json'.format(thread_id, user_to_find))
                    th.save_data_to_json(thread_content, path_2)

                    thread_likers = th.retrieve_thread_likers(thread_id)
                    print("[Threads] Likers for {} Extracted.".format(thread_id))
                    path_3 = os.path.join(base_path, "threads_info", '{}_thread_likers.json'.format(thread_id))
                    # th.save_data_to_json(thread_likers, '{}\\threads_info\\{}_thread_likers.json'.format(base_path, thread_id))
                    th.save_data_to_json(thread_likers, path_3)

                    res.append({'post_id':thread_id,
                                'post_idex':i,
                                'post_content':{'path': path_2,
                                                     'content': thread_content
                                                     },
                                "post_info" : {'path': path_3,
                                                   "threads_info" : thread_likers
                                               }
                                }
                               )
                self.person.info_threads['posts'] = res
            except Exception as e:
                print(f"[Threads] [Error] Failed to retrieve or save user threads for {user_id}: {e}")

            try:
                replies = th.retrieve_user_replies(user_id)
                print("[Threads] User Replies Extracted.")
                path_4 = os.path.join(base_path, "threads_info", 'user_{}_replies.json'.format(user_to_find))

                # th.save_data_to_json(replies, '{}\\user_{}_replies.json'.format(base_path, user_to_find))
                th.save_data_to_json(replies, path_4)
                self.person.info_threads['threads_info'] = {'path' :path_4,
                                                            'replies' : replies
                                                            }
            except Exception as e:
                print(f"[Threads] [Error] Failed to retrieve or save user replies for {user_id}: {e}")
