import requests
import json
import os
import time
from typing import Dict, Any, List, Optional

class PixtralClient:
    """Client for interacting with LLMs (Pixtral via Ollama or Claude via OpenRouter)"""
    
    _session = None

    def __init__(self):
        from config.settings import LLM_PROVIDER
        self.provider = LLM_PROVIDER
        
        if self.provider == "openrouter":
            from config.settings import OPENROUTER_URL, OPENROUTER_MODEL, OPENROUTER_API_KEY
            self.base_url = OPENROUTER_URL
            self.model = OPENROUTER_MODEL
            self.api_key = OPENROUTER_API_KEY
        elif self.provider == "openai":
            self.base_url = "https://api.openai.com/v1"
            self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
            self.api_key = os.getenv("OPENAI_API_KEY")
        else:
            from config.settings import PIXTRAL_URL, PIXTRAL_MODEL
            self.base_url = PIXTRAL_URL
            self.model = PIXTRAL_MODEL
            self.api_key = os.getenv('PIXTRAL_API_KEY', None)
        
        print(f"DEBUG: PixtralClient initialized with provider={self.provider}, model={self.model}, key_found={bool(self.api_key)}")
        
        if PixtralClient._session is None:
            PixtralClient._session = requests.Session()
        self.session = PixtralClient._session
    
    def generate(self, 
                 system_prompt: str, 
                 user_prompt: str, 
                 temperature: float = 0.1,
                 examples: Optional[List[Dict]] = None) -> Dict[str, Any]:
        """
        Generate response from configured LLM
        """
        
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add examples as history if provided
        if examples:
            for ex in examples:
                messages.append({"role": "user", "content": json.dumps(ex['input'], ensure_ascii=False)})
                messages.append({"role": "assistant", "content": json.dumps(ex['output'], ensure_ascii=False)})
        
        messages.append({"role": "user", "content": user_prompt})

        headers = {
            "HTTP-Referer": "https://github.com/Procurement-Agent", # Required by OpenRouter
            "X-Title": "Procurement Agent Tool"
        }
        if self.api_key:
            headers['Authorization'] = f'Bearer {self.api_key}'
        
        max_retries = 3
        retry_delay = 5  # Base delay for free tier rate limits
        
        for attempt in range(max_retries):
            try:
                if self.provider == "openrouter" or self.provider == "openai":
                    url = f"{self.base_url}/chat/completions"
                    payload = {
                        "model": self.model,
                        "messages": messages,
                        "temperature": temperature
                    }
                else:
                    url = f"{self.base_url}/api/chat"
                    payload = {
                        "model": self.model,
                        "messages": messages,
                        "temperature": temperature,
                        "stream": False,
                        "format": "json",
                        "options": {"num_predict": 1000}
                    }

                # Add a small delay only during retries to avoid hitting rate limits again
                if attempt > 0:
                    time.sleep(retry_delay * (attempt + 1))

                response = self.session.post(url, json=payload, headers=headers, timeout=120)
                
                # Handle rate limits
                if response.status_code == 429:
                    print(f"   [!] Rate limit (429). Retrying in {retry_delay * 2}s... (Attempt {attempt+1}/{max_retries})")
                    time.sleep(retry_delay * 2)
                    continue
                
                response.raise_for_status()
                
                result = response.json()
                
                if self.provider == "openrouter" or self.provider == "openai":
                    response_text = result['choices'][0]['message']['content']
                else:
                    message_obj = result.get('message', {})
                    response_text = message_obj.get('content', result.get('response', ''))
                
                # Try to parse as JSON
                try:
                    cleaned_text = response_text.strip()
                    if cleaned_text.startswith('```json'):
                        cleaned_text = cleaned_text[7:]
                    if cleaned_text.startswith('```'):
                        cleaned_text = cleaned_text[3:]
                    if cleaned_text.endswith('```'):
                        cleaned_text = cleaned_text[:-3]
                    return json.loads(cleaned_text.strip())
                except json.JSONDecodeError:
                    import re
                    json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                    if json_match:
                        try: return json.loads(json_match.group())
                        except: pass
                    return {"response": response_text, "error": "Could not parse as JSON"}
                    
            except Exception as e:
                # Retry on connection errors or 5xx
                if attempt < max_retries - 1 and ("429" in str(e) or "5" in str(e) or "Timeout" in str(e)):
                    print(f"   [!] LLM Attempt {attempt+1} failed: {e}. Retrying...")
                    time.sleep(retry_delay * (attempt + 1))
                    continue
                
                print(f"LLM API Error: {e}")
                raise Exception(f"LLM Provider ({self.provider}) error: {str(e)}")

    def chat(self, system_prompt: str, user_prompt: str, temperature: float = 0.7) -> Dict[str, Any]:
        """Simple chat interface"""
        return self.generate(system_prompt, user_prompt, temperature)

    def test_connection(self) -> bool:
        """Test if LLM is responding"""
        try:
            if self.provider == "openrouter":
                return self.api_key is not None and len(self.api_key) > 5
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False
