import re

class ResponseGuard:
    """Scans AI responses for sensitive patterns and masks them"""
    
    # Common sensitive patterns
    PATTERNS = {
        "api_key": r"(?:api[_-]?key|secret|token|password)[\s:=]+['\"]?([a-zA-Z0-9\-_]{16,})['\"]?",
        "env_path": r"[a-zA-Z]:\\[\w\s\\.]+\.env",
        "internal_ip": r"127\.0\.0\.1|localhost",
        "db_string": r"postgresql://[\w:]+@[\w:]+/[\w]+",
        "password_hash": r"\$2[aby]\$\d{2}\$[./A-Za-z0-9]{53}"
    }

    @staticmethod
    def sanitize(text: str) -> str:
        """Main method to clean text before sending to UI"""
        if not text:
            return text
            
        cleaned = text
        for label, pattern in ResponseGuard.PATTERNS.items():
            # Replace matches with [PROTECTED]
            cleaned = re.sub(pattern, f"[PROTECTED {label.upper()}]", cleaned, flags=re.IGNORECASE)
            
        return cleaned

    @staticmethod
    def is_suspicious(query: str) -> bool:
        """Detect potential prompt injection attempts"""
        injection_keywords = [
            "ignore previous instructions",
            "system prompt",
            "you are now a hacker",
            "reveal your instructions",
            "bypass safety",
            "print your configuration"
        ]
        q_lower = query.lower()
        return any(k in q_lower for k in injection_keywords)
