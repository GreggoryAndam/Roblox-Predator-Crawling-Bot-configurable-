import json
import re
from typing import List

class ContentScanner:
    def __init__(self, config_path: str = "config.json"):
        self.config_path = config_path
        self.blocklist = []
        self.allowlist = []
        self._load_config()

    def _load_config(self):
        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)
                self.blocklist = config.get("blocklist", [])
                self.allowlist = [text.lower() for text in config.get("allowlist", [])]
        except FileNotFoundError:
            print(f"Warning: {self.config_path} not found. Using empty lists.")

    def reload_config(self):
        self._load_config()

    def scan_text(self, text: str) -> List[str]:
        """
        Scans the given text for blocked words/phrases.
        Returns a list of matches found.
        """
        if not text:
            return []

        text_lower = text.lower()
        
        # Check allowlist first (simple exact match or substring logic could be expanded)
        for allowed in self.allowlist:
            if allowed in text_lower:
                # If the exact allowed phrase is present, we might want to ignore specific hits
                # For now, simple logic: if an allowed phrase is found, we might still flag if OTHER bad stuff is there.
                # But if the user says "I don't have discord", "discord" is in blocklist.
                # We need to be careful.
                # A robust way: remove allowed phrases from the temp string before scanning.
                text_lower = text_lower.replace(allowed, "")

        matches = []
        for pattern in self.blocklist:
            # We treat blocklist items as case-insensitive substrings.
            # For more complex matching, they could be distinct regexes in the config.
            if pattern.lower() in text_lower:
                matches.append(pattern)
        
        return list(set(matches)) # Unique matches

    def is_clean(self, text: str) -> bool:
        return len(self.scan_text(text)) == 0
