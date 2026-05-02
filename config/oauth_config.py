"""
OAuth2 Configuration for Outlook
Python 3.10+ compatible
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Azure OAuth2 Settings
CLIENT_ID = os.getenv('OUTLOOK_CLIENT_ID')
CLIENT_SECRET = os.getenv('OUTLOOK_CLIENT_SECRET')
TENANT_ID = 'consumers'  # For personal accounts
REDIRECT_URI = os.getenv('OUTLOOK_REDIRECT_URI', 'http://localhost:8069/oauth/callback')
# OAuth2 URLs
AUTHORIZE_URL = f'https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/authorize'
TOKEN_URL = f'https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/token'
# Scopes (using full Graph URIs for clarity and avoiding reserved names)
# Must be a LIST. We OMIT 'openid', 'profile', 'offline_access' as MSAL handles them automatically.
SCOPES = [
    'https://graph.microsoft.com/Mail.ReadWrite',
    'https://graph.microsoft.com/Mail.Send',
    'https://graph.microsoft.com/Calendars.ReadWrite'
]

# Defense: ensure it's a list if imported by other modules
if not isinstance(SCOPES, list):
    SCOPES = list(SCOPES)
# Token storage
TOKEN_FILE = Path('.outlook_oauth_token.json')