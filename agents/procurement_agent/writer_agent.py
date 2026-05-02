# Writer Agent: The Professional Communicator
from models.pixtral_client import PixtralClient
from typing import Dict, List
import json

class WriterAgent:
    """
    The communicator specialized in professional correspondence.
    It synthesizes business strategy and technical facts into high-end executive drafts.
    """
    
    def __init__(self):
        self.llm = PixtralClient()
        self.system_prompt = """
        You are an Elite Executive Writer.
        Your job is to write professional business emails that are clear, persuasive, and accurate.
        
        You use the Strategy from the Manager and the Findings from the Researcher to ensure your draft is of the highest quality.
        """

    def draft_response(self, 
                       sender: str, 
                       subject: str, 
                       strategy: str, 
                       tone: str, 
                       findings: List[Dict],
                       writing_style_guide: str = "",
                       custom_instructions: str = "",
                       previous_draft: str = "",
                       revision_feedback: str = "") -> Dict:
        """
        Produce a professional response draft, mirroring the user's authentic style.
        """
        
        findings_text = "\n".join([f"- {f['directive']}: {f['fact']}" for f in findings])
        
        prompt = f"""
        Draft a professional response that feels like a HUMAN wrote it, not an AI.
        
        INQUIRY FROM: {sender}
        ORIGINAL SUBJECT: {subject}
        
        STRATEGIC PLAN: {strategy}
        REQUIRED TONE: {tone}
        
        VERIFIED RESEARCH FINDINGS:
        {findings_text}
        
        {f"STRICT WRITING STYLE GUIDE (FOLLOW THIS): \n{writing_style_guide}" if writing_style_guide else ""}
        
        {f"USER CUSTOM INSTRUCTIONS: \n{custom_instructions}" if custom_instructions else ""}
        
        {f"PREVIOUS DRAFT (NEEDS REVISION):\n{previous_draft}\n\nAUDITOR FEEDBACK (FIX THESE ISSUES):\n{revision_feedback}" if previous_draft and revision_feedback else ""}
        
        INSTRUCTIONS FOR AUTHENTIC HUMAN FEEL:
        1. NO MARKDOWN: Never use **bold**, *italics*, or # headers. Real humans don't use markdown in business emails.
        2. NO SPECIAL CHARACTERS: Do not use '*' or '-' for bullet points unless the style guide says otherwise. Use plain text paragraphs.
        3. STYLE MIRRORING: If the Writing Style Guide says the user uses "Hi" instead of "Dear", or "Best" instead of "Sincerely", you MUST follow that exactly.
        4. NATURAL FLOW: Ensure sentences vary in length and sound natural.
        5. ADDRESS FINDINGS: Naturally weave the researched facts into the response.
        
        Return JSON only:
        {{
            "draft_subject": "Professional Subject Line",
            "draft_body": "The complete email body (NO MARKDOWN)",
            "confidence": 0.0-1.0
        }}
        """
        
        result = self.llm.generate(
            system_prompt=self.system_prompt + "\nIMPORTANT: You must output ONLY plain text. No markdown, no bolding, no asterisks.",
            user_prompt=prompt,
            temperature=0.4
        )
        
        return result
