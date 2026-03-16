---
name: subscription-tracker
description: |
  Monitor recurring subscriptions, track monthly/annual costs, flag unused
  subscriptions, and suggest cancellations. Integrates with bank-watcher to
  detect recurring charges. Essential for cost optimization in CEO briefings.
---

# Subscription Tracker Skill

Track and optimize recurring subscription costs.

## Installation

```bash
pip install pandas
```

## Quick Reference

### Track Subscriptions

```bash
# Analyze transactions for subscriptions
python AI_Employee_Vault/scripts/subscription_tracker.py --vault-path AI_Employee_Vault --action analyze

# List all subscriptions
python AI_Employee_Vault/scripts/subscription_tracker.py --vault-path AI_Employee_Vault --action list

# Check for unused subscriptions
python AI_Employee_Vault/scripts/subscription_tracker.py --vault-path AI_Employee_Vault --action audit

# Generate cost report
python AI_Employee_Vault/scripts/subscription_tracker.py --vault-path AI_Employee_Vault --action report
```

### With Qwen

```bash
# Analyze subscriptions
qwen "Use the subscription-tracker skill to find all recurring charges"

# Audit subscriptions
qwen "Use subscription-tracker to identify subscriptions we haven't used in 30 days"

# Generate report
qwen "Use subscription-tracker to create a monthly subscription cost report"
```

## Setup: Subscription Database

### Initialize Subscription Database

```bash
python AI_Employee_Vault/scripts/subscription_tracker.py --vault-path AI_Employee_Vault --action init
```

Creates `AI_Employee_Vault/Subscriptions/subscriptions.json`

## Workflow: Subscription Tracking

```
1. Bank Watcher imports transactions
         ↓
2. Subscription Tracker analyzes for recurring charges
         ↓
3. Identifies patterns (same amount, similar dates)
         ↓
4. Creates/updates subscription records
         ↓
5. Flags unused subscriptions (no login in 30+ days)
         ↓
6. Generates cost optimization report for CEO briefing
```

## Subscription Tracker Implementation

```python
# AI_Employee_Vault/scripts/subscription_tracker.py
import argparse
import json
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict

class SubscriptionTracker:
    # Known subscription patterns
    SUBSCRIPTION_PATTERNS = {
        'netflix': {'keywords': ['netflix'], 'name': 'Netflix'},
        'spotify': {'keywords': ['spotify'], 'name': 'Spotify'},
        'adobe': {'keywords': ['adobe', 'creative cloud'], 'name': 'Adobe Creative Cloud'},
        'notion': {'keywords': ['notion'], 'name': 'Notion'},
        'slack': {'keywords': ['slack'], 'name': 'Slack'},
        'zoom': {'keywords': ['zoom'], 'name': 'Zoom'},
        'github': {'keywords': ['github'], 'name': 'GitHub'},
        'aws': {'keywords': ['aws', 'amazon web services'], 'name': 'AWS'},
        'microsoft': {'keywords': ['microsoft', 'office 365'], 'name': 'Microsoft 365'},
        'google': {'keywords': ['google one', 'google workspace'], 'name': 'Google Workspace'},
    }
    
    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.subscriptions_folder = self.vault_path / 'Subscriptions'
        self.logs_folder = self.vault_path / 'Logs'
        self.accounting_folder = self.vault_path / 'Accounting'
        
        for folder in [self.subscriptions_folder, self.logs_folder, self.accounting_folder]:
            folder.mkdir(parents=True, exist_ok=True)
        
        self.subscriptions_file = self.subscriptions_folder / 'subscriptions.json'
        self.logins_file = self.subscriptions_folder / 'last_logins.json'
    
    def initialize(self):
        """Initialize subscription database."""
        if not self.subscriptions_file.exists():
            self.subscriptions_file.write_text(json.dumps([], indent=2))
        if not self.logins_file.exists():
            self.logins_file.write_text(json.dumps({}, indent=2))
        print("✅ Subscription database initialized")
    
    def analyze_transactions(self) -> list:
        """Analyze bank transactions for recurring charges."""
        # Load transactions
        transactions_file = self.accounting_folder / 'transactions.json'
        if not transactions_file.exists():
            print("❌ No transactions found. Run bank-watcher first.")
            return []
        
        transactions = json.loads(transactions_file.read_text())
        
        # Group by description and amount
        charges = defaultdict(list)
        for tx in transactions:
            desc = tx.get('description', '').lower()
            amount = tx.get('amount', 0)
            if amount < 0:  # Expenses only
                key = f"{desc}_{abs(amount):.2f}"
                charges[key].append(tx)
        
        # Find recurring charges (2+ occurrences)
        subscriptions = []
        for key, txs in charges.items():
            if len(txs) >= 2:  # At least 2 occurrences
                desc = txs[0].get('description', 'Unknown')
                amount = abs(float(txs[0].get('amount', 0)))
                
                # Match to known subscription
                sub_name = self._match_subscription(desc)
                
                # Calculate frequency
                dates = [datetime.fromisoformat(tx['date']) if isinstance(tx['date'], str) 
                         else tx['date'] for tx in txs]
                dates.sort()
                if len(dates) >= 2:
                    days_between = (dates[-1] - dates[0]).days / (len(dates) - 1)
                    frequency = 'monthly' if 25 <= days_between <= 35 else ('annual' if days_between > 300 else 'weekly')
                else:
                    frequency = 'unknown'
                
                subscriptions.append({
                    'name': sub_name,
                    'description': desc,
                    'amount': amount,
                    'frequency': frequency,
                    'last_charge': dates[-1].isoformat() if dates else None,
                    'occurrences': len(txs),
                    'detected_at': datetime.now().isoformat()
                })
        
        # Save subscriptions
        self._save_subscriptions(subscriptions)
        
        return subscriptions
    
    def _match_subscription(self, description: str) -> str:
        """Match description to known subscription."""
        desc_lower = description.lower()
        
        for key, pattern in self.SUBSCRIPTION_PATTERNS.items():
            if any(kw in desc_lower for kw in pattern['keywords']):
                return pattern['name']
        
        # Unknown subscription
        return description.title()[:30]
    
    def list_subscriptions(self) -> list:
        """List all tracked subscriptions."""
        if not self.subscriptions_file.exists():
            return []
        return json.loads(self.subscriptions_file.read_text())
    
    def audit_subscriptions(self) -> dict:
        """Audit subscriptions for usage."""
        subscriptions = self.list_subscriptions()
        logins = json.loads(self.logins_file.read_text()) if self.logins_file.exists() else {}
        
        now = datetime.now()
        audit_results = {
            'active': [],
            'unused_30_days': [],
            'unused_60_days': [],
            'unused_90_days': [],
            'total_monthly_cost': 0
        }
        
        for sub in subscriptions:
            # Calculate monthly cost
            monthly_cost = sub['amount']
            if sub['frequency'] == 'annual':
                monthly_cost = sub['amount'] / 12
            elif sub['frequency'] == 'weekly':
                monthly_cost = sub['amount'] * 4
            
            audit_results['total_monthly_cost'] += monthly_cost
            
            # Check last login
            sub_key = sub['name'].lower()
            last_login = logins.get(sub_key)
            
            if last_login:
                last_login_dt = datetime.fromisoformat(last_login)
                days_since_login = (now - last_login_dt).days
                
                if days_since_login > 90:
                    audit_results['unused_90_days'].append({**sub, 'days_since_login': days_since_login})
                elif days_since_login > 60:
                    audit_results['unused_60_days'].append({**sub, 'days_since_login': days_since_login})
                elif days_since_login > 30:
                    audit_results['unused_30_days'].append({**sub, 'days_since_login': days_since_login})
                else:
                    audit_results['active'].append({**sub, 'days_since_login': days_since_login})
            else:
                audit_results['unused_90_days'].append({**sub, 'days_since_login': None})
        
        # Create action file for unused subscriptions
        self._create_audit_action_file(audit_results)
        
        return audit_results
    
    def generate_report(self) -> str:
        """Generate subscription cost report."""
        audit = self.audit_subscriptions()
        
        report = f'''# Subscription Cost Report

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}

## Monthly Cost Summary

| Metric | Amount |
|--------|--------|
| Total Monthly Cost | ${audit['total_monthly_cost']:.2f} |
| Annual Projection | ${audit['total_monthly_cost'] * 12:.2f} |

## Subscription Breakdown

### Active ({len(audit['active'])})

'''
        for sub in audit['active'][:5]:
            report += f"- **{sub['name']}**: ${sub['amount']:.2f}/{sub['frequency']} (last used {sub['days_since_login']} days ago)\n"
        
        if audit['unused_30_days']:
            report += f"\n### Unused 30+ Days ({len(audit['unused_30_days'])})\n\n"
            for sub in audit['unused_30_days']:
                report += f"- ⚠️ **{sub['name']}**: ${sub['amount']:.2f}/{sub['frequency']} - {sub['days_since_login']} days since login\n"
        
        if audit['unused_90_days']:
            report += f"\n### Unused 90+ Days ({len(audit['unused_90_days'])})\n\n"
            for sub in audit['unused_90_days']:
                report += f"- 🔴 **{sub['name']}**: ${sub['amount']:.2f}/{sub['frequency']} - {sub['days_since_login'] or 'Never'} days since login\n"
        
        # Cancellation suggestions
        if audit['unused_90_days'] or audit['unused_60_days']:
            potential_savings = sum(s['amount'] for s in audit['unused_90_days'] + audit['unused_60_days'])
            report += f"\n## 💡 Cost Optimization\n\n"
            report += f"**Potential Monthly Savings:** ${potential_savings:.2f}\n\n"
            report += "Consider cancelling these unused subscriptions:\n"
            for sub in audit['unused_90_days'][:3]:
                report += f"- {sub['name']} (${sub['amount']:.2f}/{sub['frequency']})\n"
        
        # Save report
        report_file = self.subscriptions_folder / f"report_{datetime.now().strftime('%Y%m%d')}.md"
        report_file.write_text(report)
        
        return report
    
    def _save_subscriptions(self, subscriptions: list):
        """Save subscriptions to file."""
        self.subscriptions_file.write_text(json.dumps(subscriptions, indent=2))
    
    def _create_audit_action_file(self, audit: dict):
        """Create action file for subscription audit."""
        timestamp = datetime.now()
        filename = f"SUBSCRIPTION_AUDIT_{timestamp.strftime('%Y%m%d')}.md"
        filepath = self.needs_action / filename
        
        unused_count = len(audit['unused_30_days']) + len(audit['unused_60_days']) + len(audit['unused_90_days'])
        
        content = f'''---
type: subscription_audit
created: {timestamp.isoformat()}
total_monthly_cost: {audit['total_monthly_cost']:.2f}
unused_count: {unused_count}
status: pending
---

# Subscription Audit

**Generated:** {timestamp.strftime('%Y-%m-%d %H:%M')}

## Summary

| Metric | Value |
|--------|-------|
| Total Monthly Cost | ${audit['total_monthly_cost']:.2f} |
| Active Subscriptions | {len(audit['active'])} |
| Unused 30+ Days | {len(audit['unused_30_days'])} |
| Unused 90+ Days | {len(audit['unused_90_days'])} |

## Unused Subscriptions (Potential Cancellations)

'''
        for sub in audit['unused_90_days'][:5]:
            content += f"- 🔴 **{sub['name']}**: ${sub['amount']:.2f}/{sub['frequency']} ({sub['days_since_login'] or 'Never'} days)\n"
        
        content += f'''
## Suggested Actions

- [ ] Review unused subscriptions list
- [ ] Cancel subscriptions not needed
- [ ] Update last login dates if incorrect
- [ ] Move to /Done when reviewed

## Notes

_Add notes about which subscriptions to cancel_

---
*Generated by Subscription Tracker*
'''
        filepath.write_text(content)
    
    def log_login(self, service: str):
        """Log a login to a service."""
        logins = json.loads(self.logins_file.read_text()) if self.logins_file.exists() else {}
        logins[service.lower()] = datetime.now().isoformat()
        self.logins_file.write_text(json.dumps(logins, indent=2))


def main():
    parser = argparse.ArgumentParser(description='Subscription Tracker')
    parser.add_argument('--vault-path', default='..', help='Path to vault')
    parser.add_argument('--action', required=True,
                        choices=['init', 'analyze', 'list', 'audit', 'report'])
    parser.add_argument('--service', help='Service name (for login tracking)')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("💳 SUBSCRIPTION TRACKER")
    print("=" * 60)
    
    tracker = SubscriptionTracker(args.vault_path)
    
    if args.action == 'init':
        tracker.initialize()
    
    elif args.action == 'analyze':
        subscriptions = tracker.analyze_transactions()
        print(f"\n✅ Found {len(subscriptions)} subscriptions:")
        for sub in subscriptions:
            print(f"   {sub['name']}: ${sub['amount']:.2f}/{sub['frequency']}")
    
    elif args.action == 'list':
        subscriptions = tracker.list_subscriptions()
        print(f"\n📋 Tracked Subscriptions ({len(subscriptions)}):")
        for sub in subscriptions:
            print(f"   {sub['name']}: ${sub['amount']:.2f}/{sub['frequency']}")
    
    elif args.action == 'audit':
        audit = tracker.audit_subscriptions()
        print(f"\n📊 Audit Results:")
        print(f"   Active: {len(audit['active'])}")
        print(f"   Unused 30+ days: {len(audit['unused_30_days'])}")
        print(f"   Unused 90+ days: {len(audit['unused_90_days'])}")
        print(f"   Total Monthly Cost: ${audit['total_monthly_cost']:.2f}")
    
    elif args.action == 'report':
        report = tracker.generate_report()
        print("\n" + report)


if __name__ == '__main__':
    main()
```

## Output Format

### Subscription Report

```markdown
# Subscription Cost Report

**Generated:** 2026-03-14 10:30

## Monthly Cost Summary

| Metric | Amount |
|--------|--------|
| Total Monthly Cost | $127.50 |
| Annual Projection | $1,530.00 |

## Unused 90+ Days (3)

- 🔴 **Netflix**: $15.99/month - 120 days since login
- 🔴 **Adobe Creative Cloud**: $54.99/month - 95 days since login
- 🔴 **Notion**: $8.00/month - Never logged in

## 💡 Cost Optimization

**Potential Monthly Savings:** $78.98

Consider cancelling these unused subscriptions:
- Netflix ($15.99/month)
- Adobe Creative Cloud ($54.99/month)
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| No subscriptions found | Run bank-watcher first to import transactions |
| Wrong subscription names | Add to SUBSCRIPTION_PATTERNS dict |
| Login tracking not working | Call log_login() when accessing services |

## Related Skills

- `bank-watcher` - Import transactions for analysis
- `notification-skill` - Alert on price increases
- `scheduler` - Monthly subscription review

---

*Skill Version: 1.0 | Last Updated: 2026-03-14 | Silver Tier*
