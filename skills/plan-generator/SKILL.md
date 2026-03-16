---
name: plan-generator
description: |
  Create structured action plans for complex multi-step tasks. Use when tasks require
  breaking down complex work into manageable steps with tracking and progress logging.
  Creates Plan_*.md files in the Plans/ folder.
---

# Plan Generator Skill

Create structured action plans for complex tasks.

## Installation

No additional dependencies required.

## Quick Reference

### Create Plan

```bash
# Create plan for task
python AI_Employee_Vault/scripts/plan_generator.py --vault-path AI_Employee_Vault --task "Setup Gmail integration"

# With priority
python AI_Employee_Vault/scripts/plan_generator.py --vault-path AI_Employee_Vault --task "WhatsApp monitoring" --priority high

# With custom steps
python AI_Employee_Vault/scripts/plan_generator.py --vault-path AI_Employee_Vault --task "PDF reader" --steps "Install PyPDF2" "Create script" "Test"
```

### With Qwen

```bash
# Ask Qwen to create a plan
qwen "Create a detailed plan for implementing PDF reading functionality"

# Update existing plan
qwen "Update the Gmail integration plan with progress"
```

## Workflow: Plan Creation

1. Identify complex multi-step task
2. Run plan-generator skill
3. Skill creates `Plans/Plan_YYYY-MM-DD_Topic.md`
4. Work through checklist
5. Update progress log
6. Move to `Done/` when complete

## Output Format

Plan file created in `Plans/`:

```markdown
---
created: 2026-03-14T10:30:00
status: in_progress
priority: high
topic: Setup Gmail integration
---

# Plan: Setup Gmail integration

**Created:** 2026-03-14
**Status:** 🟡 In Progress
**Priority:** High

## Objective

Successfully implement: Setup Gmail integration.

## Steps

- [ ] Research Gmail API requirements
- [ ] Set up Google Cloud project
- [ ] Enable Gmail API
- [ ] Create OAuth credentials
- [ ] Install Python dependencies
- [ ] Create gmail_watcher.py script
- [ ] Test authentication flow
- [ ] Test email detection

## Resources Needed

- Python environment
- Google Cloud account
- Gmail API credentials

## Success Criteria

- [ ] All steps completed
- [ ] Plan moved to /Done
- [ ] Dashboard.md updated
```

## Priority Levels

| Priority | Use When |
|----------|----------|
| `low` | Nice to have, no deadline |
| `medium` | Normal tasks |
| `high` | Important, deadline soon |
| `critical` | Urgent, blocking other work |

## Related Skills

- `approval-workflow` - Approve plans
- `scheduler` - Schedule plan reviews
- `gmail-watcher` - Gmail implementation plan
