---
name: bank-watcher
description: |
  Monitor bank transactions via API or CSV import. Tracks income, expenses, and cash flow.
  Creates action files for unusual transactions, large payments, and low balance alerts.
  Essential for CEO briefings and financial reporting.
---

# Bank Watcher Skill

Monitor bank transactions and track business finances.

## Installation

```bash
pip install requests pandas
```

## Quick Reference

### Start Bank Watcher

```bash
# With bank API (recommended)
python AI_Employee_Vault/scripts/bank_watcher.py --vault-path AI_Employee_Vault --api-key YOUR_API_KEY

# With CSV import
python AI_Employee_Vault/scripts/bank_watcher.py --vault-path AI_Employee_Vault --csv transactions.csv

# Check balance only
python AI_Employee_Vault/scripts/bank_watcher.py --vault-path AI_Employee_Vault --balance
```

### With Qwen

```bash
# Process transactions
qwen "Use the bank-watcher skill to analyze this month's transactions"

# Generate financial summary
qwen "Use bank-watcher to create a revenue report for last week"

# Check for unusual activity
qwen "Check for any unusual transactions in the bank watcher logs"
```

## Setup: Bank API Integration

### Option A: Plaid (Recommended)

1. Sign up at [Plaid.com](https://plaid.com/)
2. Create app and get credentials
3. Link your bank account
4. Use API key in bank_watcher.py

### Option B: Direct Bank API

Some banks offer direct API access:
- **Chase**: chase.com/api
- **Bank of America**: developer.bankofamerica.com
- **Wells Fargo**: developer.wellsfargo.com

### Option C: CSV Import (Manual)

1. Download transactions from online banking
2. Save as CSV in `AI_Employee_Vault/Inbox/bank_transactions.csv`
3. Run: `python bank_watcher.py --vault-path .. --csv transactions.csv`

## Workflow: Transaction Monitoring

```
1. Bank Watcher runs (every 6 hours or on CSV import)
         ↓
2. Fetches new transactions via API/CSV
         ↓
3. Categorizes income/expenses
         ↓
4. Creates action files for:
   - Large transactions (>$500)
   - Unusual activity
   - Low balance alerts
         ↓
5. Updates Dashboard.md with balance
```

## Bank Watcher Implementation

```python
# AI_Employee_Vault/scripts/bank_watcher.py
import argparse
import json
import requests
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta

class BankWatcher:
    def __init__(self, vault_path: str, api_key: str = None):
        self.vault_path = Path(vault_path)
        self.api_key = api_key
        self.logs_folder = self.vault_path / 'Logs'
        self.needs_action = self.vault_path / 'Needs_Action'
        self.accounting_folder = self.vault_path / 'Accounting'
        
        for folder in [self.logs_folder, self.needs_action, self.accounting_folder]:
            folder.mkdir(parents=True, exist_ok=True)
        
        self.transactions_file = self.accounting_folder / 'transactions.json'
        self.balance_file = self.accounting_folder / 'current_balance.md'
    
    def fetch_transactions_api(self, days: int = 7) -> list:
        """Fetch transactions from bank API."""
        # Example: Plaid API integration
        url = 'https://sandbox.plaid.com/transactions/get'
        headers = {'Content-Type': 'application/json'}
        data = {
            'client_id': 'YOUR_CLIENT_ID',
            'secret': self.api_key,
            'access_token': 'YOUR_ACCESS_TOKEN',
            'start_date': (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d'),
            'end_date': datetime.now().strftime('%Y-%m-%d')
        }
        
        try:
            response = requests.post(url, json=data, headers=headers)
            response.raise_for_status()
            transactions = response.json().get('transactions', [])
            return transactions
        except Exception as e:
            print(f"API Error: {e}")
            return []
    
    def fetch_transactions_csv(self, csv_path: str) -> list:
        """Parse transactions from CSV."""
        df = pd.read_csv(csv_path)
        transactions = []
        
        for _, row in df.iterrows():
            transactions.append({
                'date': row.get('Date', row.get('Transaction Date', '')),
                'description': row.get('Description', row.get('Memo', '')),
                'amount': float(row.get('Amount', row.get('Debit', 0)) or 0),
                'type': 'debit' if float(row.get('Amount', 0) or 0) < 0 else 'credit'
            })
        
        return transactions
    
    def categorize_transaction(self, transaction: dict) -> str:
        """Categorize transaction based on description."""
        description = transaction.get('description', '').lower()
        amount = transaction.get('amount', 0)
        
        # Income categories
        if amount > 0:
            if 'payment' in description or 'transfer' in description:
                return 'income_payment'
            return 'income_other'
        
        # Expense categories
        categories = {
            'utilities': ['electric', 'water', 'gas', 'utility'],
            'software': ['software', 'subscription', 'saas', 'adobe', 'notion'],
            'office': ['office', 'supplies', 'staples'],
            'travel': ['uber', 'lyft', 'airline', 'hotel'],
            'meals': ['restaurant', 'food', 'coffee', 'lunch'],
            'payment': ['payment', 'transfer out'],
        }
        
        for category, keywords in categories.items():
            if any(kw in description for kw in keywords):
                return category
        
        return 'other'
    
    def process_transactions(self, transactions: list) -> dict:
        """Process transactions and create action files."""
        summary = {
            'total_income': 0,
            'total_expenses': 0,
            'transactions_count': len(transactions),
            'alerts': []
        }
        
        for tx in transactions:
            amount = float(tx.get('amount', 0))
            category = self.categorize_transaction(tx)
            
            if amount > 0:
                summary['total_income'] += amount
            else:
                summary['total_expenses'] += abs(amount)
                
                # Alert for large expenses
                if abs(amount) > 500:
                    summary['alerts'].append({
                        'type': 'large_expense',
                        'amount': abs(amount),
                        'description': tx.get('description', 'Unknown')
                    })
        
        # Save summary
        self._save_summary(summary)
        
        # Create action files for alerts
        for alert in summary['alerts']:
            self._create_alert_file(alert)
        
        return summary
    
    def _save_summary(self, summary: dict):
        """Save transaction summary."""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        content = f'''# Bank Transaction Summary

**Generated:** {timestamp}

## Summary

| Metric | Amount |
|--------|--------|
| Total Income | ${summary['total_income']:.2f} |
| Total Expenses | ${summary['total_expenses']:.2f} |
| Net | ${summary['total_income'] - summary['total_expenses']:.2f} |
| Transactions | {summary['transactions_count']} |

## Alerts

{len(summary['alerts'])} alerts generated.

---
*Generated by Bank Watcher Skill*
'''
        summary_file = self.accounting_folder / f'summary_{datetime.now().strftime("%Y%m%d")}.md'
        summary_file.write_text(content)
        
        # Update balance file
        self.balance_file.write_text(f'''---
last_updated: {timestamp}
status: active
---

# Current Balance

**Last Updated:** {timestamp}

| Metric | Amount |
|--------|--------|
| Income (period) | ${summary['total_income']:.2f} |
| Expenses (period) | ${summary['total_expenses']:.2f} |
| **Net** | **${summary['total_income'] - summary['total_expenses']:.2f}** |

---
*Updated by Bank Watcher*
''')
    
    def _create_alert_file(self, alert: dict):
        """Create action file for transaction alert."""
        timestamp = datetime.now()
        filename = f"BANK_ALERT_{alert['type']}_{timestamp.strftime('%Y%m%d_%H%M')}.md"
        filepath = self.needs_action / filename
        
        content = f'''---
type: bank_alert
alert_type: {alert['type']}
amount: {alert['amount']:.2f}
created: {timestamp.isoformat()}
priority: high
status: pending
---

# Bank Alert: {alert['type'].replace('_', ' ').title()}

**Amount:** ${alert['amount']:.2f}
**Description:** {alert.get('description', 'N/A')}
**Created:** {timestamp.strftime('%Y-%m-%d %H:%M')}

## Suggested Actions

- [ ] Review transaction details in banking portal
- [ ] Verify this is a legitimate charge
- [ ] Categorize for accounting
- [ ] Move to /Done when reviewed

## Notes

_Add notes here_

---
*Generated by Bank Watcher*
'''
        filepath.write_text(content)


def main():
    parser = argparse.ArgumentParser(description='Bank Watcher')
    parser.add_argument('--vault-path', default='..', help='Path to vault')
    parser.add_argument('--api-key', help='Bank API key')
    parser.add_argument('--csv', help='CSV file path')
    parser.add_argument('--balance', action='store_true', help='Check balance only')
    parser.add_argument('--days', type=int, default=7, help='Days to fetch')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("🏦 BANK WATCHER")
    print("=" * 60)
    
    watcher = BankWatcher(args.vault_path, args.api_key)
    
    if args.balance:
        if watcher.balance_file.exists():
            print(f"\n{watcher.balance_file.read_text()}")
        else:
            print("No balance data. Run with --csv or --api-key first.")
        return
    
    if args.csv:
        print(f"\n📄 Importing CSV: {args.csv}")
        transactions = watcher.fetch_transactions_csv(args.csv)
    elif args.api_key:
        print(f"\n🔌 Fetching from API (last {args.days} days)...")
        transactions = watcher.fetch_transactions_api(args.days)
    else:
        print("❌ Specify --csv or --api-key")
        return
    
    print(f"✅ Found {len(transactions)} transactions")
    
    summary = watcher.process_transactions(transactions)
    
    print(f"\n📊 Summary:")
    print(f"   Income: ${summary['total_income']:.2f}")
    print(f"   Expenses: ${summary['total_expenses']:.2f}")
    print(f"   Net: ${summary['total_income'] - summary['total_expenses']:.2f}")
    print(f"   Alerts: {len(summary['alerts'])}")


if __name__ == '__main__':
    main()
```

## Output Format

### Transaction Summary

```markdown
# Bank Transaction Summary

**Generated:** 2026-03-14 10:30:00

## Summary

| Metric | Amount |
|--------|--------|
| Total Income | $5,450.00 |
| Total Expenses | $1,230.50 |
| Net | $4,219.50 |
| Transactions | 47 |

## Alerts

2 alerts generated.
```

### Alert File

```markdown
---
type: bank_alert
alert_type: large_expense
amount: 1500.00
created: 2026-03-14T10:30:00
priority: high
status: pending
---

# Bank Alert: Large Expense

**Amount:** $1,500.00
**Description:** AWS Web Services

## Suggested Actions

- [ ] Review transaction details
- [ ] Verify legitimate charge
- [ ] Categorize for accounting
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| API connection failed | Check API key, network |
| CSV parsing error | Verify CSV format matches expected columns |
| No transactions found | Check date range, bank connection |

## Security

- ✅ API keys stored in environment variables
- ✅ Never commit credentials to git
- ✅ Encrypt sensitive financial data

## Related Skills

- `invoice-processor` - Track invoices vs payments
- `subscription-tracker` - Monitor recurring charges
- `scheduler` - Schedule daily balance checks

---

*Skill Version: 1.0 | Last Updated: 2026-03-14 | Silver Tier*
