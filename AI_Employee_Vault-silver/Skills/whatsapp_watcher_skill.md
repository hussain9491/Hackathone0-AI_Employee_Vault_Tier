# WhatsApp Watcher Skill

> **Tier:** Silver  
> **Status:** Ready to Implement  
> **Dependencies:** Playwright, WhatsApp Web

---

## 📋 Overview

The WhatsApp Watcher monitors WhatsApp Web for new messages containing specific keywords (urgent, invoice, payment, etc.). When detected, it creates action files in the `Needs_Action/` folder.

**Use Case:** Capture urgent WhatsApp messages and convert them to actionable tasks.

---

## 🎯 Silver Tier Requirement

This skill fulfills:
- ✅ "Two or more Watcher scripts (e.g., Gmail + WhatsApp + LinkedIn)"
- ✅ Part of the Perception layer (Watcher architecture)
- ✅ "Lead Capture: Watch WhatsApp for keywords like 'Pricing'"

---

## ⚠️ Important Notice

**Terms of Service:** Using WhatsApp Web automation may violate WhatsApp's Terms of Service. Use at your own risk and consider:
- Using a business account
- Limiting automation frequency
- Only monitoring (not sending) messages
- Compliance with local regulations

**Alternative:** Use official [WhatsApp Business API](https://developers.facebook.com/docs/whatsapp/) for production use.

---

## 📦 Prerequisites

### 1. Python Dependencies

```bash
pip install playwright
playwright install chromium
```

### 2. Folder Structure

```
AI_Employee_Vault/
├── scripts/
│   ├── base_watcher.py         # Required (Bronze tier)
│   └── whatsapp_watcher.py     # Create this
├── .obsidian/
│   └── whatsapp_session/       # Browser session storage
└── Logs/                       # Watcher logs
```

---

## 🏗️ Implementation

### WhatsApp Watcher Script

**File:** `scripts/whatsapp_watcher.py`

```python
"""
WhatsApp Watcher for AI Employee

Monitors WhatsApp Web for messages containing keywords.

Usage:
    python whatsapp_watcher.py --vault-path .. --session-path /path/to/session

⚠️ WARNING: May violate WhatsApp Terms of Service. Use responsibly.
"""

import os
import sys
import argparse
import time
from pathlib import Path
from datetime import datetime

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

# Import base watcher
from base_watcher import BaseWatcher


class WhatsAppWatcher(BaseWatcher):
    """
    WhatsApp Web watcher that monitors for keyword messages.
    """
    
    # Keywords to monitor (case-insensitive)
    DEFAULT_KEYWORDS = [
        'urgent',
        'asap', 
        'invoice',
        'payment',
        'help',
        'emergency',
        'deadline',
        'meeting',
        'call me',
        'pricing'
    ]
    
    def __init__(self, vault_path: str, session_path: str = None,
                 keywords: list = None, check_interval: int = 60):
        """
        Initialize WhatsApp watcher.
        
        Args:
            vault_path: Path to Obsidian vault
            session_path: Path to store browser session (default: vault/.obsidian/whatsapp_session)
            keywords: List of keywords to monitor
            check_interval: Seconds between checks (default: 60)
        """
        super().__init__(vault_path, check_interval)
        
        self.session_path = Path(session_path) if session_path else self.vault_path / '.obsidian' / 'whatsapp_session'
        self.keywords = keywords or self.DEFAULT_KEYWORDS
        self.processed_messages = set()
        
        # Ensure session directory exists
        self.session_path.mkdir(parents=True, exist_ok=True)
        
        self.logger.info(f"Monitoring keywords: {self.keywords}")
    
    def check_for_updates(self) -> list:
        """
        Check WhatsApp Web for new messages with keywords.
        
        Returns:
            List of message dicts with chat and text
        """
        messages = []
        
        try:
            with sync_playwright() as p:
                # Launch browser with persistent session
                browser = p.chromium.launch_persistent_context(
                    user_data_dir=str(self.session_path),
                    headless=True,
                    args=[
                        '--disable-blink-features=AutomationControlled',
                        '--no-sandbox'
                    ]
                )
                
                page = browser.pages[0] if browser.pages else browser.new_page()
                
                # Navigate to WhatsApp Web
                self.logger.info("Navigating to WhatsApp Web...")
                page.goto('https://web.whatsapp.com', timeout=60000)
                
                # Wait for chat list to load
                try:
                    page.wait_for_selector('[data-testid="chat-list"]', timeout=30000)
                    self.logger.info("WhatsApp Web loaded")
                except PlaywrightTimeout:
                    self.logger.warning("WhatsApp Web timeout - may need QR scan")
                    browser.close()
                    return []
                
                # Wait for chats to load
                time.sleep(3)
                
                # Find all chat items
                chats = page.query_selector_all('[data-testid="chat-list"] > div[role="row"]')
                
                for chat in chats:
                    try:
                        # Get chat name
                        chat_name_el = chat.query_selector('[data-testid="chat-info"]')
                        chat_name = chat_name_el.inner_text() if chat_name_el else "Unknown"
                        
                        # Get last message
                        message_el = chat.query_selector('[data-testid="conversation-info"]')
                        if not message_el:
                            message_el = chat.query_selector('span[dir="auto"]')
                        
                        if not message_el:
                            continue
                            
                        message_text = message_el.inner_text().lower()
                        
                        # Check for keywords
                        matched_keywords = [
                            kw for kw in self.keywords 
                            if kw.lower() in message_text
                        ]
                        
                        if matched_keywords:
                            # Create unique ID
                            msg_id = f"{chat_name}_{datetime.now().strftime('%Y%m%d_%H')}"
                            
                            # Skip if already processed
                            if msg_id not in self.processed_messages:
                                messages.append({
                                    'id': msg_id,
                                    'chat_name': chat_name,
                                    'text': message_text,
                                    'matched_keywords': matched_keywords,
                                    'timestamp': datetime.now().isoformat()
                                })
                                self.logger.info(
                                    f"Match found in '{chat_name}': {matched_keywords}"
                                )
                        
                    except Exception as e:
                        self.logger.debug(f"Error processing chat: {e}")
                        continue
                
                browser.close()
                
        except Exception as e:
            self.logger.error(f"Error checking WhatsApp: {e}")
        
        return messages
    
    def create_action_file(self, message) -> Path:
        """
        Create action file for WhatsApp message.
        
        Args:
            message: Message dict from check_for_updates
            
        Returns:
            Path to created action file
        """
        try:
            content = f'''---
type: whatsapp_message
chat_name: {message['chat_name']}
received: {message['timestamp']}
keywords: {', '.join(message['matched_keywords'])}
status: pending
priority: high
---

# WhatsApp Message Received

**Chat:** {message['chat_name']}  
**Received:** {message['timestamp']}  
**Keywords:** {', '.join(message['matched_keywords'])}

## Message Content

"{message['text']}"

## Suggested Actions

- [ ] Open WhatsApp and read full conversation
- [ ] Reply to message
- [ ] Take required action
- [ ] Mark as processed

## Response Draft

_Add your draft response here_

## Notes

_Add any additional notes here_

---
*Created by WhatsApp Watcher*
⚠️ Verify message in WhatsApp before taking action
'''
            
            # Create filename
            safe_name = "".join(c if c.isalnum() else '_' for c in message['chat_name'][:20])
            filepath = self.needs_action / f'WHATSAPP_{safe_name}_{datetime.now().strftime("%Y%m%d_%H%M")}.md'
            
            filepath.write_text(content)
            
            # Mark as processed
            self.processed_messages.add(message['id'])
            
            self.logger.info(f"Created action file: {filepath.name}")
            
            return filepath
            
        except Exception as e:
            self.logger.error(f"Error creating action file: {e}")
            return None
    
    def run(self):
        """
        Run the WhatsApp watcher with QR code handling.
        """
        self.logger.info(f'Starting {self.__class__.__name__}')
        self.logger.info(f'Vault path: {self.vault_path}')
        self.logger.info(f'Session path: {self.session_path}')
        self.logger.info(f'Keywords: {self.keywords}')
        
        # First run: Check if session exists
        session_files = list(self.session_path.glob('*'))
        if not session_files:
            print("\n" + "=" * 60)
            print("⚠️  FIRST TIME SETUP")
            print("=" * 60)
            print("\nWhatsApp Web requires QR code authentication.")
            print("\nOptions:")
            print("1. Run with headless=False to scan QR code")
            print("2. Use existing WhatsApp session from another tool")
            print("3. Consider WhatsApp Business API for production")
            print("\n" + "=" * 60)
        
        print("\n✅ WhatsApp Watcher starting...")
        print(f"📱 Monitoring for keywords: {', '.join(self.keywords)}")
        print(f"📁 Action files: {self.needs_action}")
        print("\nPress Ctrl+C to stop...\n")
        
        try:
            while True:
                try:
                    messages = self.check_for_updates()
                    for msg in messages:
                        self.create_action_file(msg)
                except Exception as e:
                    self.logger.error(f'Error in check loop: {e}')
                
                time.sleep(self.check_interval)
                
        except KeyboardInterrupt:
            self.logger.info(f'{self.__class__.__name__} stopped by user')
        except Exception as e:
            self.logger.error(f'Fatal error: {e}')
            raise


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='WhatsApp Watcher for AI Employee')
    parser.add_argument('--vault-path', default='..', help='Path to Obsidian vault')
    parser.add_argument('--session-path', help='Path to browser session folder')
    parser.add_argument('--keywords', nargs='+', help='Keywords to monitor')
    parser.add_argument('--interval', type=int, default=60, help='Check interval in seconds')
    parser.add_argument('--headless', action='store_true', default=True, help='Run headless')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("💬 WHATSAPP WATCHER")
    print("=" * 60)
    print("\n⚠️  WARNING: May violate WhatsApp Terms of Service")
    print("   Use responsibly and at your own risk\n")
    
    watcher = WhatsAppWatcher(
        vault_path=args.vault_path,
        session_path=args.session_path,
        keywords=args.keywords,
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
# 1. Install Playwright
pip install playwright
playwright install chromium

# 2. Run WhatsApp watcher
cd AI_Employee_Vault/scripts
python whatsapp_watcher.py --vault-path ..
```

### First Run - QR Code Authentication

The first run will require WhatsApp Web authentication. You have two options:

**Option A: Temporary Headful Run**
```bash
# Modify script temporarily: headless=False
# This opens browser for QR scan
python whatsapp_watcher.py --vault-path .. --headless
```

**Option B: Manual Session Copy**
1. Open WhatsApp Web in Chrome
2. Authenticate with QR code
3. Copy Chrome session data to `whatsapp_session/` folder

### Daily Usage

```bash
# Start WhatsApp watcher (runs continuously)
python whatsapp_watcher.py --vault-path .. --interval 60
```

### Custom Keywords

```bash
# Monitor specific keywords
python whatsapp_watcher.py --vault-path .. --keywords urgent invoice payment "call me"
```

---

## 📁 Example Output

### Action File Created in `Needs_Action/`

```markdown
---
type: whatsapp_message
chat_name: John - Client
received: 2026-03-14T15:30:00
keywords: urgent, invoice
status: pending
priority: high
---

# WhatsApp Message Received

**Chat:** John - Client  
**Received:** 2026-03-14T15:30:00  
**Keywords:** urgent, invoice

## Message Content

"Hi, can you send the invoice urgently? Need it for payment processing."

## Suggested Actions

- [ ] Open WhatsApp and read full conversation
- [ ] Reply to message
- [ ] Send invoice
- [ ] Mark as processed

## Response Draft

_Hi John, I'll send the invoice right away..._

## Notes

_Client mentioned payment processing - follow up next week_

---
*Created by WhatsApp Watcher*
⚠️ Verify message in WhatsApp before taking action
```

---

## ⚙️ Configuration

### Keyword Configuration

Default keywords:
```python
DEFAULT_KEYWORDS = [
    'urgent', 'asap', 'invoice', 'payment', 'help',
    'emergency', 'deadline', 'meeting', 'call me', 'pricing'
]
```

Custom keywords:
```bash
python whatsapp_watcher.py --keywords "buy now" "interested" "pricing" "quote"
```

### Check Interval

```bash
# Check every 30 seconds (more responsive, more resource usage)
python whatsapp_watcher.py --interval 30

# Check every 5 minutes (less resource usage)
python whatsapp_watcher.py --interval 300
```

---

## 🔒 Security & Privacy

### Best Practices

1. **Session Storage** - Store session in encrypted location
2. **Limited Monitoring** - Only check when necessary
3. **No Message Storage** - Don't store full message history
4. **Compliance** - Ensure compliance with local privacy laws

### What This Watcher Does

- ✅ Monitors WhatsApp Web for keywords
- ✅ Creates action files with message snippets
- ✅ Stores session locally

### What This Watcher Does NOT Do

- ❌ Send messages
- ❌ Access message history
- ❌ Share data externally
- ❌ Store full conversations

---

## 🐛 Troubleshooting

### Error: "WhatsApp Web timeout"

**Cause:** QR code needs to be scanned

**Fix:**
1. Run with browser visible to scan QR
2. Or copy existing session from Chrome

### Error: "playwright not found"

**Fix:**
```bash
pip install playwright
playwright install chromium
```

### No messages detected

**Check:**
1. Is WhatsApp Web loaded?
2. Are there unread messages?
3. Do messages contain your keywords?
4. Try less restrictive keywords

### Session expired

**Fix:** Delete session and re-authenticate:
```bash
rm -rf .obsidian/whatsapp_session/*
python whatsapp_watcher.py --vault-path ..
```

---

## 📊 Testing

### Test Script

```python
# test_whatsapp_watcher.py
from whatsapp_watcher import WhatsAppWatcher

# Create watcher
watcher = WhatsAppWatcher(
    vault_path='..',
    keywords=['test', 'urgent']
)

# Test check
print("Testing WhatsApp check...")
messages = watcher.check_for_updates()
print(f"Found {len(messages)} messages")

# Test action file
if messages:
    filepath = watcher.create_action_file(messages[0])
    print(f"Created: {filepath}")
```

---

## 🔗 Related Skills

| Skill | Purpose |
|-------|---------|
| `gmail_watcher_skill.md` | Monitor Gmail inbox |
| `mcp_email_skill.md` | Send emails via MCP |
| `plan_generator_skill.md` | Create action plans |

---

## 📚 Resources

- [Playwright Documentation](https://playwright.dev/python/)
- [WhatsApp Web](https://web.whatsapp.com/)
- [WhatsApp Business API](https://developers.facebook.com/docs/whatsapp/)
- [Hackathon Doc Section 2A](../Personal%20AI%20Employee%20Hackathon%200_%20Building%20Autonomous%20FTEs%20in%202026.md#watcher-architecture)

---

*Skill Version: 1.0*  
*Last Updated: 2026-03-14*  
*Silver Tier Component*  
*⚠️ Use responsibly - may violate WhatsApp ToS*
