import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database Configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://rfq_user:rfq_secure_2024@localhost:5432/tender_system_db")

# LLM Configuration
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "pixtral")  # 'pixtral' or 'openrouter'

# Pixtral Configuration (Local)
PIXTRAL_URL = os.getenv("PIXTRAL_URL", "https://ai.gcucsstudent.site")
PIXTRAL_MODEL = os.getenv("PIXTRAL_MODEL", "ai-agent:latest")

# OpenRouter Configuration (Cloud)
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "anthropic/claude-3.5-sonnet")
OPENROUTER_URL = "https://openrouter.ai/api/v1"

# Storage Configuration
STORAGE_PATH = os.getenv("STORAGE_PATH", "./storage/tenders")

# Email Configuration - Microsoft Graph
AZURE_CLIENT_ID = os.getenv("AZURE_CLIENT_ID")
AZURE_CLIENT_SECRET = os.getenv("AZURE_CLIENT_SECRET")
AZURE_TENANT_ID = os.getenv("AZURE_TENANT_ID")

# Email Configuration - Gmail
GMAIL_CREDENTIALS_FILE = os.getenv("GMAIL_CREDENTIALS_FILE", "./config/gmail_credentials.json")

# ============================================
# EMAIL INTEGRATION (IMAP)
# ============================================

# Email Providers (comma-separated list)
EMAIL_PROVIDERS = [p.strip() for p in os.getenv("EMAIL_PROVIDERS", "gmail").split(',')]

# Gmail IMAP Settings
GMAIL_HOST = os.getenv("GMAIL_HOST", "imap.gmail.com")
GMAIL_PORT = int(os.getenv("GMAIL_PORT", "993"))
GMAIL_USER = os.getenv("GMAIL_USER", "")
GMAIL_PASSWORD = os.getenv("GMAIL_PASSWORD", "")

# Outlook IMAP Settings
OUTLOOK_HOST = os.getenv("OUTLOOK_HOST", "outlook.office365.com")
OUTLOOK_PORT = int(os.getenv("OUTLOOK_PORT", "993"))
OUTLOOK_USER = os.getenv("OUTLOOK_USER", "")
OUTLOOK_PASSWORD = os.getenv("OUTLOOK_PASSWORD", "")

# Outlook OAuth2 Settings (FREE Personal Account)
OUTLOOK_OAUTH_ENABLED = os.getenv("OUTLOOK_OAUTH_ENABLED", "false").lower() == "true"
OUTLOOK_CLIENT_ID = os.getenv("OUTLOOK_CLIENT_ID", "")
OUTLOOK_CLIENT_SECRET = os.getenv("OUTLOOK_CLIENT_SECRET", "")
OUTLOOK_TENANT_ID = os.getenv("OUTLOOK_TENANT_ID", "consumers")
OUTLOOK_REDIRECT_URI = os.getenv("OUTLOOK_REDIRECT_URI", "http://localhost")

# Email Monitoring Settings
EMAIL_CHECK_FOLDER = os.getenv("EMAIL_CHECK_FOLDER", "INBOX")
EMAIL_PROCESSED_FOLDER = os.getenv("EMAIL_PROCESSED_FOLDER", "RFQ_Processed")
EMAIL_CHECK_INTERVAL = int(os.getenv("EMAIL_CHECK_INTERVAL", "300"))
EMAIL_FILTER_SUBJECTS = os.getenv("EMAIL_FILTER_SUBJECTS", "Procurement,Tender,ITT,Bid,Quotation")
EMAIL_MARK_AS_READ = os.getenv("EMAIL_MARK_AS_READ", "true")

# Timezone
TIMEZONE = os.getenv("TIMEZONE", "Asia/Riyadh")

# Company Info
COMPANY_NAME = os.getenv("COMPANY_NAME", "AI Construction Services")

# Valid Document Categories
VALID_CATEGORIES = [
    "01_Instructions",
    "02_Scope_of_Work",
    "03_Drawings",
    "04_Specifications",
    "05_BOQ",
    "06_Standards",
    "07_Commercial",
    "08_Output"
]

# Required Documents (for Procurement generation)
REQUIRED_DOCUMENTS = {
    "01_Instructions": True,
    "02_Scope_of_Work": True,
    "03_Drawings": True,
    "04_Specifications": True,
    "05_BOQ": True,
    "06_Standards": True,
    "07_Commercial": True
}
