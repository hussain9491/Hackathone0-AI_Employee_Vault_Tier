# AI Employee - Complete Usage Guide

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     AI Employee Architecture                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐      │
│  │  Perception  │───▶│  Reasoning   │───▶│    Action    │      │
│  │  (Watchers)  │    │  (Qwen Code) │    │  (MCP/Fs)    │      │
│  └──────────────┘    └──────────────┘    └──────────────┘      │
│         │                   │                   │               │
│         ▼                   ▼                   ▼               │
│  - Gmail Watcher      - Reads files     - Send emails          │
│  - WhatsApp Watcher   - Creates plans   - Post social          │
│  - File Watcher       - Moves files     - Write logs           │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Quick Start (5 Minutes)

### Step 1: Open Two Terminals

**Terminal 1** - For the Watcher (runs continuously)
**Terminal 2** - For Qwen Code (run commands as needed)

### Step 2: Start the File Watcher

```bash
cd C:\Users\user1542\Documents\GitHub\H-0-Q4\AI_Employee_Vault\scripts
python filesystem_watcher.py ..
```

**What this does:**
- Monitors the `Inbox` folder for new files
- When you drop a file, it creates an action file in `Needs_Action`
- Runs 24/7 until you press Ctrl+C

**Why:** The watcher is the "eyes" of your AI Employee. It watches for new work.

---

## Daily Workflow

### Scenario 1: Processing a File

#### 1. Drop a file in Inbox

```bash
# Place any file here:
C:\Users\user1542\Documents\GitHub\H-0-Q4\AI_Employee_Vault\Inbox\
```

**Example files:**
- `invoice_march.pdf` - An invoice to process
- `client_email.txt` - A message to respond to
- `meeting_notes.docx` - Notes to summarize

#### 2. Watcher creates action file

The watcher automatically creates:
- Copy of your file in `Needs_Action/`
- Metadata file: `Needs_Action/FILE_yourfile.md`

**Example output:**
```markdown
---
type: file_drop
original_name: invoice_march.pdf
size: 45678
dropped_at: 2026-03-14T10:30:00
status: pending
---

# File Dropped for Processing

**Original File:** `invoice_march.pdf`
**Size:** 44.61 KB
**Dropped:** 2026-03-14 10:30:00

## Suggested Actions
- [ ] Review file content
- [ ] Process or take action
- [ ] Move to /Done when complete
```

#### 3. Ask Qwen Code to process

```bash
cd C:\Users\user1542\Documents\GitHub\H-0-Q4\AI_Employee_Vault

qwen "Check the Needs_Action folder and process any pending files. For each file:
1. Read and understand the content
2. Take appropriate action
3. Move completed files to /Done"
```

**What Qwen does:**
- Reads all `.md` files in `Needs_Action`
- Processes the attached files
- Creates a plan if needed
- Moves files to `Done` when complete

---

### Scenario 2: Daily Briefing

```bash
cd C:\Users\user1542\Documents\GitHub\H-0-Q4\AI_Employee_Vault

qwen "Review the Dashboard.md and Company_Handbook.md. Check what's in Done folder today. Update the Dashboard with:
1. Number of tasks completed
2. Any patterns you noticed
3. Suggestions for tomorrow"
```

---

## Command Reference

### Starting the System

| Command | Purpose | When to Run |
|---------|---------|-------------|
| `python filesystem_watcher.py ..` | Start file watcher | Once per session (runs continuously) |
| `qwen --version` | Verify Qwen installed | Before first use |
| `qwen` | Start interactive Qwen | When you want to chat |

### Processing Files

| Command | Purpose | Example |
|---------|---------|---------|
| `qwen "Process Needs_Action"` | Process pending files | Daily |
| `qwen "Summarize FILE_invoice.md"` | Summarize specific file | As needed |
| `qwen "Create Plan.md for this task"` | Create action plan | Complex tasks |

### Maintenance

| Command | Purpose | Frequency |
|---------|---------|-----------|
| Move files from `Done` to archive | Clean up completed | Weekly |
| Check `Logs/` folder | Review errors | Weekly |
| Update `Company_Handbook.md` | Add new rules | As needed |

---

## File Flow Diagram

```
┌─────────┐     ┌──────────────┐     ┌──────────────┐     ┌─────────┐
│  Inbox  │────▶│ Needs_Action │────▶│   Approved   │────▶│  Done   │
│ (Drop)  │     │  (Pending)   │     │ (Ready/Wait) │     │(Complete)│
└─────────┘     └──────────────┘     └──────────────┘     └─────────┘
     │                  │                    │                  │
     │                  │                    │                  │
     ▼                  ▼                    ▼                  ▼
 You drop          Watcher creates      You approve        Qwen moves
 a file here       action file here     (if needed)        here when done
```

---

## Detailed Example: Processing an Invoice

### Step-by-Step Walkthrough

#### 1. Receive Invoice

You get an invoice PDF: `electric_bill_march.pdf`

#### 2. Drop in Inbox

```bash
copy electric_bill_march.pdf "C:\Users\user1542\Documents\GitHub\H-0-Q4\AI_Employee_Vault\Inbox\"
```

**Watcher output (Terminal 1):**
```
📁 New file detected: electric_bill_march.pdf
  Copied to: ..\Needs_Action\FILE_electric_bill_march.pdf
  Created metadata: ..\Needs_Action\FILE_electric_bill_march.md
```

#### 3. Check the Action File

Open: `Needs_Action/FILE_electric_bill_march.md`

```markdown
---
type: file_drop
original_name: electric_bill_march.pdf
size: 52340
dropped_at: 2026-03-14T14:22:00
status: pending
---

# File Dropped for Processing

**Original File:** `electric_bill_march.pdf`
**Size:** 51.11 KB
**Dropped:** 2026-03-14 14:22:00

## Suggested Actions
- [ ] Review file content
- [ ] Process or take action
- [ ] Move to /Done when complete
```

#### 4. Ask Qwen to Process

**Terminal 2:**
```bash
cd C:\Users\user1542\Documents\GitHub\H-0-Q4\AI_Employee_Vault

qwen "Read FILE_electric_bill_march.pdf and:
1. Extract the amount, due date, and account number
2. Check Company_Handbook.md for payment rules
3. If over $100, create an approval request in Pending_Approval
4. If under $100, log it and move to Done"
```

#### 5. Qwen's Response

Qwen will:
1. Read the PDF
2. Check your rules in `Company_Handbook.md`
3. Create approval file (if needed):

```markdown
---
type: approval_request
action: payment
amount: 150.00
recipient: Electric Company
due_date: 2026-03-20
created: 2026-03-14T14:25:00
status: pending
---

## Payment Details
- Amount: $150.00
- To: Electric Company
- Due: March 20, 2026

## To Approve
Move this file to /Approved folder.
```

#### 6. You Approve

Move the file:
```bash
move "Needs_Action/FILE_electric_bill_march.md" "Approved/"
```

#### 7. Qwen Executes

```bash
qwen "Check Approved folder and process any pending approvals"
```

Qwen logs the payment and moves files to `Done`.

---

## Troubleshooting

### Watcher Not Starting

**Error:** `ModuleNotFoundError: No module named 'watchdog'`

**Fix:**
```bash
pip install watchdog
```

### Watcher Not Detecting Files

**Check:**
1. Is watcher running? (Look for "✅ Filesystem watcher started")
2. Are you dropping in correct folder? (`Inbox/` not `Needs_Action/`)
3. Check `Logs/` folder for errors

### Qwen Not Processing Files

**Check:**
1. Is Qwen installed? `qwen --version`
2. Are you in the vault directory? `cd AI_Employee_Vault`
3. Do files have `.md` extension? (Qwen reads these)

---

## Architecture Explained

### Why Two Terminals?

| Terminal | Purpose | Runs |
|----------|---------|------|
| **Terminal 1** | Watcher (background) | Continuously (24/7) |
| **Terminal 2** | Qwen (on-demand) | When you need it |

**Watcher** = Passive listener (like a doorbell)
**Qwen** = Active processor (like a butler)

### Why Action Files?

Action files (`.md`) serve as:
1. **Memory** - Track what needs to be done
2. **Communication** - You ↔ Claude ↔ Watchers
3. **Audit Trail** - See what happened when

### Why Folder Structure?

| Folder | Purpose | Analogy |
|--------|---------|---------|
| `Inbox` | Raw input | Mailbox |
| `Needs_Action` | To-do list | Inbox tray |
| `Pending_Approval` | Waiting for you | "Sign here" pile |
| `Approved` | Ready to execute | "Go" signals |
| `Done` | Completed | Archive |

---

## Next Steps (Silver Tier)

To upgrade your system:

1. **Add Gmail Watcher** - Monitor emails automatically
2. **Add MCP Server** - Let Claude send emails
3. **Add Scheduling** - Run daily briefings at 8 AM
4. **Add Approval Workflow** - Human-in-the-loop for payments

---

## Quick Reference Card

```
┌────────────────────────────────────────────────────────────┐
│                    Daily Commands                           │
├────────────────────────────────────────────────────────────┤
│ 1. Start watcher:                                           │
│    cd scripts && python filesystem_watcher.py ..            │
│                                                             │
│ 2. Drop file in:                                            │
│    AI_Employee_Vault/Inbox/                                 │
│                                                             │
│ 3. Process with Qwen:                                       │
│    qwen "Process Needs_Action folder"                       │
│                                                             │
│ 4. Check results in:                                        │
│    AI_Employee_Vault/Done/                                  │
└────────────────────────────────────────────────────────────┘
```

---

*Generated: 2026-03-14 | Bronze Tier*
