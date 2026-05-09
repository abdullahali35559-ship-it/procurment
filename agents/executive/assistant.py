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
    """Ultra-Precise High-Performance Procurement Assistant"""
    
    def __init__(self, db: Session, user: Optional[User] = None):
        self.db = db
        self.user = user
        self.llm = PixtralClient()
        self.knowledge_base = self._load_knowledge_base()

    def _load_knowledge_base(self) -> str:
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            base_dir = os.path.dirname(os.path.dirname(current_dir))
            kb_path = os.path.join(base_dir, 'knowledge', 'abdex_data.json')
            if os.path.exists(kb_path):
                with open(kb_path, 'r', encoding='utf-8') as f:
                    return f.read()
        except Exception as e:
            print(f"KB Load Error: {e}")
        return ""

    def answer_query(self, query: str, conversation_id: Optional[int] = None, mode: str = 'enterprise') -> str:
        if conversation_id:
            user_msg = AssistantChat(conversation_id=conversation_id, role='user', content=query)
            self.db.add(user_msg)
            self.db.commit()

        q_low = query.lower().strip()
        
        # 1. FAST GREETING CHECK
        greetings = ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening', 'who are you']
        if q_low in greetings or len(q_low) < 3:
            reply = "Hello! How can I assist you today? If you have any questions about our products, services, or company details, feel free to ask!"
            if conversation_id:
                ai_msg = AssistantChat(conversation_id=conversation_id, role='assistant', content=reply)
                self.db.add(ai_msg)
                self.db.commit()
            return reply

        # 2. SMART SEARCH LOGIC (LASER PRECISION)
        kb_matches = []
        if self.knowledge_base:
            try:
                data = json.loads(self.knowledge_base)
                
                # Filter fluff words
                fluff = {'what', 'is', 'the', 'working', 'pressure', 'details', 'tell', 'about', 'find', 'show', 'for', 'this', 'provide', 'you', 'your'}
                keywords = [w for w in q_low.replace('-', ' ').split() if len(w) > 2 and w not in fluff]
                
                def is_match(item):
                    text = (item.get('name', '') + " " + item.get('description', '')).lower()
                    return any(k in text for k in keywords)

                # A. Search for Specific Products (Top Priority)
                for cat in data.get('product_categories', []):
                    for sub in cat.get('subcategories', []):
                        for p in sub.get('products', []):
                            if is_match(p): kb_matches.append(p)
                
                # B. If specific products found, DON'T search services unless explicitly asked
                explicit_service_request = any(w in q_low for w in ['service', 'services', 'offerings', 'what do you do'])
                
                if not kb_matches or explicit_service_request:
                    for s in data.get('services', []):
                        if is_match(s): 
                            kb_matches.append(s)
                            
            except Exception as e:
                print(f"Search Error: {e}")

        # Supplemental broad search for services
        if any(word in query.lower() for word in ['service', 'provide', 'offer', 'do for us']):
            try:
                service_query = "Abdex core services: Hose Testing, A-track Management, Machinery Training, Rental Equipment, Umbilical Hoses"
                extra_matches = search_knowledge_base(service_query)
                for m in extra_matches:
                    if m not in kb_matches:
                        kb_matches.append(m)
            except:
                pass

        # 3. PROMPT CONSTRUCTION
        context = json.dumps(kb_matches[:15], indent=2) if kb_matches else ""
        system_prompt = f"""
            You are the Chief Intelligence Officer at Abdex Industries. You provide elite procurement intelligence.
            
            STRICT RESPONSE RULES:
            1. Services Response:
               - General Query: Provide a detailed overview of ALL key services. For EACH service, you MUST include:
                 a. Its specific name as a header (###).
                 b. Its detailed description.
                 c. Its image in Markdown format: ![Service Name](Image URL from JSON).
                 d. Its direct link: [More details here](URL from JSON).
               - Specific Query: Provide a deep-dive for THAT service only with its Image and Link.
            2. Product Response: For products (e.g. Black Eagle), ALWAYS include:
               - Working Pressure, Bore Sizes, and Applications.
               - Product Image: ![Product Name](Image URL from JSON).
               - Product Link: [View Product details here](URL from JSON).
            3. Formatting: Use bold headers (###) and professional bullet points.
            4. Multimedia: NEVER skip an image or link if it exists in the JSON context.
            5. Tone: Elite, expert, and professional.
            
            Abdex Knowledge Base Context: {context}
            User Identity: {self.user.full_name if self.user else "Professional User"}
            """
        user_prompt = f"USER QUERY: {query}"

        # 4. GENERATE
        response = self.llm.generate(system_prompt=system_prompt, user_prompt=user_prompt)
        
        # Handle dictionary response
        if isinstance(response, dict):
            reply = response.get('response') or response.get('text') or str(response)
        else:
            reply = str(response)
            
        reply = ResponseGuard.sanitize(reply.strip())
        
        if conversation_id:
            ai_msg = AssistantChat(conversation_id=conversation_id, role='assistant', content=reply)
            self.db.add(ai_msg)
            self.db.commit()
            
        return reply

    def _retrieve_context(self, query: str) -> str:
        # Disabled for speed as requested
        return ""
