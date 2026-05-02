"""
Test Pixtral Connection
Quick script to verify Pixtral LLM connectivity
"""
import requests
import sys

def test_connection(url):
    """Test if Pixtral server is accessible"""
    print(f"Testing connection to: {url}")
    try:
        response = requests.get(f"{url}/api/tags", timeout=5)
        if response.status_code == 200:
            print("✅ Connection successful!")
            print(f"Response: {response.json()}")
            return True
        else:
            print(f"❌ Server responded with status: {response.status_code}")
            return False
    except requests.exceptions.Timeout:
        print("❌ Connection timeout - server not responding")
        return False
    except requests.exceptions.ConnectionError as e:
        print(f"❌ Connection error: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    print("=== Pixtral Connection Test ===\n")
    
    # Test different URLs
    urls_to_test = [
        "http://192.168.1.3:11434",  # Network IP
        "http://localhost:11434",     # Localhost
        "http://127.0.0.1:11434",     # Loopback IP
    ]
    
    for url in urls_to_test:
        test_connection(url)
        print()
    
    print("\nIf all tests failed, check:")
    print("1. Is Ollama/Pixtral running? (docker ps)")
    print("2. Is firewall blocking port 11434?")
    print("3. Is the IP address correct?")
