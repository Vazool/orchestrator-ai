import threading  # New import for the "Baton"
from typing import Dict

class PrivacyVault:
    def __init__(self):
        # Local, in-memory map to store real names linked to tokens
        self.map: Dict[str, str] = {}
        self.counter = 1
        self.lock = threading.Lock()  # The safety lock for parallel processing

    def mask_customer_data(self, forename: str) -> str:
        """Replaces a real name with a consistent token for this session."""
        with self.lock:  # Only one 'Chef' can grab a ticket number at a time
            token = f"{{{{forename_{self.counter}}}}}"
            self.map[token] = forename
            self.counter += 1
            return token

    def rehydrate_message(self, ai_text: str) -> str:
        """Swaps tokens back to real names in the AI response."""
        # This remains the same; reading from the map is safe
        for token, real_name in self.map.items():
            ai_text = ai_text.replace(token, real_name)
        return ai_text

# Initialize a global vault for the demo
demo_vault = PrivacyVault()