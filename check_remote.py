import requests

def check_remote():
    url = "http://192.168.1.3:11434/api/tags"
    print(f"Checking {url}...")
    try:
        res = requests.get(url, timeout=5)
        print(f"Status: {res.status_code}")
        if res.status_code == 200:
            print("Models:", res.json().get('models', []))
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_remote()
