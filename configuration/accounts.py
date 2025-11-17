# Mail Libero IG
# happycasa_2024@libero.it
# Ghirlanda.28

# Mail Google
# happycasa24@gmail.com

# global linkedin_username
# global linkedin_password
# linkedin_username = "socialmappertest@libero.it" #jackslim089@tiscali.it
# linkedin_password = "socialmapper97"

# global facebook_username
# global facebook_password
# facebook_username = "social_test@libero.it" #"lucianapasqualazzi@yahoo.com"
# facebook_password = "prova_SocialTest1" # "socialmapper97"

# global twitter_username
# global twitter_password
# twitter_username = "PSocialmapper"
# twitter_password = "socialmapper97"

# global instagram_username
# global instagram_password
# instagram_username = "happycasa614"
# instagram_password = "Ghirlanda.28" 

# global google_username
# global google_password
# google_username = ""
# google_password = ""

# global vk_username
# global vk_password
# vk_username = "+393935126036"  # Can be mobile or email
# vk_password = "socialmapper97"

# global weibo_username
# global weibo_password
# weibo_username = ""  # Can be mobile
# weibo_password = ""

# global douban_username
# global douban_password
# douban_username = ""
# douban_password = ""

# global pinterest_username
# global pinterest_password
# pinterest_username = "socialmappertest@libero.it"
# pinterest_password = "socialmapper97"

import json

from configuration.configuration import Configuration

class SocialMediaAccounts:
    config = Configuration.get_instance()

    def __init__(self, json_file=None):
        if json_file is None:
            self.json_file = self.config.get_account_data_path()
        else:
            self.json_file = json_file

        try:
            self.load_accounts()
        except (FileNotFoundError, json.JSONDecodeError) as e:
            # Initialize with an empty dictionary if loading fails
            print("Error", f"An error occurred while loading the JSON file: {e}")

            self.accounts = {
                 #'linkedin': {"username": "socialmappertest@libero.it", "password": "socialmapper97"},
                 #'linkedin': {"username": "diragoluigi@gmail.com", "password": "Socialmapper24"},
                 'linkedin': {"username": "happycasa24@gmail.com", "password": "socialmapper97"},
                'facebook': {"username": "social_test@libero.it", "password": "prova_SocialTest1"},
                 'X': {"username": "social205184", "password": "socialmapper97"}, #email: "happycasa24@gmail.com"
                #'instagram': {"username": "vexeco6853", "password": "prova_SocialTest1"},
                 'instagram': {"username": "ldirago25", "password": "Socialmapper24"},
                 #'instagram': {"username": "happycasa614", "password": "Ghirlanda.28"},
                'google': {"username": "", "password": ""},
             'pinterest': {"username": "socialmappertest@libero.it", "password": "socialmapper97"},
            }

    def get_account(self, platform):
        """Retrieve credentials for a given platform."""
        return self.accounts.get(platform, "Account not found.")

    def update_account(self, platform, username=None, password=None):
        """Update username or password for a given platform."""
        if platform in self.accounts:
            if username:
                self.accounts[platform]['username'] = username
            if password:
                self.accounts[platform]['password'] = password
            return f"{platform} account updated successfully."
        return "Account not found."

    def remove_account(self, platform):
        """Remove credentials for a given platform."""
        if platform in self.accounts:
            del self.accounts[platform]
            return f"{platform} account removed successfully."
        return "Account not found."

    def add_account(self, platform, username, password):
        """Add a new platform with credentials."""
        if platform in self.accounts:
            return "Account already exists."
        self.accounts[platform] = {"username": username, "password": password}
        return f"{platform} account added successfully."

    def list_accounts(self):
        """List all available accounts."""
        return list(self.accounts.keys())

    def load_accounts(self):
        """Load accounts from the JSON file."""
        with open(self.json_file, 'r') as file:
            self.accounts = json.load(file)

    def save_accounts(self):
        """Save accounts to the JSON file."""
        with open(self.json_file, 'w') as file:
            json.dump(self.accounts, file, indent=4)

    def update_accounts(self, updates):
        """
        Update multiple accounts at once.
        :param updates: Dictionary with platform names as keys and dictionaries containing
                        'username' and/or 'password' as values.
        """
        for platform, credentials in updates.items():
            if platform in self.accounts:
                if 'username' in credentials:
                    self.accounts[platform]['username'] = credentials['username']
                if 'password' in credentials:
                    self.accounts[platform]['password'] = credentials['password']
            else:
                self.accounts[platform] = {
                    "username": credentials.get('username', ''),
                    "password": credentials.get('password', '')
                }
        self.save_accounts()

# # Example Usage
# accounts = SocialMediaAccounts()

# # Get account details
# print(accounts.get_account('linkedin'))

# # Update account details
# print(accounts.update_account('linkedin', username="new_email@domain.com", password="newpassword123"))

# # Remove an account
# print(accounts.remove_account('google'))

# # Add a new account
# print(accounts.add_account('tiktok', username="new_user@domain.com", password="tiktokpassword"))

# # List all accounts
# print(accounts.list_accounts())
