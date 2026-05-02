from models.pixtral_client import PixtralClient
from config.prompts import RFQ_AGENT_SYSTEM_PROMPT, METADATA_EXTRACTION_PROMPT_TEMPLATE
from typing import Dict, List

class MetadataExtractor:
    """Extract tender metadata from email and documents"""
    
    def __init__(self):
        self.llm = PixtralClient()
    
    def extract_metadata(self, 
                        tender_id: str,
                        email_data: Dict,
                        documents: List[Dict]) -> Dict:
        """
        Extract metadata from email and documents
        
        Returns:
            {
                "client_name": str,
                "project_name": str,
                "tender_reference": str,
                "submission_deadline": str (ISO 8601 with +03:00),
                "procurement_deadline": str,
                "contact_person": str,
                "contact_email": str,
                "location": str,
                "trade": str,
                "confidence": float
            }
        """
        
        user_prompt = METADATA_EXTRACTION_PROMPT_TEMPLATE.format(
            email_subject=email_data.get('subject', ''),
            email_sender=email_data.get('sender', ''),
            email_body_preview=email_data.get('body', '')[:1000],
            document_list=[d['filename'] for d in documents]
        )
        
        result = self.llm.generate(
            system_prompt=RFQ_AGENT_SYSTEM_PROMPT,
            user_prompt=user_prompt
        )
        
        return result
