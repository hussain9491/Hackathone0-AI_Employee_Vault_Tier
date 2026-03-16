---
name: approval-workflow
description: |
  Manage human-in-the-loop approvals for sensitive actions (payments, emails, external
  API calls). Use when tasks require human oversight before execution. Creates approval
  requests in Pending_Approval/ and processes Approved/ files.
---

# Approval Workflow Skill

Manage human-in-the-loop approvals for sensitive actions.

## Installation

No additional dependencies required.

## Quick Reference

### Check Pending Approvals

```bash
# Check what's pending
python AI_Employee_Vault/scripts/approval_workflow.py --vault-path AI_Employee_Vault --check
```

### Execute Approved Actions

```bash
# Execute all approved actions
python AI_Employee_Vault/scripts/approval_workflow.py --vault-path AI_Employee_Vault --execute
```

### With Qwen

```bash
# Create approval request
qwen "Create an approval request for sending invoice email to client@example.com"

# Check and execute approvals
qwen "Check Approved folder and execute pending approvals"
```

## Workflow: Approval Process

1. Qwen detects sensitive action needed
2. Creates approval request in `Pending_Approval/`
3. User reviews and moves to `Approved/`
4. Qwen executes approved action
5. Moves to `Done/` and logs

## Actions Requiring Approval

| Action | Threshold |
|--------|-----------|
| Payments | All payments (configurable: >$100) |
| Email sending | All external emails |
| Social media posts | All posts |
| File deletion | Any deletion |
| API calls | External system changes |

## Output Format

Approval request in `Pending_Approval/`:

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

**Amount:** $150.00
**Recipient:** Electric Company
**Reason:** Monthly electric bill

## To Approve
Move this file to /Approved folder.

## To Reject
Move this file to /Rejected folder.
```

## User Actions

**To Approve:**
1. Review approval request
2. Move file from `Pending_Approval/` to `Approved/`
3. Qwen will execute automatically

**To Reject:**
1. Move file to `Rejected/` or delete
2. Add reason in notes (optional)

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Not executing | Run with `--execute` flag |
| Stale approvals | Check files older than 2 days |
| Missing action type | Ensure YAML frontmatter has `action:` field |

## Related Skills

- `mcp-email` - Send approved emails
- `plan-generator` - Create plans requiring approval
- `scheduler` - Schedule approval reminders
