import requests
import os
from dotenv import load_dotenv

load_dotenv()

def test_url(url, name):
    print(f"Testing {name}: {url}...")
    try:
        # Test /api/tags which usually lists models
        response = requests.get(f"{url}/api/tags", timeout=5)
        print(f"  Status: {response.status_code}")
        if response.status_code == 200:
            print(f"  Models: {response.json().get('models', [])}")
            return True
        else:
            print(f"  Error: {response.text[:100]}")
    except Exception as e:
        print(f"  Failed: {e}")
    return False

# Check remote URL from .env
remote_url = os.getenv('PIXTRAL_URL')
test_url(remote_url, "Remote Ollama")

# Check local URL
test_url("http://localhost:11434", "Local Ollama")
