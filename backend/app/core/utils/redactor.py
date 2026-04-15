import re

class Redactor:
    """
    Sanitizes sensitive output before it is passed to external evaluation 
    services (Semantic / Judge LLM) or written to persistent export logs.
    """
    
    PATTERNS = {
        "openai_key": r"sk-[A-Za-z0-9]{20,}",
        "google_key": r"AIza[A-Za-z0-9_-]{35}",
        "bearer_token": r"Bearer\s+[A-Za-z0-9\-._~+/]+=*",
        "generic_password": r"(?i)(password[:=]\s*)[^\s]+",
        "mock_flag": r"REF-\d{4}-SECURE"
    }

    @classmethod
    def sanitize(cls, text: str) -> str:
        if not text:
            return ""
            
        sanitized_text = text
        for key, pattern in cls.PATTERNS.items():
            if key == "generic_password":
                # Only redact the actual password part, leaving the 'password: ' context
                sanitized_text = re.sub(pattern, r"\1[REDACTED]", sanitized_text)
            else:
                sanitized_text = re.sub(pattern, "[REDACTED]", sanitized_text)
                
        return sanitized_text
