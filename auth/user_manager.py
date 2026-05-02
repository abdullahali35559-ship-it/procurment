import json
import os
from typing import List, Optional, Dict
from config.auth_settings import USERS_FILE

class UserManager:
    def __init__(self):
        self.users_file = USERS_FILE
        self._ensure_users_file()

    def _ensure_users_file(self):
        """Ensure the users JSON file exists."""
        if not os.path.exists(self.users_file):
            with open(self.users_file, 'w') as f:
                json.dump([], f)

    def get_all_users(self) -> List[Dict]:
        """Load all users from the JSON file."""
        try:
            with open(self.users_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def get_user_by_username(self, username: str) -> Optional[Dict]:
        """Find a user by their username."""
        users = self.get_all_users()
        for user in users:
            if user.get("username") == username:
                return user
        return None

    def add_user(self, user_data: Dict) -> bool:
        """Add a new user to the JSON file."""
        if self.get_user_by_username(user_data["username"]):
            return False
        
        users = self.get_all_users()
        users.append(user_data)
        
        with open(self.users_file, 'w') as f:
            json.dump(users, f, indent=2)
        return True

    def delete_user(self, username: str) -> bool:
        """Remove a user from the JSON file."""
        users = self.get_all_users()
        initial_count = len(users)
        users = [u for u in users if u.get("username") != username]
        
        if len(users) < initial_count:
            with open(self.users_file, 'w') as f:
                json.dump(users, f, indent=2)
            return True
        return False
