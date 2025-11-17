import os

from configuration.BrowserDriverConfigurations import BrowserDriverConfigurations

class Configuration:
    __instance = None

    def __init__(self):
        if Configuration.__instance is not None:
            raise Exception("Cannot create another instance of Configuration. Use get_instance() instead.")
        else:
            self._base_path = f'{os.getcwd()}'
            self._potential_path = os.path.join(self._base_path, "Potential_target")
            self._search_image_path = os.path.join(self._base_path, "Input-Examples", "imagefolder")
            self._path_account_data = os.path.join(self._base_path, "accounts.json")
            self._google_lens_path = os.path.join(self._potential_path, "googlelens")
            self._output_manual_path = os.path.join(self._potential_path, "manual")
            self.findCompany = os.path.join(self._potential_path, "FindCompany")

            self._screen_width = int(1080 * 0.43)

            self.browser_configuration = BrowserDriverConfigurations()

    @staticmethod
    def get_instance():
        if Configuration.__instance is None:
            Configuration.__instance = Configuration()
        return Configuration.__instance

    def get_base_path(self):
        return self._base_path

    def set_base_path(self, path):
        self._base_path = path
        self._potential_path = os.path.join(self._base_path, "Potential_target")
        self._search_image_path = os.path.join(self._base_path, "Input-Examples", "imagefolder")
        self._path_account_data = os.path.join(self._base_path, "accounts.json")
        self._google_lens_path = os.path.join(self._potential_path, "googlelens")
        self._output_manual_path = os.path.join(self._potential_path, "manual")
        self.findCompany = os.path.join(self._potential_path, "FindCompany")

    def get_output_manual_path(self):
        return self._output_manual_path

    def set_output_manual_path(self, path):
        self._output_manual_path = path

    def get_potential_path(self):
        return self._potential_path

    def set_potential_path(self, path):
        self._potential_path = path

    def get_search_image_path(self):
        return self._search_image_path

    def set_search_image_path(self, path):
        self._search_image_path = path

    def set_google_lens_path(self, path):
        self._google_lens_path = path

    def get_google_lens_path(self):
        return self._google_lens_path

    def get_account_data_path(self):
        return self._path_account_data

    def set_account_data_path(self, path):
        self._path_account_data = path

    def get_screen_width(self):
        return self._screen_width

    def set_screen_width(self, width):
        self._screen_width = width

    def set_findcompany_path(self, path):
        self.findCompany = path

    def get_findcompany_path(self):
        return self.findCompany

    def __str__(self):
        return (f"Configuration:\n"
                f"  Base Path: {self._base_path}\n"
                f"  Potential Path: {self._potential_path}\n"
                f"  Search Image Path: {self._search_image_path}\n"
                f"  Account Data Path: {self._path_account_data}\n"
                f"  Screen Width: {self._screen_width}")

'''
if __name__ == '__main__':
    # Esempio di utilizzo:
    config = Configuration.get_instance()
    print(config.get_base_path())

    config.set_base_path("\\nuovo\\percorso")
    print(config.get_base_path())
    print(config.get_fixed_path())  # Verifica che il fixed path sia stato aggiornato

    config2 = Configuration.get_instance()  # Ottiene la stessa istanza
    print(config2.get_base_path())  # Verifica che config e config2 puntino allo stesso oggetto

    config.set_screen_width(800)
    print(config2.get_screen_width())  # Verifica che config e config2 puntino allo stesso oggetto anche per screen width

    try:
        config3 = Configuration()  # Questo solleverà un'eccezione
    except Exception as e:
        print(e)
'''