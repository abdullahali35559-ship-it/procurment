import requests
import time

BASE_URL = "http://127.0.0.1:8000"

# List of all critical pages to verify
PAGES = [
    "/index.html",
    "/calendar.html",
    "/threads.html",
    "/drafts.html",
    "/assistant.html",
    "/settings.html",
    "/emails.html",
    "/attachments.html"
]

# Critical API endpoints
API_ENDPOINTS = [
    "/api/status",
    "/api/agent/status",
    "/api/dashboard/stats",
    "/api/calendar/events?days=30",
    "/api/threads",
    "/api/emails",
    "/api/attachments",
    "/api/assistant/history",
    "/api/contacts",
    "/api/oauth/status"
]

def verify_pages():
    print("\n--- Verifying Static Pages ---")
    for page in PAGES:
        url = f"{BASE_URL}{page}"
        try:
            res = requests.get(url, timeout=5)
            status = " [OK]" if res.status_code == 200 else f" [FAIL: {res.status_code}]"
            print(f"{page:<20} {status}")
        except Exception as e:
            print(f"{page:<20}  [ERROR: {e}]")

def verify_apis():
    print("\n--- Verifying API Endpoints (Headless) ---")
    # Most points will return 401 if not logged in, but we check if they are FOUND (not 404)
    for api in API_ENDPOINTS:
        url = f"{BASE_URL}{api}"
        try:
            res = requests.get(url, timeout=10)
            # 401 is OK for existence check, 404 is a FAIL
            if res.status_code == 404:
                print(f"{api:<30}  [FAIL: 404 Not Found]")
            elif res.status_code == 401:
                print(f"{api:<30}  [OK: Secured (401)]")
            elif res.status_code == 200:
                print(f"{api:<30}  [OK: Public (200)]")
            else:
                print(f"{api:<30}  [STATUS: {res.status_code}]")
        except Exception as e:
            print(f"{api:<30}  [ERROR: {e}]")

def test_cache_performance():
    print("\n--- Verifying Caching Performance ---")
    target = "/api/dashboard/stats"
    # Note: Requires auth for real testing, but we can check if it responds (401 or 200)
    # We verify if the server handles the load without hanging.
    start = time.time()
    try:
        requests.get(f"{BASE_URL}{target}", timeout=10)
        end = time.time()
        print(f"Initial request (uncached/protected): {end - start:.2f}s")
    except Exception as e:
        print(f"Performance Test Error: {e}")

if __name__ == "__main__":
    print(f"Starting System Audit at {BASE_URL}...")
    verify_apis()
    verify_pages()
    test_cache_performance()
