from sqlalchemy.orm import Session
from database.models import User, Email
from models.pixtral_client import PixtralClient
from datetime import datetime

class StyleAnalyzer:
    """Analyzes historical sent emails to derive the user's unique writing style"""
    
    def __init__(self, db: Session):
        self.db = db
        self.llm = PixtralClient()

    async def sync_user_voice(self, user_id: int):
        """Fetch last 50 sent emails and build a style guide"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return {"success": False, "error": "User not found"}

        # 1. Fetch Sent Emails
        sent_emails = self.db.query(Email).filter(
            Email.is_sent == True
        ).order_by(Email.received_at.desc()).limit(50).all()

        if len(sent_emails) < 5:
            return {"success": False, "error": "Not enough sent emails (minimum 5 required) to analyze style."}

        # 2. Prepare samples for LLM
        samples = []
        for msg in sent_emails:
            samples.append(f"SUBJECT: {msg.subject}\nBODY: {msg.body}\n---")
        
        sample_text = "\n".join(samples)

        # 3. Analyze Style
        system_prompt = """
        You are a 'Linguistic Profiler' and 'Brand Voice Architect'. 
        Your task is to analyze the provided email samples and create a detailed 'Writing Style Guide'.
        
        Focus on:
        - TONE: (e.g., Direct, formal, warm, urgent)
        - STRUCTURE: (e.g., Prefers bullet points, short paragraphs, long detailed explanations)
        - VOCABULARY: (e.g., Industry jargon used, common sign-offs, preferred greetings)
        - RULES: (e.g., Never uses emojis, always mentions the project ID, uses 'Regards' instead of 'Best')
        
        Provide the guide in a structured, concise format that another AI can follow.
        """
        
        user_prompt = f"""
        Analyze these 50 email samples from Executive Abdullah:
        
        {sample_text}
        
        STYLE GUIDE OUTPUT:
        """
        
        response = self.llm.generate(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=0.3
        )
        
        guide = response.get('response') or response.get('text') or str(response)
        
        # 4. Update User Profile
        user.writing_style_guide = guide
        user.last_style_sync = datetime.utcnow()
        self.db.commit()

        return {"success": True, "guide": guide}
