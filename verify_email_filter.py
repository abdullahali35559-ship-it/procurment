import requests
import json

BASE_URL = "http://localhost:8000/api"

def test_email_filtering():
    print("Testing Email Filtering API...")
    
    # 1. Test default fetch (should only show tenders)
    print("\n1. Fetching default (tenders only)...")
    r = requests.get(f"{BASE_URL}/emails")
    if r.status_code == 200:
        data = r.json()
        emails = data.get('data', [])
        print(f"   Received {len(emails)} emails")
        for e in emails:
            print(f"   - [{e.get('status')}] {e.get('subject')[:50]}")
            if not e.get('is_tender'):
                print("   [!] ERROR: Found non-tender in default list")
    else:
        print(f"   [!] Error: {r.status_code}")

    # 2. Test include_all=true
    print("\n2. Fetching with include_all=true...")
    r = requests.get(f"{BASE_URL}/emails?include_all=true")
    if r.status_code == 200:
        data = r.json()
        emails = data.get('data', [])
        print(f"   Received {len(emails)} emails")
        # Check if we have any non-tenders now
        has_non_tender = any(not e.get('is_tender') for e in emails)
        if has_non_tender:
            print("   [OK] Found non-tender emails as expected")
        else:
            print("   [INFO] No non-tender emails in DB yet, or filtering is still too strict")
    else:
        print(f"   [!] Error: {r.status_code}")

    # 3. Test status=junk
    print("\n3. Fetching with status=junk...")
    r = requests.get(f"{BASE_URL}/emails?status=junk")
    if r.status_code == 200:
        data = r.json()
        emails = data.get('data', [])
        print(f"   Received {len(emails)} junk emails")
        for e in emails:
            print(f"   - [JUNK] {e.get('subject')[:50]}")
            if e.get('is_tender'):
                 print("   [!] ERROR: Found tender in junk list")
    else:
        print(f"   [!] Error: {r.status_code}")

if __name__ == "__main__":
    test_email_filtering()
