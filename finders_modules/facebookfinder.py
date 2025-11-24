# -*- coding: utf-8 -*-
from __future__ import print_function

import json
import os
import re

import tkinter as tk
from tkinter import messagebox
import shutil
from datetime import datetime
from time import sleep

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from Fill_modules import fill_fb
from configuration.BrowserDriverConfigurations import BrowserDriverConfigurations
from utils.candidate import Candidate
from utils.person import Person
from finders_modules.utils_finder import normalize_name_tokens, save_image
from finders_modules.utils_finder import twoStepVerification

# Classe concreta che istanzia il crawler per il social Facebook
class Facebookfinder(object):
    timeout = 5 #timeout per rallentare l'esecuzione e similuare l'operatore delll'utente reale, per limitare blocchi anti-crawler
    #
    # Metodo init per settare proprietà del browser
    #
    # @param showbrowser Stringa legata al comando da console, se presente si richiede la visine in real-time della ricerca
    #
    def __init__(self, showbrowser, username, password):
        self.username = username
        self.password = password
        # display = Display(visible=0, size=(1600, 1024))
        # display.start()
        # if not showbrowser:
        #     os.environ['MOZ_HEADLESS'] = '1'
        
        chrome_conf = BrowserDriverConfigurations()
        self.driver = chrome_conf.get_driver(enable_profile=None)
        self.chrome_profile = chrome_conf.get_enable_profile()

        self.driver.implicitly_wait(3)
        self.driver.delete_all_cookies()
        self.wait = WebDriverWait(self.driver, 10)

        self.xpath_email = "//input[@id=\'email\']"
        self.xpath_psw = "//input[@id=\'pass\']"
        self.xpath_buttonlogin = "//button[@id=\'loginbutton\']"

        self.start_page = 'http://www.google.com/'
        self.loginPage = "https://www.facebook.com/login"

        self.rearch_page = "https://www.facebook.com/search/people/?q="

        self.info_facebook = {}

        # firefoxprofile = webdriver.FirefoxProfile()
        # firefoxprofile.set_preference("permissions.default.desktop-notification", 1)
        # firefoxprofile.set_preference("dom.webnotifications.enabled", 1)
        # firefoxprofile.set_preference("dom.push.enabled", 1)
        # self.driver = webdriver.Firefox(firefox_profile=firefoxprofile)
        # self.driver.implicitly_wait(3)
        # self.driver.delete_all_cookies()

    #
    # Metodo che effettua il login al social
    #
    # @param username Stringa che rappresenta l'username dell'account da usare per il login
    # @param password Stringa che rappresenta l'password dell'account da usare per il login
    #
    def load_or_login(self):
        cookie_file = "cookies\cookies_facebook.json"
        today = datetime.now().strftime("%Y-%m-%d")

        # Se non ci sono cookie → login
        if not os.path.exists(cookie_file):
            print("[*] Nessun cookie esistente. Faccio login...")
            return self.doLogin()

        # Leggo cookie
        try:
            with open(cookie_file, "r") as f:
                data = json.load(f)
        except:
            print("[!] Cookie corrotti. Faccio login...")
            return self.doLogin()

        # # Se i cookie non sono di oggi → login
        # if data.get("date") != today:
        #     print("[*] Cookie non aggiornati (giorno diverso). Login necessario...")
        #     return self.doLogin()

        # Cookie validi → caricamento
        print("[+] Cookie di oggi trovati. Ripristino sessione...")
        self.driver.get("https://www.facebook.com")
        sleep(2)

        for cookie in data.get("cookies", []):
            cookie.pop("sameSite", None)
            try:
                self.driver.add_cookie(cookie)
            except:
                pass

        self.driver.refresh()
        sleep(2)
        print('Current: ', self.driver.current_url)
        # Verifico se login ok
        if "feed" in self.driver.current_url or "mynetwork" in self.driver.current_url or 'home' in self.driver.current_url or 'facebook.com' in self.driver.current_url:
            print("[+] Sessione ripristinata senza login.")
            return True
        else:
            print("[!] Cookie non validi. Rifaccio login...")
            return self.doLogin()

    def doLogin(self):
        if self.chrome_profile is None:
            self.driver.get(self.start_page)
            sleep(3) # Let the user actually see something!
            try:
                self.check_cookies()
            except Exception as e:
                messagebox.showerror('Error', f'Error Google Cookies\n{e}')
                return False
        sleep(3) # Let the user actually see something!
        try:
            self.load_facebook_page()
        except Exception as e:
            messagebox.showerror('Error', f'Error Facebook Cookies\n{e}')
            return False
        sleep(2) # Let the user actually see something!
        try:
            self.facebook_login()
        except Exception as e:
            messagebox.showerror('Error', f'Error Facebook Login\n{e}')
            return False
        sleep(2) # Let the user actually see something!
        try:
            self.bypass_privacy()
        except Exception as e:
            messagebox.showerror('Error', f'Error Policy Button\n{e}')
            return False
        sleep(2)

        try:
            if 'two_step_verification' in self.driver.current_url: #correzione typo
                print('[Facebook] Verification Found!')

                risultato_verifica = twoStepVerification().two_step_verification() #uso l'istanza creata precedentemente

                if risultato_verifica is True:
                    print("[Facebook] Verification Done!")
                else:
                    print("[Facebook] Verification Not Done!")
            else:
                print('[Facebook] Verification Not Found!')
                
        except Exception as e:
            messagebox.showerror('Error', f'Error Verification!\n{e}')
            return False

        sleep(5)

        # --- SALVATAGGIO COOKIE GIORNALIERO ---
        from datetime import datetime
        import json

        cookies = self.driver.get_cookies()
        today = datetime.now().strftime("%Y-%m-%d")

        data = {
            "date": today,
            "cookies": cookies
        }
        if not os.path.exists('cookies/'):
            os.makedirs('cookies/')

        with open("cookies\cookies_facebook.json", "w") as f:
            json.dump(data, f)

        print("[+] Cookies salvati per il giorno:", today)

        return True

    def check_cookies(self):
        try:
            google_cookie_element = self.wait.until(
                EC.element_to_be_clickable((By.ID, 'CXQnmb'))
            )
            print('[Facebook] Found Google Cookies!')
            google_cookie_element.click()
            # print('Google Cookies Done!')

        except Exception as e:
            print('[Facebook] Google Cookies Not Done (timeout)!')

    def load_facebook_page(self):
            self.driver.get(self.loginPage)
            try:
                facebook_cookie_element = self.driver.find_element(By.XPATH, '//*[@id="facebook"]/body/div[3]/div[2]/div/div/div/div/div[3]/div[2]/div/div[1]/div[2]')
                facebook_cookie_element.click()
                print('[Facebook] Facebook cookies Done!')
            except Exception as e: # Cattura eccezioni più specifiche, se possibile
                print(f"[Facebook] Couldn't click Facebook cookie element!")
                pass

    def facebook_login(self):
        try:
            # Wait for the title element to contain 'Facebook'
            title_fb = WebDriverWait(self.driver, 10).until(
                EC.text_to_be_present_in_element((By.CLASS_NAME, '_9axz'), 'Facebook')
            )
            print('[Facebook] Login....')  # Print login status

            # Fill in login details using XPaths
            username_field = self.driver.find_element(By.XPATH, self.xpath_email)
            username_field.click()
            username_field.send_keys(self.username)

            password_field = self.driver.find_element(By.XPATH, self.xpath_psw)
            password_field.click()
            password_field.send_keys(self.password)

            login_button = self.driver.find_element(By.XPATH, self.xpath_buttonlogin)
            login_button.click()

        except TimeoutException:
            print('[Facebook] Facebook Page Not Done (timeout)!')
        except NoSuchElementException as e:
            print(f'[Facebook] Error finding element: {e}')  # Handle specific NoSuchElementException

    def bypass_privacy(self):
        if 'privacy/consent' in self.driver.current_url:
            print('[Facebook] Privacy Consent Found!')

            try:
                # Wait for the "Not now" button to appear
                button_policy = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'div[aria-label="Not now"]'))
                )
                button_policy.click()
            except TimeoutException:
                print('[Facebook] Button Policy Not Found (timeout)!')
            except NoSuchElementException as e:
                print(f'[Facebook] Error finding button: {e}')  # Handle specific NoSuchElementException
        else:
            print('[Facebook] No privacy Consent Found!')

    def clone_session(self):
        cookies = self.driver.get_cookies()

        # nuovo driver
        new_driver = webdriver.Chrome()
        new_driver.get("https://facebook.com")

        for cookie in cookies:
            try:
                new_driver.add_cookie(cookie)
            except:
                pass

        new_driver.refresh()
        return new_driver

    # Metodo che effettua la ricerca di una persona sul social
    #
    # @param first_name Stringa che rappresenta il nome della persona da cercare
    # @param last_name Stringa che rappresenta il cognome della persona da cercare
    # @param username Stringa che rappresenta l'username dell'account da usare per il login
    # @param password Stringa che rappresenta l'password dell'account da usare per il login
    #
    # @return picturelist Array di persone trovare rispetto al nome in input
    #
    def getFacebookProfiles(self, person, people_to_search, path_to_person):
        picturelist = []
        user_objs = []

        try:
            url = self.rearch_page + person.first_name + "%20" + person.last_name
            self.driver.get(url)

            try:
                # Ottieni direttamente il titolo
                titolo = self.driver.title
                # print(f"[Facebook] Il titolo della pagina è: {titolo}")

                if f'{person.first_name} {person.last_name}' in titolo:
                    print(f'\t[Facebook] Research Page for {person.first_name} {person.last_name} Found!')

                    # Aspetta che almeno un elemento utente sia presente
                    self.wait.until(
                        EC.presence_of_all_elements_located(
                            (By.CLASS_NAME,'xjp7ctv')
                        )
                    )
                    user_objs = self.driver.find_elements(By.CLASS_NAME,
                                                  'xjp7ctv')
                    user_objs = user_objs[1:]
                    print(f'\t[Facebook] Found {len(user_objs)} Facebook Profiles for {person.first_name} {person.last_name}!')

                else:
                    print(f'{person.first_name} {person.last_name} not found in Title Page!')

            except Exception as e:
                messagebox.showinfo('Info', f'No user found for {person.full_name} after timeout.')
                return []

            if len(user_objs) > 0:
                print(f'\t[Facebook] Collect Facebook Profiles for {person.first_name} {person.last_name}!')
                collected = 0
                for i in range(len(user_objs)):
                    user_name = ''
                    link_element = None
                    try:
                        # Trova l'elemento <a> all'interno di user_objs[i]
                        link_element = user_objs[i].find_element(By.TAG_NAME, "a")

                        user_name = link_element.text
                        print(f'\t[Facebook] User {i}: {user_name}')

                    except Exception as e:
                        print(f'[Facebook] Error finding user')
                        continue

                    if user_name:
                        
                        user_name_n1 = normalize_name_tokens(user_name)
                        p_full_name_n2 = normalize_name_tokens(person.full_name)

                        user_set = set(user_name_n1)
                        person_set = set(p_full_name_n2)

                        match = user_set.issubset(person_set)

                        if match:
                            print(f'\t[Facebook] User {i} Match Found!')
                            print(f'\t[Facebook] Searching image for User {i}')

                            # Recupera l'attributo href
                            url_profile = link_element.get_attribute("href")
                            print(f'\t[Facebook] User Profile {i} Found!')
                            if url_profile:
                                try:
                                    print(f'\t[Facebook] Searching image for User {i}')

                                    url_image_user, local_path_img = self.getProfileImage(
                                        link_user=url_profile,
                                        storing_dir_path=path_to_person,
                                        user_name=user_name,
                                        count = i)

                                    if url_image_user is not None and local_path_img is not None:
                                        print(f'\t[Facebook] Image element of {user_name} Found!')
                                        picturelist.append(
                                            Candidate(
                                                username = user_name,
                                                link_image = url_image_user,
                                                url_profile = url_profile,
                                                local_path_img = local_path_img))
                                    else:
                                        print(f'\t[Facebook] Image element of {user_name} Not Found!')
                                        continue
                                except Exception as e:
                                    print(e)
                                    continue
                            else:
                                print(f'\t[Facebook] Link of {user_name} Not Found!')

                    if collected >= people_to_search:
                        break
                    collected = collected + 1
                return picturelist
            else:
                print('[Facebook] No Facebook Profiles Found!')
                return []

        except Exception as e:
            messagebox.showerror('Error', f'Error in getFacebookProfiles: {e}')
            raise

    def getProfileImage(self, link_user, storing_dir_path, user_name, count):

        # Salva la finestra originale
        sleep(2)
        original_window = self.driver.current_window_handle
        url_image_user = None
        local_path_img = None

        # Apri una nuova scheda
        self.driver.switch_to.new_window('tab')
        print('\t\t[Facebook] New window opened!')
        sleep(2)

        # Ora lavora nella nuova scheda
        self.driver.get(link_user)
        sleep(3)

        try:

            url_image_user = self.find_image()
            if url_image_user:
                print(f'\t\t[Facebook] Image Link of {user_name} Found!')
            else:
                # print(f'[Facebook] Image Link of {user_name} NOT Found!\n')
                raise Exception(f'[Facebook] Image Link of {user_name} NOT Found!')

            local_path_img = os.path.join(storing_dir_path, f'{user_name}_{count}_fb.jpg')
            save_image(url_image_user, local_path_img)
            print(f'\t\t[Facebook] Image Link of {user_name} Save as {user_name}_{count}_fb.jpg')

        finally:
            # cleanup: chiudi la tab nuova e torna alla finestra originale
            try:
                # Chiudi la scheda corrente (quella nuova)
                self.driver.close()
                sleep(1)
                # Ritorna alla finestra originale (se ancora disponibile)
                if original_window in self.driver.window_handles:
                    self.driver.switch_to.window(original_window)
                    sleep(1)
            except Exception as cleanup_err:
                # non vogliamo che il cleanup impedisca il return o nasconda errori
                print(f'\t\t[Facebook][getProfileImage] Cleanup error: {cleanup_err}')

        return url_image_user, local_path_img

    def find_image(self):
        try:
            print('\t\t[Facebook] Find Image - First Try!')
            image_user = self.driver.find_elements(
                By.CSS_SELECTOR, f'svg[role="img"] > g > image[preserveAspectRatio="xMidYMid slice"]')
            sleep(1)
            image_user = image_user[1:][0]
            link = image_user.get_attribute('xlink:href')
            print(f'\t\t[Facebook] Found Image in First Try')
            return link

        except Exception as e:
            # print('Primo metodo non andato a buon fine')
            try:
                print('\t\t[Facebook] Find Image - Second Try!')
                image_user = self.driver.find_elements(
                    By.XPATH,
                    f'//*[@id="mount_0_0_MH"]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div/div/div[1]/div[2]/div/div/div/div[1]/div/a/div/svg/g/image')
                sleep(1)
                image_user = image_user[1:][0]
                link =  image_user.get_attribute('xlink:href')
                print(f'\t\t[Facebook] Found Image in Second Try')
                return link

            except Exception as e:
                # print('Secondo metodo non andato a buon fine')
                try:
                    print('\t\t[Facebook] Find Image - Third Try!')
                    image_user = self.driver.find_elements(
                        By.XPATH,
                        f'mount_0_0_MH > div > div:nth-child(1) > div > div.x9f619.x1n2onr6.x1ja2u2z > div > div > div.x78zum5.xdt5ytf.x1t2pt76.x1n2onr6.x1ja2u2z.x10cihs4 > div.x78zum5.xdt5ytf.x1t2pt76 > div > div > div:nth-child(1) > div.x9f619.x1ja2u2z.x78zum5.x2lah0s.x1n2onr6.xl56j7k.x1qjc9v5.xozqiw3.x1q0g3np.x1l90r2v.x1ve1bff > div > div > div > div.x15sbx0n.x1xy773u.x390vds.x13bxmoy.x14xzxk9.xmpot0u.xs6kywh.x5wy4b0 > div > a > div > svg > g > image')
                    sleep(1)
                    image_user = image_user[1:][0]
                    link = image_user.get_attribute('xlink:href')
                    print(f'\t\t[Facebook] Found Image in Third Try')
                    return link

                except Exception as e:
                    # print('Terzo metodo non andato a buon fine')
                    try:
                        print('\t\t[Facebook] Find Image - Fourth Try!')
                        # Usando XPath
                        image_element = self.driver.find_elements(By.XPATH,
                                                                 '//image[@preserveAspectRatio="xMidYMid slice"]')
                        image_element = image_element[1:][0]
                        # Recupera l'attributo
                        link =  image_element.get_attribute('xlink:href')
                        print(f'\t\t[Facebook] Found Image in Fourth Try')
                        return link

                    except Exception as e:
                        # print('Quarto metodo non andato a buon fine')
                        try:
                            print('\t\t[Facebook] Find Image - Last Try!')
                            # Se ci sono più elementi, specifica meglio
                            image_element = self.driver.find_elements(By.CSS_SELECTOR,
                                                                     'svg image[preserveAspectRatio="xMidYMid slice"]')
                            image_element = image_element[1:][0]
                            link = image_element.get_attribute('xlink:href')
                            print(f'\t\t[Facebook] Found Image in Last Try')
                            return link

                        except Exception as e:
                            print('[Facebook][ERROR] Image not Found!')
                            return None

    #
    # Metodo che estrepola le informazioni circa la persona trovata
    #
    # @param username Stringa che rappresenta l'username dell'account da usare per il login
    # @param password Stringa che rappresenta l'password dell'account da usare per il login
    # @param url Stringa legata al profilo della persona ricercata, identificata tramite face-recognition
    #
    # @return facebook Array di informazioni estrapolate circa la persona trovata
    #
    def crawlerDataFacebook(self, link_user):
        link = link_user.split('?')[0]

        self.driver.get(link)

        self.info_facebook = {"Overview": "",
                              "Work_and_Education": "", 
                              "Places_Lived": "", 
                              "Contact_and_Basic_Info": "",
                              "Family_Relationships": "", 
                              "Details_About": "",
                              "Life_Events": ""}
        
        sleep(2)

        #sezione Overview
        self.driver.get(f'{link}/about')

        def extract_from_about():

            searchresponse_about_overview = self.driver.page_source.encode('utf-8')
            soupParser_about_overview = BeautifulSoup(searchresponse_about_overview, 'html.parser')

            overview = {'Work':'Work at ',
                            'Education':'Studied at ',
                            'Places_lived':'Lives in  ',
                            'Places':'From ',
                            'Relationship':'In a Relationship with ',}
            map_idx = {
                0 : 'Work',
                1 : 'Education',
                2 : 'Places_lived',
                3 : 'Places',
                4 : 'Relationship'
            }
            divs = soupParser_about_overview.find_all('div', {'class':'x9f619 x1n2onr6 x1ja2u2z x78zum5 xdt5ytf x193iq5w xeuugli x1r8uery x1iyjqo2 xs83m0k xamitd3 x1icxu4v x25sj25 x10b6aqq x1yrsyyn'})

            if divs:
                # print(f'[Crawler Facebook Data] Found {len(divs)} information')

                for i, div in enumerate(divs):
                    # print(f'[Crawler Facebook Data] Found {i}')
                    span = div.find('span', {'class': 'xjp7ctv'})
                    if span:
                        overview[map_idx[i]] = overview[map_idx[i]] + span.text
                    else:
                        # print(f'[Crawler Facebook Data] No Span Found')
                        if i == 0:
                            overview[map_idx[i]] = 'No workplaces to show'
                        elif i == 1:
                            overview[map_idx[i]] = 'No information on education'
                        elif i == 2:
                            overview[map_idx[i]] = 'No information on places lived'
                        elif i == 3:
                            overview[map_idx[i]] = 'No information on places'
                        elif i == 4:
                            overview[map_idx[i]] = 'No information on relationship'

                return overview

            else:
                print(f'[Crawler Facebook Data] No Information found (Overview)')
                return {}

        self.info_facebook['Overview'] = extract_from_about()
        print("self.info_facebook['Overview']: ", self.info_facebook['Overview'])

        sleep(2)

        #sezione Work_and_Education
        self.driver.get(f'{link}/about_work_and_education')

        def extract_from_work_and_education():

            searchresponse_about_overview = self.driver.page_source.encode('utf-8')
            soupParser_about_overview = BeautifulSoup(searchresponse_about_overview, 'html.parser')

            Work_and_Education = {'Work':'Work at ',
                        'College':'(College) Studied at ',
                        'High school':'(High school) Studied at '
                        }
            map_idx = {
                0 : 'Work',
                1 : 'College',
                2 : 'High school'
            }

            divs = soupParser_about_overview.find_all('div', {'class':'x9f619 x1n2onr6 x1ja2u2z x78zum5 xdt5ytf x193iq5w xeuugli x1r8uery x1iyjqo2 xs83m0k xamitd3 x1icxu4v x25sj25 x10b6aqq x1yrsyyn'})

            if divs:
                # print(f'[Crawler Facebook Data] Found {len(divs)} information')
                for i, div in enumerate(divs):
                    # print(f'[Crawler Facebook Data] Found {i}')
                    span = div.find('span', {'class': 'xjp7ctv'})
                    if span:
                        Work_and_Education[map_idx[i]] = Work_and_Education[map_idx[i]] + span.text
                    else:
                        # print(f'[Crawler Facebook Data] No Span Found')
                        if i == 0:
                            Work_and_Education[map_idx[i]] = 'No workplaces to show'
                        elif i == 1:
                            Work_and_Education[map_idx[i]] = 'No information on college'
                        elif i == 2:
                            Work_and_Education[map_idx[i]] = 'No information on High school'

                return Work_and_Education

            else:
                print(f'[Crawler Facebook Data] No Information found (about_work_and_education)')
                return {}

        self.info_facebook['Work_and_Education'] = extract_from_work_and_education()
        print("self.info_facebook['Work_and_Education']: ", self.info_facebook['Work_and_Education'])

        sleep(2)

        #sezione Places_Lived
        self.driver.get(f'{link}/about_places')

        def extract_from_about_places():

            searchresponse_about_overview = self.driver.page_source.encode('utf-8')
            soupParser_about_overview = BeautifulSoup(searchresponse_about_overview, 'html.parser')

            about_places = {'Current city': '',
                              'Hometown': '',
                              }
            map_idx = {
                0: 'Current city',
                1: 'Hometown',
            }

            divs = soupParser_about_overview.find_all('div', {
                'class': 'x9f619 x1n2onr6 x1ja2u2z x78zum5 xdt5ytf x193iq5w xeuugli x1r8uery x1iyjqo2 xs83m0k xamitd3 x1icxu4v x25sj25 x10b6aqq x1yrsyyn'})

            if divs:
                # print(f'[Crawler Facebook Data] Found {len(divs)} information')
                for i, div in enumerate(divs):
                    # print(f'[Crawler Facebook Data] Found {i}')
                    span = div.find('span', {'class': 'xjp7ctv'})
                    if span:
                        about_places[map_idx[i]] = about_places[map_idx[i]] + span.text
                    else:
                        # print(f'[Crawler Facebook Data] No Span Found')
                        if i == 0:
                            about_places[map_idx[i]] = 'No current city to show'
                        elif i == 1:
                            about_places[map_idx[i]] = 'No Hometown to show'

                return about_places

            else:
                print(f'[Crawler Facebook Data] No Information found (about_places)')
                return {}

        self.info_facebook['Places_Lived'] = extract_from_about_places()
        print("self.info_facebook['Places_Lived']: ", self.info_facebook['Places_Lived'])

        sleep(3)
        #sezione Contact_and_Basic_Info
        self.driver.get(f'{link}/about_contact_and_basic_info')

        def extract_from_about_contact_and_basic_info():
            import re

            def classify_string(value: str) -> str:
                if not value or not value.strip():
                    return "None"

                v = value.strip().lower()

                # Gender keywords
                gender_keywords = ["male", "female", "maschio", "femmina", "donna"]
                if any(g in v for g in gender_keywords):
                    return "Gender"

                # URL regex
                url_pattern = re.compile(
                    r'^(https?:\/\/)?'  # http:// or https:// optional
                    r'([\da-z\.-]+)\.([a-z\.]{2,6})'  # domain name
                    r'([\/\w \.-]*)*\/?$'  # path
                )

                if url_pattern.match(value.strip()):
                    return "Link"

                # Default
                return "Contact Info"

            searchresponse_about_overview = self.driver.page_source.encode('utf-8')
            soupParser_about_overview = BeautifulSoup(searchresponse_about_overview, 'html.parser')

            about_contact_and_basic_info = {'Contact info': 'No contact info',
                              'Links': 'No Links',
                              'Gender': 'No Gender',
                              }

            spans = soupParser_about_overview.find_all('span', {
                'class': "x193iq5w xeuugli x13faqbe x1vvkbs x1xmvt09 x1lliihq x1s928wv xhkezso x1gmr53x x1cpjm7i x1fgarty x1943h6x xudqn12 x3x7a5m x6prxxf xvq8zen xo1l8bm xzsf02u x1yc453h"})

            if spans:
                # print(f'[Crawler Facebook Data] Found {len(divs)} information')
                for i, span in enumerate(spans):
                    res = classify_string(span.text.strip())
                    if res == "Gender":
                        about_contact_and_basic_info['Gender'] = span.text.strip()
                    elif res == "Link":
                        about_contact_and_basic_info['Links'] = span.text.strip()
                    elif res == "Contact Info":
                        about_contact_and_basic_info['Contact info'] = span.text.strip()
                    elif res == "None":
                        pass

                return about_contact_and_basic_info

            else:
                print(f'[Crawler Facebook Data] No Information found (about_contact_and_basic_info)')
                return {}

        self.info_facebook['Contact_and_Basic_Info'] = extract_from_about_contact_and_basic_info()
        print("self.info_facebook['Contact_and_Basic_Info']: ", self.info_facebook['Contact_and_Basic_Info'])

        sleep(2)
        #sezione Family_Relationships
        self.driver.get(f'{link}/about_family_and_relationships')

        def extract_from_about_family_and_relationships():
            import re

            def classify_string(value: str) -> str:
                if not value or not value.strip():
                    return "None"

                v = value.strip().lower()

                # Relationship keywords
                relationship_keywords = [
                    "single",
                    "engaged",
                    "married",
                    "widowed",
                    "divorced",
                    "in a relationship",
                    "complicated",
                    "separated",
                    "partnered",
                    "fidanzato",
                    "fidanzata",
                    "sposato",
                    "sposata",
                    "celibe",
                    "nubile",
                    "vedovo",
                    "vedova",
                    "divorziato",
                    "divorziata",
                    "relazione",
                    "impegnato",
                    "impegnata"
                ]

                if any(g in v for g in relationship_keywords):
                    return "relationship"

                # Default
                return "Family Member"

            searchresponse_about_overview = self.driver.page_source.encode('utf-8')
            soupParser_about_overview = BeautifulSoup(searchresponse_about_overview, 'html.parser')

            Family_Relationships = {'Relationship': 'No relationship info to show',
                              'Family Member': 'No family members to show',
                              }

            spans = soupParser_about_overview.find_all('span', {
                'class': "x193iq5w xeuugli x13faqbe x1vvkbs x1xmvt09 x1lliihq x1s928wv xhkezso x1gmr53x x1cpjm7i x1fgarty x1943h6x xudqn12 x3x7a5m x6prxxf xvq8zen xo1l8bm xzsf02u x1yc453h"})

            if spans:
                # print(f'[Crawler Facebook Data] Found {len(divs)} information')
                for i, span in enumerate(spans):
                    res = classify_string(span.text.strip())
                    if res == "relationship":
                        Family_Relationships['Relationship'] = span.text.strip()
                    elif res == "Link":
                        Family_Relationships['Family Member'] = span.text.strip()
                    elif res == "None":
                        pass

                return Family_Relationships

            else:
                print(f'[Crawler Facebook Data] No Information found (Family_Relationships)')
                return Family_Relationships

        self.info_facebook['Family_Relationships'] = extract_from_about_family_and_relationships()
        print("self.info_facebook['Family_Relationships']: ", self.info_facebook['Family_Relationships'])

        sleep(3)

        #sezione Details_About
        self.driver.get(f'{link}/about_details')

        def extract_from_about_Details_About():

            searchresponse_about_overview = self.driver.page_source.encode('utf-8')
            soupParser_about_overview = BeautifulSoup(searchresponse_about_overview, 'html.parser')

            details = {'About': 'No additional details to show',
                        'Name pronunciation': 'No name pronunciation to show',
                       'Other names': 'No other names to show',
                       'Favorite quotes': 'No favorite quotes to show',
                       }

            spans = soupParser_about_overview.find_all('span', {
                'class': "x193iq5w xeuugli x13faqbe x1vvkbs x1xmvt09 x1lliihq x1s928wv xhkezso x1gmr53x x1cpjm7i x1fgarty x1943h6x xudqn12 x3x7a5m x6prxxf xvq8zen xo1l8bm xzsf02u x1yc453h"})

            for i, span in enumerate(spans):
                if i == 0:
                    details['About'] = span.text.strip()
                elif i == 1:
                    details['Name pronunciation'] = span.text.strip()
                elif i == 2:
                    details['Other names'] = span.text.strip()
                elif i == 3:
                    details['Favorite quotes'] = span.text.strip()

            return details

        self.info_facebook['Details_About'] = extract_from_about_Details_About()
        print("self.info_facebook['Details_About']: ", self.info_facebook['Details_About'])

        sleep(3)

        #sezione Life_Events
        self.driver.get(f'{link}/about_life_events')

        def extract_from_about_life_events():

            searchresponse_about_overview = self.driver.page_source.encode('utf-8')
            soupParser_about_overview = BeautifulSoup(searchresponse_about_overview, 'html.parser')

            about_life_events = {'Life events': 'No events to show'
                       }

            spans = soupParser_about_overview.find_all('span', {
                'class': "x193iq5w xeuugli x13faqbe x1vvkbs x1xmvt09 x1lliihq x1s928wv xhkezso x1gmr53x x1cpjm7i x1fgarty x1943h6x xudqn12 x3x7a5m x6prxxf xvq8zen xo1l8bm xzsf02u x1yc453h"})

            list_res = []
            for i, span in enumerate(spans):
                list_res.append(span.text.strip())

            if list_res:
                about_life_events['Life events']=list_res
                return about_life_events
            else:
                return about_life_events

        self.info_facebook['Life_Events'] = extract_from_about_life_events()
        print("self.info_facebook['Life_Events']: ", self.info_facebook['Life_Events'])

        sleep(3)

        self.driver.close()

        return self.info_facebook
    
    def getFacebookProfile(self, person, link_user, storing_dir_path):

        self.driver.get(link_user)
        sleep(3)

        user_name = link_user.split('www.facebook.com/')[-1]

        person.social_profiles['facebook']['username'] = user_name
        person.social_profiles['facebook']['profile'] =  link_user

        if link_user:
            print(f'[Facebook] Searching {user_name}...')

            url_image_user = self.find_image()
            if url_image_user:
                person.social_profiles['facebook']['Link_image'] = url_image_user
                print(f'\t\t[Facebook] Image Link of {user_name} Found!')
            else:
                raise Exception(f'[Facebook] Image Link of {user_name} NOT Found!')

            local_path_img = os.path.join(storing_dir_path, f'{user_name}_fb.jpg')
            save_image(url_image_user, local_path_img)
            person.social_profiles['facebook']['image'] = local_path_img
            print(f'\t\t[Facebook] Image Link of {user_name} Save as {user_name}_fb.jpg')

        else:

            print(f'[Facebook] Link of {user_name} Not Found!')
            url_image_user = ''
            pass
        try:
            items_name = self.wait.until(
                EC.presence_of_all_elements_located(
                    (
                        By.CSS_SELECTOR,'h1'
                    )
                )
            )

            full_name_fb = None

            for item_name in items_name:
                full_name_fb = item_name.text

                if len(full_name_fb.split(' ')) >1:
                    full_name_fb = item_name.text
                    break
                else:
                     pass

            if full_name_fb:
                print('[Facebook] Full_name',full_name_fb)

                parts = full_name_fb.split()

                if person.full_name is None or person.full_name == "":
                    person.full_name = full_name_fb

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
                print(f"[Facebook] Full_name Not Found -> I'll use the username: {user_name}")

            person.info_facebook = self.crawlerDataFacebook(link_user=link_user)

            print('[Facebook] New Person Added')

            return person

        except Exception as e:
            messagebox.showerror('Error', f'Error Name User {e}')
            return person

    def close_driver(self):
        self.driver.close()

if __name__ == '__main__':
    link = 'https://www.facebook.com/ste.cirillo'

    from configuration import accounts
    social_account = accounts.SocialMediaAccounts().get_account(platform='facebook')

    username = social_account['username']
    password = social_account['password']

    fb = Facebookfinder(password=password,
                        username=username,
                        showbrowser=True)

    result = []
    if fb.load_or_login():
        result = fb.crawlerDataFacebook(link)

    print(result)
    print('Done')
