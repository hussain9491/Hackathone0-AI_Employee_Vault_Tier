# H-0-Q4: Personal AI Employee (Digital FTE)

> **Tagline:** Your life and business on autopilot. Local-first, agent-driven, human-in-the-loop.

A comprehensive AI-powered digital employee that proactively manages personal and business affairs 24/7 using **Qwen Code** as the reasoning engine and **Obsidian** as the knowledge base dashboard.

![Bronze Tier](https://img.shields.io/badge/Status-Bronze%20Tier%20Complete-brightgreen)
![Python](https://img.shields.io/badge/Python-3.13+-blue)
![License](https://img.shields.io/badge/License-MIT-green)

---

## 📋 Table of Contents

- [Overview](#overview)
- [How It Works](#how-it-works)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Quick Start](#quick-start)
- [Running Commands](#running-commands)
- [Hackathon Tiers](#hackathon-tiers)
- [Skills](#skills)
- [Daily Workflow](#daily-workflow)
- [Troubleshooting](#troubleshooting)
- [Resources](#resources)

---

## Overview

This project implements a **Digital FTE (Full-Time Equivalent)** - an AI agent that works like a human employee but with key advantages:

| Feature | Human FTE | Digital FTE |
|---------|-----------|-------------|
| Availability | 40 hours/week | **168 hours/week (24/7)** |
| Monthly Cost | $4,000–$8,000+ | **$500–$2,000** |
| Consistency | 85–95% accuracy | **99%+ consistency** |
| Annual Hours | ~2,000 | **~8,760** |
| Cost per Task | ~$5.00 | **~$0.50** |

### Key Capabilities

- 📥 **File Monitoring** - Automatically detects new files in Inbox
- 📝 **Action Generation** - Creates structured action files with metadata
- 🤖 **AI Processing** - Qwen Code reads, analyzes, and takes action
- ✅ **Task Completion** - Moves processed items to Done folder
- 📊 **Dashboard Updates** - Real-time status tracking in Obsidian

---

## How It Works

The AI Employee follows a **Perception → Reasoning → Action** architecture:

```
┌─────────────────────────────────────────────────────────────────┐
│                    AI Employee Workflow                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1. PERCEPTION (Watcher)                                         │
│     ┌──────────────┐                                            │
│     │  File Dropped │                                            │
│     │    in Inbox  │                                            │
│     └──────┬───────┘                                            │
│            │                                                     │
│            ▼                                                     │
│     ┌──────────────┐                                            │
│     │  Python      │                                            │
│     │  Watcher     │─── Creates action file                     │
│     │  Script      │                                            │
│     └──────┬───────┘                                            │
│            │                                                     │
│  2. REASONING (Qwen Code)                                        │
│            ▼                                                     │
│     ┌──────────────┐                                            │
│     │  Qwen Code   │                                            │
│     │  reads file  │─── Analyzes content                        │
│     │  & metadata  │─── Creates plan                            │
│     └──────┬───────┘                                            │
│            │                                                     │
│  3. ACTION (MCP/File Operations)                                 │
│            ▼                                                     │
│     ┌──────────────┐                                            │
│     │  Execute     │                                            │
│     │  - Update    │                                            │
│     │    Dashboard │                                            │
│     │  - Move to   │                                            │
│     │    Done      │                                            │
│     └──────────────┘                                            │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### File Flow

```
┌─────────┐     ┌──────────────┐     ┌──────────────┐     ┌─────────┐
│  Inbox  │────▶│ Needs_Action │────▶│   Approved   │────▶│  Done   │
│ (Drop)  │     │  (Pending)   │     │ (If Approval)│     │(Complete)│
└─────────┘     └──────────────┘     └──────────────┘     └─────────┘
     │                  │                    │                  │
     │                  │                    │                  │
     ▼                  ▼                    ▼                  ▼
 You drop          Watcher creates      You approve        Qwen moves
 a file here       action file here     (if needed)        here when done
```

---

## Architecture

### Core Components

```
┌─────────────────────────────────────────────────────────────────┐
│                     System Architecture                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐      │
│  │  Perception  │───▶│  Reasoning   │───▶│    Action    │      │
│  │  (Watchers)  │    │  (Qwen Code) │    │  (MCP/Fs)    │      │
│  └──────────────┘    └──────────────┘    └──────────────┘      │
│         │                   │                   │               │
│         ▼                   ▼                   ▼               │
│  - File Watcher       - Reads files     - File operations      │
│  - Gmail Watcher*     - Creates plans   - Dashboard updates    │
│  - WhatsApp Watcher*  - Moves files     - Logging              │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              Memory (Obsidian Vault)                      │  │
│  │  Dashboard.md │ Company_Handbook.md │ Business_Goals.md  │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘

* = Silver/Gold Tier
```

### Technology Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Reasoning Engine** | Qwen Code | AI processing and decision making |
| **Knowledge Base** | Obsidian | Local Markdown dashboard |
| **Watcher Scripts** | Python 3.13+ | File monitoring and automation |
| **File Monitoring** | watchdog | Real-time file system events |
| **Version Control** | Git/GitHub Desktop | Vault synchronization |

---

## Project Structure

```
H-0-Q4/
│
├── README.md                              # This file - Project documentation
├── QWEN.md                                # Qwen-specific context and instructions
├── skills-lock.json                       # Skill dependencies tracking
├── .gitattributes                         # Git text normalization
├── Personal AI Employee Hackathon 0_...md # Full hackathon guide (1200+ lines)
│
└── AI_Employee_Vault/                     # 📁 Obsidian Vault (Main Working Directory)
    │
    ├── Dashboard.md                       # 📊 Real-time status dashboard
    ├── Company_Handbook.md                # 📖 Rules of Engagement
    ├── BRONZE_TIER_VERIFICATION.md        # ✅ Bronze tier checklist
    ├── BRONZE_TIER_TEST_REPORT.md         # 📋 Test results
    ├── USAGE_GUIDE.md                     # 📚 Complete usage instructions
    ├── .gitignore                         # Git ignore rules
    │
    ├── Inbox/                             # 📥 Drop files here for processing
    │   └── .gitkeep
    │
    ├── Needs_Action/                      # ⏳ Pending items awaiting processing
    │   └── .gitkeep
    │
    ├── Done/                              # ✅ Completed tasks archive
    │   └── .gitkeep
    │
    ├── Pending_Approval/                  # ⚠️ Awaiting human approval
    │
    ├── Approved/                          # ✔️ Approved actions ready to execute
    │
    ├── Plans/                             # 📝 Action plans created by Qwen
    │
    ├── Briefings/                         # 📰 CEO briefings and reports
    │
    ├── Logs/                              # 📜 System logs (auto-generated)
    │
    └── scripts/                           # 🛠️ Python Scripts
        │
        ├── base_watcher.py                # Base class for all watchers
        ├── filesystem_watcher.py          # File system monitoring (Bronze)
        ├── requirements.txt               # Python dependencies
        ├── README.md                      # Scripts documentation
        │
        ├── skills/                        # 🎯 AI Skills (Extensible)
        │   ├── bronze_tier_test.py        # Bronze tier testing skill
        │   ├── pdf_skill.py*              # PDF reading (Silver)
        │   ├── xlsx_skill.py*             # Excel reading (Silver)
        │   └── diagram_skill.py*          # Diagram generation (Silver)
        │
        └── __pycache__/                   # Python cache (auto-generated)
```

---

## Quick Start

### Prerequisites

| Software | Version | Install |
|----------|---------|---------|
| Python | 3.13+ | [python.org](https://www.python.org/downloads/) |
| Qwen Code | Latest | `pip install qwen-code` |
| Obsidian | v1.10.6+ | [obsidian.md](https://obsidian.md/download) |
| Git | Latest | [git-scm.com](https://git-scm.com/) |

### 5-Minute Setup

```bash
# 1. Install Python dependencies
cd AI_Employee_Vault/scripts
pip install -r requirements.txt

# 2. Start the File Watcher (Terminal 1)
python filesystem_watcher.py ..

# 3. Process files with Qwen (Terminal 2)
cd ..
qwen "Check Needs_Action folder and process any pending files"
```

---

## Running Commands

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
| `qwen -y "..."` | Auto-approve tool actions | Batch processing |

### Maintenance

| Command | Purpose | Frequency |
|---------|---------|-----------|
| Move files from `Done` to archive | Clean up completed | Weekly |
| Check `Logs/` folder | Review errors | Weekly |
| Update `Company_Handbook.md` | Add new rules | As needed |

---

## Hackathon Tiers

### 🥉 Bronze Tier (COMPLETE ✅)

**Estimated Time:** 8-12 hours

- [x] Obsidian vault with Dashboard.md and Company_Handbook.md
- [x] One working Watcher script (File System)
- [x] Qwen Code reading from and writing to the vault
- [x] Basic folder structure: /Inbox, /Needs_Action, /Done
- [x] All AI functionality ready for Agent Skills integration

**Test Report:** `AI_Employee_Vault/BRONZE_TIER_TEST_REPORT.md`

---

### 🥈 Silver Tier (IN PROGRESS)

**Estimated Time:** 20-30 hours

- [ ] Two or more Watcher scripts (Gmail + WhatsApp + LinkedIn)
- [ ] Automatically post on LinkedIn about business
- [ ] Qwen reasoning loop that creates Plan.md files
- [ ] One working MCP server for external action (e.g., sending emails)
- [ ] Human-in-the-loop approval workflow for sensitive actions
- [ ] Basic scheduling via cron or Task Scheduler
- [ ] PDF reading skill
- [ ] Excel (XLSX) reading skill
- [ ] Diagram generation skill

---

### 🥇 Gold Tier (PLANNED)

**Estimated Time:** 40+ hours

- [ ] Full cross-domain integration (Personal + Business)
- [ ] Odoo Community accounting integration via MCP
- [ ] Facebook/Instagram integration
- [ ] Twitter (X) integration
- [ ] Multiple MCP servers for different action types
- [ ] Weekly Business and Accounting Audit with CEO Briefing
- [ ] Error recovery and graceful degradation
- [ ] Comprehensive audit logging
- [ ] Ralph Wiggum loop for autonomous multi-step completion

---

### 💎 Platinum Tier (FUTURE)

**Estimated Time:** 60+ hours

- [ ] Run AI Employee on Cloud 24/7
- [ ] Work-Zone Specialization (Cloud vs Local)
- [ ] Delegation via Synced Vault
- [ ] Odoo on Cloud VM with HTTPS and backups
- [ ] A2A (Agent-to-Agent) communication upgrade

---

## Skills

Skills are modular Python scripts that extend Qwen's capabilities for specific file types and tasks.

### Available Skills (Bronze)

| Skill | File | Status |
|-------|------|--------|
| Bronze Tier Test | `skills/bronze_tier_test.py` | ✅ Complete |

### Planned Skills (Silver)

| Skill | File | Purpose |
|-------|------|---------|
| PDF Reader | `skills/pdf_skill.py` | Extract text from PDFs |
| Excel Reader | `skills/xlsx_skill.py` | Read Excel spreadsheets |
| Diagram Generator | `skills/diagram_skill.py` | Create visual diagrams |

### Using Skills

```bash
# With Qwen
qwen "Use the bronze_tier_test skill to verify all Bronze tier requirements"

# Or directly
python skills/bronze_tier_test.py --vault-path ../
```

---

## Daily Workflow

### Morning (8:00 AM)

```bash
cd AI_Employee_Vault

# 1. Check dashboard
qwen "Review Dashboard.md and summarize today's priorities"

# 2. Process overnight files
qwen "Process all files in Needs_Action folder"
```

### During Day

```bash
# Drop files in Inbox as they arrive
copy invoice.pdf AI_Employee_Vault/Inbox/

# Watcher auto-creates action file
# Qwen processes when prompted
```

### Evening (6:00 PM)

```bash
# Review completed work
qwen "Check Done folder and update Dashboard with today's accomplishments"
```

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

### Dashboard Not Updating

**Note:** Dashboard.md is a Markdown file, not a web UI.

**To see updates:**
1. Open in **Obsidian**: Load `AI_Employee_Vault` as vault
2. Or open in **VS Code** with Markdown preview
3. Or any text editor (refresh to see changes)

---

## Resources

### Documentation

| Document | Description |
|----------|-------------|
| [`Personal AI Employee Hackathon 0_...md`](Personal%20AI%20Employee%20Hackathon%200_%20Building%20Autonomous%20FTEs%20in%202026.md) | Full hackathon guide (1200+ lines) |
| [`QWEN.md`](QWEN.md) | Qwen-specific context and instructions |
| [`AI_Employee_Vault/USAGE_GUIDE.md`](AI_Employee_Vault/USAGE_GUIDE.md) | Complete usage instructions |
| [`AI_Employee_Vault/BRONZE_TIER_TEST_REPORT.md`](AI_Employee_Vault/BRONZE_TIER_TEST_REPORT.md) | Bronze tier test results |

### External Links

- [Qwen Code Documentation](https://github.com/qwen-code/qwen-code)
- [Obsidian Download](https://obsidian.md/download)
- [Python Download](https://www.python.org/downloads/)
- [Watchdog Documentation](https://pypi.org/project/watchdog/)

### Weekly Research Meeting

- **When:** Wednesdays at 10:00 PM PKT
- **Zoom:** [Join Meeting](https://us06web.zoom.us/j/87188707642?pwd=a9XloCsinvn1JzICbPc2YGUvWTbOTr.1)
- **YouTube:** [@panaversity](https://www.youtube.com/@panaversity)

---

## License

MIT License - See project for details.

---

## Contact & Support

- **Project:** H-0-Q4 (Hackathon 0 - Q4 2026)
- **Community:** Panaversity AI Employee Hackathon
- **Status:** Bronze Tier Complete ✅

---

*Last Updated: 2026-03-14*  
*AI Employee v0.1 (Bronze Tier)*


silver Workflow

 1. Gmail Watcher → Fetches emails
                ↓
       Email Processor → Classifies & creates drafts
                ↓
       Qwen → Writes professional replies
                ↓
       Human → Reviews drafts
                ↓
       Move to Approved/ → Ready to send
                ↓
     . Orchestrator → Asks for confirmation
                ↓
     . You type 'y' → REAL EMAIL SENT! 📧
                ↓
      Done/ → Logged with message ID
