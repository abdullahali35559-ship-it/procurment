import os
from dotenv import load_dotenv

load_dotenv()

# JWT Configuration
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "procurement-agent-super-secret-key-2024")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440")) # 24 hours

# Data Paths
AUTH_DIR = os.path.join(os.getcwd(), "auth")
USERS_FILE = os.path.join(AUTH_DIR, "users.json")
SESSIONS_FILE = os.path.join(AUTH_DIR, "sessions.json")
