import sys
import json
import argparse
import os
from collections import deque
from scanner import ContentScanner
from roblox_client import RobloxClient
from reporter import Reporter

def load_config(path="config.json"):
    if not os.path.exists(path):
        print(f"Config file {path} not found. Creating default.")
        default = {
            "blocklist": ["discord", "twitter"],
            "allowlist": [],
            "output_file": "flagged_accounts.csv",
            "request_delay": 0.5,
            "crawl_limit": 100
        }
        with open(path, 'w') as f:
            json.dump(default, f, indent=4)
        return default
    with open(path, 'r') as f:
        return json.load(f)

def scan_single_user_by_id(user_id, client, scanner, reporter):
    """
    Helper to scan a user by ID. Returns True if scan was successful (profile fetched), False otherwise.
    Returns (success, username, friends_count_hint) - strict return type is just success for now.
    """
    profile = client.get_user_profile(user_id)
    if not profile:
        return False, None

    username = profile.get("name", f"ID:{user_id}")
    description = profile.get("description", "")
    display_name = profile.get("displayName", "")
    
    text_to_scan = f"{display_name}\n{description}"
    
    matches = scanner.scan_text(text_to_scan)
    if matches:
        print(f"  [!] FLAGGED: {username} ({user_id}) - Found {matches}")
        reporter.log_flagged_account(username, user_id, matches, snippet=description[:100])
    # else:
    #     print(f"  - Clean: {username}")
        
    return True, username

def run_crawler(seed_user_or_id, client, scanner, reporter, limit, depth_limit=None):
    print(f"Starting crawler with seed: {seed_user_or_id}, Limit: {limit} users.")
    
    # Initialize queue with seed
    # We need to resolve seed to ID if it's a username
    if isinstance(seed_user_or_id, str) and not seed_user_or_id.isdigit():
        seed_id = client.get_user_id(seed_user_or_id)
        if not seed_id:
            print(f"Could not resolve seed user {seed_user_or_id}")
            return
    else:
        seed_id = int(seed_user_or_id)

    # Queue stores (user_id, current_depth)
    queue = deque([(seed_id, 0)])
    visited = set([seed_id])
    scanned_count = 0

    while queue and scanned_count < limit:
        current_id, current_depth = queue.popleft()
        
        # Stop if we've gone too deep (if depth limit is set)
        if depth_limit and current_depth > depth_limit:
            continue

        print(f"[{scanned_count + 1}/{limit}] Scanning ID {current_id} (Depth {current_depth})...")
        
        success, username = scan_single_user_by_id(current_id, client, scanner, reporter)
        if success:
            scanned_count += 1
            
            # Fetch friends to expand crawler
            # Only fetch friends if we haven't hit the scan limit (to save requests)
            # And if we haven't hit depth limit (no point getting friends if we won't scan them)
            if scanned_count < limit and (not depth_limit or current_depth < depth_limit):
                friends = client.get_user_friends(current_id)
                new_friends = 0
                for friend_id in friends:
                    if friend_id not in visited:
                        visited.add(friend_id)
                        queue.append((friend_id, current_depth + 1))
                        new_friends += 1
                if new_friends:
                    print(f"    -> Added {new_friends} new friends to queue.")
        else:
            print(f"    -> Skipped (Profile fetch failed)")

def main():
    parser = argparse.ArgumentParser(description="Roblox Profile Content Scanner")
    parser.add_argument("target", nargs="?", help="Username to scan or path to text file with usernames")
    parser.add_argument("--crawl", action="store_true", help="Enable crawling mode (treats target as seed)")
    args = parser.parse_args()

    config = load_config()
    scanner = ContentScanner()
    client = RobloxClient(request_delay=config.get("request_delay", 0.5))
    reporter = Reporter(filepath=config.get("output_file", "flagged_accounts.csv"))

    if not args.target:
        print("Usage: python main.py <username> [--crawl]")
        target = input("Enter username: ").strip()
    else:
        target = args.target

    if args.crawl:
        limit = config.get("crawl_limit", 100)
        run_crawler(target, client, scanner, reporter, limit)
    elif os.path.isfile(target):
        # Bulk mode
        print(f"Reading users from {target}...")
        try:
            with open(target, 'r') as f:
                users = [line.strip() for line in f if line.strip()]
            
            print(f"Found {len(users)} users to scan.")
            for user in users:
                print(f"Scanning user: {user}")
                user_id = client.get_user_id(user)
                if user_id:
                    scan_single_user_by_id(user_id, client, scanner, reporter)
                else:
                    print(f"  - User {user} not found.")
        except Exception as e:
            print(f"Error reading file: {e}")
    else:
        # Single user mode
        print(f"Scanning user: {target}")
        user_id = client.get_user_id(target)
        if user_id:
            scan_single_user_by_id(user_id, client, scanner, reporter)
        else:
            print(f"  - User {target} not found.")

    print("\nScan complete.")

if __name__ == "__main__":
    main()
