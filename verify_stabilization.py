import requests
import json

BASE_URL = "http://localhost:8000"

def get_token():
    # Attempt to read from a common location or just try unauthenticated if needed
    # But usually we need a token. I'll try to get one from the existing session if possible
    # or just mock/skip if I can't. 
    # For now, I'll assume I can just hit them if I had a token.
    # Actually, I'll try to bypass auth if possible or find a way to get it.
    pass

def test_endpoint(path, method="GET", data=None):
    url = f"{BASE_URL}{path}"
    print(f"Testing {method} {url}...")
    try:
        # We need a token. Let's see if we can find one in the env or logs
        headers = {"Authorization": "Bearer test-token"} # This will probably fail if token is invalid
        if method == "GET":
            response = requests.get(url) # TRY UNAUTHENTICATED FIRST for some if allowed, or it will 401
        else:
            response = requests.post(url, json=data)
        
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            print("Success!")
            return response.json()
        elif response.status_code == 500:
            print("FAILURE: 500 Internal Server Error")
            print(response.text)
        else:
            print(f"Status: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error: {e}")
        return None

if __name__ == "__main__":
    print("=== API STABILIZATION VERIFICATION ===")
    
    # Check threads (to see if tagging metadata is there)
    threads = test_endpoint("/api/threads")
    if threads and threads.get('success'):
        print(f"Threads found: {len(threads.get('data', []))}")
        if threads.get('data'):
            first = threads['data'][0]
            print(f"First thread tags key present: {'tags' in first}")
            if 'tags' in first:
                print(f"Tags data: {first['tags']}")
    
    # Check drafts (to ensure 500 is gone)
    drafts = test_endpoint("/api/drafts")
    if drafts:
        print(f"Drafts success: {drafts.get('success', False)}")
    
    print("======================================")
