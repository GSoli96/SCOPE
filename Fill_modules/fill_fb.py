import time

from finders_modules import facebookfinder
from configuration import accounts
import os
from threading import Thread
from tkinter import messagebox
from tqdm import tqdm

# Metodo che estrapola le infomazioni sul social Facebook
#
# @param peoplelist Lista di persone identificate di cui recuperare le informazioni
# @return peoplelist Lista di persone aggioranata con le informazioni estrapolate
#
class fill_facebook:
    def __init__(self, peoplelist=[], people_to_search=5, show_browser=False):
        self.peoplelist = peoplelist
        self.show_browser = show_browser
        self.people_to_search = people_to_search

        social_account = accounts.SocialMediaAccounts().get_account(platform='facebook')

        self.username = social_account['username']
        self.password = social_account['password']
        self.FacebookfinderObject = None

    def login(self):
        self.FacebookfinderObject = facebookfinder.Facebookfinder(showbrowser=self.show_browser,username=self.username, password=self.password)
        return self.FacebookfinderObject.load_or_login()

    def clone_driver_session(self):
        cookies = self.FacebookfinderObject.driver.get_cookies()

        fb = facebookfinder.Facebookfinder(
            showbrowser=self.show_browser,
            username=self.username,
            password=self.password
        )

        fb.driver.get("https://facebook.com")
        for c in cookies:
            try:
                fb.driver.add_cookie(c)
            except:
                pass

        fb.driver.refresh()
        time.sleep(2)
        return fb

    def pre_processing(self):
        from threading import Thread
        import os

        def worker(p):
            try:
                # Directory Facebook per questa persona
                facebook_path = os.path.join(p.potential_path_person, 'Facebook')
                os.makedirs(facebook_path, exist_ok=True)
                print('[Facebook] Creating directory ', facebook_path.replace(os.getcwd(), ''))

                # Nuovo driver con sessione clonata
                fb = self.clone_driver_session()

                profiles = fb.getFacebookProfiles(
                    person=p,
                    people_to_search=self.people_to_search,
                    path_to_person=facebook_path
                )

                # Aggiorna la persona
                p.list_candidate_user_found_fb = profiles

                fb.close_driver()

            except Exception as e:
                print("[Facebook Error] ", p.full_name, ": ", e)
                p.list_candidate_user_found_fb = []
                return p
            return p  # 🔥 IMPORTANTE: ritorna l’oggetto aggiornato

        threads = []
        updated_people = []

        # 🚀 Avvio thread
        for person in self.peoplelist:
            th = Thread(target=lambda p=person: updated_people.append(worker(p)),
                        name=f"Thread-{person.full_name}")
            th.start()
            threads.append(th)
            th.join()

        # 🕒 Attesa terminazione
        for th in threads:
            th.join()

        # 🔥 Reinserisco gli oggetti aggiornati in self.peoplelist
        self.peoplelist = updated_people

        # for person in self.peoplelist:
        #     print('List results of ', person.full_name, ':\n')
        #     for candidate in person.list_usr_profile_fb:
        #         print('candidate: ', str(candidate))

        print('[Facebook Thread] Done')
        # 🔙 Ritorna la lista aggiornata (opzionale ma utile)
        return self.peoplelist

    def collect_information(self,peoplelist):
        self.peoplelist = peoplelist
        amount = len(self.peoplelist)

        for person in tqdm(self.peoplelist, desc="Estrazione Informazioni User", total=amount, ncols=80):
        
            def collect_info_profiles():
                global info_facebook_tmp
                info_facebook_tmp = {}

                try:
                    # Effettua la ricerca delle informazioni di una persona sul social Facebook
                    info_facebook_tmp = self.FacebookfinderObject.crawlerDataFacebook(
                        link_user = person.social_profiles['facebook']['profile'], 
                    )
                except Exception as e:
                    messagebox.showerror('Facebook Error', f'Error while making the collect_info_profiles methods.')
                    info_facebook_tmp = {}

            th1 = Thread(target=collect_info_profiles)
            th1.start()
            th1.join()

            person.info_facebook = info_facebook_tmp

        return self.peoplelist
    
    def manual_search(self, person, url_profile, storing_dir_path):
        
        if not os.path.exists(storing_dir_path):
            os.makedirs(storing_dir_path)

        try:
            # Effettua la ricerca di una persona sul social Facebook
            person  = self.FacebookfinderObject.getFacebookProfile(
                link_user= url_profile,
                storing_dir_path = storing_dir_path,
            person = person)
        except Exception as e:
            messagebox.showerror('Facebook Error', f'Error manual_search FILL FB. {e}')
            return None, False
        
        print("[Facebook Manual] Content of {} Extracted.".format(person.full_name))

        person.save_to_json(file_path=os.path.join(storing_dir_path, f'{person.full_name}.json'))

        print("[Facebook Manual] Data stored for {} in {}.\n".format(person.full_name,"{}{}.json".format(storing_dir_path,person.full_name)))
            
        return person,True
