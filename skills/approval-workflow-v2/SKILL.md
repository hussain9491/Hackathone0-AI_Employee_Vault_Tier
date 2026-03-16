---
name: approval-workflow-v2
description: |
  Human-in-the-loop approval workflow for sensitive actions (payments, emails, posts,
  API calls). Creates approval requests, tracks approvals, and executes approved actions.
  Enhanced version with multi-level approvals and expiration.
---

# Approval Workflow V2 Skill

Human-in-the-loop approval for sensitive actions.

## Installation

No additional dependencies required.

## Quick Reference

### Check Pending Approvals

```bash
# List all pending approvals
python AI_Employee_Vault/scripts/approval_workflow_v2.py --vault-path AI_Employee_Vault --check

# Execute approved actions
python AI_Employee_Vault/scripts/approval_workflow_v2.py --vault-path AI_Employee_Vault --execute

# Clean expired approvals
python AI_Employee_Vault/scripts/approval_workflow_v2.py --vault-path AI_Employee_Vault --cleanup
```

### With Qwen

```bash
# Create approval request
qwen "Create an approval request for sending invoice email to client@example.com"

# Check and execute
qwen "Check Approved folder and execute pending approvals"

# Generate approval report
qwen "Generate a report of all pending and expired approvals"
```

## Actions Requiring Approval

| Action Type | Threshold | Auto-Reject After |
|-------------|-----------|-------------------|
| Payments | All payments | 7 days |
| Email (external) | All external emails | 2 days |
| LinkedIn posts | All posts | 3 days |
| API calls (write) | All write operations | 1 day |
| File deletion | Any deletion | 7 days |
| Large payments | > $1000 | 24 hours (escalate) |

## Workflow: Approval Process

```
1. Qwen detects sensitive action
         ↓
2. Creates approval request in Pending_Approval/
         ↓
3. User receives notification (email/dashboard)
         ↓
4. User reviews and moves to Approved/ or Rejected/
         ↓
5. If Approved: Qwen executes action
         ↓
6. Logs to Logs/approvals_YYYY-MM-DD.json
```

## Approval Workflow Implementation

```python
# AI_Employee_Vault/scripts/approval_workflow_v2.py
import argparse
import json
from pathlib import Path
from datetime import datetime, timedelta

class ApprovalWorkflowV2:
    """Enhanced approval workflow with expiration and escalation."""
    
    SENSITIVE_ACTIONS = {
        'payment': {'threshold': 100, 'expires_days': 7, 'escalate_threshold': 1000},
        'email_send': {'threshold': 1, 'expires_days': 2, 'escalate_threshold': None},
        'linkedin_post': {'threshold': 1, 'expires_days': 3, 'escalate_threshold': None},
        'api_call': {'threshold': 1, 'expires_days': 1, 'escalate_threshold': None},
        'delete': {'threshold': 1, 'expires_days': 7, 'escalate_threshold': None},
    }
    
    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.pending_folder = self.vault_path / 'Pending_Approval'
        self.approved_folder = self.vault_path / 'Approved'
        self.rejected_folder = self.vault_path / 'Rejected'
        self.logs_folder = self.vault_path / 'Logs'
        
        for folder in [self.pending_folder, self.approved_folder, 
                       self.rejected_folder, self.logs_folder]:
            folder.mkdir(parents=True, exist_ok=True)
    
    def create_approval_request(self, action_type: str, details: dict,
                                description: str = '', priority: str = 'normal') -> Path:
        """Create approval request with expiration."""
        timestamp = datetime.now()
        config = self.SENSITIVE_ACTIONS.get(action_type, {'expires_days': 7})
        expires = timestamp + timedelta(days=config['expires_days'])
        
        # Determine if escalation needed
        needs_escalation = False
        if config.get('escalate_threshold') and details.get('amount', 0) > config['escalate_threshold']:
            needs_escalation = True
            priority = 'critical'
        
        # Create filename
        safe_desc = "".join(c if c.isalnum() else '_' for c in description[:30])
        filename = f"{action_type.upper()}_{safe_desc}_{timestamp.strftime('%Y%m%d_%H%M')}.md"
        filepath = self.pending_folder / filename
        
        content = self._build_content(action_type, details, description, timestamp, expires, priority, needs_escalation)
        filepath.write_text(content)
        self._log_action('created', filepath.name, action_type, {'priority': priority})
        
        return filepath
    
    def _build_content(self, action_type, details, description, timestamp, expires, priority, needs_escalation):
        """Build approval request content."""
        priority_emoji = '🔴' if priority == 'critical' else ('🟡' if priority == 'high' else '⚪')
        
        if action_type == 'payment':
            return f'''---
type: approval_request
action: payment
amount: {details.get('amount', 'N/A')}
recipient: {details.get('recipient', 'N/A')}
created: {timestamp.isoformat()}
expires: {expires.isoformat()}
priority: {priority}
status: pending
---

# Payment Approval Request {priority_emoji}

**Created:** {timestamp.strftime('%Y-%m-%d %H:%M')}
**Amount:** ${details.get('amount', 'N/A')}
**Recipient:** {details.get('recipient', 'N/A')}
**Reason:** {description}
**Expires:** {expires.strftime('%Y-%m-%d %H:%M')}

{"⚠️ **ESCALATION REQUIRED:** This payment exceeds $1000 threshold." if needs_escalation else ""}

## Payment Details

{self._format_details(details)}

## To Approve

1. Review payment details
2. Verify recipient and amount
3. Move this file to `/Approved` folder

## To Reject

1. Move this file to `/Rejected` folder
2. Add reason below

## Rejection Notes

_Add reason if rejecting_

---
*Auto-rejected after {expires.strftime('%Y-%m-%d %H:%M')} if not approved*
'''
        
        elif action_type == 'email_send':
            return f'''---
type: approval_request
action: email_send
to: {details.get('to', 'N/A')}
subject: {details.get('subject', 'N/A')}
created: {timestamp.isoformat()}
expires: {expires.isoformat()}
priority: {priority}
status: pending
---

# Email Approval Request {priority_emoji}

**Created:** {timestamp.strftime('%Y-%m-%d %H:%M')}
**To:** {details.get('to', 'N/A')}
**Subject:** {details.get('subject', 'N/A')}
**Expires:** {expires.strftime('%Y-%m-%d %H:%M')}

## Email Content

**Body:**

{details.get('body', 'No content')}

## To Approve

Move to `/Approved` to send.

## To Reject

Move to `/Rejected`.

---
*Auto-rejected after {expires.strftime('%Y-%m-%d %H:%M')}*
'''
        
        else:
            return f'''---
type: approval_request
action: {action_type}
created: {timestamp.isoformat()}
expires: {expires.isoformat()}
priority: {priority}
status: pending
---

# Approval Request: {action_type} {priority_emoji}

**Created:** {timestamp.strftime('%Y-%m-%d %H:%M')}
**Action:** {action_type}
**Description:** {description}
**Expires:** {expires.strftime('%Y-%m-%d %H:%M')}

## Details

{self._format_details(details)}

## To Approve

Move to `/Approved`.

## To Reject

Move to `/Rejected`.

---
*Auto-rejected after {expires.strftime('%Y-%m-%d %H:%M')}*
'''
    
    def _format_details(self, details: dict) -> str:
        """Format details as markdown."""
        if not details:
            return '_No additional details_'
        return '\n'.join(f"- **{k.replace('_', ' ').title()}:** {v}" for k, v in details.items())
    
    def check_pending(self) -> list:
        """Check pending approvals with status."""
        pending = []
        now = datetime.now()
        
        for f in self.pending_folder.glob('*.md'):
            content = f.read_text()
            if 'status: pending' not in content:
                continue
            
            # Parse expires
            expires = None
            for line in content.split('\n'):
                if 'expires:' in line:
                    expires = datetime.fromisoformat(line.split(':')[1].strip())
                    break
            
            age = now - datetime.fromtimestamp(f.stat().st_mtime)
            status = 'expired' if expires and now > expires else 'active'
            
            pending.append({
                'file': f.name,
                'path': f,
                'age_days': age.days,
                'status': status,
                'expires': expires
            })
        
        return pending
    
    def execute_approved(self, filepath: Path) -> dict:
        """Execute approved action."""
        content = filepath.read_text()
        
        # Parse action type
        action_type = None
        for line in content.split('\n'):
            if 'action:' in line:
                action_type = line.split(':')[1].strip()
                break
        
        if not action_type:
            return {'success': False, 'error': 'Unknown action type'}
        
        result = {'success': True, 'action': action_type, 'file': filepath.name}
        
        # Log execution
        self._log_action('executed', filepath.name, action_type, result)
        
        # Move to Done
        done_folder = self.vault_path / 'Done'
        done_folder.mkdir(parents=True, exist_ok=True)
        done_path = done_folder / f"EXECUTED_{filepath.name}"
        done_path.write_text(content + f"\n\n---\n*Executed: {datetime.now().isoformat()}*")
        
        filepath.unlink()
        return result
    
    def cleanup_expired(self) -> list:
        """Move expired approvals to Rejected."""
        now = datetime.now()
        moved = []
        
        for f in self.pending_folder.glob('*.md'):
            content = f.read_text()
            expires = None
            for line in content.split('\n'):
                if 'expires:' in line:
                    expires = datetime.fromisoformat(line.split(':')[1].strip())
                    break
            
            if expires and now > expires:
                # Move to rejected
                rejected_path = self.rejected_folder / f"EXPIRED_{f.name}"
                content += f"\n\n---\n*Auto-rejected: {now.isoformat()} (expired)*"
                rejected_path.write_text(content)
                f.unlink()
                moved.append(f.name)
                self._log_action('expired', f.name, 'unknown')
        
        return moved
    
    def _log_action(self, action: str, filename: str, action_type: str, result: dict = None):
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
    parser = argparse.ArgumentParser(description='Approval Workflow V2')
    parser.add_argument('--vault-path', default='..', help='Path to vault')
    parser.add_argument('--check', action='store_true', help='Check pending')
    parser.add_argument('--execute', action='store_true', help='Execute approved')
    parser.add_argument('--cleanup', action='store_true', help='Clean expired')
    
    args = parser.parse_args()
    workflow = ApprovalWorkflowV2(args.vault_path)
    
    if args.check:
        print("=" * 60)
        print("📋 PENDING APPROVALS")
        print("=" * 60)
        pending = workflow.check_pending()
        if pending:
            for p in pending:
                emoji = "⏰ EXPIRED" if p['status'] == 'expired' else f"🕐 {p['age_days']}d old"
                print(f"\n{emoji}: {p['file']}")
        else:
            print("\n✅ No pending approvals")
    
    if args.execute:
        print("=" * 60)
        print("⚙️  EXECUTING APPROVED")
        print("=" * 60)
        for f in workflow.approved_folder.glob('*.md'):
            print(f"\n📄 Executing: {f.name}")
            result = workflow.execute_approved(f)
            print(f"   {'✅' if result['success'] else '❌'} {result.get('error', result['action'])}")
    
    if args.cleanup:
        print("=" * 60)
        print("🧹 CLEANING EXPIRED")
        print("=" * 60)
        moved = workflow.cleanup_expired()
        if moved:
            print(f"\n✅ Moved {len(moved)} expired to Rejected:")
            for f in moved:
                print(f"   - {f}")
        else:
            print("\n✅ No expired approvals")


if __name__ == '__main__':
    main()
```

## Output Format

Approval request in `Pending_Approval/`:

```markdown
---
type: approval_request
action: payment
amount: 150.00
recipient: Electric Company
created: 2026-03-14T10:30:00
expires: 2026-03-21T10:30:00
priority: normal
status: pending
---

# Payment Approval Request ⚪

**Created:** 2026-03-14 10:30
**Amount:** $150.00
**Recipient:** Electric Company
**Expires:** 2026-03-21 10:30

## Payment Details

- **Amount:** $150.00
- **Due Date:** March 20, 2026

## To Approve

Move to `/Approved`.

## To Reject

Move to `/Rejected`.

---
*Auto-rejected after 2026-03-21 10:30*
```

## Priority Levels

| Priority | Color | Response Time | Example |
|----------|-------|---------------|---------|
| Critical | 🔴 | Immediate | Payments > $1000 |
| High | 🟡 | 4 hours | Urgent emails |
| Normal | ⚪ | 24 hours | Regular approvals |

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Not executing | Run with `--execute` flag |
| Expired approvals | Run `--cleanup` to move to Rejected |
| Missing action type | Check YAML frontmatter has `action:` |

## Related Skills

- `email-mcp` - Send approved emails
- `linkedin-poster` - Post approved content
- `scheduler` - Schedule approval reminders

---

*Skill Version: 2.0 | Last Updated: 2026-03-14 | Silver Tier*
