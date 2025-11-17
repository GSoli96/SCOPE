"""
Provide a public interface for the Threads.
"""
import json
import re
import requests
import csv
import os
import pandas as pd

class BaseThreadsInterface:
    """
    A basic interface for interacting with Threads.
    """

    def __init__(self):
        """
        Initialize the object.
        """
        self.headers_for_html_fetching = {
            "authority": "www.threads.net",
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "accept-language": "en-US,en;q=0.9",
            "cache-control": "no-cache",
            "pragma": "no-cache",
            "upgrade-insecure-requests": "1",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "sec-ch-ua": '"Google Chrome";v="120", "Not-A.Brand";v="99", "Chromium";v="120"',
            "sec-ch-ua-platform": '"Windows"',
            "sec-ch-ua-mobile": "?0",
            "sec-fetch-site": "none",
            "sec-fetch-mode": "navigate",
            "sec-fetch-user": "?1",
            "sec-fetch-dest": "document",
            "referer": "https://www.instagram.com/",
            "origin": "https://www.threads.net",
            "x-asbd-id": "129477",
            "x-ig-app-id": "238260118697367",
        }

    def retrieve_user_id(self, username: str) -> int:
        """
        Retrieve the unique identifier for a user.

        Args:
            username (str): The user's username.

        Returns:
            The user's unique identifier as an integer.
        """
        response = requests.get(
            url=f'https://www.instagram.com/{username}',
            headers=self.headers_for_html_fetching,
        )
        user_id_key_value = re.search('"user_id":"(\\d+)",', response.text).group()
        user_id = re.search('\\d+', user_id_key_value).group()
        # print(user_id)
        return int(user_id)

    def retrieve_thread_id(self, url_id: str) -> int:
        """
        Retrieve the unique identifier for a thread.

        Args:
            url_id (str): The thread's URL identifier.

        Returns:
            The thread's unique identifier as an integer.
        """
        alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_'

        thread_id = 0

        for character in url_id:
            thread_id = (thread_id * 64) + alphabet.index(character)

        return thread_id

class ThreadsInterface(BaseThreadsInterface):
    """
    A public interface for interacting with Threads.

    Each unique endpoint requires a unique document ID, predefined by the developers.
    """
    THREADS_API_URL = 'https://www.threads.net/api/graphql'

    def __init__(self):
        """
        Initialize the object.
        """
        super().__init__()

        self.api_token = self._generate_api_token()
        self.default_headers = {
            'Authority': 'www.threads.net',
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Cache-Control': 'no-cache',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Origin': 'https://www.threads.net',
            'Pragma': 'no-cache',
            'Sec-Fetch-Site': 'same-origin',
            'X-ASBD-ID': '129477',
            'X-FB-LSD': self.api_token,
            'X-IG-App-ID': '238260118697367',
        }

        print("self.api_token",self.api_token)

    def retrieve_user(self, user_id: int) -> dict:
        """
        Retrieve a user.

        Args:
            user_id (int): The user's unique identifier.

        Returns:
            The user as a dictionary.
        """
        headers = self.default_headers.copy()
        headers['X-FB-Friendly-Name'] = 'BarcelonaProfileRootQuery'

        response = requests.post(
            url=self.THREADS_API_URL,
            headers=headers,
            data={
                'lsd': self.api_token,
                'variables': json.dumps(
                    {
                        'userID': user_id,
                    }
                ),
                'doc_id': '23996318473300828',
            },
        )

        return response.json()

    def retrieve_user_threads(self, user_id: int) -> dict:
        """
        Retrieve a user's threads.

        Args:
            user_id (int): The user's unique identifier.

        Returns:
            The list of user's threads inside a dictionary.
        """
        headers = self.default_headers.copy()
        headers['X-FB-Friendly-Name'] = 'BarcelonaProfileThreadsTabQuery'

        response = requests.post(
            url=self.THREADS_API_URL,
            headers=headers,
            data={
                'lsd': self.api_token,
                'variables': json.dumps(
                    {
                        'userID': user_id,
                    }
                ),
                'doc_id': '6232751443445612',
            },
        )

        return response.json()

    def retrieve_user_replies(self, user_id: int) -> dict:
        """
        Retrieve a user's replies.

        Args:
            user_id (int): The user's unique identifier.

        Returns:
            The list of user's replies inside a dictionary.
        """
        headers = self.default_headers.copy()
        headers['X-FB-Friendly-Name'] = 'BarcelonaProfileRepliesTabQuery'

        response = requests.post(
            url=self.THREADS_API_URL,
            headers=headers,
            data={
                'lsd': self.api_token,
                'variables': json.dumps(
                    {
                        'userID': user_id,
                    }
                ),
                'doc_id': '6307072669391286',
            },
        )

        return response.json()

    def retrieve_thread(self, thread_id: int) -> dict:
        """
        Retrieve a thread.

        Args:
            thread_id (int): The thread's unique identifier.

        Returns:
            The thread as a dictionary.
        """
        headers = self.default_headers.copy()
        headers['X-FB-Friendly-Name'] = 'BarcelonaPostPageQuery'

        response = requests.post(
            url=self.THREADS_API_URL,
            headers=headers,
            data={
                'lsd': self.api_token,
                'variables': json.dumps(
                    {
                        'postID': thread_id,
                    }
                ),
                'doc_id': '5587632691339264',
            },
        )

        return response.json()

    def retrieve_thread_likers(self, thread_id: int) -> dict:
        """
        Retrieve the likers of a thread.

        Args:
            thread_id (int): The thread's unique identifier.

        Returns:
            The list of likers of the thread inside a dictionary.
        """
        response = requests.post(
            url=self.THREADS_API_URL,
            headers=self.default_headers,
            data={
                'lsd': self.api_token,
                'variables': json.dumps(
                    {
                        'mediaID': thread_id,
                    }
                ),
                'doc_id': '9360915773983802',
            },
        )

        return response.json()

    def _generate_api_token(self) -> str:
        """
        Generate a token for the Threads.

        The token, called `lsd` internally, is required for any request.
        For anonymous users, it is just generated automatically from the back-end and passed to the front-end.

        Returns:
            The token for the Threads as a string.
        """
        response = requests.get(
            url='https://www.instagram.com/instagram',
            headers=self.headers_for_html_fetching,
        )

        token_key_value = re.search(
            'LSD",\\[\\],{"token":"(.*?)"},\\d+\\]', response.text).group()
        token_key_value = token_key_value.replace('LSD",[],{"token":"', '')
        token = token_key_value.split('"')[0]

        return token

    def save_data_to_csv(self, data: dict, filename: str) -> None :
        """
        Save the provided data into a CSV file.

        Args:
            data (dict): The data to be saved.
            filename (str): The filename of the CSV file.
        """
        # Convert the dictionary to a DataFrame
        df = pd.DataFrame(data)

        # Check if file exists
        if os.path.isfile(filename):
            # If it exists, append without writing headers
            df.to_csv(filename, mode='a', header=False, index=False)
        else:
            # If it doesn't exist, write the DataFrame with headers
            df.to_csv(filename, index=False)

    def save_data_to_json(self, data: dict, filename: str):
        """
        Save the provided data into a JSON file.

        Args:
            data (dict): The data to be saved.
            filename (str): The filename of the JSON file.
        """
        if not isinstance(data, dict):
            raise TypeError("Il parametro 'data' deve essere un dizionario.")

        # Estrai la directory dal filepath
        directory = os.path.dirname(filename)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
            print(f"Directory '{directory}' creata.")

        with open(filename, 'a') as json_file:
            json.dump(data, json_file, indent=2)

''''''
if __name__ == '__main__':
    th = ThreadsInterface()
    base_path = os.getcwd()+"\\Potential_target\\ste_cirillo\\threads"
    user_to_find = "ste_cirillo"

    user_id = th.retrieve_user_id(user_to_find)
    print(f"[Threads] user_id for {user_to_find}: {user_id}")

    user = th.retrieve_user(user_id)
    print(f"[Threads] user {user_id} information Extracted!")
    th.save_data_to_json(user, '{}\\user_info.json'.format(base_path))

    threads = th.retrieve_user_threads(user_id)
    print("[Threads] User Threads Extracted.")
    th.save_data_to_json(threads, '{}\\user_{}_threads.json'.format(base_path,user_to_find))

    replies = th.retrieve_user_replies(user_id)
    print("[Threads] User Replies Extracted.")
    th.save_data_to_json(replies, '{}\\user_{}_replies.json'.format(base_path,user_to_find))

    for i,post in enumerate(threads["data"]["mediaData"]['threads']):
        thread_id = post['id']
        print(i, post['id'])

        thread_content = th.retrieve_thread(thread_id)
        print("[Threads] Content of {} Extracted.".format(thread_id))
        th.save_data_to_json(thread_content, '{}\\threads_info\\{}_{}_thread_content.json'.format(base_path,
                                                                                                thread_id,user_to_find))

        thread_likers = th.retrieve_thread_likers(thread_id)
        print("[Threads] Likers for {} Extracted.".format(thread_id))
        th.save_data_to_json(thread_likers, '{}\\threads_info\\{}_thread_likers.json'.format(base_path,thread_id))
