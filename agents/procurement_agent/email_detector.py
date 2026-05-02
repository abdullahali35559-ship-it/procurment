from models.pixtral_client import PixtralClient
from config.prompts import GENERAL_EMAIL_ASSISTANT_PROMPT, JUNK_FILTER_PROMPT
from typing import Dict

class EmailDetector:
    """Detect if emails are actionable business correspondence or junk using LLM"""
    
    def __init__(self):
        self.llm = PixtralClient()
        self.system_prompt = GENERAL_EMAIL_ASSISTANT_PROMPT
    
    def detect_actionable_email(self, 
                                email_id: str,
                                subject: str, 
                                sender: str, 
                                body: str,
                                attachments: list = None) -> Dict:
        """
        Detect if email is actionable business correspondence using LLM
        """
        
        attachment_names = [a.get('filename', '') for a in attachments] if attachments else []
        attachments_str = ", ".join(attachment_names) if attachment_names else "None"
        
        # Prepare user prompt
        user_prompt = JUNK_FILTER_PROMPT.format(
            subject=subject,
            sender=sender,
            attachments=attachments_str,
            body_preview=body[:3000]
        )
        
        # Few-shot examples for Junk vs Actionable
        examples = [
            {
                "input": {
                    "subject": "Inquiry: Project Quotation Request",
                    "sender": "client@example.com",
                    "attachments": "Specs.pdf",
                    "body": "We would like to request a quote for our upcoming project..."
                },
                "output": {
                    "type": "ACTIONABLE",
                    "is_junk": False,
                    "confidence": 0.99,
                    "reasoning": "Direct business inquiry with relevant attachments."
                }
            },
            {
                "input": {
                    "subject": "Your Hostinger Invoice #123456",
                    "sender": "billing@hostinger.com",
                    "attachments": "Invoice.pdf",
                    "body": "Thank you for your payment. Your hosting has been renewed."
                },
                "output": {
                    "type": "JUNK",
                    "is_junk": True,
                    "confidence": 0.98,
                    "reasoning": "Automated transactional receipt/invoice from a service provider."
                }
            },
            {
                "input": {
                    "subject": "Meeting: Technical Review",
                    "sender": "partner@company.com",
                    "attachments": "None",
                    "body": "Can we schedule a call to review the technical details?"
                },
                "output": {
                    "type": "ACTIONABLE",
                    "is_junk": False,
                    "confidence": 0.95,
                    "reasoning": "Communication regarding technical coordination."
                }
            }
        ]
        
        # Call LLM
        result = self.llm.generate(
            system_prompt=self.system_prompt,
            user_prompt=user_prompt,
            examples=examples,
            temperature=0.1
        )
        
        # Validate result
        if not isinstance(result, dict):
            return {"type": "ACTIONABLE", "is_junk": False, "confidence": 0.0, "error": "Invalid response format"}
        
        # Mapping for backward compatibility if needed in some parts
        result['is_actionable'] = result.get('type') == "ACTIONABLE"
        
        return result

    def detect_tender_email(self, *args, **kwargs):
        """Legacy wrapper for backward compatibility"""
        res = self.detect_actionable_email(*args, **kwargs)
        res['is_tender'] = res.get('is_actionable', False)
        return res
