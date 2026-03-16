"""
Gmail Watcher for AI Employee

Monitors Gmail for unread/important emails and creates action files in Needs_Action folder.
Part of Silver Tier deliverables.

Usage:
    python gmail_watcher.py --vault-path ../AI_Employee_Vault --credentials ../.qwen/credentials.json

Author: AI Employee Project
Tier: Silver
"""

import os
import sys
import argparse
import time
import logging
from pathlib import Path
from datetime import datetime

# Google API imports
try:
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
except ImportError:
    print("❌ Missing dependencies. Install with:")
    print("   pip install google-auth google-auth-oauthlib google-api-python-client")
    sys.exit(1)


class GmailWatcher:
    """
    Gmail watcher that monitors for unread/important emails.
    Creates action files in the Needs_Action folder for Qwen to process.
    """
    
    # Gmail API scopes
    SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
    
    def __init__(self, vault_path: str, credentials_path: str, 
                 check_interval: int = 120):
        """
        Initialize Gmail watcher.
        
        Args:
            vault_path: Path to Obsidian vault
            credentials_path: Path to Gmail OAuth credentials JSON
            check_interval: Seconds between checks (default: 120)
        """
        self.vault_path = Path(vault_path)
        self.credentials_path = Path(credentials_path)
        self.token_path = self.vault_path / 'Logs' / 'gmail_token.json'
        self.check_interval = check_interval
        self.needs_action = self.vault_path / 'Needs_Action'
        self.logs_folder = self.vault_path / 'Logs'
        
        # Ensure directories exist
        self.needs_action.mkdir(parents=True, exist_ok=True)
        self.logs_folder.mkdir(parents=True, exist_ok=True)
        
        # Setup logging
        self._setup_logging()
        
        # Track processed message IDs
        self.processed_ids = set()
        self._load_processed_ids()
        
        # Gmail service
        self.service = None
        
    def _setup_logging(self):
        """Setup logging to file and console."""
        log_file = self.logs_folder / f'gmail_watcher_{datetime.now().strftime("%Y%m%d")}.log'
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('GmailWatcher')
    
    def _load_processed_ids(self):
        """Load previously processed message IDs from disk."""
        state_file = self.logs_folder / 'gmail_processed_ids.txt'
        if state_file.exists():
            self.processed_ids = set(state_file.read_text().strip().split('\n'))
            self.logger.info(f"Loaded {len(self.processed_ids)} processed message IDs")
    
    def _save_processed_ids(self):
        """Save processed message IDs to disk."""
        state_file = self.logs_folder / 'gmail_processed_ids.txt'
        state_file.write_text('\n'.join(self.processed_ids))
    
    def _authenticate(self):
        """Authenticate with Gmail API."""
        creds = None
        
        # Load token if exists
        if self.token_path.exists():
            try:
                creds = Credentials.from_authorized_user_file(self.token_path, self.SCOPES)
                self.logger.info("Loaded existing Gmail token")
            except Exception as e:
                self.logger.warning(f"Failed to load token: {e}")
                creds = None
        
        # Refresh or create new credentials
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                self.logger.info("Refreshing expired token...")
                try:
                    creds.refresh(Request())
                except Exception as e:
                    self.logger.warning(f"Token refresh failed: {e}")
                    creds = None
            
            if not creds:
                self.logger.info("Starting OAuth flow...")
                print("\n" + "=" * 60)
                print("📧 GMAIL AUTHENTICATION")
                print("=" * 60)
                print("\nOpening browser for Gmail OAuth...")
                print("Please grant permissions when prompted.\n")
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, self.SCOPES)
                creds = flow.run_local_server(port=0)
                
                # Save token for next run
                self.token_path.write_text(creds.to_json())
                self.logger.info("Saved new Gmail token")
                print("✅ Authentication successful!\n")
        
        self.service = build('gmail', 'v1', credentials=creds)
        self.logger.info("Authenticated with Gmail API")
    
    def check_for_updates(self) -> list:
        """
        Check for new unread/important emails.
        
        Returns:
            List of new message dicts
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
            new_messages = []
            for msg in messages:
                if msg['id'] not in self.processed_ids:
                    new_messages.append(msg)
            
            if new_messages:
                self.logger.info(f"Found {len(new_messages)} new emails")
            
            return new_messages
            
        except Exception as e:
            self.logger.error(f"Error checking Gmail: {e}")
            return []
    
    def _get_message_details(self, message_id: str) -> dict:
        """Get full message details."""
        try:
            msg = self.service.users().messages().get(
                userId='me', 
                id=message_id,
                format='metadata',
                metadataHeaders=['From', 'To', 'Subject', 'Date']
            ).execute()
            
            # Extract headers
            headers = {h['name']: h['value'] for h in msg['payload']['headers']}
            
            return {
                'id': message_id,
                'from': headers.get('From', 'Unknown'),
                'to': headers.get('To', ''),
                'subject': headers.get('Subject', 'No Subject'),
                'date': headers.get('Date', datetime.now().isoformat()),
                'snippet': msg.get('snippet', '')
            }
        except Exception as e:
            self.logger.error(f"Error getting message details: {e}")
            return {}
    
    def create_action_file(self, message_id: str) -> Path:
        """
        Create action file for email.
        
        Args:
            message_id: Gmail message ID
            
        Returns:
            Path to created action file
        """
        # Get message details
        msg_details = self._get_message_details(message_id)
        
        if not msg_details.get('from'):
            return None
        
        timestamp = datetime.now()
        
        # Create safe filename from subject
        safe_subject = "".join(c if c.isalnum() else '_' for c in msg_details['subject'][:30])
        filename = f'EMAIL_{safe_subject}_{message_id[:8]}.md'
        filepath = self.needs_action / filename
        
        # Create action file content
        content = f'''---
type: email
from: "{msg_details['from']}"
to: "{msg_details['to']}"
subject: "{msg_details['subject']}"
received: "{msg_details['date']}"
gmail_id: {message_id}
created: {timestamp.isoformat()}
priority: high
status: pending
---

# Email Received

**From:** {msg_details['from']}  
**To:** {msg_details['to']}  
**Subject:** {msg_details['subject']}  
**Received:** {msg_details['date']}

## Email Preview

{msg_details['snippet']}

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
*AI Employee - Silver Tier*
'''
        
        filepath.write_text(content, encoding='utf-8')
        
        # Mark as processed
        self.processed_ids.add(message_id)
        self._save_processed_ids()
        
        self.logger.info(f"Created action file: {filepath.name}")
        
        return filepath
    
    def run(self):
        """
        Main run loop. Continuously checks for new emails and creates action files.
        """
        self.logger.info(f'Starting Gmail Watcher')
        self.logger.info(f'Vault path: {self.vault_path}')
        self.logger.info(f'Credentials: {self.credentials_path}')
        self.logger.info(f'Check interval: {self.check_interval}s')
        
        # Authenticate first
        try:
            self._authenticate()
        except Exception as e:
            self.logger.error(f'Authentication failed: {e}')
            print(f"\n❌ Authentication failed: {e}")
            print("\nMake sure:")
            print("1. credentials.json exists and is valid")
            print("2. Gmail API is enabled in Google Cloud Console")
            return
        
        print("\n" + "=" * 60)
        print("📧 GMAIL WATCHER")
        print("=" * 60)
        print(f"\n✅ Gmail Watcher started")
        print(f"📁 Monitoring for unread/important emails")
        print(f"📝 Action files: {self.needs_action}")
        print(f"⏱️  Check interval: {self.check_interval} seconds")
        print("\nPress Ctrl+C to stop...\n")
        
        try:
            while True:
                try:
                    # Check for new emails
                    messages = self.check_for_updates()
                    
                    for msg in messages:
                        self.create_action_file(msg['id'])
                    
                except Exception as e:
                    self.logger.error(f'Error in check loop: {e}')
                
                # Wait before next check
                time.sleep(self.check_interval)
                
        except KeyboardInterrupt:
            self.logger.info(f'Gmail Watcher stopped by user')
            print("\n👋 Gmail Watcher stopped")
        except Exception as e:
            self.logger.error(f'Fatal error: {e}')
            raise


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Gmail Watcher for AI Employee (Silver Tier)'
    )
    parser.add_argument(
        '--vault-path',
        default='../AI_Employee_Vault',
        help='Path to Obsidian vault'
    )
    parser.add_argument(
        '--credentials',
        default='../.qwen/credentials.json',
        help='Path to Gmail OAuth credentials JSON'
    )
    parser.add_argument(
        '--interval',
        type=int,
        default=120,
        help='Check interval in seconds (default: 120)'
    )
    parser.add_argument(
        '--once',
        action='store_true',
        help='Run once and exit (for testing)'
    )
    
    args = parser.parse_args()
    
    # Validate credentials file
    if not Path(args.credentials).exists():
        print(f"❌ Credentials file not found: {args.credentials}")
        print("\nPlease ensure credentials.json exists in the .qwen folder")
        sys.exit(1)
    
    # Create and run watcher
    watcher = GmailWatcher(
        vault_path=args.vault_path,
        credentials_path=args.credentials,
        check_interval=args.interval
    )
    
    if args.once:
        # Test mode - run once
        print("\n🧪 TEST MODE - Running once...")
        watcher._authenticate()
        messages = watcher.check_for_updates()
        print(f"\n📬 Found {len(messages)} new emails")
        for msg in messages:
            filepath = watcher.create_action_file(msg['id'])
            if filepath:
                print(f"   ✅ Created: {filepath.name}")
    else:
        # Normal mode - run continuously
        watcher.run()


if __name__ == '__main__':
    main()
