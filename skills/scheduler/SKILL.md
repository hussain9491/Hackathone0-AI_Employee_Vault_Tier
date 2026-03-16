---
name: scheduler
description: |
  Run scheduled AI Employee tasks (daily briefings, weekly audits, periodic checks).
  Use with cron (Linux/Mac) or Task Scheduler (Windows) for automated execution.
  Creates Briefings/*.md files with scheduled reports.
---

# Scheduler Skill

Run scheduled AI Employee tasks automatically.

## Installation

No additional dependencies required.

## Quick Reference

### Manual Execution

```bash
# Daily briefing
python AI_Employee_Vault/scripts/scheduler.py --vault-path AI_Employee_Vault --task daily_briefing

# Weekly audit
python AI_Employee_Vault/scripts/scheduler.py --vault-path AI_Employee_Vault --task weekly_audit

# Check pending approvals
python AI_Employee_Vault/scripts/scheduler.py --vault-path AI_Employee_Vault --task check_pending
```

### Schedule with cron (Linux/Mac)

```bash
crontab -e

# Daily briefing at 8:00 AM
0 8 * * * cd /path/to/AI_Employee_Vault/scripts && python scheduler.py --vault-path .. --task daily_briefing

# Weekly audit on Sunday at 9:00 AM
0 9 * * 0 cd /path/to/AI_Employee_Vault/scripts && python scheduler.py --vault-path .. --task weekly_audit
```

### Schedule with Task Scheduler (Windows)

```powershell
# Create scheduled task
$action = New-ScheduledTaskAction -Execute "python" `
  -Argument "scheduler.py --vault-path .. --task daily_briefing" `
  -WorkingDirectory "C:\path\to\AI_Employee_Vault\scripts"

$trigger = New-ScheduledTaskTrigger -Daily -At 8:00AM

Register-ScheduledTask -TaskName "AI_Employee_Daily_Briefing" `
  -Action $action -Trigger $trigger
```

### With Qwen

```bash
# Generate daily briefing
qwen "Run the scheduler to generate today's daily briefing"

# Weekly audit
qwen "Generate the weekly business audit report"
```

## Workflow: Scheduled Tasks

1. Schedule task (cron/Task Scheduler)
2. Scheduler runs at scheduled time
3. Creates briefing in `Briefings/`
4. Updates `Dashboard.md`
5. Ready for review

## Available Tasks

| Task | Description | Recommended Schedule |
|------|-------------|---------------------|
| `daily_briefing` | Summary of daily activity | 8:00 AM daily |
| `weekly_audit` | Business audit for the week | Sunday 9:00 AM |
| `check_pending` | Check stale approvals | Every 6 hours |

## Output Format

Daily briefing in `Briefings/`:

```markdown
---
generated: 2026-03-14T08:00:00
type: daily_briefing
date: 2026-03-14
---

# Daily Briefing: 2026-03-14

## Today's Activity

| Metric | Count |
|--------|-------|
| Completed Tasks | 5 |
| Pending Tasks | 2 |
| Awaiting Approval | 1 |

## Completed Today

- FILE_invoice_march.md
- EMAIL_project_update.md

## Suggestions

- ⏳ Pending approvals need attention
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Task not running | Check cron/Task Scheduler status |
| Permission denied | Run with appropriate user permissions |
| Python not found | Use full path to Python executable |

## Related Skills

- `plan-generator` - Create scheduled plans
- `approval-workflow` - Scheduled approval checks
- `gmail-watcher` - Scheduled email checks
