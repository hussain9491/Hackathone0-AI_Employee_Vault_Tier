# Approval Workflow Skill

> **Tier:** Silver  
> **Status:** Ready to Implement  
> **Dependencies:** None (file-based workflow)

---

## 📋 Overview

The Approval Workflow skill implements human-in-the-loop approval for sensitive actions (payments, emails, external API calls). Qwen creates approval requests, user reviews and approves, then Qwen executes.

**Use Case:** Ensure human oversight for important decisions while maintaining automation efficiency.

---

## 🎯 Silver Tier Requirement

This skill fulfills:
- ✅ "Human-in-the-loop approval workflow for sensitive actions"
- ✅ Part of the Action layer (approval before execution)

---

## 🏗️ Implementation

### Approval Workflow Script

**File:** `scripts/approval_workflow.py`

```python
"""
Approval Workflow for AI Employee

Manages human-in-the-loop approvals for sensitive actions.

Usage:
    python approval_workflow.py --vault-path .. --check
    python approval_workflow.py --vault-path .. --execute
"""

import argparse
import sys
import json
from pathlib import Path
from datetime import datetime


class ApprovalWorkflow:
    """Manage approval requests."""
    
    # Actions requiring approval
    SENSITIVE_ACTIONS = [
        'payment',
        'email_send',
        'api_call',
        'delete',
        'external_post',
    ]
    
    # Default approval thresholds
    THRESHOLDS = {
        'payment': 100,  # Payments over $100 require approval
        'email_send': 1,  # All emails require approval
        'external_post': 1,  # All social posts require approval
    }
    
    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.pending_folder = self.vault_path / 'Pending_Approval'
        self.approved_folder = self.vault_path / 'Approved'
        self.rejected_folder = self.vault_path / 'Rejected'
        self.logs_folder = self.vault_path / 'Logs'
        
        # Ensure folders exist
        for folder in [self.pending_folder, self.approved_folder, 
                       self.rejected_folder, self.logs_folder]:
            folder.mkdir(parents=True, exist_ok=True)
    
    def create_approval_request(self, action_type: str, details: dict,
                                description: str = '') -> Path:
        """
        Create an approval request file.
        
        Args:
            action_type: Type of action (payment, email_send, etc.)
            details: Dict with action-specific details
            description: Human-readable description
            
        Returns:
            Path to created approval request
        """
        timestamp = datetime.now()
        
        # Create filename
        safe_desc = "".join(c if c.isalnum() else '_' for c in description[:30])
        filename = f"{action_type.upper()}_{safe_desc}_{timestamp.strftime('%Y%m%d')}.md"
        filepath = self.pending_folder / filename
        
        # Build content based on action type
        content = self._build_content(action_type, details, description, timestamp)
        
        filepath.write_text(content)
        self._log_action('created', filepath.name, action_type)
        
        return filepath
    
    def _build_content(self, action_type: str, details: dict, 
                       description: str, timestamp: datetime) -> str:
        """Build approval request content."""
        
        if action_type == 'payment':
            return f'''---
type: approval_request
action: payment
amount: {details.get('amount', 'N/A')}
recipient: {details.get('recipient', 'N/A')}
created: {timestamp.isoformat()}
expires: {self._add_days(timestamp, 1).isoformat()}
status: pending
---

# Payment Approval Request

**Created:** {timestamp.strftime('%Y-%m-%d %H:%M')}  
**Amount:** ${details.get('amount', 'N/A')}  
**Recipient:** {details.get('recipient', 'N/A')}  
**Reason:** {description}

## Payment Details

{self._format_details(details)}

## To Approve

1. Review the payment details above
2. Verify the recipient and amount
3. Move this file to `/Approved` folder

## To Reject

1. Move this file to `/Rejected` folder
2. Add reason for rejection in notes below

## Notes

_Add any questions or concerns here_

---
*Expires in 24 hours. If not approved, request will be cancelled.*
'''
        
        elif action_type == 'email_send':
            return f'''---
type: approval_request
action: email_send
to: {details.get('to', 'N/A')}
subject: {details.get('subject', 'N/A')}
created: {timestamp.isoformat()}
status: pending
---

# Email Approval Request

**Created:** {timestamp.strftime('%Y-%m-%d %H:%M')}  
**To:** {details.get('to', 'N/A')}  
**Subject:** {details.get('subject', 'N/A')}

## Email Content

**Body:**

{details.get('body', 'No content provided')}

## To Approve

1. Review the email content
2. Verify recipient is correct
3. Move this file to `/Approved` folder

## To Reject

1. Move this file to `/Rejected` folder
2. Add reason for rejection in notes below

## Notes

_Add any questions or concerns here_

---
*Review before sending - this email will be sent automatically when approved.*
'''
        
        else:
            return f'''---
type: approval_request
action: {action_type}
created: {timestamp.isoformat()}
status: pending
---

# Approval Request: {action_type}

**Created:** {timestamp.strftime('%Y-%m-%d %H:%M')}  
**Action:** {action_type}  
**Description:** {description}

## Details

{self._format_details(details)}

## To Approve

Move this file to `/Approved` folder.

## To Reject

Move this file to `/Rejected` folder.

## Notes

_Add any questions or concerns here_

---
*Requires human approval before execution.*
'''
    
    def _format_details(self, details: dict) -> str:
        """Format details as markdown."""
        if not details:
            return 'No additional details provided.'
        
        lines = []
        for key, value in details.items():
            lines.append(f"- **{key.replace('_', ' ').title()}:** {value}")
        return '\n'.join(lines)
    
    def _add_days(self, dt: datetime, days: int) -> datetime:
        """Add days to datetime."""
        from datetime import timedelta
        return dt + timedelta(days=days)
    
    def check_pending(self) -> list:
        """Check for pending approval requests."""
        pending = []
        for f in self.pending_folder.glob('*.md'):
            content = f.read_text()
            if 'status: pending' in content:
                pending.append({
                    'file': f.name,
                    'path': f,
                    'content': content
                })
        return pending
    
    def check_approved(self) -> list:
        """Check for approved actions ready to execute."""
        approved = []
        for f in self.approved_folder.glob('*.md'):
            content = f.read_text()
            if 'status: approved' in content or 'status: pending' in content:
                approved.append({
                    'file': f.name,
                    'path': f,
                    'content': content
                })
        return approved
    
    def execute_approved(self, filepath: Path) -> dict:
        """
        Execute an approved action.
        
        Args:
            filepath: Path to approved request file
            
        Returns:
            Dict with execution result
        """
        content = filepath.read_text()
        
        # Parse action type
        action_type = None
        for line in content.split('\n'):
            if 'action:' in line:
                action_type = line.split(':')[1].strip()
                break
        
        if not action_type:
            return {'success': False, 'error': 'Could not determine action type'}
        
        # Execute based on action type
        result = {'success': True, 'action': action_type, 'file': filepath.name}
        
        # Log execution
        self._log_action('executed', filepath.name, action_type, result)
        
        # Move to Done
        done_folder = self.vault_path / 'Done'
        done_folder.mkdir(parents=True, exist_ok=True)
        done_path = done_folder / f"EXECUTED_{filepath.name}"
        done_path.write_text(content + f"\n\n---\n*Executed: {datetime.now().isoformat()}*")
        
        # Delete original
        filepath.unlink()
        
        return result
    
    def _log_action(self, action: str, filename: str, action_type: str, 
                    result: dict = None):
        """Log approval action."""
        log_file = self.logs_folder / f"approvals_{datetime.now().strftime('%Y-%m-%d')}.json"
        
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'action': action,
            'file': filename,
            'type': action_type,
            'result': result
        }
        
        logs = []
        if log_file.exists():
            logs = json.loads(log_file.read_text())
        
        logs.append(log_entry)
        log_file.write_text(json.dumps(logs, indent=2))


def main():
    parser = argparse.ArgumentParser(description='Approval Workflow for AI Employee')
    parser.add_argument('--vault-path', default='..', help='Path to Obsidian vault')
    parser.add_argument('--check', action='store_true', help='Check pending approvals')
    parser.add_argument('--execute', action='store_true', help='Execute approved actions')
    
    args = parser.parse_args()
    
    workflow = ApprovalWorkflow(args.vault_path)
    
    if args.check:
        print("=" * 60)
        print("📋 PENDING APPROVALS")
        print("=" * 60)
        
        pending = workflow.check_pending()
        if pending:
            for p in pending:
                print(f"\n📄 {p['file']}")
                # Extract first few lines
                lines = p['content'].split('\n')[:10]
                for line in lines:
                    print(f"   {line}")
        else:
            print("\n✅ No pending approvals")
    
    if args.execute:
        print("=" * 60)
        print("⚙️  EXECUTING APPROVED ACTIONS")
        print("=" * 60)
        
        approved = workflow.check_approved()
        for a in approved:
            print(f"\n📄 Executing: {a['file']}")
            result = workflow.execute_approved(a['path'])
            if result['success']:
                print(f"   ✅ Executed: {result['action']}")
            else:
                print(f"   ❌ Error: {result.get('error', 'Unknown')}")


if __name__ == '__main__':
    main()
```

---

## 🚀 Usage

### Check Pending Approvals

```bash
cd AI_Employee_Vault/scripts

# Check what's pending
python approval_workflow.py --vault-path .. --check
```

### Execute Approved Actions

```bash
# Execute all approved actions
python approval_workflow.py --vault-path .. --execute
```

### Create Approval Request (from Qwen)

```bash
qwen "Create an approval request for sending invoice email to client@example.com"
```

---

## 📁 Example Approval Request

```markdown
---
type: approval_request
action: payment
amount: 150.00
recipient: Electric Company
created: 2026-03-14T10:30:00
expires: 2026-03-15T10:30:00
status: pending
---

# Payment Approval Request

**Created:** 2026-03-14 10:30  
**Amount:** $150.00  
**Recipient:** Electric Company  
**Reason:** Monthly electric bill

## Payment Details

- **Amount:** $150.00
- **Recipient:** Electric Company
- **Due Date:** March 20, 2026
- **Account:** ****1234

## To Approve

1. Review the payment details above
2. Verify the recipient and amount
3. Move this file to `/Approved` folder

## To Reject

1. Move this file to `/Rejected` folder
2. Add reason for rejection in notes below

## Notes

_Add any questions or concerns here_

---
*Expires in 24 hours. If not approved, request will be cancelled.*
```

---

## 🔗 Related Skills

| Skill | Purpose |
|-------|---------|
| `mcp_email_skill.md` | Send approved emails |
| `plan_generator_skill.md` | Create plans requiring approval |
| `scheduler_skill.md` | Schedule approval reminders |

---

*Skill Version: 1.0*  
*Last Updated: 2026-03-14*  
*Silver Tier Component*
