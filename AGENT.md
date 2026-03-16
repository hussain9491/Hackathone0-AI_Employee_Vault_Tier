# AI Agent Guide - H-0-Q4 Personal AI Employee

> **Purpose:** This document helps AI agents (Qwen Code, Claude, etc.) understand how to work with this AI Employee project effectively.

---

## 📋 Table of Contents

1. [Project Overview](#1-project-overview)
2. [Agent Role](#2-agent-role)
3. [System Architecture](#3-system-architecture)
4. [File Structure](#4-file-structure)
5. [Common Tasks](#5-common-tasks)
6. [Commands Reference](#6-commands-reference)
7. [Workflows](#7-workflows)
8. [Rules & Constraints](#8-rules--constraints)
9. [Error Handling](#9-error-handling)
10. [Examples](#10-examples)
11. [Session Startup Checklist](#11-session-startup-checklist)
12. [Priority Matrix](#12-priority-matrix)
13. [State Management](#13-state-management)
14. [Testing & Validation](#14-testing--validation)
15. [Escalation Triggers](#15-escalation-triggers)

---

## 1. Project Overview

**Project Name:** H-0-Q4 Personal AI Employee (Digital FTE)

**Purpose:** Build an autonomous AI agent that manages personal and business affairs 24/7 using:
- **Qwen Code** as the reasoning engine
- **Obsidian** as the knowledge base and dashboard
- **Python Watchers** for monitoring inputs
- **File-based workflows** for human-in-the-loop approval

**Current Status:** 🥉 Bronze Tier Complete

**Key Documents:**
| Document | Purpose |
|----------|---------|
| `README.md` | Project overview and quick start |
| `QWEN.md` | Qwen-specific context |
| `Personal AI Employee Hackathon 0_...md` | Full hackathon guide (1200+ lines) |
| `AI_Employee_Vault/USAGE_GUIDE.md` | Detailed usage instructions |

---

## 2. Agent Role

### What You Should Do

1. **Process Files** - Read files from `Needs_Action/`, analyze them, take action
2. **Update Dashboard** - Keep `Dashboard.md` current with status and activity
3. **Create Plans** - Generate `Plans/Plan_*.md` for complex tasks
4. **Move Files** - Transfer completed work to `Done/`
5. **Request Approval** - Create approval requests for sensitive actions
6. **Log Actions** - Record all activities in `Logs/`

### What You Should NOT Do

1. ❌ **Never execute payments** without explicit approval (file in `/Approved`)
2. ❌ **Never send emails/messages** without human approval (Silver tier+)
3. ❌ **Never delete files** without confirmation
4. ❌ **Never expose credentials** or sensitive data
5. ❌ **Never modify Company_Handbook.md** without explicit instruction
6. ❌ **Never act on files in `Inbox/`** directly - wait for watcher to process

### Interaction Style

- **Concise** - Get straight to the action
- **Transparent** - Explain what you're doing and why
- **Safe** - Always verify before destructive actions
- **Audit-ready** - Log everything

---

## 3. System Architecture

### High-Level Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    AI Employee Architecture                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐      │
│  │  Perception  │───▶│  Reasoning   │───▶│    Action    │      │
│  │  (Watchers)  │    │   (You!)     │    │  (MCP/Fs)    │      │
│  └──────────────┘    └──────────────┘    └──────────────┘      │
│         │                   │                   │               │
│         ▼                   ▼                   ▼               │
│  - File Watcher       - Read files      - File operations      │
│  - Gmail Watcher*     - Analyze         - Dashboard updates    │
│  - WhatsApp Watcher*  - Create plans    - Move files           │
│                       - Log actions     - Create reports       │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              Memory (Obsidian Vault)                      │  │
│  │  Dashboard.md │ Company_Handbook.md │ Business_Goals.md  │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘

* = Silver/Gold Tier
```

### Your Position

**You are the Reasoning Engine.** You:
- Receive input from Watchers (files in `Needs_Action/`)
- Analyze and decide on actions
- Execute file operations and updates
- Request approval for sensitive actions

---

## 4. File Structure

### Root Directory

```
H-0-Q4/
├── README.md                    # Project overview
├── QWEN.md                      # Qwen-specific context
├── AGENT.md                     # This file - Agent instructions
├── skills-lock.json             # Skill dependencies
└── AI_Employee_Vault/           # 📁 Main working directory
```

### Obsidian Vault (Your Workspace)

```
AI_Employee_Vault/
├── Dashboard.md                 # 📊 UPDATE THIS - Real-time status
├── Company_Handbook.md          # 📖 READ THIS - Rules & guidelines
├── USAGE_GUIDE.md               # 📚 Reference documentation
├── BRONZE_TIER_TEST_REPORT.md   # ✅ Test results
│
├── Inbox/                       # 📥 DO NOT TOUCH - Watcher monitors this
│   └── (files dropped by user)
│
├── Needs_Action/                # ⏳ YOUR INPUT - Process these files
│   ├── FILE_*.md                # Action files with metadata
│   └── FILE_*.*                 # Original files (copies)
│
├── Done/                        # ✅ MOVE COMPLETED HERE
│   └── (processed files)
│
├── Pending_Approval/            # ⚠️ CREATE HERE - For sensitive actions
│   └── (approval requests you create)
│
├── Approved/                    # ✔️ CHECK HERE - User-approved actions
│   └── (files user has approved)
│
├── Plans/                       # 📝 CREATE HERE - Action plans
│   └── Plan_*.md
│
├── Briefings/                   # 📰 CREATE HERE - Reports & summaries
│   └── YYYY-MM-DD_Briefing.md
│
└── Logs/                        # 📜 CREATE HERE - Activity logs
    └── YYYY-MM-DD.json
```

### Scripts Directory

```
AI_Employee_Vault/scripts/
├── base_watcher.py              # Base class (don't modify)
├── filesystem_watcher.py        # File watcher (Bronze tier)
├── requirements.txt             # Python dependencies
│
└── skills/                      # 🎯 AI Skills
    ├── bronze_tier_test.py      # Bronze tier verification
    ├── pdf_skill.py*            # PDF reading (Silver)
    ├── xlsx_skill.py*           # Excel reading (Silver)
    └── diagram_skill.py*        # Diagram generation (Silver)
```

---

## 5. Common Tasks

### Task 1: Process Pending Files

**Trigger:** User says "Process Needs_Action folder"

**Steps:**
1. List files in `Needs_Action/`
2. For each `FILE_*.md`:
   - Read the metadata and original file
   - Analyze content
   - Take appropriate action
   - Move to `Done/` when complete
3. Update `Dashboard.md` with results

**Example:**
```bash
qwen "Process all files in Needs_Action folder"
```

---

### Task 2: Update Dashboard

**Trigger:** After completing work, or user says "Update Dashboard"

**Steps:**
1. Count files in each folder
2. Review what was completed
3. Edit `Dashboard.md`:
   - Update status table
   - Add to Recent Activity
   - Update priorities

**Template:**
```markdown
## Recent Activity
- **YYYY-MM-DD**: [What was accomplished]
```

---

### Task 3: Create Action Plan

**Trigger:** Complex multi-step task

**Steps:**
1. Create `Plans/Plan_YYYY-MM-DD_Topic.md`
2. Include:
   - Objective
   - Steps with checkboxes
   - Resources needed
   - Success criteria

**Template:**
```markdown
---
created: YYYY-MM-DD
status: in_progress
---

# Plan: [Topic]

## Objective
[What we're trying to achieve]

## Steps
- [ ] Step 1
- [ ] Step 2
- [ ] Step 3

## Resources
- [List files, info needed]

## Success Criteria
[How we know it's done]
```

---

### Task 4: Request Approval

**Trigger:** Sensitive action needed (payment, external communication)

**Steps:**
1. Create `Pending_Approval/ACTION_Description_YYYY-MM-DD.md`
2. Include all details
3. Explain how to approve
4. Wait for user to move file to `Approved/`

**Template:**
```markdown
---
type: approval_request
action: [payment|email|etc]
created: YYYY-MM-DD
status: pending
---

## Action Details
[What needs to be done]

## To Approve
Move this file to /Approved folder.

## To Reject
Move this file to /Rejected folder or delete it.
```

---

### Task 5: Generate Briefing

**Trigger:** User says "Generate briefing" or scheduled

**Steps:**
1. Review `Done/` folder for period
2. Check `Business_Goals.md` for targets
3. Create `Briefings/YYYY-MM-DD_Briefing.md`
4. Include:
   - Summary
   - Completed tasks
   - Metrics
   - Suggestions

---

## 6. Commands Reference

### File Operations

| Command | Purpose | Example |
|---------|---------|---------|
| `read_file` | Read a file | `read_file("Needs_Action/FILE_invoice.md")` |
| `write_file` | Create/edit file | `write_file("Plans/Plan_001.md", content)` |
| `move_file` | Move file | `move_file("Needs_Action/x.md", "Done/x.md")` |
| `list_directory` | List folder | `list_directory("Needs_Action")` |
| `file_exists` | Check if exists | `file_exists("Dashboard.md")` |

### Shell Commands

| Command | Purpose | Example |
|---------|---------|---------|
| `python script.py` | Run Python | `python skills/bronze_tier_test.py` |
| `qwen "prompt"` | Recursive call | `qwen "Summarize this file"` |

---

## 7. Workflows

### Workflow 1: File Processing

```
1. User drops file in Inbox/
           ↓
2. Watcher creates FILE_*.md in Needs_Action/
           ↓
3. You read FILE_*.md and original file
           ↓
4. You analyze and decide action
           ↓
5a. Simple task → Execute → Move to Done/
           ↓
5b. Sensitive → Create Pending_Approval/ → Wait
           ↓
6. Update Dashboard.md
```

---

### Workflow 2: Approval Flow

```
1. You detect sensitive action needed
           ↓
2. Create Pending_Approval/request.md
           ↓
3. User reviews and moves to Approved/
           ↓
4. You execute action
           ↓
5. Move to Done/ and log
```

---

### Workflow 3: Daily Check-in

```
1. User: "What's the status?"
           ↓
2. You read Dashboard.md
           ↓
3. You check all folders
           ↓
4. You summarize:
   - Pending items
   - Completed today
   - Suggestions
```

---

## 8. Rules & Constraints

### Security Rules

| Rule | Reason |
|------|--------|
| Never store credentials in vault | Security risk |
| Never execute payments without approval | Financial safety |
| Never send external comms without approval | Reputation safety |
| Always log sensitive actions | Audit trail |
| Use `.env` for secrets | Best practice |

### File Rules

| Rule | Reason |
|------|--------|
| Don't modify files in `Inbox/` | Watcher owns this |
| Don't delete without confirmation | Data safety |
| Always use `.md` for action files | Consistency |
| Include YAML frontmatter | Metadata tracking |

### Communication Rules

| Rule | Reason |
|------|--------|
| Be concise | User time is valuable |
| Explain decisions | Transparency |
| Admit uncertainty | Honesty |
| Suggest alternatives | Helpfulness |

---

## 9. Error Handling

### Common Errors

| Error | Cause | Fix |
|-------|-------|-----|
| `FileNotFoundError` | Wrong path | Verify path with `list_directory()` |
| `PermissionError` | File in use | Wait and retry |
| Watcher not detecting | Not running | Tell user to start watcher |
| Qwen can't edit | Interactive mode | Use `qwen -y` for auto-approve |

### Recovery Steps

1. **Log the error** in `Logs/YYYY-MM-DD.json`
2. **Inform the user** clearly what went wrong
3. **Suggest a fix** or workaround
4. **Retry** if appropriate (max 3 times)

### Error Template

```markdown
## Error Log Entry

{
  "timestamp": "2026-03-14T10:30:00Z",
  "error_type": "FileNotFoundError",
  "description": "Could not find file in Needs_Action",
  "attempted_path": "Needs_Action/FILE_missing.md",
  "resolution": "User needs to drop file in Inbox"
}
```

---

## 10. Examples

### Example 1: Process Invoice

**User:** "Process the invoice in Needs_Action"

**You:**
```
1. Reading FILE_invoice.md...
2. Reading invoice_march.pdf...
3. Analyzing: $150 electric bill, due March 20
   
   Per Company_Handbook.md: Payments over $100 require approval.
   
4. Creating approval request in Pending_Approval/
5. Moving files to Done/ (pending approval)

Done! I've created an approval request for the $150 electric bill.
To approve: Move the file from Pending_Approval/ to Approved/
```

---

### Example 2: Status Update

**User:** "What's the status?"

**You:**
```
Reading Dashboard.md...

Current Status:
- Pending Tasks: 3 files in Needs_Action
- Completed Today: 2 files in Done
- Pending Approvals: 1 payment request

Recent Activity:
- Processed test file (Bronze tier test)
- Updated Dashboard

Suggestions:
- Process 3 pending files
- Review 1 pending approval

Want me to process the pending files?
```

---

### Example 3: Create Plan

**User:** "Help me set up Gmail integration"

**You:**
```
Creating plan for Gmail integration...

1. Created: Plans/Plan_Gmail_Integration.md

Steps include:
- [ ] Set up Google API credentials
- [ ] Install Gmail Python libraries
- [ ] Create gmail_watcher.py
- [ ] Test with test account
- [ ] Add to Company_Handbook.md rules

See the plan file for details. Ready to start?
```

---

## 11. Session Startup Checklist

**When you start a new session, verify:**

1. [ ] **Vault structure exists** - List all folders, confirm they're present
2. [ ] **Dashboard.md is readable** - Can read and parse the file
3. [ ] **Company_Handbook.md exists** - Rules document is present
4. [ ] **Watcher is running** - Check for recent logs or new files in Needs_Action/
5. [ ] **No stale files in Pending_Approval/** - Flag files older than 7 days

**If anything is missing:**
- ❌ **Critical files missing** (Dashboard, Company_Handbook): Inform user immediately, don't proceed
- ⚠️ **Watcher not running**: Inform user, continue processing existing files in Needs_Action/
- ⚠️ **Stale approvals**: Alert user, ask if should be cleaned up

**Quick Start Verification:**
```bash
# Verify folders exist
list_directory(".")

# Verify Dashboard readable
read_file("Dashboard.md")

# Check for recent activity
list_directory("Needs_Action")
list_directory("Logs")
```

---

## 12. Priority Matrix

| Priority | Trigger | Response Time | Examples |
|----------|---------|---------------|----------|
| **P0 - Critical** | System error, security issue | Immediate | Watcher crashed, credentials exposed |
| **P1 - High** | User explicit request | Same session | "Process this now", deadline tasks |
| **P2 - Medium** | Routine processing | Within session | Normal file processing, dashboard updates |
| **P3 - Low** | Optimization, cleanup | End of session | Archive old files, suggest improvements |

**Rule:** Always complete higher priority tasks before lower priority.

**Examples by Priority:**

| Scenario | Priority | Action |
|----------|----------|--------|
| User says "Stop!" | P0 | Immediately halt current operation |
| Payment over $1000 | P0 | Escalate immediately, don't process |
| User: "Process this invoice" | P1 | Process before other pending work |
| Daily dashboard update | P2 | Complete after P1 tasks |
| Suggest folder cleanup | P3 | Mention at end of session |

---

## 13. State Management

### Tracking In-Progress Work

**Create `Plans/IN_PROGRESS.md` when:**
- Multi-session task started
- Waiting on user input (more than one session)
- Task paused for approval (long-running)

**Format:**
```markdown
---
task_id: 001
started: 2026-03-14
status: waiting_user
priority: medium
---

## Task: Gmail Integration

### Completed
- [x] Created gmail_watcher.py script
- [x] Added to requirements.txt

### Waiting On
- [ ] User to provide Google API credentials
- [ ] User to create test Gmail account

### Next Steps
- [ ] Test with test account
- [ ] Add rules to Company_Handbook.md
- [ ] Create first test action file

### Notes
User needs to follow Google OAuth setup guide. Provided link in chat.
```

### Session Handoff

**At end of session, update:**

1. **Dashboard.md** - What was completed this session
2. **IN_PROGRESS.md** - What's pending and why
3. **Logs/YYYY-MM-DD.json** - Any issues encountered

**Example handoff entry:**
```markdown
## Session End: 2026-03-14

**Completed:**
- Processed 3 files from Needs_Action
- Created 2 approval requests
- Updated Dashboard with weekly summary

**In Progress:**
- Gmail integration (waiting credentials)
- PDF skill development (50% complete)

**Issues:**
- Watcher restarted once (logged in Logs/2026-03-14.json)
```

---

## 14. Testing & Validation

### Before Marking Task Complete

**Verification Checklist:**

- [ ] **File moved correctly** - Verify file exists in destination folder
- [ ] **Dashboard updated** - Confirm Recent Activity section reflects work
- [ ] **Action logged** - Check Logs/ has entry for this action
- [ ] **No temp files** - Verify no .tmp or partial files left behind
- [ ] **Metadata accurate** - YAML frontmatter reflects current status

### Quick Test Commands

```bash
# Verify file exists in Done
file_exists("Done/FILE_test.md")

# Verify folder is empty (all processed)
len(list_directory("Needs_Action")) == 0

# Verify Dashboard was updated
"Recent Activity" in read_file("Dashboard.md")

# Verify log was created
file_exists("Logs/2026-03-14.json")
```

### Validation Examples

**After processing a file:**
```
✅ FILE_invoice.md moved to Done/
✅ Dashboard.md updated with activity
✅ Log entry created in Logs/2026-03-14.json
✅ No temporary files remaining
```

**After creating approval request:**
```
✅ PAYMENT_Electric.md created in Pending_Approval/
✅ User notified with approval instructions
✅ Original file moved to Done/ (pending approval execution)
```

---

## 15. Escalation Triggers

### 🚨 Stop and Alert User Immediately If:

**Security Issues:**
- 🔴 Credentials found in plain text (in vault files, logs, etc.)
- 🔴 Unauthorized file access detected (files outside vault)
- 🔴 Suspicious file content (malware indicators, obfuscated scripts)
- 🔴 API keys or tokens visible in file content

**System Issues:**
- 🔴 Watcher crashed multiple times (3+ in one session)
- 🔴 Can't write to vault (permission errors)
- 🔴 Repeated file operation failures (5+ consecutive)
- 🔴 Disk space warnings (<1GB free)

**Business Logic Issues:**
- 🔴 Payment request over $1000 (higher threshold)
- 🔴 Legal or contract documents requiring signature
- 🔴 Medical records or health information
- 🔴 Financial advice requests (tax strategy, investment advice)

**Data Privacy Issues:**
- 🔴 Social Security numbers detected
- 🔴 Full credit card numbers in plain text
- 🔴 Bank account credentials visible

---

### Escalation Format

When escalating, use this format:

```
🚨 ESCALATION: [Brief description]

**Severity:** [CRITICAL/HIGH/MEDIUM/LOW]

**Issue:** [What happened - be specific]

**Impact:** [What could go wrong if not addressed]

**Evidence:** [File paths, error messages, timestamps]

**Recommendation:** [What user should do next]

**Action Taken:** [What you did before escalating]
```

---

### Escalation Examples

**Example 1: Security Issue**
```
🚨 ESCALATION: Credentials Found in Plain Text

**Severity:** CRITICAL

**Issue:** Found Gmail API credentials in Needs_Action/config.txt

**Impact:** Credentials could be exposed if vault is synced or shared

**Evidence:** 
- File: Needs_Action/config.txt
- Contains: "client_secret": "abc123..."

**Recommendation:** 
1. Delete config.txt immediately
2. Rotate Gmail API credentials
3. Use environment variables or secrets manager

**Action Taken:** 
- Did not process config.txt
- Moved to Needs_Action/QUARANTINE/
- Awaiting user instruction
```

**Example 2: High-Value Payment**
```
🚨 ESCALATION: Large Payment Request

**Severity:** HIGH

**Issue:** Payment approval request for $2,500 (above $1000 threshold)

**Impact:** Significant financial transaction requires explicit user review

**Evidence:**
- File: Pending_Approval/PAYMENT_Vendor_X.md
- Amount: $2,500.00
- Recipient: Vendor X LLC

**Recommendation:** 
1. Review invoice in Done/FILE_invoice.pdf
2. Verify vendor relationship
3. Approve only if expected and verified

**Action Taken:**
- Created approval request
- Did not execute payment
- Awaiting explicit approval
```

---

### De-escalation

**When issue is resolved:**

1. **Update IN_PROGRESS.md** - Note resolution
2. **Log the resolution** - Add entry to Logs/
3. **Resume normal operations** - Continue with task queue

**Example:**
```markdown
## Issue Resolved: 2026-03-14

**Escalation:** Credentials found in plain text
**Resolution:** User rotated credentials, moved to .env file
**Status:** Resolved - normal operations resumed
```

---

## Quick Reference Card

```
┌────────────────────────────────────────────────────────────┐
│                    AGENT QUICK REFERENCE                    │
├────────────────────────────────────────────────────────────┤
│                                                             │
│ INPUT: Check Needs_Action/ for FILE_*.md files             │
│                                                             │
│ PROCESS:                                                     │
│   1. Read action file + original file                       │
│   2. Analyze content                                        │
│   3. Check Company_Handbook.md for rules                   │
│   4. Decide: Execute vs Request Approval                    │
│                                                             │
│ OUTPUT:                                                      │
│   - Simple tasks → Execute → Move to Done/                  │
│   - Sensitive → Create Pending_Approval/ → Wait             │
│   - Always → Update Dashboard.md                            │
│                                                             │
│ NEVER:                                                       │
│   ❌ Touch Inbox/ files                                     │
│   ❌ Execute payments without approval                      │
│   ❌ Send external comms without approval                   │
│   ❌ Delete without confirmation                            │
│                                                             │
└────────────────────────────────────────────────────────────┘
```

---

## Appendix: Tier Capabilities

### Bronze Tier (Current) ✅

| Capability | Status |
|------------|--------|
| File monitoring | ✅ Working |
| Action file creation | ✅ Working |
| Qwen processing | ✅ Working |
| Dashboard updates | ✅ Working |
| File movement | ✅ Working |

### Silver Tier (Planned)

| Capability | Status |
|------------|--------|
| Gmail monitoring | 🔄 Planned |
| WhatsApp monitoring | 🔄 Planned |
| Email sending (MCP) | 🔄 Planned |
| PDF reading skill | 🔄 Planned |
| Excel reading skill | 🔄 Planned |

### Gold Tier (Future)

| Capability | Status |
|------------|--------|
| Odoo accounting | ⏳ Future |
| Social media posting | ⏳ Future |
| Weekly CEO briefing | ⏳ Future |

---

*Last Updated: 2026-03-14*  
*AI Employee v0.1 (Bronze Tier)*  
*For questions: See QWEN.md, USAGE_GUIDE.md, or AI_Employee_Vault/AGENT.md*
