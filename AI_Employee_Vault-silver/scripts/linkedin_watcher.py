"""
LinkedIn Watcher for AI Employee

Monitors LinkedIn for connection requests, messages, and engagement.
Creates action files for Qwen to process and draft responses.
Part of Silver Tier deliverables for automated lead generation.

Usage:
    python linkedin_watcher.py --vault-path ../AI_Employee_Vault

Note: Uses Playwright for LinkedIn Web automation.
      First run requires manual LinkedIn login.

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

try:
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
except ImportError:
    print("❌ Missing dependencies. Install with:")
    print("   pip install playwright")
    print("   playwright install chromium")
    sys.exit(1)


class LinkedInWatcher:
    """
    LinkedIn watcher that monitors for connection requests, messages, and notifications.
    Creates action files in the Needs_Action folder for Qwen to process.
    """
    
    # Keywords that indicate potential leads
    LEAD_KEYWORDS = [
        'interested',
        'pricing',
        'quote',
        'demo',
        'service',
        'product',
        'collaboration',
        'partnership',
        'opportunity',
        'hire',
        'consulting',
        'project'
    ]
    
    def __init__(self, vault_path: str, session_path: str = None,
                 check_interval: int = 300):
        """
        Initialize LinkedIn watcher.
        
        Args:
            vault_path: Path to Obsidian vault
            session_path: Path to store browser session (default: vault/.obsidian/linkedin_session)
            check_interval: Seconds between checks (default: 300 = 5 minutes)
        """
        self.vault_path = Path(vault_path)
        self.session_path = Path(session_path) if session_path else self.vault_path / '.obsidian' / 'linkedin_session'
        self.check_interval = check_interval
        self.needs_action = self.vault_path / 'Needs_Action'
        self.logs_folder = self.vault_path / 'Logs'
        
        # Ensure directories exist
        self.needs_action.mkdir(parents=True, exist_ok=True)
        self.logs_folder.mkdir(parents=True, exist_ok=True)
        self.session_path.mkdir(parents=True, exist_ok=True)
        
        # Setup logging
        self._setup_logging()
        
        # Track processed items
        self.processed_connections = set()
        self.processed_messages = set()
        self._load_processed_ids()
        
    def _setup_logging(self):
        """Setup logging to file and console."""
        log_file = self.logs_folder / f'linkedin_watcher_{datetime.now().strftime("%Y%m%d")}.log'
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('LinkedInWatcher')
    
    def _load_processed_ids(self):
        """Load previously processed item IDs from disk."""
        conn_file = self.logs_folder / 'linkedin_connections.txt'
        msg_file = self.logs_folder / 'linkedin_messages.txt'
        
        if conn_file.exists():
            self.processed_connections = set(conn_file.read_text().strip().split('\n'))
        if msg_file.exists():
            self.processed_messages = set(msg_file.read_text().strip().split('\n'))
        
        self.logger.info(f"Loaded {len(self.processed_connections)} connections, {len(self.processed_messages)} messages")
    
    def _save_processed_ids(self):
        """Save processed item IDs to disk."""
        conn_file = self.logs_folder / 'linkedin_connections.txt'
        msg_file = self.logs_folder / 'linkedin_messages.txt'
        
        conn_file.write_text('\n'.join(self.processed_connections))
        msg_file.write_text('\n'.join(self.processed_messages))
    
    def _check_linkedin(self) -> dict:
        """
        Check LinkedIn for new activity.
        
        Returns:
            Dict with connections, messages, and notifications
        """
        results = {
            'connections': [],
            'messages': [],
            'notifications': []
        }
        
        try:
            with sync_playwright() as p:
                # Launch browser with persistent session
                self.logger.info("Launching browser...")
                browser = p.chromium.launch_persistent_context(
                    user_data_dir=str(self.session_path),
                    headless=True,
                    args=[
                        '--disable-blink-features=AutomationControlled',
                        '--no-sandbox',
                        '--disable-dev-shm-usage'
                    ]
                )
                
                page = browser.pages[0] if browser.pages else browser.new_page()
                
                # Navigate to LinkedIn
                self.logger.info("Navigating to LinkedIn...")
                page.goto('https://www.linkedin.com/', timeout=60000)
                
                # Check if logged in
                try:
                    page.wait_for_selector('.global-nav', timeout=10000)
                    self.logger.info("LinkedIn session valid")
                except PlaywrightTimeout:
                    self.logger.warning("Not logged in to LinkedIn")
                    browser.close()
                    return results
                
                # Small delay for page to load
                time.sleep(3)
                
                # Check for connection requests
                try:
                    self.logger.info("Checking connection requests...")
                    page.goto('https://www.linkedin.com/mynetwork/', timeout=30000)
                    time.sleep(2)
                    
                    # Look for invitation items
                    invitations = page.query_selector_all('.invitation-card')
                    
                    for invite in invitations[:5]:  # Limit to 5
                        try:
                            name_el = invite.query_selector('.invitation-card__actor-name')
                            headline_el = invite.query_selector('.invitation-card__actor-headline')
                            
                            if name_el:
                                name = name_el.inner_text()
                                headline = headline_el.inner_text() if headline_el else ''
                                invite_id = f"conn_{name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}"
                                
                                if invite_id not in self.processed_connections:
                                    results['connections'].append({
                                        'id': invite_id,
                                        'name': name,
                                        'headline': headline
                                    })
                        except Exception as e:
                            self.logger.debug(f"Error processing invitation: {e}")
                
                except Exception as e:
                    self.logger.debug(f"Error checking connections: {e}")
                
                # Check for messages
                try:
                    self.logger.info("Checking messages...")
                    page.goto('https://www.linkedin.com/messaging/', timeout=30000)
                    time.sleep(2)
                    
                    # Look for conversation items with unread indicator
                    conversations = page.query_selector_all('.msg-conversation-card')
                    
                    for conv in conversations[:5]:  # Limit to 5
                        try:
                            # Check for unread indicator
                            unread = conv.query_selector('[aria-label="Unread"]')
                            if not unread:
                                continue
                            
                            name_el = conv.query_selector('.msg-conversation-card__name')
                            snippet_el = conv.query_selector('.msg-conversation-card__text-preview')
                            
                            if name_el:
                                name = name_el.inner_text()
                                snippet = snippet_el.inner_text() if snippet_el else ''
                                
                                # Check for lead keywords
                                is_lead = any(kw in snippet.lower() for kw in self.LEAD_KEYWORDS)
                                
                                msg_id = f"msg_{name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}"
                                
                                if msg_id not in self.processed_messages:
                                    results['messages'].append({
                                        'id': msg_id,
                                        'name': name,
                                        'snippet': snippet,
                                        'is_lead': is_lead
                                    })
                        except Exception as e:
                            self.logger.debug(f"Error processing message: {e}")
                
                except Exception as e:
                    self.logger.debug(f"Error checking messages: {e}")
                
                browser.close()
                
        except Exception as e:
            self.logger.error(f"Error checking LinkedIn: {e}")
        
        return results
    
    def create_connection_action_file(self, connection: dict) -> Path:
        """Create action file for new connection request."""
        timestamp = datetime.now()
        filename = f"LINKEDIN_CONNECT_{connection['name'].replace(' ', '_')}_{timestamp.strftime('%Y%m%d')}.md"
        filepath = self.needs_action / filename
        
        content = f'''---
type: linkedin_connection
name: "{connection['name']}"
headline: "{connection['headline']}"
received: "{timestamp.isoformat()}"
priority: medium
status: pending
---

# LinkedIn Connection Request

**Name:** {connection['name']}  
**Headline:** {connection['headline']}  
**Received:** {timestamp.strftime('%Y-%m-%d %H:%M')}

## Suggested Actions

- [ ] Review profile
- [ ] Accept connection request
- [ ] Send personalized welcome message
- [ ] Add to CRM if relevant
- [ ] Move to /Done when processed

## Welcome Message Draft

_Hi {connection['name'].split()[0]}, thanks for connecting! I'd love to learn more about your work at..._

## Notes

_Add any notes about this connection_

---
*Created by LinkedIn Watcher*
*AI Employee - Silver Tier*
'''
        
        filepath.write_text(content)
        
        self.processed_connections.add(connection['id'])
        self._save_processed_ids()
        
        self.logger.info(f"Created connection action file: {filepath.name}")
        
        return filepath
    
    def create_message_action_file(self, message: dict) -> Path:
        """Create action file for new message."""
        timestamp = datetime.now()
        priority = 'high' if message['is_lead'] else 'medium'
        filename = f"LINKEDIN_MSG_{message['name'].replace(' ', '_')}_{timestamp.strftime('%Y%m%d')}.md"
        filepath = self.needs_action / filename
        
        content = f'''---
type: linkedin_message
name: "{message['name']}"
received: "{timestamp.isoformat()}"
priority: {priority}
status: pending
is_lead: {str(message['is_lead']).lower()}
---

# LinkedIn Message Received

**From:** {message['name']}  
**Received:** {timestamp.strftime('%Y-%m-%d %H:%M')}  
**Priority:** {'🔴 High (Potential Lead)' if message['is_lead'] else '🟡 Medium'}

## Message Preview

{message['snippet']}

## Suggested Actions

- [ ] Read full message on LinkedIn
- [ ] Draft response
- [ ] {"Qualify as potential lead" if message['is_lead'] else "Respond appropriately"}
- [ ] Move to /Done when processed

## Response Draft

_Add your draft response here_

## Notes

_Add any additional notes here_

---
*Created by LinkedIn Watcher*
*AI Employee - Silver Tier*
'''
        
        filepath.write_text(content)
        
        self.processed_messages.add(message['id'])
        self._save_processed_ids()
        
        self.logger.info(f"Created message action file: {filepath.name}")
        
        return filepath
    
    def run(self):
        """
        Main run loop. Continuously checks LinkedIn and creates action files.
        """
        self.logger.info(f'Starting LinkedIn Watcher')
        self.logger.info(f'Vault path: {self.vault_path}')
        self.logger.info(f'Session path: {self.session_path}')
        self.logger.info(f'Check interval: {self.check_interval}s')
        
        print("\n" + "=" * 60)
        print("💼 LINKEDIN WATCHER")
        print("=" * 60)
        
        # First run - check if session exists
        session_files = list(self.session_path.glob('*'))
        if not session_files:
            print("\n⚠️  FIRST TIME SETUP")
            print("=" * 60)
            print("\nLinkedIn requires manual login for first run.")
            print("\nTo initialize session:")
            print("1. Run with --login flag: python linkedin_watcher.py --login")
            print("2. Or manually open LinkedIn in Chrome and login")
            print("3. Then run this watcher again")
            print("\n" + "=" * 60)
            return
        
        print(f"\n✅ LinkedIn Watcher started")
        print(f"📁 Session: {self.session_path}")
        print(f"📝 Action files: {self.needs_action}")
        print(f"⏱️  Check interval: {self.check_interval} seconds")
        print(f"🔍 Monitoring: Connection requests, Messages")
        print("\nPress Ctrl+C to stop...\n")
        
        try:
            while True:
                try:
                    # Check LinkedIn
                    results = self._check_linkedin()
                    
                    # Process connection requests
                    for conn in results['connections']:
                        self.create_connection_action_file(conn)
                    
                    # Process messages
                    for msg in results['messages']:
                        self.create_message_action_file(msg)
                    
                    if results['connections'] or results['messages']:
                        print(f"   📬 Found {len(results['connections'])} connections, {len(results['messages'])} messages")
                    
                except Exception as e:
                    self.logger.error(f'Error in check loop: {e}')
                
                # Wait before next check
                time.sleep(self.check_interval)
                
        except KeyboardInterrupt:
            self.logger.info(f'LinkedIn Watcher stopped by user')
            print("\n👋 LinkedIn Watcher stopped")
        except Exception as e:
            self.logger.error(f'Fatal error: {e}')
            raise


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='LinkedIn Watcher for AI Employee (Silver Tier)'
    )
    parser.add_argument(
        '--vault-path',
        default='../AI_Employee_Vault',
        help='Path to Obsidian vault'
    )
    parser.add_argument(
        '--session-path',
        help='Path to browser session folder'
    )
    parser.add_argument(
        '--interval',
        type=int,
        default=300,
        help='Check interval in seconds (default: 300)'
    )
    parser.add_argument(
        '--login',
        action='store_true',
        help='Open browser for LinkedIn login (first time setup)'
    )
    parser.add_argument(
        '--once',
        action='store_true',
        help='Run once and exit (for testing)'
    )
    
    args = parser.parse_args()
    
    # Create watcher
    watcher = LinkedInWatcher(
        vault_path=args.vault_path,
        session_path=args.session_path,
        check_interval=args.interval
    )
    
    if args.login:
        # Login mode
        print("\n" + "=" * 60)
        print("🔐 LINKEDIN LOGIN")
        print("=" * 60)
        print("\nOpening browser for LinkedIn login...")
        print("Please login and wait for the page to fully load.\n")
        
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch_persistent_context(
                    user_data_dir=str(watcher.session_path),
                    headless=False  # Visible for login
                )
                page = browser.pages[0] if browser.pages else browser.new_page()
                page.goto('https://www.linkedin.com/login')
                
                print("👉 Login to LinkedIn in the browser...")
                print("👉 After successful login, wait for your feed to load")
                print("👉 Then press Enter here to save the session\n")
                input("Press Enter after you see your LinkedIn feed...")
                
                browser.close()
                print("✅ Session saved! You can now run the watcher normally.")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    elif args.once:
        # Test mode
        print("\n🧪 TEST MODE - Running once...")
        results = watcher._check_linkedin()
        print(f"\n📬 Found {len(results['connections'])} connections, {len(results['messages'])} messages")
        for conn in results['connections']:
            filepath = watcher.create_connection_action_file(conn)
            if filepath:
                print(f"   ✅ Created: {filepath.name}")
        for msg in results['messages']:
            filepath = watcher.create_message_action_file(msg)
            if filepath:
                print(f"   ✅ Created: {filepath.name}")
    
    else:
        # Normal mode
        watcher.run()


if __name__ == '__main__':
    main()
