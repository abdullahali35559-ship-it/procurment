"""
Test Pixtral LLM connection
"""

import sys
sys.path.append('.')

from models.pixtral_client import PixtralClient

def test_pixtral():
    """Test Pixtral connection and basic functionality"""
    
    print("Testing Pixtral connection...")
    
    client = PixtralClient()
    
    # Test connection
    if not client.test_connection():
        print("❌ Pixtral not responding!")
        print(f"Make sure Pixtral is running at: {client.base_url}")
        return False
    
    print("✅ Pixtral connected!")
    
    # Test generation
    print("\nTesting generation...")
    response = client.generate(
        system_prompt="You are a helpful assistant.",
        user_prompt="Say 'Hello from Procurement Agent!' in 5 words or less."
    )
    
    print(f"✅ Response: {response}")
    
    print("\n✅ All tests passed!")
    return True

if __name__ == "__main__":
    test_pixtral()
