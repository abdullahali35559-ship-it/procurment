import requests
import json

BASE_URL = "http://localhost:8000"

def verify():
    # 1. Check Tags API
    print("Checking /api/tags...")
    try:
        r = requests.get(f"{BASE_URL}/api/tags")
        print(f"Status: {r.status_code}")
        if r.status_code == 200:
            data = r.json()
            print(f"Format: {'success' in data and 'data' in data}")
            if 'data' in data:
                print(f"Tags Count: {len(data['data'])}")
        else:
            print(f"Error: {r.text}")
    except Exception as e:
        print(f"Connection failed: {e}")

    # 2. Check Threads API
    print("\nChecking /api/threads...")
    try:
        r = requests.get(f"{BASE_URL}/api/threads")
        print(f"Status: {r.status_code}")
        if r.status_code == 200:
            data = r.json()
            if 'data' in data:
                print(f"Threads Count: {len(data['data'])}")
                if len(data['data']) > 0:
                    print(f"First Thread 'tags' key: {'tags' in data['data'][0]}")
        else:
            print(f"Error: {r.text}")
    except Exception as e:
        print(f"Connection failed: {e}")

if __name__ == "__main__":
    verify()










#

INFO:     127.0.0.1:55602 - "GET /api/threads HTTP/1.1" 200 OK
INFO:     127.0.0.1:51170 - "GET /api/drafts HTTP/1.1" 200 OK
[Cache] Returning cached events for 1 days
INFO:     127.0.0.1:61043 - "GET /api/calendar/events?days=1 HTTP/1.1" 200 OK
INFO:     127.0.0.1:52937 - "GET /api/agent/status HTTP/1.1" 200 OK
Error in dashboard stats: name 'pending_replies' is not defined
INFO:     127.0.0.1:63656 - "GET /api/dashboard/stats HTTP/1.1" 200 OK
DEBUG AUTH: Received token length: 124
DEBUG AUTH: Received token length: 124
DEBUG AUTH: Received token length: 124
DEBUG AUTH: Received token length: 124
DEBUG AUTH: Successfully authenticated user: admin
DEBUG AUTH: Successfully authenticated user: admin
DEBUG AUTH: Successfully authenticated user: admin
DEBUG AUTH: Successfully authenticated user: admin
INFO:     127.0.0.1:55602 - "GET /api/threads HTTP/1.1" 200 OK
[Cache] Returning cached events for 1 days
INFO:     127.0.0.1:61043 - "GET /api/calendar/events?days=1 HTTP/1.1" 200 OK
Error in dashboard stats: name 'pending_replies' is not defined
INFO:     127.0.0.1:63656 - "GET /api/dashboard/stats HTTP/1.1" 200 OK
INFO:     127.0.0.1:51170 - "GET /api/drafts HTTP/1.1" 200 OK
DEBUG AUTH: Received token length: 124
DEBUG AUTH: Successfully authenticated user: admin
INFO:     127.0.0.1:62923 - "GET /api/threads HTTP/1.1" 200 OK
DEBUG AUTH: Received token length: 124
DEBUG AUTH: Successfully authenticated user: admin
INFO:     127.0.0.1:62923 - "GET /api/drafts HTTP/1.1" 200 OK
DEBUG AUTH: Received token length: 124
DEBUG AUTH: Successfully authenticated user: admin
[Cache] Returning cached events for 1 days
INFO:     127.0.0.1:62923 - "GET /api/calendar/events?days=1 HTTP/1.1" 200 OK
DEBUG AUTH: Received token length: 124
DEBUG AUTH: Successfully authenticated user: admin
Error in dashboard stats: name 'pending_replies' is not defined
INFO:     127.0.0.1:62923 - "GET /api/dashboard/stats HTTP/1.1" 200 OK
DEBUG AUTH: Received token length: 124
DEBUG AUTH: Successfully authenticated user: admin
INFO:     127.0.0.1:62923 - "GET /api/agent/status HTTP/1.1" 200 OK
DEBUG AUTH: Received token length: 124
DEBUG AUTH: Successfully authenticated user: admin
INFO:     127.0.0.1:62923 - "GET /api/threads HTTP/1.1" 200 OK
DEBUG AUTH: Received token length: 124
DEBUG AUTH: Successfully authenticated user: admin
INFO:     127.0.0.1:62923 - "GET /api/drafts HTTP/1.1" 200 OK
DEBUG AUTH: Received token length: 124
DEBUG AUTH: Successfully authenticated user: admin
[Cache] Returning cached events for 1 days
INFO:     127.0.0.1:62923 - "GET /api/calendar/events?days=1 HTTP/1.1" 200 OK
DEBUG AUTH: Received token length: 124
DEBUG AUTH: Successfully authenticated user: admin
Error in dashboard stats: name 'pending_replies' is not defined
INFO:     127.0.0.1:62923 - "GET /api/dashboard/stats HTTP/1.1" 200 OK
DEBUG AUTH: Received token length: 124
DEBUG AUTH: Successfully authenticated user: admin
INFO:     127.0.0.1:62923 - "GET /api/agent/status HTTP/1.1" 200 OK
DEBUG AUTH: Received token length: 124
DEBUG AUTH: Successfully authenticated user: admin
INFO:     127.0.0.1:62923 - "POST /api/process-emails HTTP/1.1" 200 OK
============================================================
EMAIL MONITORING - General Email Assistant
============================================================
Providers: gmail, outlook

CHECKING: GMAIL...
DEBUG AUTH: Received token length: 124
DEBUG AUTH: Received token length: 124
DEBUG AUTH: Received token length: 124
DEBUG AUTH: Received token length: 124
DEBUG AUTH: Successfully authenticated user: admin
DEBUG AUTH: Received token length: 124
DEBUG AUTH: Successfully authenticated user: admin
DEBUG AUTH: Successfully authenticated user: admin
DEBUG AUTH: Successfully authenticated user: admin
DEBUG AUTH: Successfully authenticated user: admin
INFO:     127.0.0.1:62923 - "GET /api/threads HTTP/1.1" 200 OK
INFO:     127.0.0.1:59919 - "GET /api/drafts HTTP/1.1" 200 OK
[Cache] Returning cached events for 1 days
INFO:     127.0.0.1:50579 - "GET /api/calendar/events?days=1 HTTP/1.1" 200 OK
Error in dashboard stats: name 'pending_replies' is not defined
INFO:     127.0.0.1:60639 - "GET /api/dashboard/stats HTTP/1.1" 200 OK
INFO:     127.0.0.1:58730 - "GET /api/agent/status HTTP/1.1" 200 OK
 Found 13 email(s)
DEBUG AUTH: Received token length: 124
DEBUG AUTH: Successfully authenticated user: admin
INFO:     127.0.0.1:58905 - "GET /api/agent/status HTTP/1.1" 200 OK
Found 13 new email(s).

Analyzing: Security alert...
=== GENERAL EMAIL ASSISTANT STARTED ===

Step 1: Analyzing actionability...
DEBUG: PixtralClient initialized with provider=pixtral, model=ai-agent:latest, key_found=False
DEBUG AUTH: Received token length: 124
DEBUG AUTH: Successfully authenticated user: admin
INFO:     127.0.0.1:58905 - "GET /api/agent/status HTTP/1.1" 200 OK
DEBUG AUTH: Received token length: 124
DEBUG AUTH: Successfully authenticated user: admin
INFO:     127.0.0.1:58905 - "GET /api/threads HTTP/1.1" 200 OK
DEBUG AUTH: Received token length: 124
DEBUG AUTH: Successfully authenticated user: admin
INFO:     127.0.0.1:58905 - "GET /api/drafts HTTP/1.1" 200 OK
DEBUG AUTH: Received token length: 124
DEBUG AUTH: Successfully authenticated user: admin
[Cache] Returning cached events for 1 days
INFO:     127.0.0.1:58905 - "GET /api/calendar/events?days=1 HTTP/1.1" 200 OK
DEBUG AUTH: Received token length: 124
DEBUG AUTH: Successfully authenticated user: admin
Error in dashboard stats: name 'pending_replies' is not defined
INFO:     127.0.0.1:58905 - "GET /api/dashboard/stats HTTP/1.1" 200 OK
DEBUG AUTH: Received token length: 124
DEBUG AUTH: Successfully authenticated user: admin
INFO:     127.0.0.1:58905 - "GET /api/agent/status HTTP/1.1" 200 OK
DEBUG AUTH: Received token length: 124
DEBUG AUTH: Successfully authenticated user: admin
INFO:     127.0.0.1:58905 - "GET /api/threads HTTP/1.1" 200 OK
DEBUG AUTH: Received token length: 124
DEBUG AUTH: Successfully authenticated user: admin
INFO:     127.0.0.1:58905 - "GET /api/drafts HTTP/1.1" 200 OK
DEBUG AUTH: Received token length: 124
DEBUG AUTH: Successfully authenticated user: admin
[Cache] Returning cached events for 1 days
INFO:     127.0.0.1:58905 - "GET /api/calendar/events?days=1 HTTP/1.1" 200 OK
DEBUG AUTH: Received token length: 124
DEBUG AUTH: Successfully authenticated user: admin
Error in dashboard stats: name 'pending_replies' is not defined
INFO:     127.0.0.1:58905 - "GET /api/dashboard/stats HTTP/1.1" 200 OK
DEBUG AUTH: Received token length: 124
DEBUG AUTH: Successfully authenticated user: admin
INFO:     127.0.0.1:58905 - "GET /api/agent/status HTTP/1.1" 200 OK
DEBUG AUTH: Received token length: 124
DEBUG AUTH: Successfully authenticated user: admin
INFO:     127.0.0.1:58905 - "GET /api/agent/status HTTP/1.1" 200 OK
DEBUG AUTH: Received token length: 124
DEBUG AUTH: Received token length: 124
DEBUG AUTH: Received token length: 124
DEBUG AUTH: Received token length: 124
DEBUG AUTH: Received token length: 124
DEBUG AUTH: Successfully authenticated user: admin
DEBUG AUTH: Successfully authenticated user: admin
DEBUG AUTH: Successfully authenticated user: admin
DEBUG AUTH: Successfully authenticated user: admin
DEBUG AUTH: Successfully authenticated user: admin
INFO:     127.0.0.1:58905 - "GET /api/threads HTTP/1.1" 200 OK
INFO:     127.0.0.1:59689 - "GET /api/drafts HTTP/1.1" 200 OK
Error in dashboard stats: name 'pending_replies' is not defined
INFO:     127.0.0.1:60247 - "GET /api/dashboard/stats HTTP/1.1" 200 OK
INFO:     127.0.0.1:51960 - "GET /api/agent/status HTTP/1.1" 200 OK
[Cache] Returning cached events for 1 days
INFO:     127.0.0.1:64202 - "GET /api/calendar/events?days=1 HTTP/1.1" 200 OK
DEBUG AUTH: Received token length: 124
DEBUG AUTH: Successfully authenticated user: admin
INFO:     127.0.0.1:64202 - "GET /api/agent/status HTTP/1.1" 200 OK
DEBUG AUTH: Received token length: 124
DEBUG AUTH: Successfully authenticated user: admin
INFO:     127.0.0.1:64202 - "GET /api/agent/status HTTP/1.1" 200 OK
DEBUG AUTH: Received token length: 124
DEBUG AUTH: Received token length: 124
DEBUG AUTH: Successfully authenticated user: admin
DEBUG AUTH: Successfully authenticated user: admin
INFO:     127.0.0.1:64202 - "GET /api/threads HTTP/1.1" 200 OK
INFO:     127.0.0.1:50773 - "GET /api/drafts HTTP/1.1" 200 OK
DEBUG AUTH: Received token length: 124
DEBUG AUTH: Received token length: 124
DEBUG AUTH: Successfully authenticated user: admin
[Cache] Returning cached events for 1 days
INFO:     127.0.0.1:64202 - "GET /api/calendar/events?days=1 HTTP/1.1" 200 OK
DEBUG AUTH: Successfully authenticated user: admin
Error in dashboard stats: name 'pending_replies' is not defined
INFO:     127.0.0.1:50773 - "GET /api/dashboard/stats HTTP/1.1" 200 OK
DEBUG AUTH: Received token length: 124
DEBUG AUTH: Received token length: 124
DEBUG AUTH: Successfully authenticated user: admin
DEBUG AUTH: Successfully authenticated user: admin
INFO:     127.0.0.1:64202 - "GET /api/agent/status HTTP/1.1" 200 OK
INFO:     127.0.0.1:50773 - "GET /api/threads HTTP/1.1" 200 OK
DEBUG AUTH: Received token length: 124
DEBUG AUTH: Received token length: 124
DEBUG AUTH: Successfully authenticated user: admin
DEBUG AUTH: Successfully authenticated user: admin
INFO:     127.0.0.1:64202 - "GET /api/drafts HTTP/1.1" 200 OK
[Cache] Returning cached events for 1 days
INFO:     127.0.0.1:50773 - "GET /api/calendar/events?days=1 HTTP/1.1" 200 OK
DEBUG AUTH: Received token length: 124
DEBUG AUTH: Successfully authenticated user: admin
Error in dashboard stats: name 'pending_replies' is not defined
INFO:     127.0.0.1:64202 - "GET /api/dashboard/stats HTTP/1.1" 200 OK
DEBUG AUTH: Received token length: 124
DEBUG AUTH: Successfully authenticated user: admin
INFO:     127.0.0.1:64202 - "GET /api/agent/status HTTP/1.1" 200 OK
DEBUG AUTH: Received token length: 124
DEBUG AUTH: Successfully authenticated user: admin
INFO:     127.0.0.1:64202 - "GET /api/agent/status HTTP/1.1" 200 OK
DEBUG AUTH: Received token length: 124
DEBUG AUTH: Received token length: 124
DEBUG AUTH: Received token length: 124
DEBUG AUTH: Received token length: 124
DEBUG AUTH: Received token length: 124
DEBUG AUTH: Successfully authenticated user: admin
DEBUG AUTH: Successfully authenticated user: admin
DEBUG AUTH: Successfully authenticated user: admin
DEBUG AUTH: Successfully authenticated user: admin
DEBUG AUTH: Successfully authenticated user: admin
INFO:     127.0.0.1:64202 - "GET /api/threads HTTP/1.1" 200 OK
[Cache] Returning cached events for 1 days
INFO:     127.0.0.1:58008 - "GET /api/calendar/events?days=1 HTTP/1.1" 200 OK
INFO:     127.0.0.1:58937 - "GET /api/drafts HTTP/1.1" 200 OK
Error in dashboard stats: name 'pending_replies' is not defined
INFO:     127.0.0.1:60783 - "GET /api/dashboard/stats HTTP/1.1" 200 OK
INFO:     127.0.0.1:62249 - "GET /api/agent/status HTTP/1.1" 200 OK
DEBUG AUTH: Received token length: 124
DEBUG AUTH: Received token length: 124
DEBUG AUTH: Received token length: 124
DEBUG AUTH: Received token length: 124
DEBUG AUTH: Successfully authenticated user: admin
DEBUG AUTH: Successfully authenticated user: admin
DEBUG AUTH: Successfully authenticated user: admin
DEBUG AUTH: Successfully authenticated user: admin
DEBUG AUTH: Received token length: 124
DEBUG AUTH: Successfully authenticated user: admin
INFO:     127.0.0.1:56841 - "GET /api/drafts HTTP/1.1" 200 OK
INFO:     127.0.0.1:54402 - "GET /api/agent/status HTTP/1.1" 200 OK
INFO:     127.0.0.1:57326 - "GET /api/threads HTTP/1.1" 200 OK
[Cache] Returning cached events for 1 days
INFO:     127.0.0.1:58751 - "GET /api/calendar/events?days=1 HTTP/1.1" 200 OK
Error in dashboard stats: name 'pending_replies' is not defined
INFO:     127.0.0.1:49804 - "GET /api/dashboard/stats HTTP/1.1" 200 OK
DEBUG AUTH: Received token length: 124
DEBUG AUTH: Received token length: 124
DEBUG AUTH: Received token length: 124
DEBUG AUTH: Received token length: 124
DEBUG AUTH: Successfully authenticated user: admin
DEBUG AUTH: Successfully authenticated user: admin
DEBUG AUTH: Successfully authenticated user: admin
DEBUG AUTH: Successfully authenticated user: admin
Error in dashboard stats: name 'pending_replies' is not defined
INFO:     127.0.0.1:49804 - "GET /api/dashboard/stats HTTP/1.1" 200 OK
INFO:     127.0.0.1:56841 - "GET /api/drafts HTTP/1.1" 200 OK
INFO:     127.0.0.1:54402 - "GET /api/threads HTTP/1.1" 200 OK
[Cache] Returning cached events for 1 days
INFO:     127.0.0.1:58751 - "GET /api/calendar/events?days=1 HTTP/1.1" 200 OK
DEBUG AUTH: Received token length: 124
DEBUG AUTH: Received token length: 124
DEBUG AUTH: Received token length: 124
DEBUG AUTH: Successfully authenticated user: admin
DEBUG AUTH: Received token length: 124
DEBUG AUTH: Successfully authenticated user: admin
DEBUG AUTH: Received token length: 124
DEBUG AUTH: Successfully authenticated user: admin
DEBUG AUTH: Successfully authenticated user: admin
DEBUG AUTH: Successfully authenticated user: admin
INFO:     127.0.0.1:58751 - "GET /api/threads HTTP/1.1" 200 OK
INFO:     127.0.0.1:57326 - "GET /api/agent/status HTTP/1.1" 200 OK
Error in dashboard stats: name 'pending_replies' is not defined
INFO:     127.0.0.1:49804 - "GET /api/dashboard/stats HTTP/1.1" 200 OK
[Cache] Returning cached events for 1 days
INFO:     127.0.0.1:56841 - "GET /api/calendar/events?days=1 HTTP/1.1" 200 OK
INFO:     127.0.0.1:54402 - "GET /api/drafts HTTP/1.1" 200 OK
❌ JUNK EMAIL detected. Confidence: 0.95. IGNORED.
[OK] Email moved to processed label and marked as read
   [--] Junk email skipped and moved to processed.

Analyzing: ...
=== GENERAL EMAIL ASSISTANT STARTED ===

Step 1: Analyzing actionability...
DEBUG: PixtralClient initialized with provider=pixtral, model=ai-agent:latest, key_found=False
DEBUG AUTH: Received token length: 124
DEBUG AUTH: Successfully authenticated user: admin
INFO:     127.0.0.1:50390 - "GET /api/agent/status HTTP/1.1" 200 OK
DEBUG AUTH: Received token length: 124
DEBUG AUTH: Successfully authenticated user: admin
INFO:     127.0.0.1:50390 - "GET /api/agent/status HTTP/1.1" 200 OK
❌ JUNK EMAIL detected. Confidence: 0.95. IGNORED.
[OK] Email moved to processed label and marked as read
   [--] Junk email skipped and moved to processed.

Analyzing: 5 days left on your trial...
=== GENERAL EMAIL ASSISTANT STARTED ===

Step 1: Analyzing actionability...
DEBUG: PixtralClient initialized with provider=pixtral, model=ai-agent:latest, key_found=False
DEBUG AUTH: Received token length: 124
DEBUG AUTH: Successfully authenticated user: admin
INFO:     127.0.0.1:50390 - "GET /api/threads HTTP/1.1" 200 OK
DEBUG AUTH: Received token length: 124
DEBUG AUTH: Successfully authenticated user: admin
INFO:     127.0.0.1:50390 - "GET /api/drafts HTTP/1.1" 200 OK
DEBUG AUTH: Received token length: 124
DEBUG AUTH: Successfully authenticated user: admin
[Cache] Returning cached events for 1 days
INFO:     127.0.0.1:50390 - "GET /api/calendar/events?days=1 HTTP/1.1" 200 OK
DEBUG AUTH: Received token length: 124
DEBUG AUTH: Successfully authenticated user: admin
Error in dashboard stats: name 'pending_replies' is not defined
INFO:     127.0.0.1:50390 - "GET /api/dashboard/stats HTTP/1.1" 200 OK
DEBUG AUTH: Received token length: 124
DEBUG AUTH: Successfully authenticated user: admin
INFO:     127.0.0.1:50390 - "GET /api/agent/status HTTP/1.1" 200 OK
DEBUG AUTH: Received token length: 124
DEBUG AUTH: Successfully authenticated user: admin
INFO:     127.0.0.1:50390 - "GET /api/threads HTTP/1.1" 200 OK
DEBUG AUTH: Received token length: 124
DEBUG AUTH: Successfully authenticated user: admin
INFO:     127.0.0.1:50390 - "GET /api/drafts HTTP/1.1" 200 OK
DEBUG AUTH: Received token length: 124
DEBUG AUTH: Successfully authenticated user: admin
[Cache] Returning cached events for 1 days
INFO:     127.0.0.1:50390 - "GET /api/calendar/events?days=1 HTTP/1.1" 200 OK
DEBUG AUTH: Received token length: 124
DEBUG AUTH: Successfully authenticated user: admin
Error in dashboard stats: name 'pending_replies' is not defined
INFO:     127.0.0.1:50390 - "GET /api/dashboard/stats HTTP/1.1" 200 OK
DEBUG AUTH: Received token length: 124
DEBUG AUTH: Successfully authenticated user: admin
INFO:     127.0.0.1:50390 - "GET /api/agent/status HTTP/1.1" 200 OK
❌ JUNK EMAIL detected. Confidence: 0.95. IGNORED.
[OK] Email moved to processed label and marked as read
   [--] Junk email skipped and moved to processed.

Analyzing: Security alert...
=== GENERAL EMAIL ASSISTANT STARTED ===

Step 1: Analyzing actionability...
DEBUG: PixtralClient initialized with provider=pixtral, model=ai-agent:latest, key_found=False
DEBUG AUTH: Received token length: 124
DEBUG AUTH: Successfully authenticated user: admin
INFO:     127.0.0.1:50390 - "GET /api/agent/status HTTP/1.1" 200 OK
❌ JUNK EMAIL detected. Confidence: 0.95. IGNORED.
DEBUG AUTH: Received token length: 124
DEBUG AUTH: Received token length: 124
DEBUG AUTH: Received token length: 124
DEBUG AUTH: Successfully authenticated user: admin
DEBUG AUTH: Successfully authenticated user: admin
DEBUG AUTH: Successfully authenticated user: admin
DEBUG AUTH: Received token length: 124
DEBUG AUTH: Received token length: 124
DEBUG AUTH: Successfully authenticated user: admin
DEBUG AUTH: Successfully authenticated user: admin
INFO:     127.0.0.1:50390 - "GET /api/threads HTTP/1.1" 200 OK
INFO:     127.0.0.1:53954 - "GET /api/drafts HTTP/1.1" 200 OK
[Cache] Returning cached events for 1 days
INFO:     127.0.0.1:53168 - "GET /api/calendar/events?days=1 HTTP/1.1" 200 OK
Error in dashboard stats: name 'pending_replies' is not defined
INFO:     127.0.0.1:49672 - "GET /api/dashboard/stats HTTP/1.1" 200 OK
INFO:     127.0.0.1:56696 - "GET /api/agent/status HTTP/1.1" 200 OK
[OK] Email moved to processed label and marked as read
   [--] Junk email skipped and moved to processed.

Analyzing: New app(s) connected to your Microsoft account...
=== GENERAL EMAIL ASSISTANT STARTED ===

Step 1: Analyzing actionability...
DEBUG: PixtralClient initialized with provider=pixtral, model=ai-agent:latest, key_found=False
DEBUG AUTH: Received token length: 124
DEBUG AUTH: Successfully authenticated user: admin
INFO:     127.0.0.1:56696 - "GET /api/agent/status HTTP/1.1" 200 OK
❌ JUNK EMAIL detected. Confidence: 0.95. IGNORED.
[OK] Email moved to processed label and marked as read
   [--] Junk email skipped and moved to processed.

Analyzing: New app(s) connected to your Microsoft account...
=== GENERAL EMAIL ASSISTANT STARTED ===

Step 1: Analyzing actionability...
DEBUG: PixtralClient initialized with provider=pixtral, model=ai-agent:latest, key_found=False
DEBUG AUTH: Received token length: 124
DEBUG AUTH: Successfully authenticated user: admin
INFO:     127.0.0.1:49401 - "GET /api/agent/status HTTP/1.1" 200 OK
DEBUG AUTH: Received token length: 124
DEBUG AUTH: Successfully authenticated user: admin
INFO:     127.0.0.1:49401 - "GET /api/threads HTTP/1.1" 200 OK
DEBUG AUTH: Received token length: 124
DEBUG AUTH: Successfully authenticated user: admin
INFO:     127.0.0.1:49401 - "GET /api/drafts HTTP/1.1" 200 OK
DEBUG AUTH: Received token length: 124
DEBUG AUTH: Successfully authenticated user: admin
[Cache] Returning cached events for 1 days
INFO:     127.0.0.1:49401 - "GET /api/calendar/events?days=1 HTTP/1.1" 200 OK
DEBUG AUTH: Received token length: 124
DEBUG AUTH: Successfully authenticated user: admin
Error in dashboard stats: name 'pending_replies' is not defined
INFO:     127.0.0.1:49401 - "GET /api/dashboard/stats HTTP/1.1" 200 OK
DEBUG AUTH: Received token length: 124
DEBUG AUTH: Successfully authenticated user: admin
INFO:     127.0.0.1:49401 - "GET /api/agent/status HTTP/1.1" 200 OK
DEBUG AUTH: Received token length: 124
DEBUG AUTH: Successfully authenticated user: admin
❌ JUNK EMAIL detected. Confidence: 0.95. IGNORED.
INFO:     127.0.0.1:49401 - "GET /api/threads HTTP/1.1" 200 OK
DEBUG AUTH: Received token length: 124
DEBUG AUTH: Successfully authenticated user: admin
INFO:     127.0.0.1:49401 - "GET /api/drafts HTTP/1.1" 200 OK
DEBUG AUTH: Received token length: 124
DEBUG AUTH: Successfully authenticated user: admin
[Cache] Returning cached events for 1 days
INFO:     127.0.0.1:49401 - "GET /api/calendar/events?days=1 HTTP/1.1" 200 OK
DEBUG AUTH: Received token length: 124
DEBUG AUTH: Successfully authenticated user: admin
Error in dashboard stats: name 'pending_replies' is not defined
INFO:     127.0.0.1:49401 - "GET /api/dashboard/stats HTTP/1.1" 200 OK
[OK] Email moved to processed label and marked as read
   [--] Junk email skipped and moved to processed.

Analyzing: Microsoft account security info was added...
=== GENERAL EMAIL ASSISTANT STARTED ===

Step 1: Analyzing actionability...
DEBUG: PixtralClient initialized with provider=pixtral, model=ai-agent:latest, key_found=False
DEBUG AUTH: Received token length: 124
DEBUG AUTH: Successfully authenticated user: admin
INFO:     127.0.0.1:49401 - "GET /api/agent/status HTTP/1.1" 200 OK
❌ JUNK EMAIL detected. Confidence: 0.95. IGNORED.
[OK] Email moved to processed label and marked as read
   [--] Junk email skipped and moved to processed.

Analyzing: Security alert...
=== GENERAL EMAIL ASSISTANT STARTED ===

Step 1: Analyzing actionability...
DEBUG: PixtralClient initialized with provider=pixtral, model=ai-agent:latest, key_found=False
DEBUG AUTH: Received token length: 124
DEBUG AUTH: Successfully authenticated user: admin
INFO:     127.0.0.1:49401 - "GET /api/agent/status HTTP/1.1" 200 OK
❌ JUNK EMAIL detected. Confidence: 0.95. IGNORED.
[OK] Email moved to processed label and marked as read
   [--] Junk email skipped and moved to processed.

Analyzing: Time to pick your plan...
=== GENERAL EMAIL ASSISTANT STARTED ===

Step 1: Analyzing actionability...
DEBUG: PixtralClient initialized with provider=pixtral, model=ai-agent:latest, key_found=False
❌ JUNK EMAIL detected. Confidence: 0.95. IGNORED.
[OK] Email moved to processed label and marked as read
   [--] Junk email skipped and moved to processed.
[OK] Disconnected from Gmail API

CHECKING: OUTLOOK...
DEBUG AUTH: Received token length: 124
DEBUG AUTH: Received token length: 124
DEBUG AUTH: Received token length: 124
DEBUG AUTH: Received token length: 124
DEBUG AUTH: Successfully authenticated user: admin
DEBUG AUTH: Received token length: 124
DEBUG AUTH: Successfully authenticated user: admin
DEBUG AUTH: Successfully authenticated user: admin
DEBUG AUTH: Successfully authenticated user: admin
DEBUG AUTH: Successfully authenticated user: admin
INFO:     127.0.0.1:63568 - "GET /api/threads HTTP/1.1" 200 OK
INFO:     127.0.0.1:50851 - "GET /api/drafts HTTP/1.1" 200 OK
[Cache] Returning cached events for 1 days
INFO:     127.0.0.1:57497 - "GET /api/calendar/events?days=1 HTTP/1.1" 200 OK
Error in dashboard stats: name 'pending_replies' is not defined
INFO:     127.0.0.1:57315 - "GET /api/dashboard/stats HTTP/1.1" 200 OK
INFO:     127.0.0.1:53349 - "GET /api/agent/status HTTP/1.1" 200 OK
[X] Token load/refresh error: API does not accept frozenset({'profile', 'openid', 'offline_access'}) value as user-provided scopes
[X] Error connecting to Graph API: Error loading OAuth token: API does not accept frozenset({'profile', 'openid', 'offline_access'}) value as user-provided scopes

Batch processing complete.
#