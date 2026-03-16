# H-0-Q4: Personal AI Employee Hackathon

## Project Overview

This repository contains the hackathon materials and setup for building a **Personal AI Employee** (Digital FTE - Full-Time Equivalent). The project demonstrates how to create an autonomous AI agent that proactively manages personal and business affairs 24/7 using:

- **Claude Code** as the reasoning engine
- **Obsidian** as the knowledge base and dashboard
- **Python Watcher scripts** for monitoring inputs (Gmail, WhatsApp, filesystems)
- **MCP (Model Context Protocol) servers** for external actions
- **Playwright** for browser automation

The architecture follows a **Perception → Reasoning → Action** pattern with human-in-the-loop approval workflows for sensitive operations.

## Quick Start (First 30 Minutes)

1. **Install prerequisites**: Claude Code, Obsidian, Python 3.13+, Node.js v24+
2. **Clone and explore**: Read `Personal AI Employee Hackathon 0_ Building Autonomous FTEs in 2026.md`
3. **Set up Obsidian vault**: Create folders: `Inbox`, `Needs_Action`, `Done`, `Pending_Approval`, `Approved`
4. **Verify skills**: Run `python .qwen/skills/browsing-with-playwright/scripts/verify.py`
5. **Create Dashboard.md**: Start with a simple summary of your goals
6. **Test Claude Code**: Run `claude --version` and try reading/writing to your vault

## Directory Structure

```
H-0-Q4/
├── Personal AI Employee Hackathon 0_ Building Autonomous FTEs in 2026.md  # Main hackathon guide
├── skills-lock.json          # Skill dependencies tracking
├── .gitattributes            # Git text normalization settings
└── .qwen/skills/             # Qwen skill configurations
    └── browsing-with-playwright/
        ├── SKILL.md          # Playwright browser automation skill documentation
        ├── references/
        │   └── playwright-tools.md
        └── scripts/
            ├── mcp-client.py     # MCP client for tool calls
            ├── start-server.sh   # Start Playwright MCP server
            ├── stop-server.sh    # Stop Playwright MCP server
            └── verify.py         # Server verification script
```

## Key Files

| File | Purpose |
|------|---------|
| `Personal AI Employee Hackathon 0_ Building Autonomous FTEs in 2026.md` | Comprehensive hackathon guide with architecture, templates, and implementation details |
| `skills-lock.json` | Tracks skill dependencies and versions |
| `.qwen/skills/browsing-with-playwright/SKILL.md` | Documentation for browser automation capabilities |

## Core Concepts

### Digital FTE Value Proposition

| Feature | Human FTE | Digital FTE |
|---------|-----------|-------------|
| Availability | 40 hours/week | 168 hours/week (24/7) |
| Monthly Cost | $4,000–$8,000+ | $500–$2,000 |
| Consistency | 85–95% accuracy | 99%+ consistency |
| Annual Hours | ~2,000 | ~8,760 |

### Architecture Layers

1. **Perception (Watchers)**: Python scripts monitoring Gmail, WhatsApp, filesystems
2. **Reasoning (Claude Code)**: Processes inputs, creates plans, decides actions
3. **Action (MCP Servers)**: Executes tasks via Model Context Protocol
4. **Memory (Obsidian)**: Long-term storage and GUI dashboard

### Key Patterns

- **Ralph Wiggum Loop**: Stop hook that keeps Claude working autonomously until task completion
- **Human-in-the-Loop**: Sensitive actions require file-based approval workflow
- **Watcher Pattern**: Lightweight scripts create `.md` files in `/Needs_Action` to trigger AI processing

## Hackathon Tiers

| Tier | Description | Estimated Time |
|------|-------------|----------------|
| **Bronze** | Foundation: Obsidian vault, one watcher, basic Claude integration | 8–12 hours |
| **Silver** | Functional: Multiple watchers, MCP servers, approval workflows | 20–30 hours |
| **Gold** | Autonomous: Full integration, accounting, weekly audits | 40+ hours |
| **Platinum** | Production: Cloud deployment, domain specialization, A2A messaging | 60+ hours |

## Prerequisites

| Component | Version | Purpose |
|-----------|---------|---------|
| Claude Code | Active subscription | Primary reasoning engine |
| Obsidian | v1.10.6+ | Knowledge base & dashboard |
| Python | 3.13+ | Watcher scripts & orchestration |
| Node.js | v24+ LTS | MCP servers |
| GitHub Desktop | Latest | Version control |

## Available Skills

### browsing-with-playwright

Browser automation for web interactions, form submissions, and data extraction.

**Server Management:**
```bash
# Start
bash .qwen/skills/browsing-with-playwright/scripts/start-server.sh

# Stop
bash .qwen/skills/browsing-with-playwright/scripts/stop-server.sh

# Verify
python .qwen/skills/browsing-with-playwright/scripts/verify.py
```

**Key Operations:**
- Navigate websites
- Fill forms and submit
- Extract data via snapshots
- Execute JavaScript
- Take screenshots

See `.qwen/skills/browsing-with-playwright/SKILL.md` for detailed usage.

## MCP Server Configuration

### Recommended MCP Servers

| Server | Capabilities | Use Case |
|--------|--------------|----------|
| `filesystem` | Read, write, list files | Built-in, use for vault operations |
| `email-mcp` | Send, draft, search emails | Gmail integration |
| `browser-mcp` | Navigate, click, fill forms | Payment portals, web automation |
| `calendar-mcp` | Create, update events | Scheduling meetings |
| `slack-mcp` | Send messages, read channels | Team communication |

### Configuration File

Configure MCP servers in `~/.config/claude-code/mcp.json`:

```json
{
  "servers": [
    {
      "name": "email",
      "command": "node",
      "args": ["/path/to/email-mcp/index.js"],
      "env": {
        "GMAIL_CREDENTIALS": "/path/to/credentials.json"
      }
    },
    {
      "name": "browser",
      "command": "npx",
      "args": ["@anthropic/browser-mcp"],
      "env": {
        "HEADLESS": "true"
      }
    }
  ]
}
```

## Operation Types & Triggers

| Operation Type | Example Task | Trigger |
|----------------|--------------|---------|
| **Scheduled** | Daily Briefing at 8:00 AM | cron (Mac/Linux) or Task Scheduler (Windows) |
| **Continuous** | Lead Capture from WhatsApp | Python watchdog monitoring `/Inbox` folder |
| **Project-Based** | Q1 Tax Preparation | Manual drag-and-drop to `/Active_Project` |

## Watcher Implementation

### Core Watcher Pattern

All watchers follow this base structure:

```python
# base_watcher.py - Template for all watchers
import time
import logging
from pathlib import Path
from abc import ABC, abstractmethod

class BaseWatcher(ABC):
    def __init__(self, vault_path: str, check_interval: int = 60):
        self.vault_path = Path(vault_path)
        self.needs_action = self.vault_path / 'Needs_Action'
        self.check_interval = check_interval
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    def check_for_updates(self) -> list:
        '''Return list of new items to process'''
        pass

    @abstractmethod
    def create_action_file(self, item) -> Path:
        '''Create .md file in Needs_Action folder'''
        pass

    def run(self):
        self.logger.info(f'Starting {self.__class__.__name__}')
        while True:
            try:
                items = self.check_for_updates()
                for item in items:
                    self.create_action_file(item)
            except Exception as e:
                self.logger.error(f'Error: {e}')
            time.sleep(self.check_interval)
```

### Watcher Types

- **Gmail Watcher**: Monitors unread/important emails, creates action files
- **WhatsApp Watcher**: Uses Playwright to monitor keywords (urgent, invoice, payment)
- **Filesystem Watcher**: Uses `watchdog` library to monitor drop folders

## Usage Guidelines

### For This Repository

1. **Read the hackathon guide** (`Personal AI Employee Hackathon 0_...md`) for full architecture details
2. **Use Qwen skills** for browser automation tasks via the Playwright MCP server
3. **Follow the Ralph Wiggum pattern** for autonomous multi-step task completion
4. **Implement human-in-the-loop** for sensitive actions (payments, approvals)

### Obsidian Vault Structure (Recommended)

```
Vault/
├── Dashboard.md              # Real-time summary
├── Company_Handbook.md       # Rules of engagement
├── Business_Goals.md         # Q1/Q2 objectives
├── Inbox/                    # Raw inputs
├── Needs_Action/             # Items awaiting processing
├── In_Progress/<agent>/      # Claimed tasks
├── Pending_Approval/         # Awaiting human approval
├── Approved/                 # Approved actions ready to execute
├── Done/                     # Completed tasks
└── Briefings/                # CEO briefings & audits
```

## Development Conventions

- **Markdown-first**: All state, plans, and communications use `.md` files
- **File-based handoffs**: Agents coordinate by moving files between folders
- **Claim-by-move rule**: First agent to move a task to `/In_Progress/<agent>/` owns it
- **Single-writer rule**: Only one agent writes to `Dashboard.md` at a time
- **Secrets isolation**: Credentials never sync via vault (use `.env` files)

## Security & Privacy Architecture

### Credential Management

- **Environment variables** for API keys: `export GMAIL_API_KEY="your-key"`
- **Secrets manager** for banking credentials (macOS Keychain, Windows Credential Manager, 1Password CLI)
- **`.env` file** (add to `.gitignore` immediately) for local development
- **Rotate credentials** monthly and after any suspected breach

Example `.env` structure:
```bash
# .env - NEVER commit this file
GMAIL_CLIENT_ID=your_client_id
GMAIL_CLIENT_SECRET=your_client_secret
BANK_API_TOKEN=your_token
WHATSAPP_SESSION_PATH=/secure/path/session
```

### Sandboxing & Isolation

- **Development Mode**: Create a `DEV_MODE` flag that prevents real external actions
- **Dry Run**: All action scripts support `--dry-run` flag (logs intended actions without executing)
- **Separate Accounts**: Use test/sandbox accounts during development
- **Rate Limiting**: Implement maximum actions per hour (e.g., max 10 emails, max 3 payments)

### Permission Boundaries

| Action Category | Auto-Approve Threshold | Always Require Approval |
|-----------------|------------------------|-------------------------|
| Email replies | To known contacts | New contacts, bulk sends |
| Payments | < $50 recurring | All new payees, > $100 |
| Social media | Scheduled posts | Replies, DMs |
| File operations | Create, read | Delete, move outside vault |

### Audit Logging

Every action must be logged:
```json
{
  "timestamp": "2026-01-07T10:30:00Z",
  "action_type": "email_send",
  "actor": "claude_code",
  "target": "client@example.com",
  "parameters": {"subject": "Invoice #123"},
  "approval_status": "approved",
  "approved_by": "human",
  "result": "success"
}
```

Store logs in `/Vault/Logs/YYYY-MM-DD.json` and retain for minimum 90 days.

## Error Handling & Recovery

### Error Categories

| Category | Examples | Recovery Strategy |
|----------|----------|-------------------|
| Transient | Network timeout, API rate limit | Exponential backoff retry |
| Authentication | Expired token, revoked access | Alert human, pause operations |
| Logic | Claude misinterprets message | Human review queue |
| Data | Corrupted file, missing field | Quarantine + alert |
| System | Orchestrator crash, disk full | Watchdog + auto-restart |

### Graceful Degradation

When components fail:
- **Gmail API down**: Queue outgoing emails locally, process when restored
- **Banking API timeout**: Never retry payments automatically, always require fresh approval
- **Claude Code unavailable**: Watchers continue collecting, queue grows for later processing
- **Obsidian vault locked**: Write to temporary folder, sync when available

### Watchdog Process

A watchdog script monitors and restarts critical processes:
```python
# watchdog.py - Monitor and restart critical processes
PROCESSES = {
    'orchestrator': 'python orchestrator.py',
    'gmail_watcher': 'python gmail_watcher.py',
    'file_watcher': 'python filesystem_watcher.py'
}
```

## Templates

### Business_Goals.md Template

```markdown
# /Vault/Business_Goals.md
---
last_updated: 2026-01-07
review_frequency: weekly
---

## Q1 2026 Objectives

### Revenue Target
- Monthly goal: $10,000
- Current MTD: $4,500

### Key Metrics to Track
| Metric | Target | Alert Threshold |
|--------|--------|-----------------|
| Client response time | < 24 hours | > 48 hours |
| Invoice payment rate | > 90% | < 80% |
| Software costs | < $500/month | > $600/month |

### Active Projects
1. Project Alpha - Due Jan 15 - Budget $2,000
2. Project Beta - Due Jan 30 - Budget $3,500
```

### CEO Briefing Template (Generated Output)

```markdown
# /Vault/Briefings/2026-01-06_Monday_Briefing.md
---
generated: 2026-01-06T07:00:00Z
period: 2025-12-30 to 2026-01-05
---

# Monday Morning CEO Briefing

## Executive Summary
Strong week with revenue ahead of target. One bottleneck identified.

## Revenue
- **This Week**: $2,450
- **MTD**: $4,500 (45% of $10,000 target)
- **Trend**: On track

## Completed Tasks
- [x] Client A invoice sent and paid
- [x] Project Alpha milestone 2 delivered

## Bottlenecks
| Task | Expected | Actual | Delay |
|------|----------|--------|-------|
| Client B proposal | 2 days | 5 days | +3 days |

## Proactive Suggestions

### Cost Optimization
- **Notion**: No team activity in 45 days. Cost: $15/month.
  - [ACTION] Cancel subscription? Move to /Pending_Approval

### Upcoming Deadlines
- Project Alpha final delivery: Jan 15 (9 days)
- Quarterly tax prep: Jan 31 (25 days)
```

### Approval Request Template

```markdown
# /Vault/Pending_Approval/PAYMENT_Client_A_2026-01-07.md
---
type: approval_request
action: payment
amount: 500.00
recipient: Client A
reason: Invoice #1234 payment
created: 2026-01-07T10:30:00Z
expires: 2026-01-08T10:30:00Z
status: pending
---

## Payment Details
- Amount: $500.00
- To: Client A (Bank: XXXX1234)
- Reference: Invoice #1234

## To Approve
Move this file to /Approved folder.

## To Reject
Move this file to /Rejected folder.
```

## Learning Resources

### Prerequisites (Complete Before Hackathon)

| Topic | Resource | Time |
|-------|----------|------|
| Presentation | [Google Slides](https://docs.google.com/presentation/d/1UGvCUk1-O8m5i-aTWQNxzg8EXoKzPa8fgcwfNh8vRjQ/edit) | 2 hours |
| Claude Code Fundamentals | [Agent Factory Docs](https://agentfactory.panaversity.org/docs/AI-Tool-Landscape/claude-code-features-and-workflows) | 3 hours |
| Obsidian Fundamentals | [help.obsidian.md](https://help.obsidian.md/Getting+started) | 30 min |
| Python File I/O | [Real Python](https://realpython.com/read-write-files-python) | 1 hour |
| MCP Introduction | [modelcontextprotocol.io](https://modelcontextprotocol.io/introduction) | 1 hour |
| Agent Skills | [Claude Docs](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview) | 2 hours |

### Core Learning (During Hackathon)

| Topic | Resource | Type |
|-------|----------|------|
| Claude + Obsidian Integration | [YouTube](https://www.youtube.com/watch?v=sCIS05Qt79Y) | Video |
| Building MCP Servers | [Quickstart](https://modelcontextprotocol.io/quickstart) | Tutorial |
| Claude Agent Teams | [YouTube](https://www.youtube.com/watch?v=0J2_YGuNrDo) | Video |
| Gmail API Setup | [Google Docs](https://developers.google.com/gmail/api/quickstart) | Docs |
| Playwright Automation | [Playwright Docs](https://playwright.dev/python/docs/intro) | Docs |

### Deep Dives (Post-Hackathon)

- **MCP Server Development**: [github.com/anthropics/mcp-servers](https://github.com/anthropics/mcp-servers)
- **Production Automation**: "Automate the Boring Stuff with Python" (free online book)
- **Odoo Integration**: [Odoo 19 External API Docs](https://www.odoo.com/documentation/19.0/developer/reference/external_api.html)

## Weekly Research Meeting

- **When**: Wednesdays at 10:00 PM PKT
- **Zoom**: https://us06web.zoom.us/j/87188707642?pwd=a9XloCsinvn1JzICbPc2YGUvWTbOTr.1
- **YouTube**: https://www.youtube.com/@panaversity

## Related Resources

- [Claude Code Agent Skills Documentation](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview)
- [Ralph Wiggum Stop Hook](https://github.com/anthropics/claude-code/tree/main/.claude/plugins/ralph-wiggum)
- [MCP Odoo Integration](https://github.com/AlanOgic/mcp-odoo-adv)
- [Oracle Cloud Free VMs](https://www.oracle.com/cloud/free/)

## Qwen Added Memories
- User uses Qwen CLI (not Claude CLI) for their AI Employee project
- User wants skills created for: PDF reading, XLS/XLSX reading, and diagram generation. Also needs README.md with architecture diagrams and project structure.
