import csv
import json
import os
from datetime import datetime

class Reporter:
    def __init__(self, filepath: str = "flagged_accounts.csv"):
        self.filepath = filepath
        self._ensure_file_exists()

    def _ensure_file_exists(self):
        # Create file with header if it doesn't exist (only for CSV)
        if self.filepath.endswith(".csv") and not os.path.exists(self.filepath):
            with open(self.filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["Timestamp", "Username", "UserID", "Profile Link", "Flagged Terms", "Snippet"])

    def log_flagged_account(self, username: str, user_id: int, flagged_terms: list, snippet: str = ""):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        profile_link = f"https://www.roblox.com/users/{user_id}/profile"
        terms_str = ", ".join(flagged_terms)
        
        print(f"[REPORT] Flagged {username} ({user_id}) for: {terms_str}")

        if self.filepath.endswith(".csv"):
            self._write_csv(timestamp, username, user_id, profile_link, terms_str, snippet)
        elif self.filepath.endswith(".json"):
            self._write_json(timestamp, username, user_id, profile_link, flagged_terms, snippet)

    def _write_csv(self, timestamp, username, user_id, profile_link, terms_str, snippet):
        # Sanitize snippet to avoid CSV breakages
        snippet = snippet.replace("\n", " ").replace("\r", "")
        with open(self.filepath, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([timestamp, username, user_id, profile_link, terms_str, snippet])

    def _write_json(self, timestamp, username, user_id, profile_link, flagged_terms, snippet):
        entry = {
            "timestamp": timestamp,
            "username": username,
            "user_id": user_id,
            "profile_link": profile_link,
            "flagged_terms": flagged_terms,
            "snippet": snippet
        }
        
        data = []
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            except json.JSONDecodeError:
                pass
        
        data.append(entry)
        
        with open(self.filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
