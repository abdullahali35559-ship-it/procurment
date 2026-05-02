import requests
import json
import time

BASE_URL = "http://127.0.0.1:8000"

def get_token():
    print("Attempting to get auth token...")
    # Based on earlier logs/common defaults for this project
    try:
        res = requests.post(f"{BASE_URL}/api/login", json={"username": "admin", "password": "adminpassword"}, timeout=5)
        if res.status_code == 200:
            token = res.json().get("access_token")
            print("Token obtained successfully.")
            return token
        else:
            print(f"Login failed: {res.status_code} - {res.text}")
            return None
    except Exception as e:
        print(f"Connection error during login: {e}")
        return None

def verify_data(token):
    if not token:
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # 1. Verify Stats
    print("\n--- Verifying Dashboard Stats ---")
    res = requests.get(f"{BASE_URL}/api/dashboard/stats", headers=headers)
    if res.status_code == 200:
        data = res.json().get("data", {})
        print("Stats Received:", json.dumps(data, indent=2))
    else:
        print(f"Stats Failed: {res.status_code}")
    
    # 2. Verify Documents Restoration
    print("\n--- Verifying Documents Data Restoration ---")
    res = requests.get(f"{BASE_URL}/api/attachments", headers=headers)
    if res.status_code == 200:
        data = res.json().get("data", [])
        print(f"Documents Count: {len(data)}")
        if len(data) > 0:
            print("Sample Document:", json.dumps(data[0], indent=2))
    else:
        print(f"Documents Failed: {res.status_code}")

    # 3. Verify Calendar End-to-End
    print("\n--- Verifying Calendar Data Sync ---")
    res = requests.get(f"{BASE_URL}/api/calendar/events?days=30", headers=headers)
    if res.status_code == 200:
        data = res.json().get("data", [])
        print(f"Calendar Events Count: {len(data)}")
    else:
        print(f"Calendar Failed: {res.status_code}")

if __name__ == "__main__":
    token = get_token()
    if token:
        verify_data(token)
    else:
        print("Skipping authenticated tests due to login failure.")
