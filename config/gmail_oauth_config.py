"""
Gmail OAuth2 Configuration
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Gmail OAuth2 Settings
GMAIL_CLIENT_ID = os.getenv('GMAIL_CLIENT_ID')
GMAIL_CLIENT_SECRET = os.getenv('GMAIL_CLIENT_SECRET')
GMAIL_REDIRECT_URI = os.getenv('GMAIL_REDIRECT_URI', 'http://localhost:8000/gmail/oauth/callback')
GMAIL_TOKEN_FILE = os.getenv('GMAIL_TOKEN_FILE', '.gmail_oauth_token.json')

# Gmail OAuth2 Scopes
GMAIL_SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/drive.readonly',
    'https://www.googleapis.com/auth/gmail.compose',
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/calendar.readonly',
    'https://www.googleapis.com/auth/calendar.events',
    'openid',
    'https://www.googleapis.com/auth/userinfo.email'
]

# OAuth2 Authorization URL
GMAIL_AUTH_BASE_URL = 'https://accounts.google.com/o/oauth2/v2/auth'
GMAIL_TOKEN_URL = 'https://oauth2.googleapis.com/token'
