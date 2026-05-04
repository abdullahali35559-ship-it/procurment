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
    """Bulletproof High-Performance Procurement Assistant"""
    
    def __init__(self, db: Session, user: Optional[User] = None):
        self.db = db
        self.user = user
        self.llm = PixtralClient()
        self.knowledge_base = self._load_knowledge_base()

    def _load_knowledge_base(self) -> str:
        """Loads knowledge base using absolute paths to avoid directory issues"""
        try:
            # Use absolute path relative to this file
            current_dir = os.path.dirname(os.path.abspath(__file__)) # agents/executive
            base_dir = os.path.dirname(os.path.dirname(current_dir)) # root
            kb_path = os.path.join(base_dir, 'knowledge', 'abdex_data.json')
            
            if os.path.exists(kb_path):
                with open(kb_path, 'r', encoding='utf-8') as f:
                    return f.read()
        except Exception as e:
            print(f"KB Load Error: {e}")
        return ""

    def answer_query(self, query: str, conversation_id: Optional[int] = None, mode: str = 'enterprise') -> str:
        """Turbo-charged and Accurate Procurement Assistant"""
        
        # 1. Background persistence
        if conversation_id:
            user_msg = AssistantChat(conversation_id=conversation_id, role='user', content=query)
            self.db.add(user_msg)
            self.db.commit()

        q_low = query.lower()
        
        # 2. FAST SMART SCAN (JSON First)
        kb_matches = []
        if self.knowledge_base and mode != 'general':
            try:
                data = json.loads(self.knowledge_base)
                keywords = [w for w in q_low.replace('-', ' ').split() if len(w) > 2]
                
                def is_match(item):
                    text = (item.get('name', '') + " " + item.get('description', '')).lower()
                    # Check for direct code matches (like 588N, CR2)
                    for k in keywords:
                        if k in text: return True
                    return False

                # Scan Services
                for s in data.get('services', []):
                    if is_match(s): kb_matches.append(s)
                # Scan Products
                for cat in data.get('product_categories', []):
                    for sub in cat.get('subcategories', []):
                        for p in sub.get('products', []):
                            if is_match(p): kb_matches.append(p)
            except: pass

        # 3. CONTEXT SELECTION (Speed Optimization)
        # Skip slow DB search for clear product queries
        business_context = ""
        is_business_intel = any(w in q_low for w in ['email', 'said', 'told', 'message', 'contract', 'file', 'abdullah'])
        if is_business_intel or (not kb_matches and not any(w in q_low for w in ['hose', 'parker', 'gates', 'uniflex', 'abdex'])):
            business_context = self._retrieve_context(query)

        # 4. PROMPT CONSTRUCTION
        kb_injection = json.dumps(kb_matches[:5], indent=2) if kb_matches else ""
        
        system_prompt = f"""
            YOU ARE THE ABDEX INDUSTRIES CHIEF OF STAFF.
            
            STRICT RULES:
            - PRODUCT FOUND: You MUST show Image and Link. 
            - FORMAT: ![Product](URL) and [View Product Details ↗](URL)
            - TONE: Executive, polished, and INSTANT.
        """
        
        user_prompt = f"""
            QUERY: {query}
            [KNOWLEDGE BASE MATCHES]: {kb_injection}
            [BUSINESS CONTEXT]: {business_context}
            
            INSTRUCTION: If matches are found, provide their details with Images and Links. If not found, admit it professionally.
        """

        # 5. GENERATE
        response = self.llm.generate(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=0.0
        )
        
        if isinstance(response, dict):
            reply = response.get('response') or response.get('text') or response.get('answer') or str(response)
        else:
            reply = str(response)
        
        reply = ResponseGuard.sanitize(reply.strip())

        if conversation_id:
            assistant_msg = AssistantChat(conversation_id=conversation_id, role='assistant', content=reply)
            self.db.add(assistant_msg)
            self.db.commit()
            
        return reply

    def _retrieve_context(self, query: str) -> str:
        """Lightweight search for business context"""
        try:
            import re
            keywords = [k.strip() for k in re.sub(r'[^\w\s]', '', query).lower().split() if len(k) > 4]
            if not keywords: return ""
            search_filter = or_(*[Email.subject.ilike(f"%{k}%") for k in keywords])
            matches = self.db.query(Email).filter(search_filter).limit(3).all()
            return "\n".join([f"Email: {m.subject} | Body: {m.body[:150]}" for m in matches])
        except: return ""
