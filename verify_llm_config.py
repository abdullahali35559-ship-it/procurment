import os
from dotenv import load_dotenv
from models.pixtral_client import PixtralClient

load_dotenv()

def test_config():
    print("--- Verifying LLM Configuration ---")
    provider = os.getenv("LLM_PROVIDER")
    model = os.getenv("OPENROUTER_MODEL") or os.getenv("OPENAI_MODEL")
    api_key = os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENAI_API_KEY")
    
    print(f"Provider: {provider}")
    print(f"Model: {model}")
    print(f"API Key Found: {bool(api_key)}")
    
    if not api_key or "your_key" in api_key:
        print("[!] Warning: API Key is still placeholder. Please update .env")
        return

    client = PixtralClient()
    try:
        print("\nTesting LLM Response (this might take a few seconds)...")
        response = client.chat("System", "Say 'LLM Config OK' if you can read this.")
        print(f"Response: {response}")
    except Exception as e:
        print(f"[X] LLM Error: {e}")

if __name__ == "__main__":
    test_config()
