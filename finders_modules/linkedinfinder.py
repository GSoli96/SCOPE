# -*- coding: utf-8 -*-
from __future__ import print_function

import json
import os
import shutil
import threading
import traceback
from datetime import datetime
from time import sleep
from tkinter import messagebox

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from configuration.BrowserDriverConfigurations import BrowserDriverConfigurations
from configuration.configuration import Configuration
from finders_modules.facebookfinder import twoStepVerification
from utils.candidate import Candidate
from utils.person import Person


# Classe concreta che istanzia il crawler per il social Linkedin
class Linkedinfinder(object):
    timeout = 1  # timeout per rallentare l'esecuzione e similuare l'operatore delll'utente reale, per limitare blocchi anti-crawler

    #
    # Metodo init per settare proprietà del browser
    #
    # @param showbrowser Stringa legata al comando da console, se presente si richiede la visine in real-time della ricerca
    #
    def __init__(self, username, password):
        self.username = username
        self.password = password

        chrome_conf = BrowserDriverConfigurations()
        self.driver = chrome_conf.get_driver(enable_profile=None)

        self.driver.implicitly_wait(3)
        self.driver.delete_all_cookies()

        self.wait = WebDriverWait(self.driver, 10)

        ##XPATH Pagina di login
        # self.xpath_button_cookies = "//*[contains(@data-control-name,'accept')]"
        self.xpath_button_cookies = "//button[contains(text(), 'Accetta') or contains(text(), 'Accept')]"
        self.xpath_username = '//input[@name="session_key"]'
        self.xpath_password = '//input[@name="session_password"]'
        self.xpath_button_login = "//button[contains(text(), 'Accedi') or contains(text(), 'Sign in')]"
        self.xpath_button_keep_connected = "//button[contains(@aria-label, 'Yes, keep all connected')]"

        self.info_linkedin = {}

    #
    # Metodo che effettua il login al social
    #
    # @param username Stringa che rappresenta l'username dell'account da usare per il login
    # @param password Stringa che rappresenta l'password dell'account da usare per il login
    #
    def load_or_login(self):
        cookie_file = "cookies\cookies_linkedin.json"
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
        #

        # Cookie validi → caricamento
        print("[+] Cookie di oggi trovati. Ripristino sessione...")
        self.driver.get("https://www.linkedin.com/uas/login")
        sleep(2)

        for cookie in data.get("cookies", []):
            cookie.pop("sameSite", None)
            try:
                self.driver.add_cookie(cookie)
            except:
                pass

        self.driver.refresh()
        sleep(2)

        # Verifico se login ok
        if "feed" in self.driver.current_url or "mynetwork" in self.driver.current_url or 'linkedin.com' in self.driver.current_url:
            print("[+] Sessione ripristinata senza login.")
            return True
        else:
            print("[!] Cookie non validi. Rifaccio login...")
            return self.doLogin()

    def doLogin(self):
        self.driver.get("https://www.linkedin.com/uas/login")
        self.driver.execute_script('localStorage.clear();')

        sleep(2)
        if (self.driver.title.encode('ascii', 'replace').startswith(
                bytes("Accesso a LinkedIn, Accesso | LinkedIn", 'utf-8'))):
            print("\n[+] LinkedIn Login Page loaded successfully [+]")

            try:
                button_cookies = self.wait.until(EC.presence_of_element_located((By.XPATH, self.xpath_button_cookies)))
                button_cookies.click()
            except:
                pass

            sleep(1)
            try:
                linkedinUsername = self.wait.until(EC.presence_of_element_located((By.XPATH, self.xpath_username)))
                linkedinUsername.send_keys(self.username)
            except:
                print("[LinkedIn] Login Page username field seems to have changed")

            sleep(1)
            try:
                linkedinPassword = self.wait.until(EC.presence_of_element_located((By.XPATH, self.xpath_password)))
                linkedinPassword.send_keys(self.password)
            except:
                print("[LinkedIn] Login Page password field seems to have changed")

            sleep(1)

            try:
                loginButton = self.wait.until(EC.presence_of_element_located((By.XPATH, self.xpath_button_login)))
                loginButton.click()
            except:
                print("[LinkedIn] Login Page Button Login field seems to have changed")

            sleep(2)

            try:
                keepConnectedButton = self.wait.until(
                    EC.presence_of_element_located((By.XPATH, self.xpath_button_keep_connected)))
                keepConnectedButton.click()
            except:
                pass

            sleep(2)

            try:
                if 'challenge' in self.driver.current_url:  # correzione typo
                    print('[LinkedIn] Verification Found!')

                    risultato_verifica = twoStepVerification().two_step_verification()  # uso l'istanza creata precedentemente

                    if risultato_verifica is True:
                        print("[LinkedIn] Verification Done!")
                    else:
                        print("[LinkedIn] Verification Not Done!")
                else:
                    print('[LinkedIn] Verification Not Found!')

            except Exception as e:
                messagebox.showerror('Error', f'Error Verification!\n{e}')
                return False

            if (self.driver.title.encode('utf8', 'replace') == bytes("Accesso a LinkedIn, Accesso | LinkedIn",
                                                                     'utf-8')):
                print("[-] LinkedIn Login Failed [-]\n")
            else:
                print("[+] LinkedIn Login Success [+]\n")
        else:
            print("LinkedIn Login Page title field seems to have changed.")
        sleep(2)

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

        with open("cookies\cookies_linkedin.json", "w") as f:
            json.dump(data, f)

        print("[+] Cookies salvati per il giorno:", today)

        return True

    def clone_session(self):
        cookies = self.driver.get_cookies()

        # nuovo driver
        new_driver = webdriver.Chrome()
        new_driver.get("https://linkedin.com")

        for cookie in cookies:
            try:
                new_driver.add_cookie(cookie)
            except:
                pass

        new_driver.refresh()
        return new_driver

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
    def getLinkedinProfiles(self, person, people_to_search, path_to_person):
        picturelist = []

        first_name = person.first_name
        last_name = person.last_name

        url = "https://www.linkedin.com/search/results/people/?keywords=" + first_name + "%20" + last_name + "&origin=SWITCH_SEARCH_VERTICAL"
        self.driver.get(url)
        sleep(3)

        searchresponse = self.driver.page_source.encode('utf-8')
        soupParser = BeautifulSoup(searchresponse, 'html.parser')

        li_people = soupParser.find_all('li', {'class': 'HprSUGvkdCIPfbgQQypSmfjOMDqZHCRoKJlg'})

        if li_people is not None and len(li_people) != 0:
            collected = 0
            print('-' * 30)
            for i in range(len(li_people)):

                li = li_people[i]

                try:
                    first_box = li.find('a', {'class': "RXGjbzcIFiUDdEDItiylehhPqXbXsZFcQyf"})
                    if first_box is not None:
                        print(f'\t[Linkedin] Box of user {i} found!')
                        url_profile = first_box.get('href')

                        if url_profile is not None:
                            print(f'\t[Linkedin] Link of user {i} found!')
                            link_name = li.find('span', {"aria-hidden": "true"})

                            if link_name is not None:
                                user_name = link_name.text.strip()

                                if user_name is not None:
                                    print(f'\t[Linkedin] Username of user {i} Found!')
                                    print(f'\t[Linkedin] Username found: {user_name}')
                                    import unicodedata

                                    def normalize_name_tokens(s: str):
                                        import unicodedata

                                        s = s.lower()
                                        s = ''.join(
                                            c for c in unicodedata.normalize('NFKD', s)
                                            if not unicodedata.combining(c)
                                        )
                                        tokens = s.split()  # splitta e rimuove spazi multipli
                                        return sorted(tokens)  # ordina alfabeticamente

                                    user_name_n1 = normalize_name_tokens(user_name)
                                    p_full_name_n2 = normalize_name_tokens(person.full_name)

                                    match = set(user_name_n1) == set(p_full_name_n2)

                                    if match:
                                        print(f'\t[Linkedin] User {i} Match Found!')
                                        print(f'\t[Linkedin] Searching image for User {i}')

                                        url_image_user, local_path_img = self.getProfileImage(link_user=url_profile,
                                                                                              storing_dir_path=path_to_person,
                                                                                              user_name=user_name,
                                                                                              count=i)

                                        if url_image_user is not None and local_path_img is not None:
                                            print(f'\t[Linkedin] Image element of {user_name} Found!')
                                            print(f'\t[Linkedin] Image of {user_name} saved in {local_path_img}!')
                                            picturelist.append(
                                                Candidate(username=user_name,
                                                          link_image=url_image_user,
                                                          url_profile=url_profile,
                                                          local_path_img=local_path_img)
                                            )
                                        else:
                                            print(f'\t[Linkedin] Image element of {user_name} Not Found!')
                                    else:
                                        print(f'\t[Linkedin] {user_name} of user Not Match with {person.full_name}!')
                                else:
                                    raise Exception(f'\t[Linkedin] user_name(None)_{i}')
                            else:
                                raise Exception(f'\t[Linkedin] link_name(None)_{i}')
                        else:
                            raise Exception(f'\t[Linkedin] url_profile(None)_{i}')
                    else:
                        raise Exception(f'\t[Linkedin] first_box(None)_{i}')
                except Exception as e:
                    print(f'{e}')
                    continue

                if collected >= people_to_search:
                    break
                collected = collected + 1
                print('-'*30)

            return picturelist
        else:
            print('[Linkedin] List of people not found [-]')

    #
    # Metodo che effettua la ricerca di una persona sul social
    #
    # @param username Stringa che rappresenta l'username dell'account da usare per il login
    # @param password Stringa che rappresenta l'password dell'account da usare per il login
    # @param url Stringa legata al profilo della persona ricercata, identificata tramite face-recognition
    #
    # @return info Array di informazioni estrapolate circa la persona trovata
    #
    def crawlerDataLinkedin(self, url, full_name):
        info = {"Cellulare": "", "Sito Web": "", "Email": "", "Compleanno": "", "Città": "",
                "Impiego": "", "Indirizzo": "", "Messaggistica": "", "Biografia": "", "Formazione": "",
                "Esperienze": "", "Competenze": "", "Corsi": "", "Lingue": "", }

        self.driver.get(url)

        # estrapolo le informazioni circa l'impiego
        try:
            element = self.driver.find_element(By.XPATH,'//*[@class="text-body-medium break-words"]')
            impiego = str(element.text)
            info["Impiego"] = ((impiego.encode('ascii', 'ignore')).decode('ascii'))
            print('[LinkedIn] Found Impiego: ', info['Impiego'])
        except Exception as e:
            print(e)
            pass

        # estrapolo le informazioni circa la città di residenza
        try:
            element1 = self.driver.find_element(By.XPATH,
                '//*[@class="text-body-small inline t-black--light break-words"]')
            residenza = str(element1.text.strip())

            info["Città"] = ((residenza.encode('ascii', 'ignore')).decode('ascii'))
            print('[LinkedIn] Found citta: ', info['Città'])

        except Exception as e:
            print(e)
            pass

        biografia = ""
        esperienze = ""
        formazione = ""
        skills = ""
        corsi = ""
        lingue = ""

        # 🟥 Mappatura sezioni EN/IT
        SECTION_MAP = {
            "about": ["About", "Informazioni"],
            "experience": ["Experience", "Esperienza"],
            "education": ["Education", "Formazione"],
            "skills": ["Skills", "Competenze"],
            "courses": ["Courses", "Corsi"],
            "languages": ["Languages", "Lingue"],
        }

        # 🟦 Sezioni che quando incontrate devono fermare il parsing
        STOP_WORDS = [# EN
                        "Interests", "Influencers", "Companies",
                        # IT
                        "Interessi", "Influencer", "Aziende",
        ]

        # 🟩 Variabili stato (quale sezione è attiva)
        current_section = None

        try:
            root = self.driver.find_element(By.XPATH, '//*[@class="display-flex ph5 pv3"]')
            elements = root.find_elements(By.XPATH, '//*[@class="visually-hidden"]')

            print(f"[LinkedIn] Found {len(elements)} information items")

            for idx, elem in enumerate(elements):
                text_tmp = elem.text.strip()

                # 🟥 Stop parsing
                if text_tmp in STOP_WORDS:
                    break

                # 🟦 Identifica se la linea è un titolo di sezione
                detected_section = None
                for section_key, names in SECTION_MAP.items():
                    if text_tmp in names:
                        detected_section = section_key
                        break

                # Se è una sezione → aggiorna lo stato e salta al prossimo ciclo
                if detected_section:
                    current_section = detected_section
                    print(f"[LinkedIn] → Switched to section: {current_section}")
                    continue

                # 🟩 Ignora linee vuote o rumorose
                if not text_tmp or text_tmp in SECTION_MAP or text_tmp in STOP_WORDS:
                    continue

                # 🟧 Aggiungi il contenuto alla sezione corretta
                if current_section == "about":
                    biografia += " " + text_tmp
                elif current_section == "experience":
                    esperienze += " " + text_tmp
                elif current_section == "education":
                    formazione += " " + text_tmp
                elif current_section == "skills":
                    skills += " " + text_tmp
                elif current_section == "courses":
                    corsi += " " + text_tmp
                elif current_section == "languages":
                    lingue += " " + text_tmp

            # 🔥 Pulizia finale (ASCII safe)
            info["Biografia"] = biografia.encode("ascii", "ignore").decode("ascii")
            info["Esperienze"] = esperienze.encode("ascii", "ignore").decode("ascii")
            info["Formazione"] = formazione.encode("ascii", "ignore").decode("ascii")
            info["Competenze"] = skills.encode("ascii", "ignore").decode("ascii")
            info["Corsi"] = corsi.encode("ascii", "ignore").decode("ascii")
            info["Lingue"] = lingue.encode("ascii", "ignore").decode("ascii")

        except Exception as e:
            traceback.print_exc()
            print("[LinkedIn] Error during parsing:", e)
            pass

        ActionChains(self.driver).move_to_element(self.driver.find_element(By.XPATH,
            '//*[@class="ember-view link-without-visited-state cursor-pointer text-heading-small inline-block break-words"]')).click().perform()
        sleep(3)
        # carico la sezione delle Contact-info
        title_Contact_Info = self.driver.find_elements(By.XPATH,
            '//*[@class="pv-contact-info__header t-16 t-black t-bold"]')

        print(f'[LinkedIn] Contact Info Found {len(title_Contact_Info)} items')
        for e in title_Contact_Info:
            print(f'[LinkedIn] {e.text}')
            # estrapolo le informazioni circa Sito Web
            if e.text == 'Websites' or e.text == 'Sito Web':
                sito = []
                tipo_Sito = []
                info_Sito = []
                try:
                    elenco = e.find_element(By.XPATH,'//*[@class="list-style-none"]')
                    elenco1 = elenco.find_elements(By.TAG_NAME,'li')
                    temp1 = elenco1[0].find_elements(By.XPATH,
                        '//*[@class="pv-contact-info__contact-link link-without-visited-state"]')
                    for t in temp1:
                        sito.append(str(t.text.strip()))

                    temp2 = elenco1[0].find_elements(By.XPATH,'//*[@class="t-14 t-black--light t-normal"]')

                    for t1 in temp2:
                        tipo_Sito.append(str(t1.text.strip()))

                    for numero in range(len(sito)):
                        info_Sito.append(sito[numero] + " " + tipo_Sito[numero])
                except Exception as e:
                    print(e)
                    continue

                if info_Sito.count != 0:
                    info["Sito Web"] = " - ".join(info_Sito)
                else:
                    info["Sito Web"] = ""

            # estrapolo le informazioni circa Cellulare
            elif e.text == 'Phone' or e.text == 'Cellulare' or e.text == 'Phone Number' or e.text == 'Telefono':
                cellulare = ""
                tipo_cellulare = ""
                info_cellulare = []

                try:
                    temp1 = e.find_element(By.XPATH,'//*[@class="t-14 t-black t-normal"]')
                    cellulare = str(temp1.text.strip())

                    temp2 = e.find_element(By.XPATH,'//*[@class="t-14 t-black--light t-normal"]')
                    tipo_cellulare = str(temp2.text.strip())

                    info_cellulare.append(cellulare + " " + tipo_cellulare)
                except Exception as e:
                    print(e)
                    continue

                if info_cellulare.count != 0:
                    info["Cellulare"] = " - ".join(info_cellulare)
                else:
                    info["Cellulare"] = ""

            # estrapolo le informazioni circa Indirizzo
            elif e.text == 'Address':
                indirizzo = ""
                try:
                    temp1 = e.find_element(By.XPATH,
                        '//*[@class="pv-contact-info__contact-link link-without-visited-state t-14"]')
                    indirizzo = str(temp1.text.strip())
                except Exception as e:
                    print(e)
                    continue
                info["Indirizzo"] = indirizzo

            # estrapolo le informazioni circa Email
            elif e.text == 'Email':
                email = ""
                try:
                    temp1 = e.find_element(By.XPATH,
                        '//*[@class="pv-contact-info__contact-link link-without-visited-state t-14"]')
                    email = str(temp1.text.strip())
                except Exception as e:
                    print(e)
                    continue
                info["Email"] = email

            # estrapolo le informazioni circa Messaggistica istantanea
            elif e.text == 'IM':
                im = []
                tipo_IM = []
                info_IM = []
                try:
                    elenco = e.find_element(By.XPATH,'//*[@class="list-style-none"]')
                    elenco1 = elenco.find_element(By.TAG_NAME, 'li')

                    temp1 = elenco1[0].find_elements(By.XPATH,
                        '//*[@class="pv-contact-info__contact-item t-14 t-black t-normal"]')
                    for t in temp1:
                        im.append(str(t.text.strip()))

                    temp2 = elenco1[0].find_elements(By.XPATH,'//*[@class="t-14 t-black--light t-normal"]')

                    for t1 in temp2:
                        tipo_IM.append(str(t1.text.strip()))

                    for numero in range(len(im)):
                        info_IM.append(im[numero] + " " + tipo_IM[numero])
                except Exception as e:
                    print(e)
                    continue

                if info_IM.count != 0:
                    info["Messaggistica"] = " - ".join(info_IM)
                else:
                    info["Messaggistica"] = ""

            # estrapolo le informazioni circa Compleanno
            elif e.text == 'Birthday':
                compleanno = ""
                try:
                    temp1 = e.find_element(By.XPATH,'//*[@class="pv-contact-info__contact-item t-14 t-black t-normal"]')
                    compleanno = str(temp1.text.strip())
                except Exception as e:
                    print(e)
                    continue

                info["Compleanno"] = compleanno
        return info

    #
    # Metodo che elimina tutti i cookies presenti
    #
    def testdeletecookies(self):
        self.driver.delete_all_cookies()

    #
    # Metodo che termnina la sessione
    #
    def kill(self):
        self.driver.quit()

    def getProfileImage(self, link_user, storing_dir_path, user_name, count):

        # Salva la finestra originale
        sleep(2)
        original_window = self.driver.current_window_handle
        url_image_user = None
        local_path_img = None

        # Apri una nuova scheda
        self.driver.switch_to.new_window('tab')
        print('\t[Linkedin] New window opened!')
        sleep(2)

        # Ora lavora nella nuova scheda
        self.driver.get(link_user)
        sleep(3)

        try:
            local_path_img = os.path.join(storing_dir_path, f'{user_name}_{count}_li.jpg')
            url_image_user = self.find_image(user_name)
            if url_image_user is not None:
                threading.Thread(
                    target=self.save_img,
                    args=(url_image_user, local_path_img)
                ).start()

                print(f'\t[Linkedin] Image Link of {user_name} Save as {user_name}_{count}_li.jpg')
            else:
                raise Exception(f'[Linkedin] Image Link of {user_name} NOT Found!')

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
                print(f'\t[Linkedin][getProfileImage] Cleanup error: {cleanup_err}')

        return url_image_user, local_path_img

    def save_img(self, url_image_user, local_path_img):
        self.save_image(url_image_user, local_path_img)

    def find_image(self, user_name):
        sleep(3)
        try:
            print('\t\t[Linkedin] Find Image - First Try!')
            image_user = self.driver.find_elements(
                By.XPATH, f'button > img')

            sleep(1)
            image_user = image_user[1:][0]
            link = image_user.get_attribute('xlink:href')
            print(f'\t\t[Linkedin] Found Image in First Try: {link}')
            return link

        except Exception as e:
            print('\t\t[Linkedin] Image Not Found - First Try!')
            try:
                print('\t\t[Linkedin] Find Image - Second Try!')
                image_user = self.driver.find_elements(
                    By.XPATH,
                    f'//*[@id="mount_0_0_MH"]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div/div/div[1]/div[2]/div/div/div/div[1]/div/a/div/svg/g/image')
                sleep(1)
                image_user = image_user[1:][0]
                link =  image_user.get_attribute('xlink:href')
                print(f'\t\t[Linkedin] Found Image in Second Try: {link}')
                return link

            except Exception as e:
                print('\t\t[Linkedin] Image Not Found - Second Try!')
                try:
                    print('\t\t[Linkedin] Find Image - Third Try!')
                    image_user = self.driver.find_elements(
                        By.XPATH,
                        f'mount_0_0_MH > div > div:nth-child(1) > div > div.x9f619.x1n2onr6.x1ja2u2z > div > div > div.x78zum5.xdt5ytf.x1t2pt76.x1n2onr6.x1ja2u2z.x10cihs4 > div.x78zum5.xdt5ytf.x1t2pt76 > div > div > div:nth-child(1) > div.x9f619.x1ja2u2z.x78zum5.x2lah0s.x1n2onr6.xl56j7k.x1qjc9v5.xozqiw3.x1q0g3np.x1l90r2v.x1ve1bff > div > div > div > div.x15sbx0n.x1xy773u.x390vds.x13bxmoy.x14xzxk9.xmpot0u.xs6kywh.x5wy4b0 > div > a > div > svg > g > image')
                    sleep(1)
                    image_user = image_user[1:][0]
                    link = image_user.get_attribute('xlink:href')
                    print(f'\t\t[Linkedin] Found Image in Third Try: {link}')
                    return link

                except Exception as e:
                    print('\t\t[Linkedin] Image Not Found - Third Try!')
                    try:
                        print('\t\t[Linkedin] Find Image - Fourth Try!')
                        # Usando XPath
                        image_element = self.driver.find_elements(By.XPATH,
                                                                 '//image[@preserveAspectRatio="xMidYMid slice"]')
                        image_element = image_element[1:][0]
                        # Recupera l'attributo
                        link =  image_element.get_attribute('xlink:href')
                        print(f'\t\t[Linkedin] Found Image in Fourth Try: {link}')
                        return link

                    except Exception as e:
                        print('\t\t[Linkedin] Image Not Found - Fourth Try!')
                        try:
                            print('\t\t[Linkedin] Find Image - Fifth Try!')
                            # Se ci sono più elementi, specifica meglio
                            image_element = self.driver.find_elements(By.CSS_SELECTOR,
                                                                     'svg image[preserveAspectRatio="xMidYMid slice"]')
                            image_element = image_element[1:][0]
                            link = image_element.get_attribute('xlink:href')
                            print(f'\t\t[Linkedin] Found Image in Fifth Try: {link}')
                            return link

                        except Exception as e:
                            print('\t\t[Linkedin] Image Not Found - Fifth Try!')
                            try:
                                print('\t\t[Linkedin] Find Image - Sixth Try!')
                                # Se ci sono più elementi, specifica meglio
                                image_element = self.driver.find_elements(By.CLASS_NAME,
                                                                          'PZXZImliEjGADcCcZFRacyNUYVXcWNKCaWLc pv-top-card-profile-picture__image--show evi-image ember-view')
                                image_element = image_element[1:][0]
                                link = image_element.get_attribute('src')
                                print(f'\t\t[Linkedin] Found Image in Last Try: {link}')
                                return link

                            except Exception as e:
                                print('\t\t[Linkedin] Image Not Found - Sixth Try!')
                                try:
                                    searchresponse = self.driver.page_source.encode('utf-8')
                                    soupParser = BeautifulSoup(searchresponse, 'html.parser')

                                    print('\t\t[Linkedin] Find Image - Seventh Try!')
                                    # Se ci sono più elementi, specifica meglio
                                    image_element = soupParser.find('img',
                                                                             {'title':f'{user_name}', 'alt': f'{user_name}'})
                                    link = image_element.get('src')
                                    if 'data:image/gif;base64' in link:
                                        raise Exception("The user doesn't have an image - Seventh Try!")

                                    print(f'\t\t[Linkedin] Found Image in Seventh Try: {link}')

                                    return link

                                except Exception as e:
                                    try:
                                        print('\t\t[Linkedin] Find Image - Last Try!')
                                        # Se ci sono più elementi, specifica meglio
                                        image_element = self.driver.find_elements(By.XPATH,
                                                                                  '/ html / body / div[6] / div[3] / div / div / div[2] / div / div / main / section[1] / div[2] / div[1] / div[1] / div / button / img')
                                        image_element = image_element[1:][0]
                                        link = image_element.get_attribute('src')
                                        print(f'\t\t[Linkedin] Found Image in Last Try: {link}')
                                        return link

                                    except Exception as e:
                                        print('\t\t[Linkedin] Image Not Found - Last Try!')
                                        return None

    def save_image(self, url_image_user, local_path_img):
        try:
            response = requests.get(url_image_user, stream=True)
            response.raise_for_status()

            with open(f'{local_path_img}', 'wb') as out_file:
                response.raw.decode_content = True
                shutil.copyfileobj(response.raw, out_file)
            del response

        except requests.exceptions.RequestException as e:
            messagebox.showerror('Error', f'Error while create jpg image')
            pass

    def getLinkedinProfile(self, person, user_name, link_to_user, storage_dir_path_local):

        self.driver.get(link_to_user)
        sleep(3)

        if user_name:
            print(f'[Linkedin] Searching {user_name}...')
            person.social_profiles['linkedin']['username'] = user_name
            person.social_profiles['linkedin']['profile'] = link_to_user

            try:
                items_name = str(self.driver.title.encode('utf8', 'replace').decode('utf8'))
                print(f'[Linkedin] Found title {items_name}')
                full_name_li = items_name.replace('| LinkedIn', '').strip()
                print(f'[Linkedin] Found full name {full_name_li}')

                if full_name_li:

                    if person.full_name is None or person.full_name == "":
                        person.full_name = full_name_li

                    parts = full_name_li.split()

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

                    print(f'[Linkedin] Found first name {person.first_name}')
                    print(f'[Linkedin] Found last name {person.last_name}')

                    url_image_user = self.find_image(full_name_li)

                    print(f'[Linkedin] Image Link of {user_name} Found!')

                    local_path_img = os.path.join(storing_dir_path, f'{user_name}_li.jpg')
                    threading.Thread(
                        target=self.save_img,
                        args=(url_image_user, local_path_img)
                    ).start()

                    person.social_profiles['linkedin']['image'] = url_image_user

                    print(f'[Linkedin] Image Link of {user_name} Saved!')

                    person.info_linkedin = self.crawlerDataLinkedin(url=link_to_user, full_name=full_name_li)
                    person.potential_path_person = storage_dir_path_local
                    person.original_person_image = url_image_user

                    print('[Linkedin] New Person Added')

                    return person
                else:
                    print(f"[Linkedin] Full_name Not Found -> I'll use the username: {user_name}")
                    full_name_li = user_name

            except Exception as e:
                messagebox.showerror('Error', f'Error Name User {e}')
                return []
        else:
            print(f'[Linkedin] Link of {user_name} Not Found!')
            url_image_user = ''
            pass

if __name__ == '__main__':
    username = "ethicspaper46@gmail.com"
    password = "ethicspaper46"

    first_name = "Stefano"
    last_name = "Cirillo"

    link = 'https://www.linkedin.com/in/stefano-cirillo/'

    user_name = link.split('https://www.linkedin.com/in/')[-1].split('/')[0]

    print(f'Searching Linkedin {user_name}...')

    potential_path = '.\\StefanoCirillo\\Automatic\\'
    os.makedirs(potential_path, exist_ok=True)

    l = Linkedinfinder(username, password)

    if l.load_or_login():
        config = Configuration.get_instance()

        storing_dir_path = os.path.join(config.get_output_manual_path(), user_name, "linkedin")

        potential_path = '.\\StefanoCirillo\\Manual\\'
        os.makedirs(potential_path, exist_ok=True)

        list_people = l.getLinkedinProfile(user_name=user_name,
                                           link_to_user=link,
                                           storage_dir_path_local=potential_path
                                           )






