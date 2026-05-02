import requests
import os
import json
from dotenv import load_dotenv

load_dotenv()

def test_new_llm():
    url = os.getenv('PIXTRAL_URL')
    model = os.getenv('PIXTRAL_MODEL')
    print(f"Testing New LLM Endpoint: {url}")
    print(f"Model: {model}")
    
    chat_url = f"{url}/api/chat"
    data = {
        "model": model,
        "messages": [
            {"role": "user", "content": "Hello, are you online? Please reply with 'ONLINE'"}
        ],
        "stream": False
    }
    
    try:
        response = requests.post(chat_url, json=data, timeout=30)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            content = result.get('message', {}).get('content', '')
            print(f"Response: {content}")
            if "ONLINE" in content.upper():
                print("✅ Connection Successful!")
                return True
            else:
                print("⚠️ Unexpected response content.")
        else:
            print(f"❌ Error: {response.text}")
    except Exception as e:
        print(f"❌ Failed to connect: {e}")
    return False

if __name__ == "__main__":
    test_new_llm()
