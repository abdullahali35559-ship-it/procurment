import requests
import json

def check_ollama():
    platforms = ["http://localhost:11434", "https://ai.gcucsstudent.site"]
    
    for base in platforms:
        print(f"\n--- Checking {base} ---")
        try:
            # Check tags/models
            tags_res = requests.get(f"{base}/api/tags", timeout=5)
            if tags_res.status_code == 200:
                models = tags_res.json().get('models', [])
                print(f"[OK] Reachable. Found {len(models)} models:")
                for m in models:
                    print(f"  - {m['name']}")
                
                if models:
                    # Try a very simple chat with the first model
                    model_name = models[0]['name']
                    print(f"\n[2] Attempting simple chat with '{model_name}'...")
                    chat_payload = {
                        "model": model_name,
                        "messages": [{"role": "user", "content": "hi"}],
                        "stream": False
                    }
                    chat_res = requests.post(f"{base}/api/chat", json=chat_payload, timeout=30)
                    if chat_res.status_code == 200:
                        print("[SUCCESS] Chat API responded correctly.")
                        print(chat_res.json().get('message', {}).get('content'))
                    else:
                        print(f"[FAILED] Chat API returned {chat_res.status_code}: {chat_res.text}")
            else:
                print(f"[FAILED] Tags API returned {tags_res.status_code}")
        except Exception as e:
            print(f"[ERROR] Could not connect: {e}")

if __name__ == "__main__":
    check_ollama()
