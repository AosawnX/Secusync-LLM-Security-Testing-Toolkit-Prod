import re

PATTERNS = {
    "openai_key": r"sk-[A-Za-z0-9]{20,}",
    "google_key": r"AIza[A-Za-z0-9_-]{35}",
    "bearer_token": r"Bearer\s+[A-Za-z0-9\-._~+/]+=*",
    "injection_marker": r"(injected|compromised|password123|admin)"
}

class DeterministicAnalyzer:
    @staticmethod
    def analyze(response: str) -> list[str]:
        if not response:
             return []
             
        matches = []
        for name, pattern in PATTERNS.items():
            if re.search(pattern, response, re.IGNORECASE):
                matches.append(name)
                
        return matches
