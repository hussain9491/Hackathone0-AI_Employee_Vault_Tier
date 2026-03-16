---
name: whatsapp-watcher
description: |
  Monitor WhatsApp Web for messages containing keywords (urgent, invoice, payment, etc.).
  Uses Playwright for browser automation. Creates action files for Qwen to process.
  ⚠️ Use responsibly - may violate WhatsApp ToS. Consider Business API for production.
---

# WhatsApp Watcher Skill

Monitor WhatsApp Web for keyword messages.

## Installation

```bash
pip install playwright
playwright install chromium
```

## ⚠️ Important Notice

**Terms of Service:** Using WhatsApp Web automation may violate WhatsApp's Terms of Service.

**Use Cases:**
- ✅ Personal automation (low volume)
- ✅ Development/testing
- ❌ Commercial use (use WhatsApp Business API)

## Quick Reference

### Start WhatsApp Watcher

```bash
# First time (requires QR scan)
python AI_Employee_Vault/scripts/whatsapp_watcher.py --vault-path AI_Employee_Vault

# With custom keywords
python AI_Employee_Vault/scripts/whatsapp_watcher.py --vault-path AI_Employee_Vault --keywords urgent invoice payment "call me"

# Custom interval
python AI_Employee_Vault/scripts/whatsapp_watcher.py --vault-path AI_Employee_Vault --interval 30
```

### With Qwen

```bash
# Process WhatsApp messages
qwen "Check Needs_Action for WhatsApp messages and prioritize urgent ones"

# Summarize messages
qwen "Summarize all WhatsApp messages from today"
```

## Setup: First Run

### Step 1: Install Dependencies

```bash
pip install playwright
playwright install chromium
```

### Step 2: First Run (QR Authentication)

```bash
cd AI_Employee_Vault/scripts
python whatsapp_watcher.py --vault-path ..
```

**First run requires QR scan:**

1. Script opens browser (or shows QR in terminal)
2. Open WhatsApp on phone
3. Go to Settings → Linked Devices
4. Scan QR code
5. Session saved for future runs

### Step 3: Verify Session

Session saved in `.obsidian/whatsapp_session/`. Subsequent runs use saved session.

## Workflow: Message Processing

```
1. WhatsApp Watcher runs (every 60 seconds)
         ↓
2. Checks WhatsApp Web for keyword messages
         ↓
3. Creates action file in Needs_Action/
         ↓
4. Qwen processes and drafts response
         ↓
5. User approves and sends
```

## Monitored Keywords

**Default Keywords:**
- urgent
- asap
- invoice
- payment
- help
- emergency
- deadline
- meeting
- call me
- pricing

**Custom Keywords:**
```bash
python whatsapp_watcher.py --vault-path .. --keywords "buy now" interested "send quote" demo
```

## Output Format

Action file in `Needs_Action/`:

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

"Hi, can you send the invoice urgently?"

## Suggested Actions

- [ ] Open WhatsApp and read full conversation
- [ ] Reply to message
- [ ] Send invoice
- [ ] Mark as processed

## Response Draft

_Hi John, sending the invoice now..._

## Notes

_Follow up tomorrow_
```

## Configuration

### Check Interval

```bash
# Check every 30 seconds (more responsive)
python whatsapp_watcher.py --vault-path .. --interval 30

# Check every 5 minutes (less resource usage)
python whatsapp_watcher.py --vault-path .. --interval 300
```

### Session Path

```bash
# Custom session location
python whatsapp_watcher.py --vault-path .. --session-path /secure/path/session
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "playwright not found" | Run `pip install playwright && playwright install chromium` |
| "QR code timeout" | Run with visible browser first time |
| "Session expired" | Delete session folder and re-authenticate |
| No messages detected | Check keyword list, verify WhatsApp Web is accessible |

## Security

- ✅ Session stored locally
- ✅ No message history stored
- ✅ Read-only (no sending)

**Add to `.gitignore`:**
```
.obsidian/whatsapp_session/
```

## Alternative: WhatsApp Business API

For production use, consider official API:

- [WhatsApp Business Platform](https://developers.facebook.com/docs/whatsapp/)
- Official support
- Higher rate limits
- No ToS concerns

## Related Skills

- `email-mcp` - Send email responses
- `approval-workflow-v2` - Approve message responses
- `gmail-watcher` - Monitor email alongside WhatsApp

---

*Skill Version: 1.0 | Last Updated: 2026-03-14 | Silver Tier | ⚠️ Use Responsibly*
