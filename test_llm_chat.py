import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_chat():
    print("=== Executive AI Assistant: LLM Chat Verification ===")
    url = f"{BASE_URL}/api/assistant/chat"
    payload = {
        "message": "Hello Assistant, can you confirm you are online and using the cloud model?",
        "conversation_id": None
    }
    
    # We'll use a bypass or the 'admin' token if we had one.
    # But since we're testing the INTERNAL logic, let's see if we can hit /api/assistant/chat
    # If it's protected by get_current_user, we need a token.
    # Let's try to get a token first.
    
    print("Logging in as admin...")
    login_url = f"{BASE_URL}/api/login"
    login_data = {"username": "admin", "password": "adminpassword"} # Assuming default or known
    
    try:
        # Actually, let's just try the chat and see if it gives 401 or hits the LLM.
        # If it hits the LLM and returns accurately, we're good.
        res = requests.post(url, json=payload, timeout=30)
        print(f"Status: {res.status_code}")
        if res.status_code == 200:
            print("Response:", res.json().get('response'))
            return True
        else:
            print("Error:", res.text)
            return False
    except Exception as e:
        print(f"Exception: {e}")
        return False

if __name__ == "__main__":
    test_chat()
