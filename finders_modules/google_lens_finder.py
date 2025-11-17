from google_img_source_search import ReverseImageSearcher
from google_img_source_search import SafeMode
from configuration.configuration import Configuration
import os
import requests
from urllib.parse import urljoin
import mimetypes
from bs4 import BeautifulSoup
import re
import time
from urllib.parse import urlparse


class GoogleLensFinder:
    def __init__(self):
        self.rev_img_searcher = ReverseImageSearcher()
        self.rev_img_searcher.switch_safe_mode(SafeMode.DISABLED)
        self.config = Configuration.get_instance()
        self.name = ""

    def set_name(self, name_user):
        self.name = name_user

    def search_user_by_file(self, img_path):
        return self.rev_img_searcher.search_by_file(img_path)

    def search_user_by_url(self, img_url):
        try:
            return self.rev_img_searcher.search(img_url)
        except Exception as e:
            print(f"[GoogleLens] Error during image search with URL: {e}")
            return None  # Or handle error differently

    def download_search_results_original(self, search_results, top_k=5, type_search="file"):
        results_dict = {}
        path_to_store = self.config.get_google_lens_path()

        os.makedirs(path_to_store, exist_ok=True)
        timestamp_ns = time.time_ns()

        filepath_html = ""

        # print("\n[search_results]",search_results,"\n")

        for i, item in enumerate(search_results):
            print(i, item)
            if i >= top_k: break
            try:
                # Scarica HTML
                page_response = requests.get(item, timeout=10)
                page_response.raise_for_status()
                soup = BeautifulSoup(page_response.content, "html.parser")
                if type_search == 'dir':
                    filepath_html = os.path.join(path_to_store, f"{str(timestamp_ns)}")
                else:
                    filepath_html = os.path.join(path_to_store, self.name)

                print("[filepath_html] filepath_html", filepath_html)
                os.makedirs(filepath_html, exist_ok=True)
                with open(os.path.join(filepath_html, f"page_{i}.html"), "w", encoding="utf-8") as f:
                    f.write(str(soup))

                # Scarica Immagine
                image_url = item
                #if not image_url.startswith("http"): image_url = urljoin(item, image_url)
                image_response = requests.get(image_url, stream=True, timeout=10)
                image_response.raise_for_status()

                content_type = image_response.headers.get('content-type')
                if content_type and "image" in content_type:
                    ext = mimetypes.guess_extension(content_type)
                    if ext:
                        filename_image = f"image_{i}{ext}"
                    else:
                        filename_image = f"image_{i}.jpg"
                    filepath_image = os.path.join(filepath_html, filename_image)

                    with open(filepath_image, "wb") as f:
                        for chunk in image_response.iter_content(1024):
                            f.write(chunk)
                    results_dict[filepath_image] = os.path.join(filepath_html, f"page_{i}.html")
                else:
                    print(f"[GoogleLens] URL non valido per l'immagine: {image_url}")
                print(f"[GoogleLens] Scaricati pagina e immagine per: {item}")
            except requests.exceptions.RequestException as e:
                print(f"[GoogleLens] Errore durante il download dell'URL {item}: {e}")
            except Exception as e:
                print(f"[GoogleLens] Si è verificato un errore inaspettato: {e}")
                raise

        return results_dict,filepath_html

    def download_search_results(self, search_results, top_k=5, type_search="file"):
        results_dict = {}
        path_to_store = self.config.get_google_lens_path()

        os.makedirs(path_to_store, exist_ok=True)
        timestamp_ns = time.time_ns()

        filepath_html = ""

        # print("\n[search_results]",search_results,"\n")

        for i, item in enumerate(search_results):
            print(i, item)
            if i > top_k: break
            try:
                if type_search == 'dir':
                    filepath_html = os.path.join(path_to_store, f"{str(timestamp_ns)}")
                else:
                    filepath_html = os.path.join(path_to_store, self.name)

                if "image" not in self.check_url_type(item):
                    # Scarica HTML
                    page_response = requests.get(item, timeout=10)
                    page_response.raise_for_status()
                    soup = BeautifulSoup(page_response.content, "html.parser")

                    os.makedirs(filepath_html, exist_ok=True)
                    with open(os.path.join(filepath_html, f"page_{i}.html"), "w", encoding="utf-8") as f:
                        f.write(str(soup))
                    print("[filepath_html] URL", item)
                    print("[filepath_html] soup", soup)
                    print("[filepath_html] filepath_html", os.path.join(filepath_html, f"page_{i}.html"))

                else:
                    # Scarica Immagine
                    #if not image_url.startswith("http"): image_url = urljoin(item, image_url)
                    image_response = requests.get(item, stream=True, timeout=10)
                    image_response.raise_for_status()

                    content_type = image_response.headers.get('content-type')
                    if content_type and "image" in content_type:
                        ext = mimetypes.guess_extension(content_type)
                        if ext:
                            filename_image = f"image_{i}{ext}"
                        else:
                            filename_image = f"image_{i}.jpg"
                        filepath_image = os.path.join(filepath_html, filename_image)

                        with open(filepath_image, "wb") as f:
                            for chunk in image_response.iter_content(1024):
                                f.write(chunk)
                        results_dict[filepath_image] = os.path.join(filepath_html, f"page_{i}.html")
                    else:
                        print(f"[GoogleLens] URL non valido per l'immagine: {item}")
            except requests.exceptions.RequestException as e:
                print(f"[GoogleLens] Errore durante il download dell'URL {item}: {e}")
            except Exception as e:
                print(f"[GoogleLens] Si è verificato un errore inaspettato: {e}")
                raise

        return results_dict,filepath_html

    def extract_text_from_html_page(self, percorso_html):
        """
        Estrae il testo dal body di un file HTML locale, rimuovendo tabulazioni e newline,
        e lo restituisce come stringa.

        Args:
            percorso_html: Il percorso del file HTML di input.

        Returns:
            Una stringa contenente il testo estratto, o None in caso di errore.
        """
        try:
            with open(percorso_html, 'r', encoding='utf-8') as file_html:
                soup = BeautifulSoup(file_html, 'html.parser')

                body = soup.find('body')

                if body:
                    testo = body.get_text(strip=True)

                    testo_pulito = re.sub(r'[\n]+', ' ', testo)
                    # testo_pulito = re.sub(r' +', ' ', testo_pulito).strip()

                    return testo_pulito  # Restituisce la stringa
                else:
                    print("Tag <body> non trovato nel file HTML.")
                    return None  # restituisce none se non trova il tag body

        except FileNotFoundError:
            print(f"Errore: File non trovato: {percorso_html}")
            return None  # Restituisce None in caso di errore
        except Exception as e:
            print(f"Si è verificato un errore: {e}")
            return None  # restituisce none in caso di errore

    def check_url_type(self, url):
        """
        Determina se un URL punta a un'immagine o a una pagina HTML.

        Args:
            url (str): L'URL da controllare.

        Returns:
            str: "image" se l'URL punta a un'immagine, "html" se punta a una pagina HTML,
                 "unknown" altrimenti.
        """

        try:
            response = requests.head(url)
            content_type = response.headers.get('Content-Type')

            # Controlla l'estensione del file
            if url.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
                return "image"

            # Controlla il content type
            if content_type and content_type.startswith('image/'):
                return "image"
            elif content_type and content_type.startswith('text/html'):
                return "html"

            # Analizza l'URL per indizi
            parsed_url = urlparse(url)
            if 'images' in parsed_url.path or 'profile_images' in parsed_url.path:
                return "image"
            return "webpage"

        except requests.exceptions.RequestException as e:
            print(f"Errore durante la richiesta: {e}")
            return "unknown"

if __name__ == '__main__':
    image_url = 'https://nsfjournals.com/assets/images/ijcsm-editorial-board/stefano-cirillo.jpg'
    image_url = 'https://files.brumbrum.it/blog/wp-content/uploads/2019/10/13165214/Lancia-Ypsilon-allestimenti-scheda-tecnica.jpg.webp'
    image_path = '/Users/stefanocirillo/Desktop/Soda_United/Input-Examples/imagefolder/Stefano Cirillo.jpg'
    image_url = 'https://s3.amazonaws.com/peerj_prod_upload/images/profile/s%2Ft%2FZ6TcszFifFDHa91cHUyC5Q%3D%3D%2Fi200_656468cc2a7318.67028619.jpeg'
    image_path = '/Users/stefanocirillo/Desktop/Soda_United/Potential_target/googlelens/1646936763848/image_0.jpg'

    name = "Stefano"
    surname = "Cirillo"

    name = "Giuseppe"
    surname = "Polese"

    google_lens = GoogleLensFinder()
    res = google_lens.search_user_by_file(image_path)
    for search_item in res:
        result = google_lens.check_url_type(search_item)
        print(f"L'URL {search_item} è un: {result}")

    if res:
        local_files_path = google_lens.download_search_results(res)
        print(local_files_path)
    '''
    res2 = google_lens.search_user_by_url(image_url)
    for search_item in res2:
        print(f'Title: {search_item.page_title}')
        print(f'Site: {search_item.page_url}')
        print(f'Img: {search_item.image_url}\n')
    '''