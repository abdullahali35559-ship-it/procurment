import requests
import time
import json

BASE_URL = "http://127.0.0.1:8000"

def test_endpoint(name, path, params=None):
    print(f"\n[*] Testing {name} ({path})...")
    start_time = time.time()
    try:
        url = f"{BASE_URL}{path}"
        # Some endpoints require auth if they use Depends(get_current_user)
        # We'll try without auth first as we're testing on localhost
        response = requests.get(url, params=params, timeout=15)
        duration = time.time() - start_time
        
        print(f"    Status: {response.status_code}")
        print(f"    Time:   {duration:.2f}s")
        
        if response.status_code == 200:
            data = response.json()
            success = data.get('success', False)
            print(f"    Success Field: {success}")
            if success:
                items = data.get('data', [])
                if isinstance(items, list):
                    print(f"    Received {len(items)} items.")
                elif isinstance(items, dict):
                    print(f"    Received data: {list(items.keys())}")
            return True, duration
        else:
            print(f"    Error: {response.text[:100]}")
            return False, duration
    except Exception as e:
        print(f"    Exception: {e}")
        return False, 0

def run_suite():
    print("=== Executive AI Assistant: System Health Audit ===")
    
    results = []
    
    # 1. Dashboard Stats (Performance Test)
    results.append(test_endpoint("Dashboard Stats", "/api/dashboard/stats"))
    
    # 2. Calendar Events (Sync Test)
    results.append(test_endpoint("Calendar Events", "/api/calendar/events", params={"days": 7}))
    
    # 3. Documents/Attachments (Restoration Test)
    results.append(test_endpoint("Documents Page", "/api/attachments/all"))
    
    # 4. Business Threads (Core Logic Test)
    results.append(test_endpoint("Business Threads", "/api/threads"))
    
    print("\n" + "="*50)
    print("SUMMARY:")
    all_ok = all(r[0] for r in results)
    avg_speed = sum(r[1] for r in results) / len(results) if results else 0
    
    if all_ok:
        print("[SUCCESS] All core non-LLM systems are operational.")
    else:
        print("[WARNING] Some systems returned errors. Check logs.")
    
    print(f"Average Response Time: {avg_speed:.2f}s")
    
    if avg_speed < 1.0:
        print("[PERFORMANCE] Excellent. Caching is working.")
    elif avg_speed < 3.0:
        print("[PERFORMANCE] Acceptable.")
    else:
        print("[PERFORMANCE] Slow. Optimization or network sync might be needed.")

if __name__ == "__main__":
    run_suite()
