from models.pixtral_client import PixtralClient
import json
from typing import List, Dict

class StyleAgent:
    """
    Analyzes user-provided samples and historical emails to extract 
    linguistic patterns, tone, and formatting preferences.
    """
    
    def __init__(self):
        self.client = PixtralClient()

    def analyze_samples(self, samples: str) -> str:
        """
        Analyze raw email samples and return a structured Style Guide.
        """
        if not samples or len(samples.strip()) < 50:
            return "No sufficient samples provided for style analysis."

        prompt = f"""
        ANALYZE THE FOLLOWING EMAIL SAMPLES AND EXTRACT A WRITING STYLE GUIDE.
        
        SAMPLES:
        {samples}
        
        TASK:
        Identify the following characteristics from the samples:
        1. Opening Preference: (e.g., 'Hi [Name]', 'Dear [Name]', or direct)
        2. Closing Preference: (e.g., 'Best regards,', 'Thanks,', 'Regards,')
        3. Sentence Structure: (Short/Direct, Long/Explanatory, Bullet points used?)
        4. Tone: (Formal, Casual, Urgent, Enthusiastic, Minimalist)
        5. Vocabulary Level: (Simple, Professional/Technical, Complex)
        6. Unique Quirks: (Does the user use specific emojis, certain phrases, or unique punctuation?)

        OUTPUT FORMAT:
        Provide a concise 'Style Profile' in plain text (no markdown) that another AI can use to mimic this user.
        """

        try:
            analysis = self.client.chat(
                system_prompt="You are a Linguistic Expert and Tone Analyzer. Your job is to create a blueprint of a person's writing style so it can be perfectly replicated.",
                user_prompt=prompt
            )
            # Handle if the response is a dict from PixtralClient (some models return JSON)
            if isinstance(analysis, dict):
                return analysis.get('response', analysis.get('analysis', str(analysis)))
            return analysis.strip()
        except Exception as e:
            print(f"Error in style analysis: {e}")
            return "Error analyzing writing style."

    def extract_style_from_emails(self, emails: List[Dict]) -> str:
        """
        Takes a list of email objects (subject/body) and analyzes them for tone.
        """
        combined_text = ""
        for email in emails[:10]: # Analyze last 10 for speed
            combined_text += f"\nSubject: {email.get('subject')}\nBody: {email.get('body')}\n---"
        
        return self.analyze_samples(combined_text)
