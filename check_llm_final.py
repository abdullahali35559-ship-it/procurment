import requests

def check_cloud():
    url = "https://ai.gcucsstudent.site/api/tags"
    print(f"Checking {url}...")
    try:
        res = requests.get(url, timeout=10)
        print(f"Cloud Status: {res.status_code}")
        if res.status_code == 200:
            print("Cloud Models:", res.json().get('models', []))
    except Exception as e:
        print(f"Cloud Error: {e}")

def check_local():
    url = "http://localhost:11434/api/tags"
    print(f"\nChecking {url}...")
    try:
        res = requests.get(url, timeout=5)
        print(f"Local Status: {res.status_code}")
        if res.status_code == 200:
            models = res.json().get('models', [])
            print(f"Local Models Count: {len(models)}")
            for m in models:
                print(f" - {m.get('name')}")
    except Exception as e:
        print(f"Local Error: {e}")

if __name__ == "__main__":
    check_cloud()
    check_local()
