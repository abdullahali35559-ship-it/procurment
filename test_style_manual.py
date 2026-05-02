import requests
import json
import time

BASE_URL = "http://localhost:8069" # Standard port in main.py
# Use the superadmin account created in init_admin
AUTH = ("superadmin", "superadmin123")

def test_style_mirroring_manual():
    print("=== Testing Style Mirroring (Manual Paste) ===")
    
    # 1. Login to get session
    session = requests.Session()
    login_resp = session.post(f"{BASE_URL}/api/auth/login", data={
        "username": "superadmin",
        "password": "superadmin123"
    })
    
    if login_resp.status_code != 200:
        print(f"FAILED: Login failed with {login_resp.status_code}")
        return

    # 2. Paste 4 sample emails to settings
    samples = """
    Email 1: Hi Team, hope you're good. Just wanted to check on the progress. Best, Abdullah.
    Email 2: Hi there, can we get an update on the Procurement? Thanks! Best, Abdullah.
    Email 3: Hi, please find the documents attached. Let me know if you need anything else. Best, Abdullah.
    Email 4: Hi, great job on the last project. Looking forward to the next one. Best, Abdullah.
    """
    
    print("Sending sample emails to /api/user/settings...")
    update_resp = session.put(f"{BASE_URL}/api/user/settings", json={
        "brand_voice": samples,
        "custom_instructions": "Always end with 'Best, Abdullah'."
    })
    
    if update_resp.status_code == 200:
        print("SUCCESS: Settings updated and analysis triggered.")
        data = update_resp.json()
        print(f"Message: {data.get('message')}")
    else:
        print(f"FAILED: Status {update_resp.status_code}, Body: {update_resp.text}")

    # Wait a bit for DB commit/refresh
    time.sleep(2)

    # 3. Check profile to see if writing_style_guide was generated
    print("Fetching profile to verify Style Guide...")
    me_resp = session.get(f"{BASE_URL}/api/auth/me")
    if me_resp.status_code == 200:
        profile = me_resp.json()
        guide = profile.get("writing_style_guide")
        if guide:
            print("\n--- GENERATED STYLE GUIDE ---")
            print(guide)
            print("-----------------------------\n")
            print("SUCCESS: AI has understood the tone and created a guide!")
        else:
            print("FAILED: Style guide is empty. AI analysis might be still running or failed.")
    else:
        print(f"FAILED: Could not fetch profile. Status {me_resp.status_code}")

if __name__ == "__main__":
    # Ensure server is running or this will fail
    try:
        test_style_mirroring_manual()
    except Exception as e:
        print(f"ERROR: Make sure the server is running on {BASE_URL}. Exception: {e}")
