import requests
import json
import time

BASE_URL = "http://localhost:5001"

def test_auth_flow():
    print("--- Starting Auth Flow Verification ---")
    
    # 1. Register a new user
    print("\n1. Testing User Registration...")
    reg_data = {
        "username": f"testuser_{int(time.time())}",
        "password": "testpassword123",
        "email": "test@example.com"
    }
    response = requests.post(f"{BASE_URL}/api/auth/register", json=reg_data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    if response.status_code != 200:
        print("FAIL: Registration failed")
        return

    # 2. Login to get JWT
    print("\n2. Testing User Login...")
    login_data = {
        "username": reg_data["username"],
        "password": reg_data["password"]
    }
    response = requests.post(f"{BASE_URL}/api/auth/login", data=login_data)
    print(f"Status: {response.status_code}")
    
    if response.status_code != 200:
        print("FAIL: Login failed")
        return
        
    token = response.json().get("access_token")
    print("SUCCESS: Received access token")

    # 3. Access protected route without token
    print("\n3. Testing Protected Route (No Token)...")
    response = requests.get(f"{BASE_URL}/api/drafts")
    print(f"Status (Expected 401): {response.status_code}")
    if response.status_code == 401:
        print("SUCCESS: Access denied as expected")
    else:
        print(f"FAIL: Unexpected status {response.status_code}")

    # 4. Access protected route with valid token
    print("\n4. Testing Protected Route (With Valid Token)...")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/api/drafts", headers=headers)
    print(f"Status (Expected 200): {response.status_code}")
    if response.status_code == 200:
        print("SUCCESS: Access granted")
    else:
        print(f"FAIL: Unexpected status {response.status_code}")
        print(response.text)

    # 5. Logout
    print("\n5. Testing Logout...")
    response = requests.post(f"{BASE_URL}/api/auth/logout", headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print("SUCCESS: Logged out")
    else:
        print("FAIL: Logout failed")

    # 6. Access protected route after logout
    print("\n6. Testing Protected Route (After Logout)...")
    response = requests.get(f"{BASE_URL}/api/drafts", headers=headers)
    print(f"Status (Expected 401): {response.status_code}")
    if response.status_code == 401:
        print("SUCCESS: Token invalidated successfully")
    else:
        print(f"FAIL: Token still valid after logout")

if __name__ == "__main__":
    # Ensure server is running or instructions for the user
    print("NOTE: Ensure the FastAPI server is running on http://localhost:5001 before running this test.")
    try:
        test_auth_flow()
    except requests.exceptions.ConnectionError:
        print("\nERROR: Could not connect to server. Is it running?")
