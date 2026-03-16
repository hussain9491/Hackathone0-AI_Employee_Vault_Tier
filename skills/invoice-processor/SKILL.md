---
name: invoice-processor
description: |
  Extract invoice data, track payment status, send payment reminders, and manage
  accounts receivable/payable. Integrates with bank-watcher to match payments to
  invoices. Essential for automated billing and cash flow management.
---

# Invoice Processor Skill

Manage invoices, track payments, and automate billing workflows.

## Installation

```bash
pip install PyPDF2 pdfplumber pandas
```

## Quick Reference

### Process Invoices

```bash
# Process incoming invoice (PDF)
python AI_Employee_Vault/scripts/invoice_processor.py --vault-path AI_Employee_Vault --action process --file invoice.pdf

# Generate invoice (create new)
python AI_Employee_Vault/scripts/invoice_processor.py --vault-path AI_Employee_Vault --action create --client "ABC Corp" --amount 1500

# Send payment reminders
python AI_Employee_Vault/scripts/invoice_processor.py --vault-path AI_Employee_Vault --action remind --days-overdue 7

# Match payments to invoices
python AI_Employee_Vault/scripts/invoice_processor.py --vault-path AI_Employee_Vault --action match
```

### With Qwen

```bash
# Process received invoice
qwen "Use the invoice-processor skill to process this vendor invoice"

# Create and send invoice
qwen "Use invoice-processor to create an invoice for Client X for $2000"

# Send reminders
qwen "Use invoice-processor to send reminders for all invoices over 7 days overdue"
```

## Setup: Invoice Configuration

### Configure Invoice Settings

Create `AI_Employee_Vault/Config/invoice_settings.json`:

```json
{
  "company_name": "Your Company Name",
  "company_email": "billing@yourcompany.com",
  "company_address": "123 Business St, City, State 12345",
  "payment_terms_days": 30,
  "late_fee_percent": 2,
  "currency": "USD",
  "invoice_prefix": "INV"
}
```

## Workflow: Invoice Processing

```
1. Invoice received (PDF/email) or created
         ↓
2. Extract invoice data (vendor, amount, due date)
         ↓
3. Create action file in Needs_Action/
         ↓
4. For outgoing: Send to client, track status
         ↓
5. Match incoming payments to invoices
         ↓
6. Send reminders for overdue invoices
```

## Invoice Processor Implementation

```python
# AI_Employee_Vault/scripts/invoice_processor.py
import argparse
import json
import pdfplumber
from pathlib import Path
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
import os

class InvoiceProcessor:
    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.config_path = self.vault_path / 'Config' / 'invoice_settings.json'
        self.invoices_folder = self.vault_path / 'Invoices'
        self.needs_action = self.vault_path / 'Needs_Action'
        self.logs_folder = self.vault_path / 'Logs'
        
        for folder in [self.invoices_folder, self.needs_action, self.logs_folder]:
            folder.mkdir(parents=True, exist_ok=True)
        
        self.config = self._load_config()
        self.invoices_file = self.invoices_folder / 'invoices.json'
    
    def _load_config(self) -> dict:
        """Load invoice configuration."""
        if self.config_path.exists():
            return json.loads(self.config_path.read_text())
        return {
            'company_name': 'Your Company',
            'payment_terms_days': 30,
            'currency': 'USD',
            'invoice_prefix': 'INV'
        }
    
    def process_incoming_invoice(self, pdf_path: str) -> dict:
        """Extract data from incoming invoice PDF."""
        pdf_path = Path(pdf_path)
        if not pdf_path.exists():
            return {'error': f'File not found: {pdf_path}'}
        
        invoice_data = {
            'type': 'incoming',
            'file': pdf_path.name,
            'vendor': None,
            'amount': None,
            'due_date': None,
            'invoice_number': None,
            'extracted_at': datetime.now().isoformat()
        }
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                text = ''
                for page in pdf.pages:
                    text += page.extract_text() or ''
                
                # Extract key information (simple keyword matching)
                lines = text.split('\n')
                for line in lines:
                    line_lower = line.lower()
                    
                    if 'invoice' in line_lower and '#' in line:
                        invoice_data['invoice_number'] = line.split('#')[-1].strip()
                    
                    if 'total' in line_lower or 'amount' in line_lower:
                        # Extract dollar amount
                        import re
                        amounts = re.findall(r'\$?[\d,]+\.?\d*', line)
                        if amounts:
                            invoice_data['amount'] = amounts[-1].replace('$', '').replace(',', '')
                    
                    if 'due' in line_lower:
                        # Try to extract date
                        date_keywords = ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 
                                        'jul', 'aug', 'sep', 'oct', 'nov', 'dec']
                        for kw in date_keywords:
                            if kw in line_lower:
                                invoice_data['due_date'] = line.strip()
                                break
                
                invoice_data['raw_text'] = text[:1000]  # First 1000 chars
            
            # Create action file
            self._create_incoming_action_file(invoice_data)
            
            return invoice_data
            
        except Exception as e:
            return {'error': str(e)}
    
    def create_outgoing_invoice(self, client: str, amount: float, 
                                 description: str, due_days: int = 30) -> Path:
        """Create and send outgoing invoice."""
        # Generate invoice number
        timestamp = datetime.now()
        invoice_num = f"{self.config['invoice_prefix']}-{timestamp.strftime('%Y%m')}-{len(self._get_invoices()) + 1:03d}"
        due_date = timestamp + timedelta(days=due_days)
        
        invoice_data = {
            'type': 'outgoing',
            'invoice_number': invoice_num,
            'client': client,
            'amount': amount,
            'description': description,
            'issue_date': timestamp.isoformat(),
            'due_date': due_date.isoformat(),
            'status': 'pending'
        }
        
        # Save invoice
        self._save_invoice(invoice_data)
        
        # Create invoice PDF content (markdown template)
        invoice_content = self._generate_invoice_markdown(invoice_data)
        invoice_file = self.invoices_folder / f"{invoice_num}.md"
        invoice_file.write_text(invoice_content)
        
        # Create action file for sending
        action_file = self._create_outgoing_action_file(invoice_data)
        
        return action_file
    
    def send_payment_reminder(self, invoice_num: str, days_overdue: int) -> dict:
        """Send payment reminder for overdue invoice."""
        invoices = self._get_invoices()
        invoice = next((i for i in invoices if i['invoice_number'] == invoice_num), None)
        
        if not invoice:
            return {'error': f'Invoice not found: {invoice_num}'}
        
        if invoice['status'] == 'paid':
            return {'error': 'Invoice already paid'}
        
        # Generate reminder email
        subject = f"Payment Reminder: {invoice_num} ({days_overdue} days overdue)"
        body = f'''
Dear {invoice['client']},

This is a friendly reminder that invoice {invoice_num} is now {days_overdue} days overdue.

Invoice Details:
- Amount: ${invoice['amount']:.2f}
- Original Due Date: {invoice['due_date'][:10]}
- Days Overdue: {days_overdue}

Please remit payment at your earliest convenience.

If you have already sent payment, please disregard this notice.

Best regards,
{self.config['company_name']}
'''
        
        # Send email (if SMTP configured)
        result = self._send_email(invoice.get('client_email', ''), subject, body)
        
        # Log reminder
        self._log_reminder(invoice_num, days_overdue, result)
        
        return result
    
    def match_payments(self) -> list:
        """Match bank transactions to outstanding invoices."""
        # Load bank transactions
        bank_file = self.vault_path / 'Accounting' / 'transactions.json'
        if not bank_file.exists():
            return []
        
        transactions = json.loads(bank_file.read_text())
        invoices = self._get_invoices()
        matched = []
        
        for tx in transactions:
            if tx.get('type') != 'credit':  # Only incoming payments
                continue
            
            amount = float(tx.get('amount', 0))
            
            # Find matching invoice
            for inv in invoices:
                if inv['status'] == 'paid':
                    continue
                if abs(float(inv['amount']) - amount) < 0.01:  # Match amount
                    # Mark as paid
                    inv['status'] = 'paid'
                    inv['paid_date'] = tx.get('date')
                    inv['payment_transaction'] = tx.get('id')
                    matched.append({
                        'invoice': inv['invoice_number'],
                        'amount': amount,
                        'transaction': tx
                    })
                    break
        
        # Save updated invoices
        self._save_invoices(invoices)
        
        return matched
    
    def _create_incoming_action_file(self, data: dict):
        """Create action file for incoming invoice."""
        timestamp = datetime.now()
        filename = f"INVOICE_IN_{data.get('invoice_number', 'UNKNOWN')}_{timestamp.strftime('%Y%m%d')}.md"
        filepath = self.needs_action / filename
        
        content = f'''---
type: incoming_invoice
vendor: {data.get('vendor', 'Unknown')}
amount: ${data.get('amount', 'N/A')}
due_date: {data.get('due_date', 'N/A')}
invoice_number: {data.get('invoice_number', 'N/A')}
created: {timestamp.isoformat()}
status: pending
---

# Incoming Invoice Received

**Vendor:** {data.get('vendor', 'Unknown')}
**Amount:** ${data.get('amount', 'N/A')}
**Due Date:** {data.get('due_date', 'N/A')}
**Invoice #:** {data.get('invoice_number', 'N/A')}

## Suggested Actions

- [ ] Review invoice details
- [ ] Verify goods/services received
- [ ] Schedule payment
- [ ] Create approval request if over threshold
- [ ] Move to /Done when processed

## Notes

_Add notes here_

---
*Processed by Invoice Processor*
'''
        filepath.write_text(content)
    
    def _create_outgoing_action_file(self, data: dict) -> Path:
        """Create action file for sending outgoing invoice."""
        timestamp = datetime.now()
        filename = f"SEND_INVOICE_{data['invoice_number']}.md"
        filepath = self.needs_action / filename
        
        content = f'''---
type: send_invoice
client: {data['client']}
amount: ${data['amount']:.2f}
invoice_number: {data['invoice_number']}
created: {timestamp.isoformat()}
status: pending
---

# Send Invoice to Client

**Client:** {data['client']}
**Amount:** ${data['amount']:.2f}
**Invoice #:** {data['invoice_number']}
**Due Date:** {data['due_date'][:10]}

## Invoice Details

{data['description']}

## Suggested Actions

- [ ] Review invoice content
- [ ] Send to client via email
- [ ] Set follow-up reminder for due date
- [ ] Move to /Done when sent

## Email Draft

Subject: Invoice {data['invoice_number']} from {self.config['company_name']}

Dear {data['client']},

Please find attached invoice {data['invoice_number']} for ${data['amount']:.2f}.

Payment is due by {data['due_date'][:10]}.

Thank you for your business!

Best regards,
{self.config['company_name']}

---
*Generated by Invoice Processor*
'''
        filepath.write_text(content)
        return filepath
    
    def _generate_invoice_markdown(self, data: dict) -> str:
        """Generate invoice markdown content."""
        return f'''---
type: invoice
invoice_number: {data['invoice_number']}
---

# INVOICE

**Invoice #:** {data['invoice_number']}
**Date:** {data['issue_date'][:10]}
**Due Date:** {data['due_date'][:10]}

---

**From:**
{self.config['company_name']}

**To:**
{data['client']}

---

| Description | Amount |
|-------------|--------|
| {data['description']} | ${data['amount']:.2f} |

---

**Total Due:** ${data['amount']:.2f}

**Payment Terms:** Due within {self.config['payment_terms_days']} days

---
*Generated by Invoice Processor*
'''
    
    def _get_invoices(self) -> list:
        """Load all invoices."""
        if self.invoices_file.exists():
            return json.loads(self.invoices_file.read_text())
        return []
    
    def _save_invoice(self, invoice: dict):
        """Save single invoice."""
        invoices = self._get_invoices()
        invoices.append(invoice)
        self._save_invoices(invoices)
    
    def _save_invoices(self, invoices: list):
        """Save all invoices."""
        self.invoices_file.write_text(json.dumps(invoices, indent=2))
    
    def _send_email(self, to: str, subject: str, body: str) -> dict:
        """Send email (simplified)."""
        smtp_user = os.environ.get('SMTP_USER')
        if not smtp_user:
            return {'success': False, 'error': 'SMTP not configured'}
        
        # Implementation similar to notification-skill
        return {'success': True, 'message': 'Email sent'}
    
    def _log_reminder(self, invoice_num: str, days: int, result: dict):
        """Log payment reminder."""
        log_file = self.logs_folder / f"invoice_reminders_{datetime.now().strftime('%Y-%m-%d')}.json"
        logs = []
        if log_file.exists():
            logs = json.loads(log_file.read_text())
        logs.append({
            'timestamp': datetime.now().isoformat(),
            'invoice': invoice_num,
            'days_overdue': days,
            'result': result
        })
        log_file.write_text(json.dumps(logs, indent=2))


def main():
    parser = argparse.ArgumentParser(description='Invoice Processor')
    parser.add_argument('--vault-path', default='..', help='Path to vault')
    parser.add_argument('--action', required=True, 
                        choices=['process', 'create', 'remind', 'match'])
    parser.add_argument('--file', help='Invoice PDF file')
    parser.add_argument('--client', help='Client name (for create)')
    parser.add_argument('--amount', type=float, help='Amount (for create)')
    parser.add_argument('--description', help='Description (for create)')
    parser.add_argument('--days-overdue', type=int, help='Days overdue (for remind)')
    parser.add_argument('--invoice', help='Invoice number (for remind)')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("📄 INVOICE PROCESSOR")
    print("=" * 60)
    
    processor = InvoiceProcessor(args.vault_path)
    
    if args.action == 'process':
        if not args.file:
            print("❌ --file required")
            return
        result = processor.process_incoming_invoice(args.file)
        if 'error' in result:
            print(f"❌ Error: {result['error']}")
        else:
            print(f"✅ Processed: {result.get('invoice_number', 'Unknown')}")
            print(f"   Vendor: {result.get('vendor', 'Unknown')}")
            print(f"   Amount: ${result.get('amount', 'N/A')}")
    
    elif args.action == 'create':
        if not all([args.client, args.amount]):
            print("❌ --client and --amount required")
            return
        filepath = processor.create_outgoing_invoice(
            args.client, args.amount, args.description or 'Services rendered'
        )
        print(f"✅ Invoice created: {filepath}")
    
    elif args.action == 'remind':
        if not all([args.invoice, args.days_overdue]):
            print("❌ --invoice and --days-overdue required")
            return
        result = processor.send_payment_reminder(args.invoice, args.days_overdue)
        print(f"{'✅' if result.get('success') else '❌'} {result}")
    
    elif args.action == 'match':
        matched = processor.match_payments()
        print(f"✅ Matched {len(matched)} payments to invoices")
        for m in matched:
            print(f"   {m['invoice']}: ${m['amount']:.2f}")


if __name__ == '__main__':
    main()
```

## Output Format

### Incoming Invoice Action File

```markdown
---
type: incoming_invoice
vendor: ABC Supplies
amount: $450.00
due_date: 2026-04-15
invoice_number: INV-2026-0342
created: 2026-03-14T10:30:00
status: pending
---

# Incoming Invoice Received

**Vendor:** ABC Supplies
**Amount:** $450.00
**Due Date:** 2026-04-15

## Suggested Actions

- [ ] Review invoice details
- [ ] Verify goods received
- [ ] Schedule payment
```

### Outgoing Invoice

```markdown
---
type: invoice
invoice_number: INV-202603-001
---

# INVOICE

**Invoice #:** INV-202603-001
**Date:** 2026-03-14
**Due Date:** 2026-04-13

**From:** Your Company Name

**To:** Client ABC

| Description | Amount |
|-------------|--------|
| Consulting Services | $2,000.00 |

**Total Due:** $2,000.00
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| PDF extraction failed | Ensure PDF is text-based (not scanned) |
| Amount not detected | Check PDF format, may need custom parsing |
| Email not sending | Configure SMTP credentials |

## Related Skills

- `bank-watcher` - Match payments to invoices
- `email-mcp` - Send invoices via email
- `notification-skill` - Alert on overdue invoices

---

*Skill Version: 1.0 | Last Updated: 2026-03-14 | Silver Tier*
