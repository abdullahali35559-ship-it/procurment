"""
Procurement Agent Wrapper
Restores the RFQAgent class interface by mapping it to the centralized processing logic
"""
from scripts.run_rfq_agent import process_incoming_email

class RFQAgent:
    """
    Main Agent class for processing incoming emails
    """
    def __init__(self):
        pass
        
    def process_incoming_email(self, email_data):
        """
        Process an incoming email using the centralized workflow
        """
        return process_incoming_email(email_data)
