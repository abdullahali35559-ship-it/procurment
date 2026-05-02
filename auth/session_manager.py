import json
import os
from typing import List, Optional, Dict
from config.auth_settings import SESSIONS_FILE

class SessionManager:
    def __init__(self):
        self.sessions_file = SESSIONS_FILE
        self._ensure_sessions_file()

    def _ensure_sessions_file(self):
        """Ensure the sessions JSON file exists."""
        if not os.path.exists(self.sessions_file):
            with open(self.sessions_file, 'w') as f:
                json.dump([], f)

    def get_all_sessions(self) -> List[Dict]:
        """Load all active sessions from the JSON file."""
        try:
            with open(self.sessions_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def add_session(self, username: str, token: str, expires_at: float):
        """Add a new active session."""
        sessions = self.get_all_sessions()
        sessions.append({
            "username": username,
            "token": token,
            "expires_at": expires_at
        })
        
        with open(self.sessions_file, 'w') as f:
            json.dump(sessions, f, indent=2)

    def is_token_valid(self, token: str) -> bool:
        """Check if a token exists in the active sessions."""
        import time
        sessions = self.get_all_sessions()
        now = time.time()
        
        # Also clean up expired sessions
        valid_sessions = [s for s in sessions if s.get("expires_at", 0) > now]
        if len(valid_sessions) < len(sessions):
             with open(self.sessions_file, 'w') as f:
                json.dump(valid_sessions, f, indent=2)
        
        for session in valid_sessions:
            if session.get("token") == token:
                return True
        return False

    def revoke_session(self, token: str):
        """Remove a session (logout)."""
        sessions = self.get_all_sessions()
        sessions = [s for s in sessions if s.get("token") != token]
        
        with open(self.sessions_file, 'w') as f:
            json.dump(sessions, f, indent=2)
