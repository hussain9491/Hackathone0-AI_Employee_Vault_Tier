---
name: email-mcp
description: |
  MCP server for sending emails via Gmail API or SMTP. Enables Qwen to send emails,
  create drafts, and manage email workflows. Includes human-in-the-loop approval
  for sensitive emails.
---

# Email MCP Server Skill

Send emails via MCP server with approval workflow.

## Installation

### Option A: Python (Recommended)

```bash
cd AI_Employee_Vault/scripts/mcp-email
uv init email-server
uv venv
source .venv/Scripts/activate  # Windows
uv add mcp httpx googleapis google-auth
```

### Option B: Node.js

```bash
cd AI_Employee_Vault/scripts/mcp-email
npm init -y
npm install @modelcontextprotocol/sdk zod nodemailer
```

## Quick Reference

### Start Email MCP Server

```bash
# Python version
python AI_Employee_Vault/scripts/mcp-email/email_server.py

# Node.js version
node AI_Employee_Vault/scripts/mcp-email/email_server.js
```

### Configure in Qwen/Claude

**File:** `~/.config/qwen-code/mcp.json`

```json
{
  "mcpServers": {
    "email": {
      "command": "python",
      "args": ["C:/Users/user1542/Documents/GitHub/H-0-Q4/AI_Employee_Vault/scripts/mcp-email/email_server.py"],
      "env": {
        "SMTP_HOST": "smtp.gmail.com",
        "SMTP_PORT": "587",
        "SMTP_USER": "your-email@gmail.com",
        "SMTP_PASS": "your-app-password"
      }
    }
  }
}
```

### With Qwen

```bash
# Send email directly
qwen "Use the email-mcp server to send an email to test@example.com"

# Create draft for approval
qwen "Use email-mcp to create a draft email for the invoice"

# Check sent emails
qwen "Use email-mcp to search sent emails for 'invoice'"
```

## Setup: Gmail App Password

### Step 1: Enable 2FA

1. Go to [Google Account](https://myaccount.google.com/)
2. Security → 2-Step Verification → Enable

### Step 2: Create App Password

1. Security → 2-Step Verification → App passwords
2. Select app: "Mail"
3. Select device: "Other"
4. Name: "AI Employee"
5. Copy 16-character password
6. Use in SMTP_PASS environment variable

## Email MCP Server Implementation

### Python Version

```python
# AI_Employee_Vault/scripts/mcp-email/email_server.py
from mcp.server.fastmcp import FastMCP
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from pathlib import Path

mcp = FastMCP("email")

VAULT_PATH = Path(os.environ.get('VAULT_PATH', 'AI_Employee_Vault'))

@mcp.tool()
async def send_email(to: str, subject: str, body: str, is_html: bool = False) -> str:
    """
    Send an email via SMTP.
    
    Args:
        to: Recipient email address
        subject: Email subject
        body: Email body text
        is_html: Whether body is HTML (default: False)
    
    Returns:
        Confirmation message
    """
    msg = MIMEMultipart('html' if is_html else 'plain')
    msg['From'] = os.environ['SMTP_USER']
    msg['To'] = to
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'html' if is_html else 'plain'))
    
    try:
        with smtplib.SMTP(os.environ['SMTP_HOST'], int(os.environ.get('SMTP_PORT', 587))) as server:
            server.starttls()
            server.login(os.environ['SMTP_USER'], os.environ['SMTP_PASS'])
            server.send_message(msg)
        
        # Log sent email
        log_sent_email(to, subject)
        return f"✅ Email sent to {to}"
    except Exception as e:
        return f"❌ Error: {str(e)}"

@mcp.tool()
async def create_draft(to: str, subject: str, body: str) -> str:
    """
    Create a draft email (requires approval before sending).
    
    Args:
        to: Recipient email address
        subject: Email subject
        body: Email body
    
    Returns:
        Draft file path
    """
    draft_path = VAULT_PATH / 'Pending_Approval' / f"DRAFT_{subject.replace(' ', '_')}.md"
    draft_path.parent.mkdir(parents=True, exist_ok=True)
    
    content = f'''---
type: email_draft
to: {to}
subject: {subject}
created: {datetime.now().isoformat()}
status: pending
---

# Email Draft

**To:** {to}
**Subject:** {subject}

## Body

{body}

## To Approve

Move this file to /Approved folder to send.

## To Reject

Move to /Rejected or delete.
'''
    draft_path.write_text(content)
    return f"📝 Draft created: {draft_path}"

@mcp.tool()
async def search_sent(query: str, max_results: int = 10) -> str:
    """
    Search sent emails.
    
    Args:
        query: Search query
        max_results: Maximum results (default: 10)
    
    Returns:
        Search results
    """
    log_file = VAULT_PATH / 'Logs' / 'sent_emails.json'
    if not log_file.exists():
        return "No sent emails found"
    
    import json
    logs = json.loads(log_file.read_text())
    results = [l for l in logs if query.lower() in l.get('subject', '').lower() or query.lower() in l.get('to', '').lower()]
    
    return f"Found {len(results[:max_results])} emails:\n" + "\n".join(f"- {r['to']} - {r['subject']} ({r['date']})" for r in results[:max_results])

def log_sent_email(to: str, subject: str):
    """Log sent email to file."""
    import json
    log_file = VAULT_PATH / 'Logs' / 'sent_emails.json'
    logs = []
    if log_file.exists():
        logs = json.loads(log_file.read_text())
    logs.append({
        'to': to,
        'subject': subject,
        'date': datetime.now().isoformat()
    })
    log_file.write_text(json.dumps(logs, indent=2))

if __name__ == "__main__":
    mcp.run(transport="stdio")
```

## Workflow: Email with Approval

```
1. Qwen needs to send email
         ↓
2. Creates draft in Pending_Approval/
         ↓
3. User reviews and moves to Approved/
         ↓
4. Qwen sends via MCP server
         ↓
5. Logs to sent_emails.json
```

## Environment Variables

Create `.env` file:

```bash
# Email MCP Configuration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASS=xxxx-xxxx-xxxx-xxxx  # App password
VAULT_PATH=C:/Users/user1542/Documents/GitHub/H-0-Q4/AI_Employee_Vault
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "Authentication failed" | Use app password, not regular password |
| "Connection timeout" | Check SMTP_HOST and SMTP_PORT |
| Server not showing up | Verify absolute paths in mcp.json |
| Email not sending | Check spam folder, verify 2FA enabled |

## Security

- ✅ Use app passwords (not main password)
- ✅ Store credentials in environment variables
- ✅ Log all sent emails
- ✅ Require approval for external emails

## Related Skills

- `gmail-watcher` - Receive emails
- `approval-workflow-v2` - Approve email drafts
- `linkedin-poster` - Post to LinkedIn

---

*Skill Version: 1.0 | Last Updated: 2026-03-14 | Silver Tier*
