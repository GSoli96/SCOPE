import unicodedata

def normalize_name_tokens(s: str):
    import unicodedata

    s = s.lower()
    s = ''.join(
        c for c in unicodedata.normalize('NFKD', s)
        if not unicodedata.combining(c)
    )

    # sostituisco i simboli non alfanumerici con spazio
    s = ''.join(
        c if c.isalnum() or c.isspace() else ' '
        for c in s
    )

    tokens = s.split()
    return sorted(tokens)


def save_image(url_image_user, local_path_img):
    try:
        response = requests.get(url_image_user, stream=True)
        response.raise_for_status()

        with open(f'{local_path_img}', 'wb') as out_file:
            response.raw.decode_content = True
            shutil.copyfileobj(response.raw, out_file)
        del response

    except requests.exceptions.RequestException as e:
        raise Exception('Error', f'Error while create jpg image')


class twoStepVerification:  # Esempio di classe che contiene i metodi
    def __init__(self):
        self.risposta_utente = None  # Variabile di istanza per memorizzare la risposta

    def chiedi_conferma(self, root):
        """Mostra una finestra di messaggio con pulsanti Sì/No e gestisce la risposta."""

        # risposta = messagebox.askyesno("Conferma", "Hai inserito il codice corretto?", parent=root)
        risposta = messagebox.askyesno("Conferma", "Inserisci il codice!\n Poi premi ok!", parent=root)
        self.risposta_utente = risposta #salva la risposta nella variabile di classe

        root.destroy()  # Chiude la finestra e termina il ciclo degli eventi

    def two_step_verification(self):
        root = tk.Tk()
        root.withdraw()

        # Forza la finestra in primo piano
        root.attributes('-topmost', True)
        root.lift()
        root.focus_force()

        # messagebox.showwarning('[USER]', 'Inserisci il codice!\n Poi premi ok!', parent=root, )
        self.chiedi_conferma(root)

        return self.risposta_utente

# Funzione per analizzare una stringa e determinare la categoria
def categorize_string(input_string):
    # Regex per identificare una email
    email_regex = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')

    # Regex per identificare un sito web
    website_regex = re.compile(r'(https?://)?(www\.)?[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(/\S*)?')

    # Regex per identificare il nome di mesi in italiano o inglese
    months_regex = re.compile(
        r'\b(' +
        r'|'.join([
            'Gennaio', 'Febbraio', 'Marzo', 'Aprile', 'Maggio', 'Giugno', 'Luglio', 'Agosto', 'Settembre', 'Ottobre', 'Novembre', 'Dicembre',
            'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'
        ]) + r')\b',
        re.IGNORECASE
    )

    # Regex per identificare una data di compleanno (giorno + mese)
    birthday_regex = re.compile(r'\b(\d{1,2})\s+(' +
        r'|'.join([
            'Gennaio', 'Febbraio', 'Marzo', 'Aprile', 'Maggio', 'Giugno', 'Luglio', 'Agosto', 'Settembre', 'Ottobre', 'Novembre', 'Dicembre',
            'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'
        ]) + r')\b',
        re.IGNORECASE
    )

    # Regex per identificare un anno (ad esempio anno di nascita)
    year_regex = re.compile(r'\b(19\d{2}|20[01]\d|202[0-4])\b')

    # Regex per identificare una lingua
    language_regex = re.compile(r'\b(Italiano|English|Français|Español|Deutsch|Português|Русский|中文|日本語|한국어)\b', re.IGNORECASE)

    # Categorizzare la stringa
    if email_regex.search(input_string):
        return "email"
    elif website_regex.search(input_string):
        return "website"
    elif months_regex.search(input_string):
        return "month"
    elif birthday_regex.search(input_string):
        return "birthday"
    elif year_regex.search(input_string):
        return "birth year"
    elif language_regex.search(input_string):
        return "language"
    else:
        return "unknown"
