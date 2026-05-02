"""
Outlook OAuth2 IMAP Fetcher
Uses token from FastAPI OAuth flow
Python 3.10+ compatible
"""
import os
import json
from pathlib import Path
from imapclient import IMAPClient
import ssl
class OutlookOAuthFetcher:
    """Fetch Outlook emails using OAuth2 token from FastAPI"""
    
    def __init__(self):
        self.email = os.getenv('OUTLOOK_USER')
        self.token_file = Path('.outlook_oauth_token.json')
        self.imap_client = None
    
    def get_access_token(self):
        """Load access token from file"""
        
        if not self.token_file.exists():
            raise Exception(
                "No OAuth token found! "
                "Please authenticate first:\n"
                "1. Start API: python -m uvicorn api.main:app --reload\n"
                "2. Open: http://localhost:5001/oauth/login\n"
                "3. Login with Microsoft account"
            )
        
        try:
            with open(self.token_file, 'r') as f:
                token_data = json.load(f)
            
            if 'access_token' not in token_data:
                raise Exception("Invalid token file")
            
            return token_data['access_token']
            
        except Exception as e:
            raise Exception(f"Error loading OAuth token: {e}")
    
    def connect_imap(self):
        """Connect to Outlook IMAP using OAuth2"""
        
        # Get token
        token = self.get_access_token()
        
        # Connect to IMAP server
        ssl_context = ssl.create_default_context()
        self.imap_client = IMAPClient(
            'outlook.office365.com',
            port=993,
            ssl_context=ssl_context
        )
        
        # Authenticate using OAuth2 XOAUTH2 format
        # Note: Graph API tokens need different format than standard OAuth2
        auth_string = f'user={self.email}\x01auth=Bearer {token}\x01\x01'
        
        try:
            # Try standard OAuth2 login
            self.imap_client.oauth2_login(self.email, token)
            print(f"[OK] Connected to Outlook via OAuth2!")
            return self.imap_client
        except Exception as e:
            # Fallback: Try with auth string
            print(f"Standard OAuth2 failed, trying auth string format...")
            try:
                self.imap_client.login(self.email, auth_string)
                print(f"[OK] Connected to Outlook via OAuth2 (alternate method)")
                return self.imap_client
            except Exception as e2:
                raise Exception(f"OAuth2 IMAP login failed: {e}. Alternate method also failed: {e2}")
    
    def disconnect(self):
        """Disconnect from IMAP"""
        if self.imap_client:
            try:
                self.imap_client.logout()
            except:
                pass