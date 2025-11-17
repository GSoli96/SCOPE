# -*- coding: utf-8 -*-
from __future__ import print_function
from selenium import webdriver
from time import sleep
import sys
import os
from bs4 import BeautifulSoup
from configuration.BrowserDriverConfigurations import BrowserDriverConfigurations
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

# Classe concreta che istanzia il crawler per il social Instagram
class Instagramfinder(object):

    def __init__(self, showbrowser, username, password):
        self.username = username
        self.password = password

        chrome_conf = BrowserDriverConfigurations()
        self.driver = chrome_conf.get_driver(enable_profile=None)

        self.driver.implicitly_wait(3)
        self.driver.delete_all_cookies()

        self.wait = WebDriverWait(self.driver, 10)

        ##XPATH Pagina di login
        self.xpath_button_cookies = "//button[contains(text(), 'cookie')]"
        self.xpath_username = '//input[@name="username"]'
        self.xpath_password = '//input[@name="password"]'
        self.xpath_button_login = "//div[text()='Log in']"
        self.xpath_button_save_credentials = "//button[text()='Save info']"

        ##Elementi per la ricerca
        self.css_button_search = "svg[aria-label*='Search'], svg[aria-label*='Cerca']"
        self.css_input_search_bar = "input[placeholder*='Search'], input[placeholder*='Cerca']"
        self.xpath_button_non_personalizzati = "//div[contains(@aria-label, 'Not personalized') or contains(@aria-label, 'Non personalizzati')]"
        self.xpath_user_list_non_personalizzati = self.xpath_button_non_personalizzati+"/ancestor::*[3]/*[3]//a"

        self.xpath_button_per_te = "//div[contains(@aria-label, 'For you') or contains(@aria-label, 'Per te')]"
        self.xpath_user_list_per_te = self.xpath_button_per_te+"/ancestor::*[3]/*[3]//a"

    #
    # Metodo che effettua il login al social
    #
    def doLogin(self):
        self.driver.get("https://www.instagram.com/accounts/login/?hl=en")
        self.driver.execute_script('localStorage.clear();')

        # convert unicode in instagram title to spaces for comparison
        titleString = ''.join([i if ord(i) < 128 else ' ' for i in self.driver.title])

        if (titleString.startswith("Login")):
            print("[Instagram]","[+] Instagram Login Page loaded successfully [+]")
            try:
                button_cookies = self.wait.until(EC.presence_of_element_located((By.XPATH, self.xpath_button_cookies)))
                button_cookies.click()
            except Exception as e:
                print(f"[Instagram] Errore Allow all cookies: {e}")
                pass

            sleep(1)
            try:
                instagramUsername = self.wait.until(EC.presence_of_element_located((By.XPATH, self.xpath_username)))
                instagramUsername.send_keys(self.username)
            except:
                print("[Instagram]","Instagram Login Page username field seems to have changed")
                pass

            sleep(1)
            try:
                instagramPassword = self.wait.until(EC.presence_of_element_located((By.XPATH, self.xpath_password)))
                instagramPassword.send_keys(self.password)
            except:
                print("[Instagram]","Instagram Login Page password field seems to have changed")
                pass

            sleep(1)
            try:
                loginButton = self.wait.until(EC.presence_of_element_located((By.XPATH, self.xpath_button_login)))
                parent = loginButton.find_element(By.XPATH, "./..")  # XPath './..' seleziona il genitore diretto
                parent.click()
            except:
                print("[Instagram]","Instagram Login Page Button Login field seems to have changed")

            sleep(1)
            try:
                saveCredentialsButton = self.wait.until(EC.presence_of_element_located((By.XPATH, self.xpath_button_save_credentials)))
                saveCredentialsButton.click()
            except:
                print("[Instagram]","Instagram Login Page Button Save Credentials field seems to have changed")

            print("[+] Instagram Login Success [+]\n")

            #sleep(100)
        else:
            print("[Instagram]","Instagram Login Page title field seems to have changed")

    def open_search_bar(self, first_name, last_name, counter):
        sleep(2)
        print("[Instagram]","Opening the search bar...")
        try:
            if counter >= 1:
                #print("\t\topen_search_bar counter > 0", first_name, last_name, counter)
                #ogni volta che rifaccio una ricerca con un nuovo nome, chiudo e riapro il menu di ricerca
                button_search = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, self.css_button_search)))
                button_search.click()
                sleep(2)
            button_search = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, self.css_button_search)))
            #print("\t\topen_search_bar button_search", button_search)
            button_search.click()
        except Exception as e:
            print("[Instagram]",'Error while opening search bar {}'.format(sys.exc_info()[-1].tb_lineno) + "\n"+e)
            picturelist = []
            pass

        try:
            search_bar = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, self.css_input_search_bar)))
            search_bar.clear()
            search_bar.send_keys("{} {}".format(first_name, last_name))
            search_bar.send_keys(Keys.ENTER)
        except Exception as e:
            print("[Instagram]",'Error while searching names with search bar {}'.format(sys.exc_info()[-1].tb_lineno) + "\n"+e)
            pass

    #
    # Metodo che effettua la ricerca di una persona sul social
    #
    # @param first_name Stringa che rappresenta il nome della persona da cercare
    # @param last_name Stringa che rappresenta il cognome della persona da cercare
    #
    # @return picturelist Array di persone trovare rispetto al nome in input
    #
    def getInstagramProfiles(self, first_name, last_name, counter=1):
        self.open_search_bar(first_name, last_name, counter)
        sleep(2)
        profile_picture = {}

        try:
            print("[Instagram] User Extraction For You...")
            third_child_per_te = self.wait.until(EC.presence_of_all_elements_located((By.XPATH, self.xpath_user_list_per_te)))
            sleep(1)
            for element in third_child_per_te:
                href = element.get_attribute('href').replace("?hl=en","")  # Estrai l'href
                img = element.find_element(By.TAG_NAME, 'img')# Trova l'immagine del profilo all'interno del tag <a>
                if img:
                    img_src = img.get_attribute('src')
                    if str(href) not in profile_picture:
                        #print("[Instagram]","href", href, 'img_src', img_src)
                        print("[Instagram]","href", href)
                    profile_picture[str(href)] = str(img_src)
                else:
                    profile_picture[str(href)] = None
            print("[Instagram]",len(profile_picture),"Extracted from For You profiles\n")
        except Exception as e:
            print("[Instagram]",'Error while searching profiles in For You {}'.format(sys.exc_info()[-1].tb_lineno) + "\n"+e)
            pass

        try:
            button_non_personalizzati = self.wait.until(EC.presence_of_element_located((By.XPATH, self.xpath_button_non_personalizzati)))
            button_non_personalizzati.click()
            print("[Instagram] User Extraction from Not Personalized...")
            sleep(2)
            third_child = self.wait.until(EC.presence_of_all_elements_located((By.XPATH, self.xpath_user_list_non_personalizzati)))
            print("[Instagram] third_child Not Personalized OK\n")
        except Exception as e:
            print('[Instagram] Error while searching profiles in Not Personalized {}'.format(sys.exc_info()[-1].tb_lineno) + "\n"+e)
            pass

        # Ciclo per estrarre i dati
        for element in third_child:
            href = element.get_attribute('href').replace("?hl=en","")  # Estrai l'href
            img = element.find_element(By.TAG_NAME, 'img')
            if img:
                img_src = img.get_attribute('src')
                if str(href) not in profile_picture:
                    #print("href",href,'img_src',img_src)
                    print("[Instagram]","href",href)
                profile_picture[str(href)] = str(img_src)
            else:
                profile_picture[str(href)] = None
        print("[Instagram]",len(profile_picture),"Extracted from non-personalized and for you profiles\n")
        sleep(2)
        return profile_picture

    ##################################################
    ################# Metodi non usati ###############
    ##################################################
    '''
    #
    # Metodo che estrae tutti i link e l'attributo alt di ogni immagine di una persona su instagram
    #
    # @param post_ig Lista di Stringhe che contiene il link e l'attributo alt di ogni immagine
    # @param number_post Intero che rappresenta il numero di post pubblicati da una persona
    # @param name Stringa che rappresenta il nome della persona
    #
    # @return post_ig Lista delle immagini e alt che sono state estrapolate dal profilo
    #
    def get_links(self, post_ig, number_post, name):
        # cerco le immagini dei post sul profilo instagram
        list_img = self.driver.find_elements_by_xpath(
            "//img[@class='x5yr21d xu96u03 x10l6tqk x13vifvy x87ps6o xh8yej3']")
        # per ogni immagine risultante dalla ricerca, ne estrapola il link e l'alt
        for image in list_img:
            try:

                link = image.get_attribute("src")
                alt_img = image.get_attribute("alt")
                alt = ((alt_img.encode('ascii', 'ignore')).decode('ascii'))
                tupla = (link, (alt.replace("\n", " ").strip()))
                if tupla not in post_ig:
                    post_ig.append(tupla)
                elif tupla in post_ig:
                    continue

                sys.stdout.write(
                    "\rInstagram Post Found: %i/%i  : %s                            " % (
                    len(post_ig), number_post, name))
                sys.stdout.flush()
            except Exception as e:
                # traceback.print_exc()
                # print(e)
                continue
        return post_ig

        #

    # Metodo che permete lo scroll della pagina del profilo instagram
    #
    # @param speed Intero che rappresenta di quanto la pagina dovrà scrollare
    # @param number_post Intero che rappresenta il numero di post pubblicati da una persona
    # @param name Stringa che rappresenta il nome della persona
    #
    # @return post Lista di tuple, dove ognuna contiene i post che sono state estrapolati dal profilo
    #
    def scroll_down_page(self, speed, number_post, name):
        post = []
        current_scroll_position, new_height = 0, 1
        while current_scroll_position <= new_height:
            sleep(1)
            post = self.get_links(post, number_post, name)
            current_scroll_position += speed
            self.driver.execute_script("window.scrollTo(0, {});".format(current_scroll_position))
            new_height = self.driver.execute_script("return document.body.scrollHeight")
        return post

    #
    # Metodo che estrae tutti i post di una persona su instagram
    #
    # @param username Stringa che rappresenta l'username dell'account da usare per il login
    # @param password Stringa che rappresenta l'password dell'account da usare per il login
    # @param person variabile di tipo Person che rappresenta la persona trovata su instangram
    #
    def extract_Instagramimage(self, username, password, person):
        sleep(1)
        # verifico se il login è ancora valido, altrimenti lo rieseguo
        if "login" in self.driver.current_url:
            self.doLogin(username, password)
            print('login non valido')
            sleep(3)
            if "login" in self.driver.current_url:
                print("Instagram Timeout Error, session has expired and attempts to reestablish have failed")

        self.driver.get(person.instagram)
        self.driver.maximize_window()
        sleep(2)

        number_post_text = self.driver.find_element_by_xpath("//*[@class='_ac2a']").text
        number_post = 0
        try:
            number_post = int(number_post_text.replace(" ", "").replace(".", "").replace(",", ""))
        except Exception as e:
            # traceback.print_exc(); print(e)
            pass
        post = []
        try:
            outputDir_InfoIG = "SM-Results\\raccolta_info_imageIG\\" + person.full_name

            if not os.path.exists(outputDir_InfoIG):
                os.makedirs(outputDir_InfoIG)

            outputfilename_InfoIG = outputDir_InfoIG + "\\Info_img_Instagram_" + person.full_name + ".csv"
            filewriter_InfoIG = open(outputfilename_InfoIG.format(outputfilename_InfoIG), 'w')
            titlestring_InfoIG = "link_Img,alt_Img"
            filewriter_InfoIG.write(titlestring_InfoIG)
            filewriter_InfoIG.write("\n")

            if (number_post > 0):
                post = self.scroll_down_page(250, number_post, person.full_name)
                for tupla in post:
                    try:
                        tmp = str(tupla[0]) + " , " + str(tupla[1]) + "\n"
                        filewriter_InfoIG.write(tmp)
                    except Exception as e:
                        # traceback.print_exc(); print(e)
                        continue
                filewriter_InfoIG.close()
            elif (number_post == 0):
                # print("No posts found")
                filewriter_InfoIG.close()
                os.remove(outputfilename_InfoIG)
        except Exception as e:
            # traceback.print_exc(); print(e)
            pass

    #
    # Metodo che effettua la ricerca di una persona sul social
    #
    # @param username Stringa che rappresenta l'username dell'account da usare per il login
    # @param password Stringa che rappresenta l'password dell'account da usare per il login
    # @param url Stringa legata al profilo della persona ricercata, identificata tramite face-recognition
    #
    # @return instagram Array di informazioni estrapolate circa la persona trovata
    #
    def crawlerDataInstagram(self, url):
        instagram = {"Biografia": "", "Sito_Personale": ""}
        self.driver.get(url)
        sleep(1)
        # verifico se il login è ancora valido, altrimenti lo rieseguo
        if "login" in self.driver.current_url:
            self.doLogin()
            print('Login non valido')
            sleep(3)
            if "login" in self.driver.current_url:
                print("Instagram Timeout Error, session has expired and attempts to reestablish have failed")

        # estrapolo la Biografia della persona trovata
        biografia = ""

        try:
            container = self.driver.find_elements_by_xpath('//div[@class="_aacl _aacp _aacu _aacx _aad6 _aade"]')
            biografia = ((container[3].text).encode('ascii', 'ignore').decode('ascii')) + ''
            instagram['Biografia'] = biografia.replace('\n', ' ')

        except Exception as e:
            # traceback.print_exc(); print(e)
            instagram['Biografia'] = ""
            pass

        # ESTRAPOLA DATI dal sito personale, se presente
        try:

            tmp_driver_site = self.driver.find_element_by_class_name('_aa_c')
            tmp_driver_site_tag = tmp_driver_site.find_element_by_tag_name('a')
            tmp_sito = tmp_driver_site_tag.get_attribute('href')
            instagram['Sito_Personale'] = tmp_sito
        except Exception as e:
            # traceback.print_exc(); print(e)
            instagram['Sito_Personale'] = ""
            pass

        return instagram

    #
    # Metodo che elimina tutti i cookies presenti
    #
    def testdeletecookies(self):
        self.driver.delete_all_cookies()
    '''

    #
    # Metodo che termnina la sessione
    #
    def kill(self):
        self.driver.quit()

