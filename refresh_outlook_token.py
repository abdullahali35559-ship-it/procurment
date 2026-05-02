"""
Outlook OAuth2 Token Refresh Script
Automatically refreshes Outlook access token when expired
"""

import os
import json
from dotenv import load_dotenv
from msal import ConfidentialClientApplication
from datetime import datetime, timedelta

load_dotenv()

CLIENT_ID = os.getenv("OUTLOOK_CLIENT_ID")
CLIENT_SECRET = os.getenv("OUTLOOK_CLIENT_SECRET")
TENANT_ID = os.getenv("OUTLOOK_TENANT_ID", "common")

AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
SCOPES = ["https://graph.microsoft.com/Mail.Read", 
          "https://graph.microsoft.com/Mail.Send",
          "https://graph.microsoft.com/Calendars.ReadWrite"]

TOKEN_FILE = ".outlook_oauth_token.json"


def load_token():
    """Load existing token from file"""
    try:
        with open(TOKEN_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ Token file not found: {TOKEN_FILE}")
        print("Run: python run_outlook_oauth.py first")
        return None


def save_token(token_data):
    """Save token to file"""
    with open(TOKEN_FILE, "w") as f:
        json.dump(token_data, f, indent=2)
    print(f"✅ Token saved to {TOKEN_FILE}")


def is_token_expired(token_data):
    """Check if access token is expired or will expire soon"""
    if "expires_in" not in token_data:
        return True
    
    # Token is considered expired if it expires in less than 5 minutes
    expires_at = token_data.get("expires_at", 0)
    current_time = datetime.now().timestamp()
    
    # If no expires_at, calculate from expires_in
    if expires_at == 0:
        # Assume token was just created
        expires_at = current_time + token_data["expires_in"]
        token_data["expires_at"] = expires_at
        save_token(token_data)
    
    time_until_expiry = expires_at - current_time
    
    if time_until_expiry < 300:  # Less than 5 minutes
        return True
    
    return False


def refresh_token():
    """Refresh the Outlook access token using refresh token"""
    print("=" * 60)
    print("🔄 Outlook Token Refresh")
    print("=" * 60)
    
    # Load existing token
    token_data = load_token()
    if not token_data:
        return None
    
    # Check if refresh token exists
    if "refresh_token" not in token_data:
        print("❌ No refresh token found!")
        print("You need to re-authenticate.")
        print("Run: python run_outlook_oauth.py")
        return None
    
    # Check if token is still valid
    if not is_token_expired(token_data):
        expires_at = token_data.get("expires_at", 0)
        current_time = datetime.now().timestamp()
        minutes_left = int((expires_at - current_time) / 60)
        print(f"✅ Token is still valid for {minutes_left} minutes")
        return token_data["access_token"]
    
    print("⏳ Token expired or expiring soon. Refreshing...")
    
    # Create MSAL client
    app = ConfidentialClientApplication(
        CLIENT_ID,
        authority=AUTHORITY,
        client_credential=CLIENT_SECRET
    )
    
    # Refresh token
    try:
        result = app.acquire_token_by_refresh_token(
            token_data["refresh_token"],
            scopes=SCOPES
        )
        
        if "access_token" in result:
            # Update token data with new values
            result["expires_at"] = datetime.now().timestamp() + result["expires_in"]
            save_token(result)
            
            print("\n🎉 Token refreshed successfully!")
            print(f"✅ New token expires in: {result['expires_in'] // 60} minutes")
            print(f"✅ Refresh token: {'Available' if 'refresh_token' in result else 'Not available'}")
            
            return result["access_token"]
        else:
            print(f"\n❌ Failed to refresh token")
            print(f"Error: {result.get('error_description', 'Unknown error')}")
            print("\nYou may need to re-authenticate.")
            print("Run: python run_outlook_oauth.py")
            return None
            
    except Exception as e:
        print(f"\n❌ Exception during token refresh: {str(e)}")
        return None


def get_valid_token():
    """Get a valid access token (refresh if needed)"""
    token_data = load_token()
    if not token_data:
        return None
    
    if is_token_expired(token_data):
        return refresh_token()
    else:
        return token_data["access_token"]


if __name__ == "__main__":
    # Test token refresh
    access_token = refresh_token()
    
    if access_token:
        print("\n" + "=" * 60)
        print("✅ SUCCESS! Token is ready to use")
        print("=" * 60)
        
        # Optional: Test with Microsoft Graph API
        print("\n🧪 Testing token with Microsoft Graph API...")
        
        import requests
        
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.get(
            "https://graph.microsoft.com/v1.0/me",
            headers=headers
        )
        
        if response.status_code == 200:
            user_data = response.json()
            print(f"✅ Authenticated as: {user_data.get('userPrincipalName')}")
        else:
            print(f"❌ API test failed: {response.status_code}")
    else:
        print("\n" + "=" * 60)
        print("❌ Failed to get valid token")
        print("=" * 60)
