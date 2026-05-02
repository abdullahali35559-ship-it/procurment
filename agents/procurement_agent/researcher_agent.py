# Researcher Agent: The Technical Investigator
from models.pixtral_client import PixtralClient
from typing import Dict, List
import json

class ResearcherAgent:
    """
    The investigator specialized in deep document analysis.
    It resolves the directives issued by the Manager by scanning technical data and finding verified facts.
    """
    
    def __init__(self):
        self.llm = PixtralClient()
        self.system_prompt = """
        You are a Specialized Business Researcher with "Deep Document Intelligence".
        Your job is to find specific, verified facts, including complex data from TABLES, EXCEL SHEETS, and TECHNICAL DOCUMENTS.
        
        TABLE ANALYSIS RULES:
        - When encountering a table (Markdown format), treat it as structured data. 
        - Pay attention to headers, units (like USD, kg, m2), and column relationships.
        - If asked for a "best rate" or "total", compare values across rows carefully.
        - Look for hidden footnotes or small print that might qualify a data point.
        
        Your objective is absolute accuracy. If the data is not in the source, state it clearly.
        """

    def investigate(self, directives: List[str], email_context: str, document_contexts: List[Dict]) -> Dict:
        """
        Execute directives using available contexts with Deep Intelligence.
        """
        
        doc_content_text = ""
        for d in document_contexts:
            raw = d.get('raw_text', '')
            if not raw:
                raw = d.get('summary', 'No content available')
            doc_content_text += f"--- FILE: {d.get('filename')} ---\n{raw}\n\n"
        
        prompt = f"""
        Execute the following Directives based on the Email Context and the Deep Content (including Tables) of Attached Documents.
        
        DIRECTIVES:
        {json.dumps(directives, indent=2)}
        
        EMAIL CONTEXT:
        {email_context}
        
        DOCUMENT CONTENTS (RAW/TABLES):
        {doc_content_text}
        
        Return your findings in the following JSON format:
        {{
            "findings": [
                {{
                    "directive": "The original directive",
                    "fact": "The specific data found (be precise, include units/rows)",
                    "source": "e.g. Email body or File Name"
                }}
            ],
            "unresolved_directives": ["Lists directives that could not be verified"],
            "technical_notes": "Any other critical observations, especially regarding data trends or table anomalies."
        }}
        """
        
        result = self.llm.generate(
            system_prompt=self.system_prompt,
            user_prompt=prompt,
            temperature=0.0
        )
        
        return result
