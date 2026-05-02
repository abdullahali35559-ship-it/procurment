import requests
import json

def check_api_for_emails():
    # Calling the local API
    url = "http://localhost:8000/api/emails"
    params = {"include_all": True}
    
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            emails = data.get("data", [])
            print(f"Total emails from API: {len(emails)}")
            
            # Look for IDs 190 and 191
            found_ids = [e.get("id") for e in emails]
            print(f"IDs 190 and 191 in results? 190: {190 in found_ids}, 191: {191 in found_ids}")
            
            # Print last 5 to see the order/dates
            print("\nFirst 5 emails from API:")
            for e in emails[:5]:
                print(f"  {e.get('received_at')} | {e.get('id')} | {e.get('subject')[:50]}")
                
            # Print target emails if found
            for e in emails:
                if e.get("id") in [190, 191]:
                    print(f"\n[FOUND] Email {e.get('id')}:")
                    print(json.dumps(e, indent=2))
        else:
            print(f"API Error: {response.status_code}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_api_for_emails()
