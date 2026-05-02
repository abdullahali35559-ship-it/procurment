"""
Debug script to test Microsoft Graph API connection
Tests different endpoints to identify 403 error cause
"""
import json
import requests
from pathlib import Path

def load_token():
    """Load OAuth2 token"""
    token_file = Path('.outlook_oauth_token.json')
    
    if not token_file.exists():
        print("[X] No token file found!")
        return None
    
    with open(token_file, 'r') as f:
        token_data = json.load(f)
    
    print("[OK] Token loaded")
    print(f"   Token type: {token_data.get('token_type')}")
    print(f"   Has refresh: {bool(token_data.get('refresh_token'))}")
    print(f"   Scopes: {token_data.get('scope', '').split()}")
    print()
    
    return token_data['access_token']

def test_endpoint(url, token, description):
    """Test a Graph API endpoint"""
    print(f"Testing: {description}")
    print(f"URL: {url}")
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            print("[OK] SUCCESS!")
            data = response.json()
            print(f"Response keys: {list(data.keys())[:5]}")
        else:
            print(f"[X] FAILED")
            print(f"Response: {response.text[:500]}")
        
    except Exception as e:
        print(f"[X] ERROR: {e}")
    
    print("-" * 60)
    print()

if __name__ == "__main__":
    print("=" * 60)
    print("MICROSOFT GRAPH API DIAGNOSTIC TEST")
    print("=" * 60)
    print()
    
    # Load token
    token = load_token()
    
    if not token:
        print("Cannot proceed without token!")
        exit(1)
    
    # Test different endpoints
    base_url = 'https://graph.microsoft.com/v1.0'
    
    endpoints = [
        (f"{base_url}/me", "User Profile"),
        (f"{base_url}/me/mailFolders", "Mail Folders"),
        (f"{base_url}/me/messages", "Messages"),
        (f"{base_url}/me/messages?$top=1", "Messages (limited)"),
    ]
    
    for url, description in endpoints:
        test_endpoint(url, token, description)
    
    print("=" * 60)
    print("DIAGNOSTIC COMPLETE")
    print("=" * 60)
