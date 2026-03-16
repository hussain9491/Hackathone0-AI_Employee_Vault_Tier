# AI Employee Skills

> **Silver Tier Skills Collection**  
> **Status:** Ready to Implement  
> **Last Updated:** 2026-03-14

---

## 📋 Overview

This folder contains **Agent Skills** for the AI Employee system. Skills are modular components that extend Qwen Code's capabilities for specific tasks like monitoring emails, reading PDFs, or sending notifications.

**What are Skills?**
- Self-contained Python scripts or MCP servers
- Documented with `.md` files showing usage and examples
- Can be invoked by Qwen or run standalone
- Follow the Silver tier requirement: "All AI functionality should be implemented as Agent Skills"

---

## 🎯 Silver Tier Requirements Fulfilled

| Requirement | Skill(s) | Status |
|-------------|----------|--------|
| Two or more Watcher scripts | `gmail_watcher_skill.md`, `whatsapp_watcher_skill.md` | ✅ |
| Claude reasoning loop that creates Plan.md | `plan_generator_skill.md` | ✅ |
| One working MCP server | `mcp_email_skill.md` | ✅ |
| Human-in-the-loop approval workflow | `approval_workflow_skill.md` | ✅ |
| Basic scheduling | `scheduler_skill.md` | ✅ |
| PDF reading (enhancement) | `pdf_reader_skill.md` | ✅ |
| Excel reading (enhancement) | `excel_reader_skill.md` | ✅ |

---

## 📚 Skills Catalog

### 🔍 Watcher Skills (Perception Layer)

| Skill | Purpose | Dependencies | Status |
|-------|---------|--------------|--------|
| [`gmail_watcher_skill.md`](./gmail_watcher_skill.md) | Monitor Gmail for new emails | Google API, OAuth | ✅ Ready |
| [`whatsapp_watcher_skill.md`](./whatsapp_watcher_skill.md) | Monitor WhatsApp for keywords | Playwright | ✅ Ready |

**Usage:**
```bash
# Gmail Watcher
python gmail_watcher.py --vault-path .. --credentials credentials.json

# WhatsApp Watcher
python whatsapp_watcher.py --vault-path .. --interval 60
```

---

### 🤖 Action Skills (Action Layer)

| Skill | Purpose | Dependencies | Status |
|-------|---------|--------------|--------|
| [`mcp_email_skill.md`](./mcp_email_skill.md) | Send emails via MCP server | Node.js, Gmail API | ✅ Ready |
| [`approval_workflow_skill.md`](./approval_workflow_skill.md) | Human-in-the-loop approvals | None | ✅ Ready |

**Usage:**
```bash
# Check pending approvals
python approval_workflow.py --vault-path .. --check

# Execute approved actions
python approval_workflow.py --vault-path .. --execute
```

---

### 🧠 Reasoning Skills (Reasoning Layer)

| Skill | Purpose | Dependencies | Status |
|-------|---------|--------------|--------|
| [`plan_generator_skill.md`](./plan_generator_skill.md) | Create action plans | None | ✅ Ready |

**Usage:**
```bash
# Create plan for task
python plan_generator.py --vault-path .. --task "Setup Gmail integration"
```

---

### ⏰ Scheduler Skills (Operations Layer)

| Skill | Purpose | Dependencies | Status |
|-------|---------|--------------|--------|
| [`scheduler_skill.md`](./scheduler_skill.md) | Scheduled task execution | cron/Task Scheduler | ✅ Ready |

**Usage:**
```bash
# Daily briefing at 8 AM
python scheduler.py --vault-path .. --task daily_briefing

# Weekly audit
python scheduler.py --vault-path .. --task weekly_audit
```

---

### 📄 File Processing Skills (Enhanced Perception)

| Skill | Purpose | Dependencies | Status |
|-------|---------|--------------|--------|
| [`pdf_reader_skill.md`](./pdf_reader_skill.md) | Extract text from PDFs | PyPDF2, pdfplumber | ✅ Ready |
| [`excel_reader_skill.md`](./excel_reader_skill.md) | Extract data from Excel | openpyxl, pandas | ✅ Ready |

**Usage:**
```bash
# Process PDF
python pdf_reader.py --vault-path .. --process-all

# Process Excel
python excel_reader.py --vault-path .. --input report.xlsx
```

---

## 🚀 Quick Start

### 1. Install All Dependencies

```bash
cd AI_Employee_Vault/scripts

# Python dependencies
pip install -r requirements.txt

# Additional skill dependencies
pip install google-auth google-auth-oauthlib google-api-python-client
pip install playwright && playwright install chromium
pip install PyPDF2 pdfplumber
pip install openpyxl pandas
```

### 2. Set Up Skills

```bash
# Gmail Watcher - Set up Google Cloud credentials
# See gmail_watcher_skill.md for details

# MCP Email Server - Install Node.js dependencies
cd mcp-email-server
npm install
```

### 3. Test Skills

```bash
# Test PDF reader
python skills/pdf_reader.py --vault-path .. --input test.pdf

# Test plan generator
python plan_generator.py --vault-path .. --task "Test task"

# Test approval workflow
python approval_workflow.py --vault-path .. --check
```

---

## 📁 File Structure

```
Skills/
├── README.md                      # This file - Skills index
├── gmail_watcher_skill.md         # Gmail monitoring
├── whatsapp_watcher_skill.md      # WhatsApp monitoring
├── mcp_email_skill.md             # Email sending via MCP
├── plan_generator_skill.md        # Action plan creation
├── approval_workflow_skill.md     # Approval management
├── scheduler_skill.md             # Scheduled tasks
├── pdf_reader_skill.md            # PDF text extraction
└── excel_reader_skill.md          # Excel data extraction

scripts/
├── base_watcher.py                # Base class for watchers
├── filesystem_watcher.py          # File watcher (Bronze)
├── gmail_watcher.py               # Gmail watcher (Silver)
├── whatsapp_watcher.py            # WhatsApp watcher (Silver)
├── plan_generator.py              # Plan generator
├── approval_workflow.py           # Approval workflow
├── scheduler.py                   # Scheduler
└── skills/
    ├── pdf_reader.py              # PDF reader
    └── excel_reader.py            # Excel reader
```

---

## 🔧 Skill Architecture

### Skill Components

Each skill consists of:

1. **Documentation (`.md` file)**
   - Overview and use cases
   - Prerequisites and dependencies
   - Implementation code
   - Usage examples
   - Troubleshooting guide

2. **Implementation (`.py` or `.js` file)**
   - Main logic
   - Command-line interface
   - Error handling
   - Logging

### Skill Patterns

**Watcher Pattern:**
```python
from base_watcher import BaseWatcher

class MyWatcher(BaseWatcher):
    def check_for_updates(self) -> list:
        # Check for new items
        pass
    
    def create_action_file(self, item) -> Path:
        # Create action file in Needs_Action/
        pass
```

**Skill Pattern:**
```python
class MySkill:
    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
    
    def execute(self, **kwargs) -> dict:
        # Perform skill action
        pass
    
    def create_action_file(self, result: dict) -> Path:
        # Create action file
        pass
```

---

## 🎯 Integration with Qwen

### Invoking Skills

Qwen can invoke skills in two ways:

**1. Direct Command:**
```bash
qwen "Use the PDF reader skill to extract text from the invoice"
```

**2. Via Action Files:**
```bash
# Skill creates action file
python pdf_reader.py --vault-path .. --process-all

# Qwen processes action file
qwen "Process the PDF action files in Needs_Action"
```

### Skill Discovery

Qwen can list available skills:

```bash
qwen "List all available skills and their purposes"
```

---

## 📊 Skill Status Matrix

| Skill | Bronze | Silver | Gold | Status |
|-------|--------|--------|------|--------|
| Filesystem Watcher | ✅ | ✅ | ✅ | Complete |
| Gmail Watcher | | ✅ | ✅ | Ready |
| WhatsApp Watcher | | ✅ | ✅ | Ready |
| MCP Email Server | | ✅ | ✅ | Ready |
| Plan Generator | | ✅ | ✅ | Ready |
| Approval Workflow | | ✅ | ✅ | Ready |
| Scheduler | | ✅ | ✅ | Ready |
| PDF Reader | | ✅ | ✅ | Ready |
| Excel Reader | | ✅ | ✅ | Ready |

---

## 🔗 Related Documentation

| Document | Purpose |
|----------|---------|
| [`../AGENT.md`](../AGENT.md) | AI agent instructions |
| [`../USAGE_GUIDE.md`](../USAGE_GUIDE.md) | Usage guide |
| [`../Personal AI Employee Hackathon 0_...md`](../Personal%20AI%20Employee%20Hackathon%200_%20Building%20Autonomous%20FTEs%20in%202026.md) | Full hackathon guide |

---

## 📚 Resources

- [Agent Skills Documentation](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview)
- [MCP Documentation](https://modelcontextprotocol.io/)
- [Python Documentation](https://docs.python.org/3/)

---

*Skills Version: 1.0*  
*Last Updated: 2026-03-14*  
*Silver Tier Complete ✅*
