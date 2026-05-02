import sys
import os

# Add project root to sys.path
project_root = os.getcwd()
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from models.pixtral_client import PixtralClient

def test():
    print("--- Executive AI Assistant: LLM Connectivity Test ---")
    try:
        client = PixtralClient()
        
        print(f"[*] Provider: {client.provider}")
        print(f"[*] Model:    {client.model}")
        print(f"[*] Endpoint: {client.base_url}")
        
        print("\n[1] Testing connection to LLM server...")
        connected = client.test_connection()
        
        if not connected and client.provider == "pixtral":
            print("[!] Connection to configured IP failed. Trying localhost fallback...")
            client.base_url = "http://localhost:11434"
            connected = client.test_connection()
            
        if connected:
            print("[OK] LLM Server is reachable.")
            
            print("\n[2] Testing generation (Pixtral/Mistral)...")
            try:
                response = client.chat(
                    system_prompt="You are a helpful executive assistant. Respond with a JSON object containing a 'status' field set to 'online'.",
                    user_prompt="Status check."
                )
                print("[OK] Generation successful. Result:")
                print(response)
                
                if isinstance(response, dict) and response.get('status') == 'online':
                    print("\n[SUCCESS] LLM is fully operational and following system instructions.")
                else:
                    print("\n[WARNING] LLM responded but formatting might be unexpected.")
            except Exception as e:
                print(f"[ERROR] Generation failed: {e}")
        else:
            print("[FAILED] LLM Server is NOT reachable.")
            print("Please ensure your Ollama server is running and the URL in config/settings.py is correct.")
            
    except Exception as e:
        print(f"[CRITICAL ERROR] Failed to initialize LLM client: {e}")

if __name__ == "__main__":
    test()
