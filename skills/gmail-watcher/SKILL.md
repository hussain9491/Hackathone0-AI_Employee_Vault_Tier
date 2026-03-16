---
name: gmail-watcher
description: |
  Monitor Gmail for new unread/important emails. Creates action files in Needs_Action/
  for Qwen to process. Uses Gmail API with OAuth 2.0 authentication. Use for automatic
  email triage and response workflows.
---

# Gmail Watcher Skill

Monitor Gmail inbox and create action files for new emails.

## Installation

```bash
pip install google-auth google-auth-oauthlib google-api-python-client
```

## Quick Reference

### Start Gmail Watcher

```bash
# First time (opens browser for OAuth)
python AI_Employee_Vault/scripts/gmail_watcher.py --vault-path AI_Employee_Vault --credentials credentials.json

# Subsequent runs (uses saved token)
python AI_Employee_Vault/scripts/gmail_watcher.py --vault-path AI_Employee_Vault --credentials credentials.json --interval 120
```

### With Qwen

```bash
# Process emails captured by watcher
qwen "Check Needs_Action folder for new emails and process them"

# Summarize emails
qwen "Read and summarize all email action files in Needs_Action"
```

## Setup: Gmail API Credentials

### Step 1: Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create new project: "AI Employee"
3. Enable **Gmail API**
4. Go to **Credentials** → **Create Credentials** → **OAuth 2.0 Client ID**
5. Download `credentials.json`
6. Place in `AI_Employee_Vault/scripts/credentials.json`

### Step 2: First Run Authentication

```bash
cd AI_Employee_Vault/scripts
python gmail_watcher.py --vault-path .. --credentials credentials.json
```

This opens browser for OAuth. Grant permissions. Token saved automatically.

## Workflow: Email Processing

```
1. Gmail Watcher runs (every 2 minutes)
         ↓
2. Checks for unread/important emails
         ↓
3. Creates action file in Needs_Action/
         ↓
4. Qwen processes action file
         ↓
5. Moves to Done/ when complete
```

## Output Format

Action file created in `Needs_Action/`:

```markdown
---
type: email
from: "John Doe <john@example.com>"
subject: "Project Update Meeting"
received: "Mon, 14 Mar 2026 10:30:00 -0700"
priority: high
status: pending
gmail_id: 18f3c5a2b9d4e1f0
---

# Email Received

**From:** John Doe <john@example.com>
**Subject:** Project Update Meeting
**Received:** Mon, 14 Mar 2026 10:30:00 -0700

## Suggested Actions

- [ ] Read full email in Gmail
- [ ] Reply to sender
- [ ] Forward to relevant party
- [ ] Archive after processing

## Response Draft

_Hi John, I'll be there..._

## Notes

_Add notes here_
```

## Configuration

### Check Interval

```bash
# Check every 2 minutes (default)
python gmail_watcher.py --vault-path .. --credentials credentials.json --interval 120

# Check every 5 minutes
python gmail_watcher.py --vault-path .. --credentials credentials.json --interval 300
```

### Gmail Query

Modify in `gmail_watcher.py`:

```python
# Unread and important (default)
q='is:unread is:important'

# From specific sender
q='from:boss@company.com is:unread'

# With attachments
q='has:attachment is:unread'

# Multiple conditions
q='(from:client.com OR from:partner.com) is:unread'
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "Credentials not found" | Place credentials.json in scripts folder |
| "Token expired" | Delete `Logs/gmail_token.pickle` and re-authenticate |
| "Gmail API not enabled" | Enable in Google Cloud Console |
| No emails detected | Check if emails are marked as important |

## Security

- ✅ Token stored locally (not synced)
- ✅ Read-only scope by default
- ✅ Credentials never committed to git

Add to `.gitignore`:
```
credentials.json
*token.pickle
```

## Related Skills

- `email-mcp` - Send emails via MCP
- `approval-workflow-v2` - Approve email responses
- `scheduler` - Schedule email checks

---

*Skill Version: 1.0 | Last Updated: 2026-03-14 | Silver Tier*
