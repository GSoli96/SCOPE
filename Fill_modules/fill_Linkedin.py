import os
import time

from configuration import accounts
from finders_modules import linkedinfinder

#
# Metodo che estrapola le infomazioni sul social Linkedin
#
# @param peoplelist Lista di persone identificate di cui recuperare le informazioni
# @return peoplelist Lista di persone aggioranata con le informazioni estrapolate
#
class fill_linkedin():
    def __init__(self, peoplelist, people_to_search, show_browser=False):
        self.peoplelist = peoplelist
        self.show_browser = show_browser
        self.people_to_search = people_to_search

        social_account = accounts.SocialMediaAccounts().get_account(platform='linkedin')
        self.username = social_account['username']
        self.password = social_account['password']

        self.linkedin_connector = None

        # print('[Linkedin] peoplelist',self.peoplelist)
        # print('[Linkedin] people_to_search',self.people_to_search)

    # Login function for LinkedIn for company browsing (Credits to LinkedInt from MDSec)
    def login(self):
        #metodo Funzionante senza APIs
        #self.LinkedinfinderObject = linkedinfinder.Linkedinfinder(self.show_browser, self.username, self.password)
        #self.LinkedinfinderObject.doLogin()

        #Metodo che si connette alle APIs
        print('[Linkedin] Linkedin login Processing..')
        self.linkedin_connector = linkedinfinder.Linkedinfinder(self.username, self.password)
        self.linkedin_connector.load_or_login()
        print('[Linkedin] Linkedin login successful')

    def pre_processing(self, limit=10):
        #itero sulle persone da estrarre nella ricerca di Social Mapper
        for person in self.peoplelist:
            first_name = person.first_name
            last_name = person.last_name
            print("[Linkedin] Processing",first_name,last_name)

            save_path = os.path.join(person.potential_path_person, 'Linkedin')
            os.makedirs(save_path, exist_ok=True)

            profiles = self.linkedin_connector.getLinkedinProfiles(person=person, people_to_search=self.people_to_search, path_to_person=save_path)

            person.list_usr_profile_linkedin = profiles
            person.list_candidate_user_found_linkedin = profiles

        return self.peoplelist

    def extract_network_and_contact_information(self, username_to_search, storage_dir_path_local):
        return self.linkedin_connector.extract_contact_and_network_information_from_username(username_to_search, storage_dir_path_local)

    def manual_search(self,person, username_candidate, link_to_user, storage_dir_path_local):
        # self.linkedin_connector.extract_information_from_username(username_to_search, storage_dir_path_local)
        # self.linkedin_connector.extract_contact_and_network_information_from_username(username_to_search, storage_dir_path_local)
        return self.linkedin_connector.getLinkedinProfile(
            person = person,
            user_name = username_candidate,
            link_to_user = link_to_user,
            storage_dir_path_local = storage_dir_path_local
        )
