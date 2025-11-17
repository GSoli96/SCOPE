# -*- coding: utf-8 -*-
from __future__ import print_function

import json
import shutil
import sys
import threading
# -*- coding: utf-8 -*-
import traceback
from threading import Thread
from time import sleep

import chromedriver_autoinstaller
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from twitter_scraper_selenium import scrape_profile

class BrowserDriverConfigurations:
    def __init__(self):
        current_path = os.getcwd()
        self.parent_path = os.path.dirname(current_path)
        chromedriver_autoinstaller.install(path=self.parent_path)
        self.__enable_profile = None

    def get_chrome_user_data_dir(self):
        if sys.platform.startswith('win'):
            base_paths = [
                os.path.expanduser('~\\AppData\\Local\\Google\\Chrome\\User Data'),
                os.path.expanduser('~\\AppData\\Local\\Google\\Chrome Beta\\User Data'),
                os.path.expanduser('~\\AppData\\Local\\Google\\Chrome SxS\\User Data'),
                os.path.expanduser('~\\AppData\\Local\\Google\\Chrome for Testing\\User Data'),
                os.path.expanduser('~\\AppData\\Local\\Chromium\\User Data'),
            ]
        elif sys.platform.startswith('darwin'):  # macOS
            base_paths = [
                os.path.expanduser('~/Library/Application Support/Google/Chrome'),
                os.path.expanduser('~/Library/Application Support/Google/Chrome Beta'),
                os.path.expanduser('~/Library/Application Support/Google/Chrome Canary'),
                os.path.expanduser('~/Library/Application Support/Google/Chrome for Testing'),
                os.path.expanduser('~/Library/Application Support/Chromium'),
            ]
        elif sys.platform.startswith('linux'):
            base_paths = [
                os.path.expanduser('~/.config/google-chrome'),
                os.path.expanduser('~/.config/google-chrome-beta'),
                os.path.expanduser('~/.config/google-chrome-unstable'),
                os.path.expanduser('~/.config/google-chrome-for-testing'),
                os.path.expanduser('~/.config/chromium'),
            ]
        else:
            raise OSError("[ChromeConfiguration] Unsupported operating system.")

        for base_path in base_paths:
            if os.path.exists(base_path):
                # print(f"[ChromeConfiguration] Base path found: {base_path}")
                return base_path

        print("[ChromeConfiguration] No base path found.")
        return None

    def configure_chrome_profile(self, chrome_options, base_path):
        if base_path:
            profile_dir = None
            for item in os.listdir(base_path):
                full_path = os.path.join(base_path, item)
                if os.path.isdir(full_path) and (item == "Default" or item.startswith("Profile ")):
                    # print(f"[ChromeConfiguration] Profile found: {full_path}")
                    profile_dir = item
                    # break

            if profile_dir:
                profile_path = os.path.join(base_path, profile_dir)
                chrome_options.add_argument(f"user-data-dir={base_path}")
                chrome_options.add_argument(f"--profile-directory={profile_dir}")
                print(f"[ChromeConfiguration] Using profile: {profile_path}")
            else:
                print("[ChromeConfiguration] No profile found. A new Chrome session will be started without a profile.")
        else:
            print("[ChromeConfiguration] No base path found, so no profile will be used.")
        return chrome_options

    def get_chrome_configurations(self, enable_profile=None):
        self.__enable_profile = enable_profile
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_experimental_option("useAutomationExtension", False)
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("--no-sandbox")  # to remove in production
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--mute-audio")
        chrome_options.add_argument("--disable-notifications")
        chrome_options.add_argument("--disable-popup-blocking")
        chrome_options.add_argument("--disable-gcm-registration")
        prefs = {
            "profile.default_content_setting_values.notifications": 2
        }
        chrome_options.add_experimental_option("prefs", prefs)
        prefs = {
            "credentials_enable_service": False,
            "profile.password_manager_enabled": False,
            "profile.default_content_setting_values.notifications": 2
        }
        chrome_options.add_experimental_option("prefs", prefs)
        chrome_options.add_argument("--disable-infobars")

        # chrome_options.add_argument("--headless") #to start in headless mode

        base_path = self.get_chrome_user_data_dir()
        if self.__enable_profile:
            chrome_options = self.configure_chrome_profile(chrome_options, base_path)

        return chrome_options

    def get_driver(self, enable_profile=None):
        try:
            self.__enable_profile = enable_profile
            '''
            Se enable_profile=True, carica uno dei profili che sono salvati in Chrome.
            Nota: se si ha un'altra sessione gia aperta di Chrome va in errore
            '''
            chrome_options = self.get_chrome_configurations(enable_profile=self.__enable_profile)
            self.driver = webdriver.Chrome(options=chrome_options)
        except:
            chrome_options = self.get_chrome_configurations()
            self.driver = webdriver.Chrome(options=chrome_options)

        return self.driver

    def get_enable_profile(self):
        return self.__enable_profile

    def get_installation_path(self):
        return self.parent_path

# Classe concreta che istanzia il crawler per il social Twitter
class Twitterfinder(object):
    timeout = 5  # timeout per rallentare l'esecuzione e similuare l'operatore delll'utente reale, per limitare blocchi anti-crawler

    #
    # Metodo init per settare proprietà del browser
    #
    # @param showbrowser Stringa legata al comando da console, se presente si richiede la visine in real-time della ricerca
    #
    def __init__(self, showbrowser=False, username=None, password=None):

        self.username = username
        self.password = password

        chrome_options = BrowserDriverConfigurations().get_chrome_configurations()
        self.driver = webdriver.Chrome(options=chrome_options)

        self.driver.implicitly_wait(3)
        self.driver.delete_all_cookies()

        self.login_page = "https://x.com/i/flow/login"

        self.inputfield_username = '//*[@autocomplete="username"]'
        self.inputfield_password = "session[password]"

        self.xpath_buttonNext = '//*[@id="layers"]/div[2]/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div/div/div/button[2]'
        self.xpath_buttonLogin = '//*[@id="layers"]/div[2]/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div[2]/div/div[1]/div/div/button'

    # Metodo che effettua il login al social
    #
    # @param username Stringa che rappresenta l'username dell'account da usare per il login
    # @param password Stringa che rappresenta l'password dell'account da usare per il login
    #
    def doLogin(self):
        self.driver.get(self.login_page)
        self.driver.execute_script('localStorage.clear();')
        sleep(4)

        if (self.driver.title.encode('ascii', 'replace').startswith(bytes("Login on", 'utf-8'))):
            print("\n[+] Twitter Login Page loaded successfully [+]")
            try:
                twUsername = self.driver.find_element(By.XPATH, self.inputfield_username)
            except:
                print(
                    "Twitter Login Page username field seems to have changed"
                )
                return False
            twUsername.send_keys(self.username)
            sleep(2)

            try:
                button_next = self.driver.find_element(By.XPATH, self.xpath_buttonNext)
                print("\n[+] Twitter Login Page: Button Found! [+]")
                button_next.click()
                sleep(2)

            except Exception as e:
                print('Error')

            try:
                # twPassword = self.driver.find_element_by_xpath("//input[@class='js-password-field']")
                twPassword = self.driver.find_element(By.NAME, self.inputfield_password)
            except:
                print(
                    "Twitter Login Page password field seems to have changed, please make an issue on: https://github.com/Greenwolf/social_mapper")
                return False
            twPassword.send_keys(self.password)
            sleep(2)

            try:
                twLoginButton = self.driver.find_element(By.XPATH, self.xpath_buttonLogin)
            except:
                print(
                    "Twitter Login Page login button name seems to have changed, please make an issue on: https://github.com/Greenwolf/social_mapper")
                traceback.print_exc()
                return False

            twLoginButton.click()
            sleep(5)

            if (self.driver.title.encode('ascii', 'replace').startswith(bytes("Login on", 'utf-8'))):
                print("[-] Twitter Login Failed [-]\n")
                return False
            else:
                print("[+] Twitter Login Success [+]\n")
                return True
        else:
            print(
                "Twitter Login Page title field seems to have changed, please make an issue on: https://github.com/Greenwolf/social_mapper")
            return False

    #
    # Metodo che effettua la ricerca di una persona sul social
    #
    # @param first_name Stringa che rappresenta il nome della persona da cercare
    # @param last_name Stringa che rappresenta il cognome della persona da cercare
    # @param username Stringa che rappresenta l'username dell'account da usare per il login
    # @param password Stringa che rappresenta l'password dell'account da usare per il login
    #
    # @return picturelist Array di persone trovare rispetto al nome in input
    #
    def getTwitterProfiles(self, first_name, last_name):
        # effettua la ricerca compilando il campo apposito
        url = f"https://x.com/search?q={first_name}%20{last_name}&src=typed_query"
        self.driver.get(url)
        sleep(3)
        searchresponse = self.driver.page_source.encode('utf-8')
        soupParser = BeautifulSoup(searchresponse, 'html.parser')
        picturelist = []

        # per ogni persona risultante dalla ricerca, ne estrapola la foto
        for element in soupParser.find_all('div', {
            'class': 'css-18t94o4 css-1dbjc4n r-1ny4l3l r-1j3t67a r-1w50u8q r-o7ynqc r-6416eg'}):
            try:
                link = element.find('a')['href']
                smallpic = element.find('img')['src']
                # replaced1 = smallpic.replace("_bigger.jpg","_400x400.jpg")
                # profilepic = replaced1.replace("_bigger.jpeg","_400x400.jpg")
                profilepic = smallpic.replace("_reasonably_small.", "_400x400.")
                picturelist.append(["https://x.com/" + link, profilepic, 1.0])

            except:
                print("Error")
                continue
        return picturelist

    #
    # Metodo che effettua la ricerca di una persona sul social
    #
    # @param username Stringa che rappresenta l'username dell'account da usare per il login
    # @param password Stringa che rappresenta l'password dell'account da usare per il login
    # @param url Stringa legata al profilo della persona ricercata, identificata tramite face-recognition
    #
    # @return info Array di informazioni estrapolate circa la persona trovata
    #
    def crawlerDataTwitter(self, url):
        info = {"Città_twitter": "", "Sito_twitter": "", "Twitter_Biografia": ""}
        self.driver.get(url)
        sleep(1)
        # verifico se il login è ancora valido, altrimenti lo rieseguo
        if "login" in self.driver.current_url:
            self.doLogin(self.username, self.password)
            sleep(3)
            if "login" in self.driver.current_url:
                print("Twitter Timeout Error, session has expired and attempts to reestablish have failed")
        searchresponse = self.driver.page_source.encode('utf-8')
        soupParser = BeautifulSoup(searchresponse, 'html.parser')
        sleep(1)
        # estrapolo la Biografia della persona trovata
        for element in soupParser.findAll('div', {'data-testid': 'UserDescription'}):
            try:
                for element2 in element.findAll('span', {
                    'class': 'css-901oao css-16my406 r-1qd0xha r-ad9z0x r-bcqeeo r-qvutc0'}):
                    biografia = element2.text
                    info["Twitter_Biografia"] = biografia
            # info["Cellulare"] = cellulare
            except Exception as e:
                print(e)
        # estrapolo, per ogni persona trovata, la città e il sito web
        for element in soupParser.findAll('div', {'data-testid': 'UserProfileHeader_Items'}):
            try:
                for element2 in element.findAll('span', {
                    'class': 'css-901oao css-16my406 r-1qd0xha r-ad9z0x r-bcqeeo r-qvutc0'}):
                    città = element2.text
                    info["Città_twitter"] = città
                    break
                for element2 in element.findAll('a', {
                    'class': 'css-4rbku5 css-18t94o4 css-901oao css-16my406 r-13gxpu9 r-1loqt21 r-4qtqp9 r-1qd0xha r-ad9z0x r-zso239 r-bcqeeo r-qvutc0'}):
                    sito = element2.text
                    info["Sito_twitter"] = sito
            except Exception as e:
                print(e)

        return info

    #
    # Metodo che termnina la sessione
    #
    def kill(self):
        self.driver.quit()

class Candidate:
    def __init__(self, username, link_image, url_profile, local_path_img):
        self.username = username
        self.url_profile = url_profile
        self.local_path_img = local_path_img
        self.link_image = link_image

    def get_username(self):
        return self.username

    def get_url_profile(self):
        return self.url_profile

    def get_local_path_img(self):
        return self.local_path_img

    def get_link_image(self):
        return self.link_image

    def __str__(self):
        return (f"username: {self.username}\n"
                f"url_profile: {self.url_profile}\n"
                f"local_path_img: {self.local_path_img}\n"
                f"link_image: {self.link_image}\n")

    def candidate_to_dict(self):
        return {
            'username': self.username,
            'url_profile': self.url_profile,
            'local_path_img': self.local_path_img,
            'link_image': self.link_image

        }

    def save_to_json(self, file_path):
        """Saves the person's data to a JSON file."""
        try:
            with open(file_path, "w") as file:
                file.write(json.dumps(self.__dict__, indent=4))

        except Exception as e:
            print(f"An error occurred while saving data: {e}")

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

class Person:
    def __init__(self, first_name=None,
                 last_name=None,
                 original_person_image=None,
                 potential_path_person=None):
        self.first_name = first_name
        self.last_name = last_name
        self.full_name = f"{first_name} {last_name}"
        self.original_person_image = original_person_image
        self.potential_path_person = potential_path_person
        self.path_twitter_post = None

        self.list_candidate_user_found_fb = []
        self.list_candidate_user_found_linkedin = []
        self.list_candidate_user_found_threads = []
        self.list_candidate_user_found_X = []
        self.list_candidate_user_found_instagram = []

        # Initialize social media links and images
        self.social_profiles = {
            'linkedin': {"username": "", "profile": "", "image": "", "Link_image": "", 'Face_Recognition_Result': ""},
            'facebook': {"username": "", "profile": "", "image": "", "Link_image": "", 'Face_Recognition_Result': ""},
            'X': {"username": "", "profile": "", "image": "", "Link_image": "", 'Face_Recognition_Result': ""},
            'instagram': {"username": "", "profile": "", "image": "", "Link_image": "", 'Face_Recognition_Result': ""},
            'threads': {"user_id": "", "username": "", "profile": "", "image": "", "Link_image": "",
                        'Face_Recognition_Result': ""},
        }

        # Profile information for each social media
        self.info_facebook = {"Overview": "", "Work_and_Education": "", "Places_Lived": "",
                              "Contact_and_Basic_Info": "",
                              "Family_Relationships": "", "Details_About": "", "Life_Events": ""}

        self.info_linkedin = {}

        self.info_X = {'path_tweets': "", 'tweets': "", 'other_info': ""}

        self.info_threads = {'Path_profile': "", "user_threads": "", "posts": "", "threads_info": ""}

        self.info_instagram = {"Biografia": "", "Sito_Personale": "", 'Path_profile': ""}

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    def add_social_profile(self, platform, profile_url, profile_image_url=None):
        """Adds or updates a social profile."""
        if platform in self.social_profiles:
            self.social_profiles[platform]['profile'] = profile_url
            self.social_profiles[platform]['image'] = profile_image_url or ""
        else:
            print(f"{platform} is not a recognized platform.")

    def get_social_profile(self, platform):
        """Retrieves profile information for a given social media platform."""
        return self.social_profiles.get(platform, "Social platform not found.")

    def update_person_info(self, platform, info_dict):
        """Updates the person's info for a specific platform."""
        platform_info_attr = f"info_{platform}"
        if hasattr(self, platform_info_attr):
            getattr(self, platform_info_attr).update(info_dict)
        else:
            print(f"{platform} info not found.")

    def remove_social_profile(self, platform):
        """Removes a social profile from the person."""
        if platform in self.social_profiles:
            self.social_profiles[platform] = {"profile": "", "image": ""}
        else:
            print(f"{platform} is not a recognized platform.")

    def __str__(self):
        return (f"First Name: {self.first_name}\n"
                f"Last Name: {self.last_name}\n"
                f"Full Name: {self.full_name}\n"
                f"Original Person Image: {self.original_person_image}\n"
                f"Potential Path Person: {self.potential_path_person}\n"
                f"Candidate Users Found on Facebook: {self.serialize_candidates(self.list_candidate_user_found_fb)}\n"
                f"Candidate Users Found on LinkedIn: {self.serialize_candidates(self.list_candidate_user_found_linkedin)}\n"
                f"Candidate Users Found on Threads: {self.serialize_candidates(self.list_candidate_user_found_threads)}\n"
                f"Candidate Users Found on X: {self.serialize_candidates(self.list_candidate_user_found_X)}\n"
                f"Candidate Users Found on Instagram: {self.serialize_candidates(self.list_candidate_user_found_instagram)}\n"
                f"Social Profiles: {self.social_profiles}\n"
                f"Facebook Info: {self.info_facebook}\n"
                f"LinkedIn Info: {self.info_linkedin}\n"
                f"X Info: {self.info_X}\n"
                f"Threads Info: {self.info_threads}\n"
                f"Instagram Info: {self.info_instagram}")

    def save_to_json(self, file_path):
        """Saves the person's data to a JSON file."""
        try:
            with open(file_path, "w") as file:
                file.write(json.dumps(self.person_to_dict(), indent=4))

        except Exception as e:
            print(f"An error occurred while saving data: {e}")

    def serialize_candidates(self, candidates_list):
        # Converte ogni Candidate in stringa usando __str__()
        result_list = []
        for candidate in candidates_list:
            result_list.append(candidate.candidate_to_dict())
        return result_list

    def person_to_dict(self):
        """Return a JSON-serializable dict of the Person object."""

        return {
            "first_name": self.first_name,
            "last_name": self.last_name,
            "full_name": self.full_name,
            "original_person_image": self.original_person_image,
            "potential_path_person": self.potential_path_person,

            # 🔥 QUI viene fatta la conversione Candidate -> stringa
            "list_candidate_user_found_fb": self.serialize_candidates(self.list_candidate_user_found_fb) if len(
                self.list_candidate_user_found_fb) > 0 else [],
            "list_candidate_user_found_linkedin": self.serialize_candidates(
                self.list_candidate_user_found_linkedin) if len(self.list_candidate_user_found_linkedin) > 0 else [],
            "list_candidate_user_found_threads": self.serialize_candidates(
                self.list_candidate_user_found_threads) if len(self.list_candidate_user_found_threads) > 0 else [],
            "list_candidate_user_found_X": self.serialize_candidates(self.list_candidate_user_found_X) if len(
                self.list_candidate_user_found_X) > 0 else [],
            "list_candidate_user_found_instagram": self.serialize_candidates(
                self.list_candidate_user_found_instagram) if len(self.list_candidate_user_found_instagram) > 0 else [],

            "social_profiles": self.social_profiles,
            "info_facebook": self.info_facebook,
            "info_linkedin": self.info_linkedin,
            "info_X": self.info_X,
            "info_threads": self.info_threads,
            "info_instagram": self.info_instagram,
        }

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

#
# Metodo che estrapola le infomazioni sul social Twitter
#
# @param peoplelist Lista di persone identificate di cui recuperare le informazioni
# @return peoplelist Lista di persone aggioranata con le informazioni estrapolate
#
class fill_twitter:
    def __init__(self, peoplelist = None, people_to_search = 5, show_browser=False):
        if peoplelist is None:
            peoplelist = []
        self.peoplelist = peoplelist
        self.show_browser = show_browser
        self.people_to_search = people_to_search
        self.path = f'Fill_modules/People_dir/'
        os.makedirs(self.path, exist_ok=True)

        # social_account = accounts.SocialMediaAccounts().get_account(platform='X')
        #
        # self.username = social_account['username']
        # self.password = social_account['password']
        self.TwitterfinderObject = None

    def pre_processing(self):
        path_twitter_post = os.path.join(
            self.path,
            'twitter', 'automatic')

        if not os.path.exists(path_twitter_post):
            os.makedirs(path_twitter_post, exist_ok=True)

        print('[X] Path people_list: ', path_twitter_post)

        for idx, person in enumerate(self.peoplelist):

            x_username = (person.full_name).replace(' ', '')
            print('\t[X Twitter] Username: ', x_username)
            
            path_twitter_post_user = os.path.join(path_twitter_post, x_username)

            if not os.path.exists(path_twitter_post_user):
                os.makedirs(path_twitter_post_user, exist_ok=True)

            print(f'\t[X] Path {x_username} people_list: {path_twitter_post_user}')

            person_x = self.pre_processing_manual(
                x_username=x_username,
                twit_dir=path_twitter_post_user
            )

            person.info_X = person_x.info_X
            person.social_profiles = person_x.social_profiles

            full_name = person_x.info_X['other_info']['full_name']
            if person.full_name is None or person.full_name == '':
                person.full_name = full_name

            first_name = person_x.info_X['other_info']['first_name']
            if person.first_name is None or person.first_name == '':
                person.first_name = first_name

            last_name = person_x.info_X['other_info']['last_name']
            if person.last_name is None or person.last_name == '':
                person.last_name = last_name

            original_person_image = person_x.info_X['other_info']['profile_image']
            if person.original_person_image is None or person.original_person_image == '':
                person.original_person_image = original_person_image

            if person.path_twitter_post is None or person.path_twitter_post == '':
                person.path_twitter_post = path_twitter_post_user

            print(f'[X] Pre processing done for {x_username}.')
            path = f"{path_twitter_post_user}/{x_username}_person_tw.json"
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(person.person_to_dict(), f, indent=4)

        print(f'[X] Pre processing Done for all.')

        return self.peoplelist, path_twitter_post
            
    def pre_processing_manual(self,
                              url= None,
                              x_username= None,
                              twit_dir=None):

        if twit_dir is not None:
            if not os.path.exists(twit_dir):
                os.makedirs(twit_dir, exist_ok=True)
                print('\t[X (Twitter) Manual] Directory of {} created!'.format(x_username))
        else:
            twit_dir = os.path.join(
                self.path,
                'twitter', 'manual', x_username)

            if not os.path.exists(twit_dir):
                os.makedirs(twit_dir, exist_ok=True)

        print('\t[X Twitter Manual] Path: ', twit_dir)

        print('\t[X (Twitter) Manual] Scraping of {} in Progress!'.format(x_username))

        global start
        start = False

        file_name = f'{x_username}_tweets_tw.json'
        path_save = os.path.join(twit_dir,file_name)

        def collect_tweet():
            global start
            start = True
            try:
                print('\t[X (Twitter) Manual] Collecting Tweets')

                # Effettua la ricerca di una persona sul social Facebook
                scrape_profile(
                    twitter_username= x_username,
                    output_format="json",
                    tweets_count=100,
                    directory=twit_dir,
                    filename=file_name.split('.')[0],
                    headless=False,
                    browser='chrome'
                    )
                print('\t[X (Twitter) Manual] Collecting Tweets Done!')

                with open(path_save, 'r') as file:
                    data = json.load(file)

                # Per scrivere il JSON formattato su un file
                with open(path_save, 'w') as file:
                    json.dump(data, file, indent=4)
            except Exception as e:
                print('\t[X (Twitter) Manual] Error while making the collect_tweet methods.')
                data = {}
                with open(path_save, 'w') as file:
                    json.dump(data, file, indent=4)
                print('Salvato file vuoto: ', {data == {}})
                start = False
                pass
        
        th1 = Thread(target=collect_tweet)
        th1.start()

        th1.join()
        start = False
        
        print('\t[X (Twitter) Manual] Scraping of {} Done!'.format(x_username))
        print('\t[X (Twitter) Manual] Saving Data..')

        with open(path_save, 'r') as file:
            data = json.load(file)
        print(f'\t[X (Twitter) Manual] Saved in {path_save}')

        if data != {}:
            data_tmp = {
                'username': find_first_key_value(data, 'username'),
                'name': find_first_key_value(data, 'name'),
                'profile_picture': find_first_key_value(data, 'profile_picture'),
                'tweet_url': find_first_key_value(data, 'tweet_url'),
            }

            username_candidate = data_tmp['username']
            full_name_candidate = data_tmp['name']
            first_name_candidate = full_name_candidate.split(' ')[0] if full_name_candidate else None
            last_name_candidate = full_name_candidate.split(' ')[-1] if full_name_candidate else None
            profile_image_candidate = data_tmp['profile_picture']
            url_profile = data_tmp['tweet_url'].split(r'\status')[0] if data_tmp['tweet_url'] else None

            local_path_img = os.path.join(twit_dir, f'{username_candidate}_tw.jpg')

            list_candidate_user_found_X =  {
                "username": username_candidate,
                "full_name": full_name_candidate,
                "first_name": first_name_candidate,
                "last_name": last_name_candidate,
                "profile_image": profile_image_candidate,
                "url_profile": url_profile,
                "path_file" : path_save,
                'local_path_img': local_path_img,
            }

            threading.Thread(
                target=self.save_img,
                args=(profile_image_candidate, local_path_img)
            ).start()

            print(f'\t[X (Twitter) Manual] Image saved in {local_path_img}')

            person = Person(
                first_name=first_name_candidate,
                last_name=last_name_candidate,
                original_person_image=local_path_img,
                potential_path_person=twit_dir)

            person.social_profiles['X']['username'] = x_username
            person.social_profiles['X']['profile'] = url_profile
            person.social_profiles['X']['Link_image'] = profile_image_candidate
            person.social_profiles['X']['image'] = local_path_img
            person.info_X['path_tweets'] = path_save
            person.info_X['tweets'] = data
            person.info_X['other_info'] = list_candidate_user_found_X
            person.info_X['username'] = x_username

            print('\t[X (Twitter) Manual] Pre processing manual done')
            return person
        else:
            self.TwitterfinderObject = Twitterfinder()
            driver = self.TwitterfinderObject.driver
            driver.get(url)
            try:
                name = driver.find_element(By.CLASS_NAME, "css-1jxf684 r-bcqeeo r-1ttztb7 r-qvutc0 r-poiln3")
            except NoSuchElementException:
                print('\t[X (Twitter) Manual] Error while finding the name.')
                name = None
                pass

            print('\t[X Twitterfinder] Searching name!')

            person = Person(
                first_name=None,
                last_name=None,
                original_person_image=None,
                potential_path_person=twit_dir)

            if name is not None:
                full_name_tw = name.text
                if full_name_tw:
                    print('\t[X (Twitterfinder) Manual] Name: ', name)

                    parts = full_name_tw.split()

                    if person.full_name is None or person.full_name == "":
                        person.full_name = full_name_tw

                    if (person.first_name is None or
                            person.last_name is None or
                                person.last_name == "" or
                                    person.first_name == ""):
                        if len(parts) == 0:
                            person.first_name = ""
                            person.last_name = ""

                        elif len(parts) == 1:
                            person.first_name = parts[0]
                            person.last_name = ""

                        elif len(parts) == 2:
                            person.first_name = parts[0]
                            person.last_name = parts[1]

                        else:
                            # Tutto tranne l'ultima parola è nome
                            person.first_name = " ".join(parts[:-1])
                            # L'ultima parola è il cognome
                            person.last_name = parts[-1]
                else:
                    print(f"[Twitterfinder] Full_name Not Found -> I'll use the username: {x_username}")
                    person.first_name = x_username
                    person.last_name = x_username
            else:
                print(f"[Twitterfinder] Full_name Not Found -> I'll use the username: {x_username}")
                person.first_name = x_username
                person.last_name = x_username

            person.info_X['username'] = x_username
            person.social_profiles['X']['username'] = x_username
            person.social_profiles['X']['profile'] = url

            return person, twit_dir

    def save_img(self, url_image_user, local_path_img):
        self.save_image(url_image_user, local_path_img)

    def save_image(self, url_image_user, local_path_img):
        try:
            response = requests.get(url_image_user, stream=True)
            response.raise_for_status()

            with open(f'{local_path_img}', 'wb') as out_file:
                response.raw.decode_content = True
                shutil.copyfileobj(response.raw, out_file)
            del response

        except requests.exceptions.RequestException as e:
            print('Error', f'Error while create jpg image')
            pass

    def collect_informations(self,peoplelist):
        self.peoplelist = peoplelist
        amount = len(self.peoplelist)
        # self.TwitterfinderObject = Twitterfinder()
        for person in self.peoplelist:
        
            def collect_info_profiles():
                global info_X_tmp
                info_X_tmp = {}

                try:
                    # Effettua la ricerca delle informazioni di una persona sul social Facebook
                    info_X_tmp = self.TwitterfinderObject.crawlerDataTwitter(
                        link_user = person.social_profiles['X']['profile'], 
                    )
                except Exception as e:
                    print('X (Twitter) Error', f'Error while making the collect_info_profiles methods.')
                    info_X_tmp = {}
                    raise

            th1 = Thread(target=collect_info_profiles)
            th1.start()
            th1.join()

            person.info_X = info_X_tmp

            person.save_to_json(os.path.join(person.path_twitter_post, f'{person.full_name}_{idx}_tw.json'))

        return self.peoplelist

    def collect_info_person(self, link_user):

        try:
            # Effettua la ricerca delle informazioni di una persona sul social Facebook
            info_X_tmp = self.TwitterfinderObject.crawlerDataTwitter(
                link_user=link_user,
            )
        except Exception as e:
            print('X (Twitter) Error', f'Error while making the collect_info_profiles methods.')
            info_X_tmp = {}
            raise

        return info_X_tmp

import argparse
import os

def manual(url, username):
    print("[X (Twitter)]", " Manual")

    tw = fill_twitter(show_browser=False)

    x_username = (url.split('x.com/')[-1])
    print('\t[X (Twitter)]', " x_username ", x_username)

    return tw.pre_processing_manual(
        url=url,
        x_username = x_username,
    )

def automatic(peoplelist, show_browser, people_to_search):

    x = fill_twitter(peoplelist=peoplelist, show_browser=show_browser,
                                  people_to_search=people_to_search)
    return x.pre_processing()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("--url", required=False)
    parser.add_argument("--task", required=False)
    parser.add_argument("--peoplelist", required=False)
    parser.add_argument("--people_to_search", required=False)

    args = parser.parse_args()

    if args.task == 'Manual_S':
        x_username = (args.url.split('x.com/')[-1])
        # Chiamata alla funzione manual con parametri CLI
        person, path_save = manual(
            url=args.url,
            username=x_username,
        )

        print('[Twitter X] Manual Single Terminated.')
        path = f"{path_save}/{x_username}_person_tw.json"
        with open(path, 'w') as f:
            json.dump(person.person_to_dict(), f)
        print(f'[Twitter X] Manual Single Saved in {path}.')

    elif args.task == "Automatic":

        print('[Twitter X] Automatic')

        print('[Twitter X] Searching path: ', args.peoplelist)
        print('[Twitter X] Actual path: ', os.getcwd())

        if args.peoplelist:
            with open(args.peoplelist, 'r') as f:
                data = json.load(f)

        people = []
        for idx, p_data in data.items():
            person = load_from_json(data=p_data)
            people.append(person)

        people_list, path_twitter_post = automatic(
            peoplelist=people,
            show_browser=False,
            people_to_search=int(args.people_to_search)
        )

        json_people = {}
        for idx, person in enumerate(people_list):
            json_people[idx] = person.person_to_dict()

        path = 'Fill_modules/peoplelist_result.json'
        with open(path, 'w') as f:
            json.dump(json_people, f)
        print('[X] File di appoggio ri_salvato!')

        print('[Twitter X] Automatic Terminated.')
        print(f'[Twitter X] Saving in {path_twitter_post}.')
        print('[Twitter X] Automatic Saved.')