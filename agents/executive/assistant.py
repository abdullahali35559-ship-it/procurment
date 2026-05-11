import os
import json
from sqlalchemy.orm import Session
from sqlalchemy import or_, desc, String
from datetime import datetime
from database.models import Email, Thread, Attachment, AssistantChat, User
from models.pixtral_client import PixtralClient
from typing import List, Dict, Optional
from api.utils.security import ResponseGuard

class ExecutiveAssistant:
    """Official Abdex Industries Assistant - High Reliability v5"""
    
    def __init__(self, db: Session, user: Optional[User] = None):
        self.db = db
        self.user = user
        self.llm = PixtralClient()
        self.kb = self._load_knowledge_base()

    def _load_knowledge_base(self) -> dict:
        try:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            kb_path = os.path.join(base_dir, 'knowledge', 'abdex_data.json')
            if os.path.exists(kb_path):
                with open(kb_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"KB Load Error: {e}")
        return {}

    def answer_query(self, query: str, conversation_id: Optional[int] = None, mode: str = 'enterprise') -> str:
        if conversation_id:
            user_msg = AssistantChat(conversation_id=conversation_id, role='user', content=query)
            self.db.add(user_msg)
            self.db.commit()

        q_low = query.lower().strip()
        
        # 1. GREETING CHECK
        greetings = ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening']
        if q_low in greetings or len(q_low) < 3:
            reply = "Welcome to Abdex Industries. I'm your fluid transfer specialist. How can I help you today?"
            if conversation_id:
                ai_msg = AssistantChat(conversation_id=conversation_id, role='assistant', content=reply)
                self.db.add(ai_msg)
                self.db.commit()
            return reply

        # 2. ENHANCED SEARCH LOGIC (SKU & CONTACT AWARE)
        company_info = self.kb.get('company', {})
        query_words = set(query.lower().replace("|", " ").replace("-", " ").split())
        kb_matches = []
        
        # Priority 1: If asking for contact info
        if any(word in ["contact", "phone", "email", "address", "number", "location", "call", "reach"] for word in query_words):
            kb_matches.append({"type": "contact_info", "data": company_info.get('contacts', company_info.get('contact', {}))})

        # Search Services
        for service in self.kb.get('services', []):
            search_pool = (service['name'] + " " + service.get('description', '')).lower()
            if any(word in search_pool for word in query_words):
                kb_matches.append(service)
        
        # Search Categories and Products
        for cat_name, category in self.kb.get('product_categories', {}).items():
            if any(word in cat_name.lower() for word in query_words):
                kb_matches.append({"type": "category", "name": cat_name, "description": category.get('description', '')})

            for product in category.get('products', []):
                search_pool = (product['name'] + " " + product.get('sku', '') + " " + product.get('description', '') + " " + " ".join(product.get('tags', []))).lower()
                if any(word in search_pool for word in query_words if len(word) > 2):
                    product['category'] = cat_name
                    kb_matches.append(product)

        context_str = f"Company Profile: {json.dumps(company_info)}\n\nRelevant Data:\n" + json.dumps(kb_matches[:15], indent=2)

        # 3. STRICT PROFESSIONAL TECHNICAL PROMPT (WITH HARDCODED CONTACTS)
        system_prompt = f"""
            You are the Official Abdex Industries AI Assistant.
            
            BUSINESS CONTACT INFORMATION (SHARE ONLY IF ASKED OR PRODUCT NOT FOUND):
            - Australia (Melbourne): +61 (0) 3 9796 3044 | sales@abdex.com.au
            - Australia (Perth): +61 (0) 8 9418 3044 | sales@abdex.com.au
            - Australia (Brisbane): +61 (0) 7 3185 2788 | sales@abdex.com.au
            - United Kingdom: +44 (0) 1525 377 770 | sales@abdex.co.uk
            - Singapore: +65 9753 7478 | sales@abdex.sg

            STRICT RULES:
            1. GREETINGS: If the user says "Hello", "Hi", etc., respond professionally like "Hello! I am the Abdex Technical Assistant. How can I help you with our products or services today?". DO NOT show contact info for a simple hello.
            2. CONTACT REQUESTS: If asked for contact, phone, or address, share the information above.
            3. TECHNICAL SPECS: ONLY use the provided 'Relevant Data'. If an item is missing, then point them to the contact info.
            
            4. FORMATTING (Clean List):
               **[Number]. [Name]**: [Technical Description]. More details can be found [here](PAGE_URL).
               <div style="margin:10px 0;"><img src="/api/image-proxy?url=IMAGE_URL" style="max-width:100%; border-radius:15px; box-shadow:0 4px 12px rgba(0,0,0,0.1); display:block;"></div>
            
            5. TONE: Professional and precise.
            
            Context Data:
            {context_str}
            """
        
        user_prompt = f"Technical Request: {query}"

        # 4. GENERATION
        response = self.llm.generate(system_prompt=system_prompt, user_prompt=user_prompt)
        
        if isinstance(response, dict):
            reply = response.get('response') or response.get('text') or str(response)
        else:
            reply = str(response)
            
        reply = reply.strip()
        
        if conversation_id:
            ai_msg = AssistantChat(conversation_id=conversation_id, role='assistant', content=reply)
            self.db.add(ai_msg)
            self.db.commit()
            
        return reply

    def _retrieve_context(self, query: str) -> str:
        return ""
