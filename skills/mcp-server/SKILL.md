---
name: mcp-server
description: |
  Model Context Protocol (MCP) server for AI Employee. Exposes tools and resources
  to AI clients (Qwen, Claude) for interacting with external systems. Use for sending
  emails, accessing databases, browser automation, and other external integrations.
---

# MCP Server Skill

Build and run MCP (Model Context Protocol) servers for AI Employee integrations.

## What is MCP?

**MCP (Model Context Protocol)** is an open standard for connecting AI applications to external systems.

**Analogy:** MCP is like a **USB-C port for AI** — it provides a standardized way to connect AI to your data and tools.

### What MCP Enables
- 📧 Send emails via Gmail/SMTP
- 🌐 Browser automation via Playwright
- 📊 Access databases and APIs
- 📁 Read/write local files
- 🔔 Send notifications (Slack, SMS)

---

## Installation

### Python (Recommended for AI Employee)

```bash
# Install uv (Python package manager)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create MCP server project
cd AI_Employee_Vault/scripts
uv init mcp-server
cd mcp-server
uv venv
source .venv/Scripts/activate  # Windows
uv add "mcp[cli]" httpx

# Or with pip
pip install mcp httpx
```

### Node.js

```bash
cd AI_Employee_Vault/scripts
mkdir mcp-server && cd mcp-server
npm init -y
npm install @modelcontextprotocol/sdk zod@3
npm install -D @types/node typescript
```

---

## Quick Reference

### Create MCP Server (Python)

```python
# AI_Employee_Vault/scripts/mcp-server/email_server.py
from mcp.server.fastmcp import FastMCP
import smtplib
from email.mime.text import MIMEText

mcp = FastMCP("ai-employee-email")

@mcp.tool()
async def send_email(to: str, subject: str, body: str) -> str:
    """
    Send an email via SMTP.
    
    Args:
        to: Recipient email address
        subject: Email subject line
        body: Email body text
    
    Returns:
        Confirmation message with message ID
    """
    # Create message
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = 'ai-employee@company.com'
    msg['To'] = to
    
    # Send via SMTP
    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login('user@gmail.com', 'password')
        server.send_message(msg)
    
    return f"Email sent to {to} with subject: {subject}"

@mcp.tool()
async def send_approval_request(to: str, action_type: str, details: str) -> str:
    """
    Send an approval request email.
    
    Args:
        to: Approver email address
        action_type: Type of action requiring approval
        details: Details of the action
    
    Returns:
        Confirmation message
    """
    body = f"""
Approval Request

Action Type: {action_type}
Details: {details}

Please reply with APPROVE or REJECT.
"""
    return await send_email(to, f"Approval Request: {action_type}", body)

if __name__ == "__main__":
    mcp.run(transport="stdio")
```

### Create MCP Server (Node.js)

```javascript
// AI_Employee_Vault/scripts/mcp-server/email_server.js
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";

const server = new McpServer({ 
  name: "ai-employee-email", 
  version: "1.0.0" 
});

server.registerTool("send_email", {
  description: "Send an email via SMTP",
  inputSchema: {
    to: z.string().email().describe("Recipient email address"),
    subject: z.string().describe("Email subject"),
    body: z.string().describe("Email body text"),
  },
}, async ({ to, subject, body }) => {
  // Email sending logic here
  return { 
    content: [{ type: "text", text: `Email sent to ${to}` }] 
  };
});

server.registerTool("send_approval_request", {
  description: "Send an approval request email",
  inputSchema: {
    to: z.string().email().describe("Approver email"),
    action_type: z.string().describe("Type of action"),
    details: z.string().describe("Action details"),
  },
}, async ({ to, action_type, details }) => {
  return { 
    content: [{ type: "text", text: `Approval request sent to ${to}` }] 
  };
});

async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
}

main().catch(console.error);
```

---

### Configure MCP Client (Qwen/Claude)

**File:** `~/.config/qwen-code/mcp.json` (or `claude_desktop_config.json`)

```json
{
  "mcpServers": {
    "ai-employee-email": {
      "command": "python",
      "args": [
        "C:/Users/user1542/Documents/GitHub/H-0-Q4/AI_Employee_Vault/scripts/mcp-server/email_server.py"
      ],
      "env": {
        "SMTP_HOST": "smtp.gmail.com",
        "SMTP_PORT": "587",
        "SMTP_USER": "your-email@gmail.com",
        "SMTP_PASS": "your-app-password"
      }
    },
    "ai-employee-files": {
      "command": "python",
      "args": [
        "C:/Users/user1542/Documents/GitHub/H-0-Q4/AI_Employee_Vault/scripts/mcp-server/file_server.py"
      ]
    }
  }
}
```

---

## MCP Server Templates

### 1. Email Server (Gmail/SMTP)

```python
# email_server.py
from mcp.server.fastmcp import FastMCP
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

mcp = FastMCP("email")

@mcp.tool()
async def send_email(to: str, subject: str, body: str, is_html: bool = False) -> str:
    """Send an email via SMTP."""
    msg = MIMEMultipart('html' if is_html else 'plain')
    msg['From'] = os.environ['SMTP_USER']
    msg['To'] = to
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'html' if is_html else 'plain'))
    
    with smtplib.SMTP(os.environ['SMTP_HOST'], int(os.environ.get('SMTP_PORT', 587))) as server:
        server.starttls()
        server.login(os.environ['SMTP_USER'], os.environ['SMTP_PASS'])
        server.send_message(msg)
    
    return f"✅ Email sent to {to}"

@mcp.tool()
async def send_draft(to: str, subject: str, body: str) -> str:
    """Create a draft email (requires approval before sending)."""
    # Save draft to file for approval workflow
    draft_path = f"Drafts/{subject.replace(' ', '_')}.md"
    with open(draft_path, 'w') as f:
        f.write(f"To: {to}\nSubject: {subject}\n\n{body}")
    
    return f"📝 Draft created: {draft_path}"

if __name__ == "__main__":
    mcp.run(transport="stdio")
```

### 2. File Server (Vault Access)

```python
# file_server.py
from mcp.server.fastmcp import FastMCP
from pathlib import Path
import shutil

mcp = FastMCP("files")

VAULT_PATH = Path("C:/Users/user1542/Documents/GitHub/H-0-Q4/AI_Employee_Vault")

@mcp.tool()
async def read_file(path: str) -> str:
    """Read a file from the vault."""
    file_path = VAULT_PATH / path
    if not file_path.exists():
        return f"❌ File not found: {path}"
    return file_path.read_text()

@mcp.tool()
async def write_file(path: str, content: str) -> str:
    """Write content to a file in the vault."""
    file_path = VAULT_PATH / path
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(content)
    return f"✅ Written to {path}"

@mcp.tool()
async def move_file(source: str, destination: str) -> str:
    """Move a file within the vault (e.g., for approval workflow)."""
    src_path = VAULT_PATH / source
    dst_path = VAULT_PATH / destination
    
    if not src_path.exists():
        return f"❌ Source not found: {source}"
    
    dst_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(src_path), str(dst_path))
    return f"✅ Moved {source} → {destination}"

@mcp.tool()
async def list_folder(path: str) -> str:
    """List files in a vault folder."""
    folder_path = VAULT_PATH / path
    if not folder_path.exists():
        return f"❌ Folder not found: {path}"
    
    files = [f.name for f in folder_path.iterdir()]
    return f"📁 {path}:\n" + "\n".join(f"  - {f}" for f in files)

if __name__ == "__main__":
    mcp.run(transport="stdio")
```

### 3. Browser Server (Playwright)

```python
# browser_server.py
from mcp.server.fastmcp import FastMCP
from playwright.sync_api import sync_playwright

mcp = FastMCP("browser")

@mcp.tool()
async def navigate(url: str) -> str:
    """Navigate to a URL and return page title."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url)
        title = page.title()
        browser.close()
    return f"📄 {title} ({url})"

@mcp.tool()
async def screenshot(url: str, output_path: str) -> str:
    """Take a screenshot of a webpage."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url)
        page.screenshot(path=output_path)
        browser.close()
    return f"📸 Screenshot saved to {output_path}"

if __name__ == "__main__":
    mcp.run(transport="stdio")
```

---

## With Qwen

```bash
# Use MCP email server
qwen "Use the mcp-server email tool to send a test email to test@example.com"

# Use MCP file server
qwen "Use the mcp-server file tools to read Dashboard.md and summarize it"

# Use MCP for approval workflow
qwen "Create an approval request using the MCP email server"
```

---

## MCP Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    MCP Architecture                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐         ┌──────────────┐         ┌──────────┐│
│  │  AI Client   │◄───────►│  MCP Server  │◄───────►│ External ││
│  │  (Qwen)      │  JSON   │  (Your Code) │  API/DB │  System  ││
│  │              │  RPC    │              │         │  (Gmail) ││
│  └──────────────┘         └──────────────┘         └──────────┘│
│                                                                  │
│  Communication: stdio or HTTP                                    │
│  Message Format: JSON-RPC 2.0                                    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## MCP Capabilities

| Capability | Description | Example |
|------------|-------------|---------|
| **Tools** | Functions AI can call | `send_email()`, `read_file()` |
| **Resources** | Data AI can read | File contents, API responses |
| **Prompts** | Pre-written templates | Email templates, report formats |

---

## Best Practices

### Logging (Critical!)

```python
# ❌ WRONG - Never write to stdout (corrupts JSON-RPC)
print("Debug info")  # BAD!

# ✅ CORRECT - Write to stderr
import sys
print("Debug info", file=sys.stderr)

# Or use logging
import logging
logging.basicConfig(level=logging.INFO)
logging.info("Server started")
```

### Security

```python
# ✅ Use environment variables for secrets
import os
SMTP_PASS = os.environ['SMTP_PASS']

# ✅ Validate all inputs
@mcp.tool()
async def send_email(to: str, subject: str, body: str) -> str:
    if not '@' in to:
        return "❌ Invalid email address"
    # ... rest of logic

# ✅ Rate limiting
from datetime import datetime, timedelta

last_sent = None

@mcp.tool()
async def send_email(to: str, subject: str, body: str) -> str:
    global last_sent
    if last_sent and datetime.now() - last_sent < timedelta(minutes=1):
        return "❌ Rate limit: 1 email per minute"
    last_sent = datetime.now()
    # ... send email
```

---

## Troubleshooting

### Server Not Showing Up

```bash
# Check JSON syntax
python -m json.tool ~/.config/qwen-code/mcp.json

# Verify paths are absolute
# Check file permissions
# Restart Qwen/Claude completely
```

### Check Logs

```bash
# MCP logs (location varies by client)
tail -f ~/Library/Logs/Qwen/mcp*.log

# Or check stderr output from server
```

### Test Server Directly

```bash
# Run server directly to check for errors
python email_server.py

# Should see no output (stdio mode)
# Errors will print to stderr
```

---

## Related Skills

| Skill | Purpose |
|-------|---------|
| `approval-workflow` | Use MCP for approval emails |
| `browsing-with-playwright` | Browser automation via MCP |
| `scheduler` | Schedule MCP server tasks |

---

## Resources

- [Official MCP Documentation](https://modelcontextprotocol.io/)
- [MCP GitHub](https://github.com/modelcontextprotocol)
- [MCP Inspector](https://github.com/modelcontextprotocol/inspector)
- [Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [TypeScript SDK](https://github.com/modelcontextprotocol/typescript-sdk)

---

*Skill Version: 1.0*  
*Last Updated: 2026-03-14*  
*Silver Tier Component*  
*Based on Official MCP Documentation*
