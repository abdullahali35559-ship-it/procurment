# Manager Agent: The Brain of the Multi-Agent System
from models.pixtral_client import PixtralClient
from typing import Dict, List
import json

class ManagerAgent:
    """
    The orchestrator that analyzes incoming inquiries and directs specialized agents.
    It determines the professional context and provides 'Inquiry Directives' for researchers.
    """
    
    def __init__(self):
        self.llm = PixtralClient()
        self.system_prompt = """
        You are the Executive Manager of a professional Business Command Center.
        Your role is to analyze a new business inquiry and produce a strategic plan.
        
        You must decide:
        1. Is this a legitimate business inquiry that requires a detailed response?
        2. What specific facts or data points must the Researcher find in the attachments?
        3. What is the priority and professional tone required?
        """

    def analyze_inquiry(self, sender: str, subject: str, body: str, attachment_names: List[str]) -> Dict:
        """
        Analyze the intent and provide directives.
        """
        
        prompt = f"""
        Analyze this incoming email and decide how our team should handle it.
        
        SENDER: {sender}
        SUBJECT: {subject}
        BODY: {body}
        ATTACHMENTS: {", ".join(attachment_names) if attachment_names else "None"}
        
        Return your analysis in the following JSON format:
        {{
            "is_business_inquiry": true/false,
            "business_segment": "e.g. Sales, Project Inquiry, Technical Support, Partnership",
            "priority": "Low/Medium/High/Urgent",
            "strategic_plan": "A brief sentence on how to handle this",
            "suggested_tags": ["Category 1", "Category 2"],
            "researcher_directives": [
                "Directive 1: e.g. Find the total price for the cement",
                "Directive 2: e.g. Extract the delivery timeline",
                "Directive 3: e.g. Identify any technical constraints"
            ],
            "writer_tone": "e.g. Highly Formal, Friendly but Professional, Direct and Brief"
        }}
        """
        
        result = self.llm.generate(
            system_prompt=self.system_prompt,
            user_prompt=prompt,
            temperature=0.1
        )
        
        return result
