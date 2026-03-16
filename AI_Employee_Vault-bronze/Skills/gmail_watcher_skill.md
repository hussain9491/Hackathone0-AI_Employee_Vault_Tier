# Gmail Watcher Skill

> **Tier:** Silver  
> **Status:** Ready to Implement  
> **Dependencies:** Google Gmail API, OAuth 2.0 credentials

---

## 📋 Overview

The Gmail Watcher monitors your Gmail inbox for new, unread, and important emails. When detected, it creates action files in the `Needs_Action/` folder for Qwen to process.

**Use Case:** Automatically capture important emails and turn them into actionable tasks.

---

## 🎯 Silver Tier Requirement

This skill fulfills:
- ✅ "Two or more Watcher scripts (e.g., Gmail + WhatsApp + LinkedIn)"
- ✅ Part of the Perception layer (Watcher architecture)

---

## 📦 Prerequisites

### 1. Google Cloud Project Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable Gmail API
4. Create OAuth 2.0 credentials
5. Download `credentials.json`

### 2. Python Dependencies

```bash
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

### 3. Folder Structure

```
AI_Employee_Vault/
├── scripts/
│   ├── base_watcher.py         # Required (Bronze tier)
│   └── gmail_watcher.py        # Create this
├── .env                        # Store credentials path
└── Logs/                       # Watcher logs
```

---

## 🏗️ Implementation

### Gmail Watcher Script

**File:** `scripts/gmail_watcher.py`

```python
"""
Gmail Watcher for AI Employee

Monitors Gmail for unread/important emails and creates action files.

Usage:
    python gmail_watcher.py --vault-path .. --credentials /path/to/credentials.json
"""

import os
import sys
import argparse
from pathlib import Path
from datetime import datetime

# Google API imports
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import pickle

# Import base watcher
from base_watcher import BaseWatcher


class GmailWatcher(BaseWatcher):
    """
    Gmail watcher that monitors for unread/important emails.
    """
    
    # Gmail API scopes
    SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
    
    def __init__(self, vault_path: str, credentials_path: str, 
                 token_path: str = None, check_interval: int = 120):
        """
        Initialize Gmail watcher.
        
        Args:
            vault_path: Path to Obsidian vault
            credentials_path: Path to Gmail OAuth credentials JSON
            token_path: Path to store token (default: vault/Logs/gmail_token.pickle)
            check_interval: Seconds between checks (default: 120)
        """
        super().__init__(vault_path, check_interval)
        
        self.credentials_path = Path(credentials_path)
        self.token_path = Path(token_path) if token_path else self.vault_path / 'Logs' / 'gmail_token.pickle'
        self.service = None
        self.processed_ids = set()
        
        # Load or create credentials
        self._authenticate()
        
    def _authenticate(self):
        """Authenticate with Gmail API."""
        creds = None
        
        # Load token if exists
        if self.token_path.exists():
            with open(self.token_path, 'rb') as token:
                creds = pickle.load(token)
        
        # Refresh or create new credentials
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, self.SCOPES)
                creds = flow.run_local_server(port=0)
            
            # Save token for next run
            self.token_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.token_path, 'wb') as token:
                pickle.dump(creds, token)
        
        self.service = build('gmail', 'v1', credentials=creds)
        self.logger.info("Authenticated with Gmail API")
    
    def check_for_updates(self) -> list:
        """
        Check for new unread/important emails.
        
        Returns:
            List of new message IDs
        """
        try:
            # Query: unread and important emails
            results = self.service.users().messages().list(
                userId='me',
                q='is:unread is:important',
                maxResults=10
            ).execute()
            
            messages = results.get('messages', [])
            
            # Filter out already processed
            new_messages = [
                m for m in messages 
                if m['id'] not in self.processed_ids
            ]
            
            if new_messages:
                self.logger.info(f"Found {len(new_messages)} new emails")
            
            return new_messages
            
        except Exception as e:
            self.logger.error(f"Error checking Gmail: {e}")
            return []
    
    def create_action_file(self, message) -> Path:
        """
        Create action file for email.
        
        Args:
            message: Gmail message dict
            
        Returns:
            Path to created action file
        """
        try:
            # Get full message details
            msg = self.service.users().messages().get(
                userId='me', 
                id=message['id'],
                format='metadata',
                metadataHeaders=['From', 'To', 'Subject', 'Date']
            ).execute()
            
            # Extract headers
            headers = {h['name']: h['value'] for h in msg['payload']['headers']}
            
            # Parse email address from "Name <email@example.com>"
            from_email = headers.get('From', 'Unknown')
            subject = headers.get('Subject', 'No Subject')
            received = headers.get('Date', datetime.now().isoformat())
            
            # Create action file content
            content = f'''---
type: email
from: {from_email}
subject: {subject}
received: {received}
priority: high
status: pending
gmail_id: {message['id']}
---

# Email Received

**From:** {from_email}  
**Subject:** {subject}  
**Received:** {received}

## Suggested Actions

- [ ] Read full email in Gmail
- [ ] Reply to sender
- [ ] Forward to relevant party
- [ ] Archive after processing

## Response Draft

_Add your draft response here_

## Notes

_Add any additional notes here_

---
*Created by Gmail Watcher*
'''
            
            # Create filename (sanitize subject)
            safe_subject = "".join(c if c.isalnum() else '_' for c in subject[:30])
            filepath = self.needs_action / f'EMAIL_{safe_subject}_{message["id"][:8]}.md'
            
            # Write file
            filepath.write_text(content)
            
            # Mark as processed
            self.processed_ids.add(message['id'])
            
            self.logger.info(f"Created action file: {filepath.name}")
            
            return filepath
            
        except Exception as e:
            self.logger.error(f"Error creating action file: {e}")
            return None


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Gmail Watcher for AI Employee')
    parser.add_argument('--vault-path', default='..', help='Path to Obsidian vault')
    parser.add_argument('--credentials', required=True, help='Path to Gmail credentials JSON')
    parser.add_argument('--token-path', help='Path to token file (optional)')
    parser.add_argument('--interval', type=int, default=120, help='Check interval in seconds')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("📧 GMAIL WATCHER")
    print("=" * 60)
    
    watcher = GmailWatcher(
        vault_path=args.vault_path,
        credentials_path=args.credentials,
        token_path=args.token_path,
        check_interval=args.interval
    )
    
    watcher.run()


if __name__ == '__main__':
    main()
```

---

## 🚀 Usage

### First-Time Setup

```bash
# 1. Install dependencies
cd AI_Employee_Vault/scripts
pip install -r requirements.txt

# 2. Run Gmail watcher (first time will open browser for OAuth)
python gmail_watcher.py --vault-path .. --credentials /path/to/credentials.json
```

### Daily Usage

```bash
# Start Gmail watcher (runs continuously)
python gmail_watcher.py --vault-path .. --credentials credentials.json
```

### With Qwen

```bash
# Process emails captured by Gmail watcher
qwen "Check Needs_Action folder for new emails and process them"
```

---

## 📁 Example Output

### Action File Created in `Needs_Action/`

```markdown
---
type: email
from: "John Doe <john@example.com>"
subject: "Project Update Meeting Tomorrow"
received: "Mon, 14 Mar 2026 10:30:00 -0700"
priority: high
status: pending
gmail_id: 18f3c5a2b9d4e1f0
---

# Email Received

**From:** John Doe <john@example.com>  
**Subject:** Project Update Meeting Tomorrow  
**Received:** Mon, 14 Mar 2026 10:30:00 -0700

## Suggested Actions

- [ ] Read full email in Gmail
- [ ] Reply to sender
- [ ] Forward to relevant party
- [ ] Archive after processing

## Response Draft

_Add your draft response here_

## Notes

_Add any additional notes here_

---
*Created by Gmail Watcher*
```

---

## ⚙️ Configuration

### Environment Variables

Create `.env` file:

```bash
# Gmail Watcher Configuration
GMAIL_CREDENTIALS_PATH=/path/to/credentials.json
GMAIL_TOKEN_PATH=/path/to/token.pickle
GMAIL_CHECK_INTERVAL=120
```

### Gmail Query Examples

Modify the `check_for_updates` query for different filtering:

```python
# Unread and important
q='is:unread is:important'

# From specific sender
q='from:boss@company.com is:unread'

# With attachments
q='has:attachment is:unread'

# About specific topic
q='subject:invoice is:unread'

# Multiple conditions
q='(from:client.com OR from:partner.com) is:unread'
```

---

## 🔒 Security

### Best Practices

1. **Never commit credentials** - Add to `.gitignore`:
   ```
   credentials.json
   *token.pickle
   ```

2. **Use minimal scopes** - Only request `gmail.readonly` for watching

3. **Rotate credentials** - Regenerate OAuth credentials periodically

4. **Secure token storage** - Store token.pickle in secure location

### Permissions

| Scope | Purpose | Risk Level |
|-------|---------|------------|
| `gmail.readonly` | Read emails | Low |
| `gmail.send` | Send emails | Medium (Silver tier+) |
| `gmail.modify` | Label/archive emails | Medium |

---

## 🐛 Troubleshooting

### Error: "Credentials file not found"

**Fix:** Verify path is absolute and file exists:
```bash
ls -la /path/to/credentials.json
```

### Error: "Token expired"

**Fix:** Delete token file and re-authenticate:
```bash
rm Logs/gmail_token.pickle
python gmail_watcher.py --credentials credentials.json
```

### Error: "Gmail API not enabled"

**Fix:** Enable Gmail API in Google Cloud Console:
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Select your project
3. APIs & Services → Library
4. Search "Gmail API" → Enable

### No emails detected

**Check:**
1. Are there unread emails?
2. Are they marked as important by Gmail?
3. Try less restrictive query: `q='is:unread'`

---

## 📊 Testing

### Test Script

```python
# test_gmail_watcher.py
from gmail_watcher import GmailWatcher

# Create watcher
watcher = GmailWatcher(
    vault_path='..',
    credentials_path='credentials.json'
)

# Test authentication
print("Testing authentication...")
assert watcher.service is not None
print("✅ Authentication successful")

# Test check for updates
print("Testing email check...")
emails = watcher.check_for_updates()
print(f"✅ Found {len(emails)} emails")

# Test action file creation
if emails:
    print("Testing action file creation...")
    filepath = watcher.create_action_file(emails[0])
    print(f"✅ Created: {filepath}")
```

---

## 🔗 Related Skills

| Skill | Purpose |
|-------|---------|
| `mcp_email_skill.md` | Send emails via MCP server |
| `whatsapp_watcher_skill.md` | Monitor WhatsApp messages |
| `plan_generator_skill.md` | Create action plans from emails |

---

## 📚 Resources

- [Gmail API Documentation](https://developers.google.com/gmail/api)
- [Google OAuth 2.0 Guide](https://developers.google.com/identity/protocols/oauth2)
- [Gmail Query Search](https://support.google.com/mail/answer/7190?hl=en)
- [Hackathon Doc Section 2A](../Personal%20AI%20Employee%20Hackathon%200_%20Building%20Autonomous%20FTEs%20in%202026.md#watcher-architecture)

---

*Skill Version: 1.0*  
*Last Updated: 2026-03-14*  
*Silver Tier Component*
