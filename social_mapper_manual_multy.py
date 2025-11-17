from tqdm import tqdm
from configuration.configuration import Configuration
import os
import pandas as pd
from Fill_modules import fill_insta
from Fill_modules import fill_Linkedin
from Fill_modules import fill_fb
# from Fill_modules import fill_twitter
from Fill_modules.fill_threads import ThreadsInterface
from social_mapper_manual import socialMapper_ManualExecutor
from utils.person import Person


class socialMapper_ManualExecutor_multiple:
    def __init__(self, path_accounts_users,
                 task_type='Candidate Extraction'):

        self.config = Configuration.get_instance()
        self.show_browser = False
        self.peoplelist = []
        self.path_accounts_users = path_accounts_users

    def run(self):
        print(f"Running Manual Social Mapper Multiple Users...")
        accounts_users = pd.read_csv(self.path_accounts_users)

        for i,row in accounts_users.iterrows():
            #print(i,row)
            facebook_value = row['Facebook']
            linkedin_value = row['LinkedIn']
            instagram_value = row['Instagram']
            threads_value = row['Threads']
            x_value = row['Twitter']

            # Social sites
            social_sites = {}
            if pd.notna(facebook_value) and len(str(facebook_value)) > 0:  # conversione a stringa per gestire i float
                social_sites['fb'] = str(facebook_value).rstrip('/')  # conversione a stringa per gestire i float

            if pd.notna(instagram_value) and len(str(instagram_value)) > 0:  # conversione a stringa per gestire i float
                social_sites['ig'] = str(instagram_value).rstrip('/')  # conversione a stringa per gestire i float

            if pd.notna(linkedin_value) and len(str(linkedin_value)) > 0:  # conversione a stringa per gestire i float
                social_sites['ln'] = str(linkedin_value).rstrip('/')  # conversione a stringa per gestire i float

            if pd.notna(threads_value) and len(str(threads_value)) > 0:  # conversione a stringa per gestire i float
                social_sites['th'] = str(threads_value).rstrip('/')  # conversione a stringa per gestire i float

            if pd.notna(x_value) and len(str(x_value)) > 0:  # conversione a stringa per gestire i float
                social_sites['x'] = str(x_value).rstrip('/')  # conversione a stringa per gestire i float

            manual_executor = socialMapper_ManualExecutor(social_sites=social_sites)
            self.peoplelist.append(manual_executor.run())

        return self.peoplelist