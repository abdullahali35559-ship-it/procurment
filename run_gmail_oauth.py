"""
Gmail OAuth2 Re-authentication Script
Simple script to get new Gmail token with gmail.compose scope
"""

import os
import json
from pathlib import Path
from google_auth_oauthlib.flow import InstalledAppFlow
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Gmail OAuth2 Scopes
SCOPES = [
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

def authenticate_gmail():
    """Authenticate with Gmail and save token"""
    
    print("=" * 60)
    print("Gmail OAuth2 Re-authentication")
    print("=" * 60)
    print()
    print("NEW SCOPE: gmail.compose (for creating draft emails)")
    print()
    
    # Create client config
    client_config = {
        "installed": {
            "client_id": os.getenv('GMAIL_CLIENT_ID'),
            "client_secret": os.getenv('GMAIL_CLIENT_SECRET'),
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": ["http://localhost:8085/"]
        }
    }
    
    print("Starting OAuth flow...")
    print("Browser will open automatically")
    print()
    
    # Run OAuth flow with explicit browser opening
    flow = InstalledAppFlow.from_client_config(
        client_config,
        scopes=SCOPES
    )
    
    # Force browser to open
    credentials = flow.run_local_server(
        port=8085,
        prompt='consent',
        open_browser=True,  # Explicitly enable browser opening
        success_message='✅ Authentication successful! You can close this window.'
    )
    
    # Save token
    token_data = {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes
    }
    
    token_file = Path('.gmail_oauth_token.json')
    with open(token_file, 'w') as f:
        json.dump(token_data, f, indent=2)
    
    print()
    print("=" * 60)
    print("✅ SUCCESS!")
    print("=" * 60)
    print(f"Token saved to: {token_file.absolute()}")
    print()
    print("Scopes granted:")
    for scope in credentials.scopes:
        print(f"  ✅ {scope}")
    print()
    print("=" * 60)
    print()
    print("Now you can run: .\\process_emails.bat")
    print()

if __name__ == "__main__":
    try:
        authenticate_gmail()
    except Exception as e:
        print()
        print("=" * 60)
        print("❌ ERROR")
        print("=" * 60)
        print(f"Error: {e}")
        print()
        print("Make sure .env has:")
        print("  GMAIL_CLIENT_ID=your-client-id")
        print("  GMAIL_CLIENT_SECRET=your-client-secret")
        print("=" * 60)
