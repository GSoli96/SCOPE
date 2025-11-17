import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import os, sys
from webdriver_manager.chrome import ChromeDriverManager  # Import per webdriver_manager
import chromedriver_autoinstaller

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
                    #break

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


    def get_driver(self,enable_profile=None):
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


if __name__ == "__main__":
    config = BrowserDriverConfigurations()
    driver = config.get_driver(enable_profile=None)
    driver.get("https://www.google.com")
    time.sleep(20)
