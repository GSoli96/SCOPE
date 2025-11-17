import json
import os
from linkedin_api import Linkedin
import requests
from fake_headers import Headers

class LinkedinLoader():
    def __init__(self, username, password):
        self.api = Linkedin(username, password)

    def perform_search_by_name(self, first_name, last_name, limit=20,**kwargs):
        """
            Searches for LinkedIn profiles based on the specified criteria.

            Parameters:
            ----------
            keywords : str, optional
                Keywords to search on.

            current_company : list of str, optional
                A list of company URN IDs to filter current companies.

            past_companies : list of str, optional
                A list of company URN IDs to filter past companies.

            regions : list of str, optional
                A list of geo URN IDs to filter by regions.

            industries : list of str, optional
                A list of industry URN IDs to filter by industries.

            schools : list of str, optional
                A list of school URN IDs to filter by schools attended.

            profile_languages : list of str, optional
                A list of 2-letter language codes (e.g., 'en', 'fr') to filter by profile languages.

            contact_interests : list of str, optional
                A list containing one or both of "proBono" and "boardMember" to filter by contact interests.

            service_categories : list of str, optional
                A list of service category URN IDs to filter by service categories.

            network_depth : str, optional (Deprecated)
                Use network_depths instead. One of "F", "S", or "O" (first, second, or third+ connections).

            network_depths : list of str, optional
                A list containing one or many of "F", "S", and "O" (first, second, or third+ connections).

            include_private_profiles : bool, optional
                Whether to include private profiles in the search results. Defaults to False.

            keyword_first_name : str, optional
                First name to search for.

            keyword_last_name : str, optional
                Last name to search for.

            keyword_title : str, optional
                Job title to search for.

            keyword_company : str, optional
                Company name to search for.

            keyword_school : str, optional
                School name to search for.

            connection_of : str, optional
                Connection of a LinkedIn user, specified by their profile URN ID.

            limit : int, optional
                Maximum number of results to return. Defaults to -1 (no limit).

            Returns:
            -------
            list
                A list of profiles matching the specified criteria.

        """
        profiles = self.api.search_people(keyword_first_name=first_name,
                                    keyword_last_name=last_name,
                                    include_private_profiles=True,
                                    limit=limit, **kwargs)
        return profiles

    def perform_search_by_keywords(self, first_name, last_name, limit=20, **kwargs):
        """
            Searches for LinkedIn profiles based on the specified criteria.

            Parameters:
            ----------
            keywords : str, optional
                Keywords to search on.

            current_company : list of str, optional
                A list of company URN IDs to filter current companies.

            past_companies : list of str, optional
                A list of company URN IDs to filter past companies.

            regions : list of str, optional
                A list of geo URN IDs to filter by regions.

            industries : list of str, optional
                A list of industry URN IDs to filter by industries.

            schools : list of str, optional
                A list of school URN IDs to filter by schools attended.

            profile_languages : list of str, optional
                A list of 2-letter language codes (e.g., 'en', 'fr') to filter by profile languages.

            contact_interests : list of str, optional
                A list containing one or both of "proBono" and "boardMember" to filter by contact interests.

            service_categories : list of str, optional
                A list of service category URN IDs to filter by service categories.

            network_depth : str, optional (Deprecated)
                Use network_depths instead. One of "F", "S", or "O" (first, second, or third+ connections).

            network_depths : list of str, optional
                A list containing one or many of "F", "S", and "O" (first, second, or third+ connections).

            include_private_profiles : bool, optional
                Whether to include private profiles in the search results. Defaults to False.

            keyword_first_name : str, optional
                First name to search for.

            keyword_last_name : str, optional
                Last name to search for.

            keyword_title : str, optional
                Job title to search for.

            keyword_company : str, optional
                Company name to search for.

            keyword_school : str, optional
                School name to search for.

            connection_of : str, optional
                Connection of a LinkedIn user, specified by their profile URN ID.

            limit : int, optional
                Maximum number of results to return. Defaults to -1 (no limit).

            Returns:
            -------
            list
                A list of profiles matching the specified criteria.

        """
        profiles = self.api.search_people(keywords="{} {}".format(first_name, last_name),
                                    include_private_profiles=True,
                                    limit=limit, **kwargs)
        return profiles

    def extract_information_from_username(self, username_id,storage_dir_path_local):
        print('QUI2')
        profile = self.api.get_profile(urn_id=username_id)

        print(30*"#","\n",profile)
        print(30*"#","\n")
        if not os.path.exists(storage_dir_path_local):
            os.makedirs(storage_dir_path_local)

        print("[Linkedin2] Search Completed for {}.".format(username_id))
        with open("{}{}.json".format(storage_dir_path_local,username_id), "w") as outfile:
            json.dump(profile, outfile)
        print("[Linkedin2] Data stored for {}.\n".format(username_id))
        return profile

    def extract_contact_and_network_information_from_username(self, username_id,storage_dir_path_local):
        contact_info = self.api.get_profile_contact_info(username_id)
        print("[contact_info]", contact_info)
        network_info = self.api.get_profile_network_info(username_id)
        print("[network_info]", network_info)
        return contact_info,network_info

    def download_image(self,image_url, dir_path):
        img_data = requests.get(image_url).content
        with open(dir_path, 'wb') as handler:
            handler.write(img_data)

if __name__ == '__main__':
    # Authenticate using any Linkedin user account credentials
    # api = Linkedin('diragoluigi@gmail.com', 'Socialmapper24')
    #api = Linkedin('happycasa24@gmail.com', 'socialmapper97')

    first_name = "Stefano"
    last_name = "Cirillo"
    linkedin_connector = LinkedinLoader('happycasa24@gmail.com', 'socialmapper97')

    profiles = linkedin_connector.perform_search_by_keywords(first_name, last_name, limit=2)
    print(profiles)

    for d in profiles:
        storage_dir_path_local = "./Potential_target/{} {}/linkedin/profile_candidates/".format(first_name, last_name)

        profile_found = linkedin_connector.extract_information_from_username(d['urn_id'],storage_dir_path_local)

        #questo controllo è necessario perche alcuni profili non hanno foto
        if profile_found['displayPictureUrl']:
            img_path_to_download_100 = "{}{}".format(profile_found['displayPictureUrl'],profile_found['img_100_100'])
            img_path_to_download_200 = "{}{}".format(profile_found['displayPictureUrl'],profile_found['img_200_200'])
            img_path_to_download_400 = "{}{}".format(profile_found['displayPictureUrl'],profile_found['img_400_400'])

            print('[img_path_to_download_100]',img_path_to_download_100)
            print('[img_path_to_download_200]',img_path_to_download_200)
            print('[img_path_to_download_400]',img_path_to_download_400)

            image_path_local = "{}{}".format(storage_dir_path_local,d['urn_id'])
            if len(profile_found['img_100_100']) > 0: linkedin_connector.download_image(img_path_to_download_100, image_path_local+"_100.jpg")
            if len(profile_found['img_200_200']) > 0: linkedin_connector.download_image(img_path_to_download_200, image_path_local+"_200.jpg")
            if len(profile_found['img_400_400']) > 0: linkedin_connector.download_image(img_path_to_download_400, image_path_local+"_400.jpg")

    #linkedin_connector.extract_image_from_username(username_id_main)