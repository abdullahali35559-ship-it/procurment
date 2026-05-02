import json
import requests
from pathlib import Path
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

def check_outlook_token():
    print("Checking Outlook/OneDrive Token...")
    token_file = Path('.outlook_oauth_token.json')
    if not token_file.exists():
        print("❌ .outlook_oauth_token.json not found")
        return
    
    try:
        with open(token_file) as f:
            token_data = json.load(f)
            access_token = token_data.get('access_token')
        
        if not access_token:
            print("❌ No access token in file")
            return
            
        headers = {'Authorization': f'Bearer {access_token}'}
        response = requests.get('https://graph.microsoft.com/v1.0/me', headers=headers)
        
        if response.status_code == 200:
            user_data = response.json()
            print(f"✅ Authenticated as: {user_data.get('displayName')} ({user_data.get('userPrincipalName')})")
            
            # Check for drive access
            drive_response = requests.get('https://graph.microsoft.com/v1.0/me/drive', headers=headers)
            if drive_response.status_code == 200:
                print("✅ OneDrive access confirmed")
            else:
                print(f"⚠️  OneDrive access check failed: {drive_response.status_code}")
        else:
            print(f"❌ Authentication failed: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"❌ Error: {e}")

def check_google_token():
    print("\nChecking Google Drive Token...")
    token_file = Path('.gmail_oauth_token.json')
    if not token_file.exists():
        print("❌ .gmail_oauth_token.json not found")
        return
    
    try:
        with open(token_file) as f:
            token_data = json.load(f)
            
        creds = Credentials(
            token=token_data.get('token'),
            refresh_token=token_data.get('refresh_token'),
            token_uri=token_data.get('token_uri'),
            client_id=token_data.get('client_id'),
            client_secret=token_data.get('client_secret'),
            scopes=token_data.get('scopes')
        )
        
        service = build('drive', 'v3', credentials=creds)
        user_info = service.about().get(fields='user').execute()
        user = user_info.get('user', {})
        print(f"✅ Authenticated as: {user.get('displayName')} ({user.get('emailAddress')})")
        print("✅ Google Drive access confirmed")
        
    except Exception as e:
        print(f"❌ Authentication failed or Error: {e}")

if __name__ == "__main__":
    check_outlook_token()
    check_google_token()
