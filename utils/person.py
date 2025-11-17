import json
import time

from utils.candidate import Candidate


class Person:
    def __init__(self, first_name = None,
                 last_name = None,
                 original_person_image = None,
                 potential_path_person = None):
        self.first_name = first_name
        self.last_name = last_name
        self.full_name = f"{first_name} {last_name}"
        self.original_person_image = original_person_image
        self.potential_path_person = potential_path_person

        self.list_candidate_user_found_fb = []
        self.list_candidate_user_found_linkedin = []
        self.list_candidate_user_found_threads = []
        self.list_candidate_user_found_X = []
        self.list_candidate_user_found_instagram = []

        # Initialize social media links and images
        self.social_profiles = {
            'linkedin': {"username": "", "profile": "", "image": "", "Link_image": "", 'Face_Recognition_Result': ""},
            'facebook': {"username": "", "profile": "", "image": "", "Link_image": "", 'Face_Recognition_Result': ""},
                'X': {"username": "", "profile": "", "image": "", "Link_image": "", 'Face_Recognition_Result':""},
            'instagram': {"username": "", "profile": "", "image": "", "Link_image": "", 'Face_Recognition_Result': ""},
            'threads': {"user_id":"","username": "", "profile": "", "image": "", "Link_image": "", 'Face_Recognition_Result': ""},
        }

        # Profile information for each social media
        self.info_facebook = {"Overview": "","Work_and_Education": "", "Places_Lived": "", "Contact_and_Basic_Info": "",
                              "Family_Relationships": "", "Details_About": "", "Life_Events": ""}
        
        self.info_linkedin = {}
        
        self.info_X = {'path_tweets':"", 'tweets': "", 'other_info': ""}

        self.info_threads = {'Path_profile':"", "user_threads":"","posts":"", "threads_info": ""}

        self.info_instagram = {"Biografia": "", "Sito_Personale": "", 'Path_profile':""}

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    def add_social_profile(self, platform, profile_url, profile_image_url=None):
        """Adds or updates a social profile."""
        if platform in self.social_profiles:
            self.social_profiles[platform]['profile'] = profile_url
            self.social_profiles[platform]['image'] = profile_image_url or ""
        else:
            print(f"{platform} is not a recognized platform.")

    def get_social_profile(self, platform):
        """Retrieves profile information for a given social media platform."""
        return self.social_profiles.get(platform, "Social platform not found.")

    def update_person_info(self, platform, info_dict):
        """Updates the person's info for a specific platform."""
        platform_info_attr = f"info_{platform}"
        if hasattr(self, platform_info_attr):
            getattr(self, platform_info_attr).update(info_dict)
        else:
            print(f"{platform} info not found.")

    def remove_social_profile(self, platform):
        """Removes a social profile from the person."""
        if platform in self.social_profiles:
            self.social_profiles[platform] = {"profile": "", "image": ""}
        else:
            print(f"{platform} is not a recognized platform.")

   
    def __str__(self):
        return (f"First Name: {self.first_name}\n"
                f"Last Name: {self.last_name}\n"
                f"Full Name: {self.full_name}\n"
                f"Original Person Image: {self.original_person_image}\n"
                f"Potential Path Person: {self.potential_path_person}\n"
                f"Candidate Users Found on Facebook: {self.serialize_candidates(self.list_candidate_user_found_fb)}\n"
                f"Candidate Users Found on LinkedIn: {self.serialize_candidates(self.list_candidate_user_found_linkedin)}\n"
                f"Candidate Users Found on Threads: {self.serialize_candidates(self.list_candidate_user_found_threads)}\n"
                f"Candidate Users Found on X: {self.serialize_candidates(self.list_candidate_user_found_X)}\n"
                f"Candidate Users Found on Instagram: {self.serialize_candidates(self.list_candidate_user_found_instagram)}\n"
                f"Social Profiles: {self.social_profiles}\n"
                f"Facebook Info: {self.info_facebook}\n"
                f"LinkedIn Info: {self.info_linkedin}\n"
                f"X Info: {self.info_X}\n"
                f"Threads Info: {self.info_threads}\n"
                f"Instagram Info: {self.info_instagram}")
    
    def save_to_json(self, file_path):
        """Saves the person's data to a JSON file."""
        try:
            with open(file_path, "w") as file:
                file.write(json.dumps(self.person_to_dict(), indent=4))

        except Exception as e:
            print(f"An error occurred while saving data: {e}")

    def serialize_candidates(self, candidates_list):
        # Converte ogni Candidate in stringa usando __str__()
        result_list = []
        for candidate in candidates_list:
            result_list.append(candidate.candidate_to_dict())
        return result_list

    def person_to_dict(self):
        """Return a JSON-serializable dict of the Person object."""

        return {
            "first_name": self.first_name,
            "last_name": self.last_name,
            "full_name": self.full_name,
            "original_person_image": self.original_person_image,
            "potential_path_person": self.potential_path_person,

            # 🔥 QUI viene fatta la conversione Candidate -> stringa
            "list_candidate_user_found_fb": self.serialize_candidates(self.list_candidate_user_found_fb) if len(self.list_candidate_user_found_fb)>0 else [],
            "list_candidate_user_found_linkedin": self.serialize_candidates(self.list_candidate_user_found_linkedin) if len(self.list_candidate_user_found_linkedin)>0 else [],
            "list_candidate_user_found_threads": self.serialize_candidates(self.list_candidate_user_found_threads) if len(self.list_candidate_user_found_threads)>0 else [],
            "list_candidate_user_found_X": self.serialize_candidates(self.list_candidate_user_found_X) if len(self.list_candidate_user_found_X)>0 else [],
            "list_candidate_user_found_instagram": self.serialize_candidates(self.list_candidate_user_found_instagram) if len(self.list_candidate_user_found_instagram)>0 else [],

            "social_profiles": self.social_profiles,
            "info_facebook": self.info_facebook,
            "info_linkedin": self.info_linkedin,
            "info_X": self.info_X,
            "info_threads": self.info_threads,
            "info_instagram": self.info_instagram,
        }

# # Example usage
# person = Person(first_name="John", last_name="Doe", person_image="path/to/image.jpg")

# # Add a social profile
# person.add_social_profile("linkedin", "https://linkedin.com/in/johndoe", "path/to/linkedin_image.jpg")

# # Get social profile info
# print(person.get_social_profile("linkedin"))

# # Update social information
# person.update_person_info("facebook", {"Work_and_Education": "Software Engineer", "Contact_and_Basic_Info": "123-456-7890"})

# # Remove a social profile
# person.remove_social_profile("linkedin")

# # Check total social profiles
# print("Number of social profiles:", person.numero_social)
