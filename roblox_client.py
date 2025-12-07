import requests
import time

class RobloxClient:
    def __init__(self, request_delay: float = 0.5):
        self.base_url = "https://users.roblox.com"
        self.request_delay = request_delay
    
    def get_user_id(self, username: str) -> int:
        """
        Resolves a username to a Roblox User ID.
        Returns None if user not found.
        """
        time.sleep(self.request_delay)
        url = f"{self.base_url}/v1/usernames/users"
        payload = {
            "usernames": [username],
            "excludeBannedUsers": True
        }
        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            data = response.json()
            if data['data']:
                return data['data'][0]['id']
            return None
        except requests.RequestException as e:
            print(f"Error resolving username {username}: {e}")
            return None

    def get_user_profile(self, user_id: int) -> dict:
        """
        Fetches public user information (description, display name, etc).
        """
        time.sleep(self.request_delay)
        url = f"{self.base_url}/v1/users/{user_id}"
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error fetching profile for {user_id}: {e}")
            return None

    def get_user_friends(self, user_id: int) -> list:
        """
        Fetches a list of friend User IDs for the given user.
        """
        time.sleep(self.request_delay)
        url = f"https://friends.roblox.com/v1/users/{user_id}/friends"
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            # The API returns a list of friend objects in 'data'
            # Each object has an 'id' field.
            return [friend['id'] for friend in data.get('data', [])]
        except requests.RequestException as e:
            print(f"Error fetching friends for {user_id}: {e}")
            return []
