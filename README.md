# Roblox Profile Scanner Bot

A Python tool designed to scan Roblox user profiles for inappropriate content found in their "About" section and display names. It supports single-user scanning, bulk list scanning, and an autonomous crawler mode that traverses user friend lists.

## Features

- **Content Scanning**: Detects keywords/phrases defined in a customizable blocklist.
- **Crawler Mode**: Starts from a seed user and recursively scans their friends (BFS) to find connected accounts.
- **Bulk Scanning**: Process a list of usernames from a text file.
- **Detailed Reporting**: Generates a CSV report (`flagged_accounts.csv`) with details of flagged profiles.
- **Configurable**: Easily adjust blocked terms, crawl limits, and request delays.

## Installation

1. Clone this repository.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
   (Only requires `requests`)

## Configuration

Edit `config.json` to customize the bot's behavior. It will be generated with defaults on first run.

```json
{
    "blocklist": [
        "discord",
        "snapchat",
        "badword_here"
    ],
    "allowlist": [
        "i do not have discord"
    ],
    "output_file": "flagged_accounts.csv",
    "request_delay": 0.5,
    "crawl_limit": 100
}
```

- **blocklist**: List of terms to flag.
- **crawl_limit**: Maximum number of unique users to scan during a crawl session.

## Usage

### Single User Scan
Scan a specific user by username.
```bash
python main.py UsernameHere
```

### Crawler Mode
Start with a "seed" user and automatically scan their friends, and their friends' friends.
```bash
python main.py UsernameHere --crawl
```

### Bulk Scan from File
Scan a list of users provided in a text file (one username per line).
```bash
python main.py users.txt
```

## Output

Results are saved to `flagged_accounts.csv` (or the file specified in config).
The report includes:
- Timestamp
- Username & User ID
- Profile Link
- Flagged Terms found
- A snippet of the text that triggered the flag

## Disclaimer

This tool is for educational and moderation aid purposes only. Use responsibly and in accordance with Roblox Terms of Use.
