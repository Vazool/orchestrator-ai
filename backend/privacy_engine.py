import re
from typing import Dict, Tuple

class PrivacyVault:
    def __init__(self):
        # Local, in-memory map to store real names linked to tokens
        self.map: Dict[str, str] = {}
        self.counter = 1

    def mask_customer_data(self, forename: str) -> str:
        """Replaces a real name with a consistent token for this session."""
        token = f"{{{{forename_{self.counter}}}}}"
        self.map[token] = forename
        self.counter += 1
        return token

    def rehydrate_message(self, ai_text: str) -> str:
        """Swaps tokens back to real names in the AI response."""
        for token, real_name in self.map.items():
            ai_text = ai_text.replace(token, real_name)
        return ai_text

# Initialize a global vault for the demo
demo_vault = PrivacyVault()