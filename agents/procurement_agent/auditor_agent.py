# Auditor Agent: The Quality Controller
from models.pixtral_client import PixtralClient
from typing import Dict, List
import json

class AuditorAgent:
    """
    The final quality controller in the Multi-Agent system.
    It compares the drafted response against Management Strategy and Researcher Findings
    to ensure absolute accuracy, professional tone, and compliance.
    """
    
    def __init__(self):
        self.llm = PixtralClient()
        self.system_prompt = """
        You are the Elite Quality Auditor for executive business communications.
        Your job is to ruthlessly review draft emails before they are sent to clients.
        
        You must verify:
        1. Does the draft perfectly align with the Manager's Strategic Plan?
        2. Are ALL facts found by the Researcher clearly addressed?
        3. Is the tone consistently executive and professional?
        
        You will return an approval status and constructive feedback.
        """

    def review_draft(self, 
                       subject: str, 
                       draft_body: str, 
                       strategy: str, 
                       findings: List[Dict]) -> Dict:
        """
        Produce a compliance and quality audit of the drafted response.
        """
        
        findings_text = "\n".join([f"- {f['directive']}: {f['fact']} (Source: {f['source']})" for f in findings])
        
        prompt = f"""
        Audit the following draft against our internal requirements.
        
        MANAGER'S STRATEGY: 
        {strategy}
        
        RESEACHER'S VERIFIED FACTS THAT MUST BE INCLUDED:
        {findings_text}
        
        ======================
        DRAFT SUBJECT: {subject}
        DRAFT BODY: 
        {draft_body}
        ======================
        
        INSTRUCTIONS:
        1. Check if the draft is missing any verified facts.
        2. Check if the tone is too casual or unprofessional.
        3. If there are any flaws, set "is_approved" to false and provide clear "revision_feedback".
        4. If it is perfect, set "is_approved" to true.
        
        Return JSON only:
        {{
            "is_approved": true/false,
            "revision_feedback": "Specific feedback for the writer to fix the draft (or leave empty if approved)",
            "quality_score": 1-10
        }}
        """
        
        result = self.llm.generate(
            system_prompt=self.system_prompt,
            user_prompt=prompt,
            temperature=0.0 # Zero temperature for strict factual checking
        )
        
        return result
