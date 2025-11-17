import json

class Candidate:
    def __init__(self, username, link_image, url_profile, local_path_img):
        self.username = username
        self.url_profile = url_profile
        self.local_path_img = local_path_img
        self.link_image =link_image

    def get_username(self):
        return self.username

    def get_url_profile(self):
        return self.url_profile

    def get_local_path_img(self):
        return self.local_path_img

    def get_link_image(self):
        return self.link_image

    def __str__(self):
        return (f"username: {self.username}\n"
                f"url_profile: {self.url_profile}\n"
                f"local_path_img: {self.local_path_img}\n"
                f"link_image: {self.link_image}\n")

    def candidate_to_dict(self):
        return {
            'username': self.username,
            'url_profile': self.url_profile,
            'local_path_img': self.local_path_img,
            'link_image': self.link_image

        }
    
    def save_to_json(self, file_path):
        """Saves the person's data to a JSON file."""
        try:
            with open(file_path, "w") as file:
                file.write(json.dumps(self.__dict__, indent=4))  

        except Exception as e:
            print(f"An error occurred while saving data: {e}")

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
