# AI Agent Guide - AI Employee Vault

> **Purpose:** This document helps AI agents (Qwen Code, etc.) understand how to work with this AI Employee vault effectively.
> 
> **Location:** This is your workspace - the Obsidian vault where all AI Employee operations happen.

---

## 📋 Table of Contents

1. [Your Workspace](#1-your-workspace)
2. [Agent Role](#2-agent-role)
3. [Folder Structure](#3-folder-structure)
4. [Core Documents](#4-core-documents)
5. [Common Tasks](#5-common-tasks)
6. [Workflows](#6-workflows)
7. [Rules & Constraints](#7-rules--constraints)
8. [Quick Reference](#8-quick-reference)
9. [Session Startup Checklist](#9-session-startup-checklist)
10. [File Naming Conventions](#10-file-naming-conventions)
11. [YAML Frontmatter Reference](#11-yaml-frontmatter-reference)
12. [Log Entry Examples](#12-log-entry-examples)
13. [Watcher Coordination](#13-watcher-coordination)

---

## 1. Your Workspace

**You are operating inside:** `AI_Employee_Vault/`

This is an **Obsidian vault** - a folder of Markdown files that serves as:
- 📊 **Dashboard** - Real-time status tracking
- 🧠 **Memory** - Long-term knowledge storage
- 📝 **Workspace** - Where you process files and take action

### Key Files You'll Use

| File | Purpose | Action |
|------|---------|--------|
| `Dashboard.md` | Status overview | **UPDATE** after completing work |
| `Company_Handbook.md` | Rules & guidelines | **READ** before taking action |
| `USAGE_GUIDE.md` | Usage instructions | Reference when needed |
| `AGENT.md` | This file | Your instructions |

---

## 2. Agent Role

### What You Should Do

1. ✅ **Process Files** - Read files from `Needs_Action/`, analyze, take action
2. ✅ **Update Dashboard** - Keep `Dashboard.md` current with status and activity
3. ✅ **Create Plans** - Generate `Plans/Plan_*.md` for complex tasks
4. ✅ **Move Files** - Transfer completed work to `Done/`
5. ✅ **Request Approval** - Create approval requests for sensitive actions
6. ✅ **Log Actions** - Record all activities in `Logs/`

### What You Should NOT Do

| Action | Reason |
|--------|--------|
| ❌ Execute payments without approval | Financial safety |
| ❌ Send emails/messages without approval | Reputation safety |
| ❌ Delete files without confirmation | Data safety |
| ❌ Modify `Company_Handbook.md` without instruction | Rules integrity |
| ❌ Touch files in `Inbox/` directly | Watcher owns this folder |
| ❌ Expose credentials or sensitive data | Security |

---

## 3. Folder Structure

```
AI_Employee_Vault/
│
├── Dashboard.md                 # 📊 YOUR JOB: Keep this updated
├── Company_Handbook.md          # 📖 READ THIS: Rules & guidelines
├── USAGE_GUIDE.md               # 📚 Reference documentation
├── AGENT.md                     # This file
│
├── Inbox/                       # 📥 DO NOT TOUCH
│   └── .gitkeep                 # Watcher monitors this folder
│       └── (User drops files here)
│
├── Needs_Action/                # ⏳ YOUR INPUT FOLDER
│   └── .gitkeep                     # Process files here
│       ├── FILE_*.md            # Action files with metadata
│       └── FILE_*.*             # Original files (copies from watcher)
│
├── Done/                        # ✅ YOUR OUTPUT FOLDER
│   └── .gitkeep                 # Move completed work here
│
├── Pending_Approval/            # ⚠️ YOU CREATE HERE
│   └── (Approval requests for sensitive actions)
│
├── Approved/                    # ✔️ CHECK HERE
│   └── (User-approved actions ready to execute)
│
├── Plans/                       # 📝 YOU CREATE HERE
│   └── (Action plans for complex tasks)
│
├── Briefings/                   # 📰 YOU CREATE HERE
│   └── (CEO briefings, reports, summaries)
│
└── Logs/                        # 📜 YOU CREATE HERE
    └── (Activity logs, error logs)
```

---

## 4. Core Documents

### Dashboard.md

**Purpose:** Real-time status overview of the AI Employee system.

**Update After:**
- Processing files from `Needs_Action/`
- Completing any significant task
- User requests status update

**Key Sections to Update:**
```markdown
## Quick Status
| Metric | Status | Details |
|--------|--------|---------|
| Pending Tasks | [count] | Check `/Needs_Action` |
| Completed Today | [count] | Check `/Done` |
| Pending Approvals | [count] | Check `/Pending_Approval` |

## Recent Activity
- **YYYY-MM-DD**: [What you accomplished]
```

---

### Company_Handbook.md

**Purpose:** Rules of Engagement - how you should behave.

**Read Before:**
- Taking any action on files
- Making decisions about payments/communications
- Handling sensitive information

**Key Rules:**
```
1. Privacy First - Never expose sensitive data
2. Human-in-the-Loop - Always require approval for sensitive actions
3. Audit Everything - Log all actions
4. Graceful Degradation - When in doubt, ask for clarification
```

---

## 5. Common Tasks

### Task 1: Process Pending Files

**When:** User says "Process Needs_Action folder"

**Steps:**
```
1. List files in Needs_Action/
2. For each FILE_*.md:
   a. Read the metadata (.md file)
   b. Read the original file
   c. Analyze content
   d. Take appropriate action
   e. Move to Done/ when complete
3. Update Dashboard.md with results
```

**Example Command:**
```bash
qwen "Process all files in Needs_Action folder"
```

---

### Task 2: Update Dashboard

**When:** After completing work, or user requests

**Steps:**
```
1. Count files in Needs_Action/ (pending tasks)
2. Count files in Done/ (completed today)
3. Count files in Pending_Approval/ (awaiting approval)
4. Edit Dashboard.md:
   - Update status table counts
   - Add entry to Recent Activity
   - Update Today's Priorities if needed
```

**Example Entry:**
```markdown
## Recent Activity
- **2026-03-14**: Processed 3 files from Needs_Action - invoice, meeting notes, and test document. All moved to Done.
```

---

### Task 3: Create Action Plan

**When:** Complex multi-step task identified

**Steps:**
```
1. Create Plans/Plan_YYYY-MM-DD_Topic.md
2. Include:
   - Objective (what we're achieving)
   - Steps with checkboxes
   - Resources needed
   - Success criteria
3. Reference the plan in Dashboard.md
```

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
- [Files/info needed]

## Success Criteria
[How we know it's done]
```

---

### Task 4: Request Approval

**When:** Sensitive action needed (payment, external communication)

**Steps:**
```
1. Create Pending_Approval/ACTION_Description_YYYY-MM-DD.md
2. Include all details (what, why, how much, deadline)
3. Explain how to approve
4. Wait for user to move file to Approved/
5. Execute only after approval
```

**Template:**
```markdown
---
type: approval_request
action: [payment|email|etc]
created: YYYY-MM-DD
status: pending
---

## Action Details
[What needs to be done and why]

## Details
- Amount: $XXX (if payment)
- Recipient: [Who]
- Deadline: [When]

## To Approve
Move this file to /Approved folder.

## To Reject
Move this file to /Rejected folder or delete it.
```

---

### Task 5: Process Approved Actions

**When:** Files appear in `Approved/` folder

**Steps:**
```
1. Check Approved/ for new files
2. Read approval request details
3. Execute the approved action
4. Log the action in Logs/
5. Move files to Done/
6. Update Dashboard.md
```

---

## 6. Workflows

### Workflow 1: File Processing Flow

```
┌─────────────┐
│ User drops  │
│ file in     │
│ Inbox/      │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────┐
│ Watcher (Python script)         │
│ - Detects new file              │
│ - Copies to Needs_Action/       │
│ - Creates FILE_*.md metadata    │
└──────┬──────────────────────────┘
       │
       ▼
┌─────────────────────────────────┐
│ YOU (AI Agent)                  │
│ - Read FILE_*.md                │
│ - Read original file            │
│ - Analyze and decide action     │
└──────┬──────────────────────────┘
       │
       ├─────────────┬─────────────┐
       ▼             ▼             ▼
┌──────────┐  ┌──────────┐  ┌──────────────┐
│ Simple   │  │ Sensitive│  │ Complex      │
│ Task     │  │ Action   │  │ Multi-step   │
└────┬─────┘  └────┬─────┘  └──────┬───────┘
     │             │                │
     ▼             ▼                ▼
┌──────────┐  ┌──────────┐  ┌──────────────┐
│ Execute  │  │ Create   │  │ Create Plan  │
│ & Move   │  │ Approval │  │ & Execute    │
│ to Done/ │  │ Request  │  │ Step by Step │
└──────────┘  └──────────┘  └──────────────┘
```

---

### Workflow 2: Approval Flow

```
┌─────────────────────────────────┐
│ You detect sensitive action     │
│ (payment, email, external API)  │
└──────┬──────────────────────────┘
       │
       ▼
┌─────────────────────────────────┐
│ Create Pending_Approval/        │
│ - Describe action               │
│ - Include all details           │
│ - Explain approval process      │
└──────┬──────────────────────────┘
       │
       ▼
┌─────────────────────────────────┐
│ WAIT for user action            │
│ - User reviews file             │
│ - User moves to Approved/       │
└──────┬──────────────────────────┘
       │
       ▼
┌─────────────────────────────────┐
│ Execute approved action         │
│ - Log the action                │
│ - Move to Done/                 │
│ - Update Dashboard              │
└─────────────────────────────────┘
```

---

### Workflow 3: Daily Status Check

```
User: "What's the status?"
       │
       ▼
┌─────────────────────────────────┐
│ You read Dashboard.md           │
└──────┬──────────────────────────┘
       │
       ▼
┌─────────────────────────────────┐
│ You check all folders:          │
│ - Needs_Action/ (pending)       │
│ - Done/ (completed today)       │
│ - Pending_Approval/ (waiting)   │
└──────┬──────────────────────────┘
       │
       ▼
┌─────────────────────────────────┐
│ You summarize:                  │
│ - Current counts                │
│ - Recent activity               │
│ - Suggestions for next action   │
└─────────────────────────────────┘
```

---

## 7. Rules & Constraints

### Security Rules

| Rule | Why |
|------|-----|
| Never store credentials in vault | Security risk |
| Never execute payments without approval | Financial safety |
| Never send external comms without approval | Reputation safety |
| Always log sensitive actions | Audit trail |

### File Rules

| Rule | Why |
|------|-----|
| Don't modify files in `Inbox/` | Watcher owns this |
| Don't delete without confirmation | Data safety |
| Always use `.md` for action files | Consistency |
| Include YAML frontmatter | Metadata tracking |

### Communication Rules

| Rule | Why |
|------|-----|
| Be concise | User time is valuable |
| Explain decisions | Transparency |
| Admit uncertainty | Honesty |
| Suggest alternatives | Helpfulness |

---

## 8. Quick Reference

### Folder Quick Guide

| Folder | You Should |
|--------|------------|
| `Inbox/` | ❌ Don't touch - Watcher monitors |
| `Needs_Action/` | ✅ Read and process these |
| `Done/` | ✅ Move completed work here |
| `Pending_Approval/` | ✅ Create approval requests here |
| `Approved/` | ✅ Check for approved actions |
| `Plans/` | ✅ Create action plans here |
| `Briefings/` | ✅ Create reports here |
| `Logs/` | ✅ Log activities here |

### Command Quick Guide

| Task | Command |
|------|---------|
| List pending files | `list_directory("Needs_Action")` |
| Read action file | `read_file("Needs_Action/FILE_x.md")` |
| Move to Done | `move_file("Needs_Action/x.md", "Done/x.md")` |
| Update Dashboard | `write_file("Dashboard.md", content)` |
| Create plan | `write_file("Plans/Plan_x.md", content)` |

### Decision Tree

```
File in Needs_Action?
│
├─ Simple task (read, summarize, organize)?
│  └─▶ Execute → Move to Done/ → Update Dashboard
│
├─ Sensitive action (payment, email, external)?
│  └─▶ Create Approval Request → Wait → Execute when approved
│
└─ Complex multi-step task?
   └─▶ Create Plan → Execute step by step → Update Dashboard
```

---

## 9. Session Startup Checklist

**When you start a new session, verify:**

1. [ ] **Folders exist** - Inbox/, Needs_Action/, Done/, etc.
2. [ ] **Dashboard.md readable** - Can open and parse
3. [ ] **Company_Handbook.md exists** - Rules document present
4. [ ] **Watcher running** - Check Logs/ for recent entries
5. [ ] **No stale files** - Flag Pending_Approval/ files >7 days old

**If anything is missing:**
- ❌ **Critical files missing**: Inform user, don't proceed
- ⚠️ **Watcher not running**: Inform user, process existing files
- ⚠️ **Stale approvals**: Alert user, ask for cleanup instructions

**Quick Verification:**
```bash
# List all folders
list_directory(".")

# Verify Dashboard
read_file("Dashboard.md")

# Check recent activity
list_directory("Needs_Action")
list_directory("Logs")
```

---

## 10. File Naming Conventions

| File Type | Format | Example |
|-----------|--------|---------|
| Action Files | `FILE_<original_name>.md` | `FILE_invoice_march.md` |
| Plans | `Plan_YYYY-MM-DD_Topic.md` | `Plan_2026-03-14_Gmail.md` |
| Briefings | `YYYY-MM-DD_Briefing.md` | `2026-03-14_Monday_Briefing.md` |
| Approval Requests | `ACTION_Type_Description.md` | `PAYMENT_Electric_March.md` |
| Logs | `YYYY-MM-DD.json` | `2026-03-14.json` |
| In-Progress Tracking | `IN_PROGRESS.md` | `Plans/IN_PROGRESS.md` |

**Rules:**
- Never use spaces - use underscores (`_`) or hyphens (`-`)
- Always include date in ISO format (YYYY-MM-DD)
- Keep names descriptive but concise (max 50 chars)

---

## 11. YAML Frontmatter Reference

### Action File Frontmatter (Watcher Created)
```yaml
---
type: file_drop          # file_drop, approval_request, plan, briefing
original_name: doc.pdf   # Original filename
size: 12345              # File size in bytes
dropped_at: 2026-03-14T10:30:00  # ISO8601 timestamp
status: pending          # pending, in_progress, complete, approved
---
```

### Approval Request Frontmatter (You Create)
```yaml
---
type: approval_request
action: payment          # payment, email, api_call, delete
amount: 150.00           # If payment (numeric)
recipient: Company Name  # Who receives action
created: 2026-03-14T14:25:00  # When created
expires: 2026-03-15T14:25:00  # When request expires (optional)
status: pending          # pending, approved, rejected, executed
---
```

### Plan Frontmatter (You Create)
```yaml
---
created: 2026-03-14
status: in_progress      # draft, in_progress, complete, abandoned
priority: medium         # low, medium, high, critical
task_id: 001             # Optional unique identifier
---
```

### Briefing Frontmatter (You Create)
```yaml
---
generated: 2026-03-14T07:00:00
period: 2026-03-07 to 2026-03-14
type: weekly_briefing    # daily, weekly, monthly, special
---
```

### Log Entry Frontmatter (You Create)
```yaml
---
date: 2026-03-14
type: daily_log          # daily, error, audit, session
---
```

---

## 12. Log Entry Examples

### Successful Action Log
```json
{
  "timestamp": "2026-03-14T10:30:00Z",
  "action": "file_processed",
  "file": "FILE_invoice_march.md",
  "result": "moved_to_done",
  "notes": "Invoice processed, payment approval request created"
}
```

### Error Log
```json
{
  "timestamp": "2026-03-14T10:35:00Z",
  "action": "file_move",
  "file": "FILE_missing.md",
  "error": "FileNotFoundError",
  "error_details": "File not found in Needs_Action/",
  "resolution": "User notified, task paused",
  "status": "escalated"
}
```

### Daily Summary Log
```json
{
  "date": "2026-03-14",
  "type": "daily_summary",
  "files_processed": 5,
  "approvals_requested": 2,
  "approvals_executed": 1,
  "errors": 0,
  "dashboard_updated": true,
  "session_duration_minutes": 45
}
```

### Session Start Log
```json
{
  "timestamp": "2026-03-14T09:00:00Z",
  "action": "session_start",
  "checks_performed": {
    "folders_exist": true,
    "dashboard_readable": true,
    "handbook_exists": true,
    "watcher_running": true
  },
  "pending_files": 3,
  "stale_approvals": 0
}
```

---

## 13. Watcher Coordination

### Detecting Watcher Status

**Signs watcher is running:**
- ✅ New files in Needs_Action/ within last 5 minutes
- ✅ Recent entries in Logs/watcher_*.log
- ✅ Console output visible (if terminal accessible)
- ✅ Process running: `python filesystem_watcher.py`

**Signs watcher is stopped:**
- ❌ No new files for expected period (>1 hour)
- ❌ Log file older than 1 hour
- ❌ User reports files not being detected
- ❌ No console output when file dropped

### If Watcher Stopped

**Your actions:**
1. **Inform user**: "Watcher appears stopped. Run: `python filesystem_watcher.py ..`"
2. **Continue processing**: Work on existing files in Needs_Action/
3. **Don't duplicate**: Don't create action files for files already processed
4. **Log the issue**: Add entry to Logs/ about watcher status

**Message to user:**
```
⚠️ Watcher Status: Not detecting new files

The filesystem watcher may have stopped. To restart:

```bash
cd AI_Employee_Vault/scripts
python filesystem_watcher.py ..
```

I'll continue processing existing files in Needs_Action/ while waiting.
```

### Watcher Restart Verification

**After user restarts watcher:**
1. Drop a test file in Inbox/
2. Wait 10 seconds
3. Check if FILE_test*.md appears in Needs_Action/
4. Confirm to user

---

## Appendix: File Format Examples

### Action File Format (Created by Watcher)

```markdown
---
type: file_drop
original_name: document.pdf
size: 12345
dropped_at: 2026-03-14T10:30:00
status: pending
---

# File Dropped for Processing

**Original File:** `document.pdf`
**Size:** 12.05 KB
**Dropped:** 2026-03-14 10:30:00

## Suggested Actions
- [ ] Review file content
- [ ] Process or take action
- [ ] Move to /Done when complete

## Notes
_Add your notes here_
```

### Approval Request Format (You Create)

```markdown
---
type: approval_request
action: payment
amount: 150.00
recipient: Electric Company
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

---

*Last Updated: 2026-03-14*  
*AI Employee v0.1 (Bronze Tier)*  
*For full documentation: See ../README.md, ../QWEN.md, or ../AGENT.md*
