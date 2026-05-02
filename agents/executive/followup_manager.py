import os
import sys
from datetime import datetime, timedelta, timezone
from typing import List, Dict
from sqlalchemy import select, and_, not_, func
from sqlalchemy.orm import Session

sys.path.append(os.getcwd())
from models.pixtral_client import PixtralClient
from database.models import Email, Thread, FollowupTask, Contact
from config.prompts import GENERAL_EMAIL_ASSISTANT_PROMPT

FOLLOW_UP_PROMPT = """
You are an expert Executive Assistant. 
Analyze the following email that was SENT by the user to a client/contact. 
It has been 3 days and there has been NO reply.

SENT EMAIL:
Subject: {subject}
Body: {body}

CONTACT: {contact_name}

TASK: Generate a very polite, professional, and brief follow-up draft. 
The goal is to gently remind them about the previous message without being pushy. 
If the original message was an inquiry, the follow-up should be a simple check-in.

Format your response as a JSON object:
{{
    "suggested_body": "The follow-up text here...",
    "reasoning": "Brief explanation of why this follow-up is needed"
}}
"""

class FollowupManager:
    """Analyze sent emails and suggest follow-ups for stale threads"""
    
    def __init__(self, db_session: Session):
        self.db = db_session
        self.llm = PixtralClient()
        self.stale_threshold_days = 3
        
    def find_stale_threads(self) -> List[Email]:
        """
        Find threads where the last message was SENT by us and is older than threshold
        """
        threshold_date = datetime.now() - timedelta(days=self.stale_threshold_days)
        
        # Subquery: Find the latest email for each thread
        subq = self.db.query(
            Email.thread_id,
            func.max(Email.received_at).label('max_date')
        ).group_by(Email.thread_id).subquery()
        
        # Main query: Find threads where the latest email is SENT and older than threshold
        stale_emails = self.db.query(Email).join(
            subq,
            and_(
                Email.thread_id == subq.c.thread_id,
                Email.received_at == subq.c.max_date
            )
        ).filter(
            Email.is_sent == True,
            Email.received_at <= threshold_date
        ).all()
        
        return stale_emails

    def generate_suggestions(self):
        """Main loop to identify and generate follow-up tasks"""
        stale_list = self.find_stale_threads()
        print(f"Found {len(stale_list)} stale thread(s) requiring follow-up.")
        
        new_tasks = 0
        for email in stale_list:
            # Check if a pending task already exists
            existing = self.db.query(FollowupTask).filter(
                FollowupTask.thread_id == email.thread_id,
                FollowupTask.status == 'PENDING'
            ).first()
            
            if existing:
                continue
                
            print(f"   Generating suggestion for thread: {email.subject[:50]}...")
            
            # Fetch contact name for context
            thread = self.db.query(Thread).filter(Thread.thread_id == email.thread_id).first()
            contact_name = thread.contact_name if thread else "Contact"
            
            # Call LLM
            prompt = FOLLOW_UP_PROMPT.format(
                subject=email.subject,
                body=email.body[:1000], # Trucate for LLM context
                contact_name=contact_name
            )
            
            try:
                response = self.llm.generate(
                    system_prompt=GENERAL_EMAIL_ASSISTANT_PROMPT,
                    user_prompt=prompt,
                    temperature=0.3
                )
                
                suggested_body = response.get('suggested_body', '')
                
                # Create Task
                new_task = FollowupTask(
                    thread_id=email.thread_id,
                    original_email_id=email.email_id,
                    recipient=email.sender, # In a sent email, sender field might store recipients or we use thread info
                    suggested_body=suggested_body,
                    due_at=datetime.now() + timedelta(days=1), # Suggest sending it tomorrow
                    status='PENDING'
                )
                self.db.add(new_task)
                new_tasks += 1
                
            except Exception as e:
                print(f"      [!] Error generating suggestion: {e}")
                
        self.db.commit()
        return new_tasks

if __name__ == "__main__":
    from database.connection import SessionLocal
    db = SessionLocal()
    mgr = FollowupManager(db)
    mgr.generate_suggestions()
    db.close()
