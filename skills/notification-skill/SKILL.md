---
name: notification-skill
description: |
  Send urgent alerts via SMS, Slack, Push notifications, or email. Use for critical
  system alerts, payment failures, deadline reminders, and emergency notifications.
  Ensures you never miss important time-sensitive information.
---

# Notification Skill

Send urgent alerts via multiple channels (SMS, Slack, Push, Email).

## Installation

```bash
pip install requests slack_sdk twilio
```

## Quick Reference

### Send Notification

```bash
# Slack notification
python AI_Employee_Vault/scripts/notification_skill.py --vault-path AI_Employee_Vault --channel slack --message "Payment received!"

# SMS notification
python AI_Employee_Vault/scripts/notification_skill.py --vault-path AI_Employee_Vault --channel sms --to +1234567890 --message "Urgent: Server down"

# Push notification
python AI_Employee_Vault/scripts/notification_skill.py --vault-path AI_Employee_Vault --channel push --title "Alert" --message "Low balance warning"

# Email notification
python AI_Employee_Vault/scripts/notification_skill.py --vault-path AI_Employee_Vault --channel email --to user@example.com --subject "Alert" --body "Something needs attention"
```

### With Qwen

```bash
# Send urgent alert
qwen "Use the notification-skill to send an urgent Slack alert about the server outage"

# Send payment reminder
qwen "Use notification-skill to SMS the client about overdue invoice"

# Send daily summary
qwen "Use notification-skill to send a push notification with today's summary"
```

## Setup: Notification Channels

### Slack

1. Create Slack app at [api.slack.com](https://api.slack.com/apps)
2. Add "Incoming Webhooks" feature
3. Create webhook URL for your channel
4. Save webhook URL as environment variable

```bash
export SLACK_WEBHOOK_URL="https://hooks.slack.com/services/XXX/YYY/ZZZ"
```

### Twilio (SMS)

1. Sign up at [twilio.com](https://www.twilio.com/)
2. Get phone number
3. Copy Account SID and Auth Token

```bash
export TWILIO_ACCOUNT_SID="ACxxxxxxxx"
export TWILIO_AUTH_TOKEN="your_auth_token"
export TWILIO_PHONE_NUMBER="+1234567890"
```

### Pushover (Push Notifications)

1. Sign up at [pushover.net](https://pushover.net/)
2. Create application
3. Get API token and user key

```bash
export PUSHOVER_API_TOKEN="your_app_token"
export PUSHOVER_USER_KEY="your_user_key"
```

## Notification Skill Implementation

```python
# AI_Employee_Vault/scripts/notification_skill.py
import argparse
import os
import requests
from pathlib import Path
from datetime import datetime

class NotificationSkill:
    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.logs_folder = self.vault_path / 'Logs'
        self.logs_folder.mkdir(parents=True, exist_ok=True)
        
        # Load credentials from environment
        self.slack_webhook = os.environ.get('SLACK_WEBHOOK_URL')
        self.twilio_sid = os.environ.get('TWILIO_ACCOUNT_SID')
        self.twilio_token = os.environ.get('TWILIO_AUTH_TOKEN')
        self.twilio_phone = os.environ.get('TWILIO_PHONE_NUMBER')
        self.pushover_token = os.environ.get('PUSHOVER_API_TOKEN')
        self.pushover_user = os.environ.get('PUSHOVER_USER_KEY')
    
    def send_slack(self, message: str, channel: str = None, urgent: bool = False) -> dict:
        """Send Slack notification."""
        if not self.slack_webhook:
            return {'success': False, 'error': 'Slack webhook not configured'}
        
        payload = {
            'text': message,
            'username': 'AI Employee',
            'icon_emoji': ':robot_face:'
        }
        
        if urgent:
            payload['attachments'] = [{
                'color': 'danger',
                'fields': [{
                    'title': 'Priority',
                    'value': '🔴 URGENT',
                    'short': True
                }]
            }]
        
        try:
            response = requests.post(self.slack_webhook, json=payload)
            response.raise_for_status()
            self._log('slack', message, 'success')
            return {'success': True, 'channel': 'slack'}
        except Exception as e:
            self._log('slack', message, f'error: {e}')
            return {'success': False, 'error': str(e)}
    
    def send_sms(self, to: str, message: str) -> dict:
        """Send SMS via Twilio."""
        if not all([self.twilio_sid, self.twilio_token, self.twilio_phone]):
            return {'success': False, 'error': 'Twilio not configured'}
        
        from twilio.rest import Client
        
        try:
            client = Client(self.twilio_sid, self.twilio_token)
            message = client.messages.create(
                body=message,
                from_=self.twilio_phone,
                to=to
            )
            self._log('sms', f"To {to}: {message.body[:50]}", 'success')
            return {'success': True, 'message_sid': message.sid}
        except Exception as e:
            self._log('sms', f"To {to}", f'error: {e}')
            return {'success': False, 'error': str(e)}
    
    def send_push(self, title: str, message: str, priority: int = 0) -> dict:
        """Send push notification via Pushover."""
        if not all([self.pushover_token, self.pushover_user]):
            return {'success': False, 'error': 'Pushover not configured'}
        
        url = 'https://api.pushover.net/1/messages.json'
        data = {
            'token': self.pushover_token,
            'user': self.pushover_user,
            'title': title,
            'message': message,
            'priority': priority
        }
        
        try:
            response = requests.post(url, data=data)
            response.raise_for_status()
            self._log('push', f"{title}: {message[:50]}", 'success')
            return {'success': True}
        except Exception as e:
            self._log('push', title, f'error: {e}')
            return {'success': False, 'error': str(e)}
    
    def send_email(self, to: str, subject: str, body: str) -> dict:
        """Send email notification."""
        import smtplib
        from email.mime.text import MIMEText
        
        smtp_user = os.environ.get('SMTP_USER')
        smtp_pass = os.environ.get('SMTP_PASS')
        smtp_host = os.environ.get('SMTP_HOST', 'smtp.gmail.com')
        smtp_port = int(os.environ.get('SMTP_PORT', 587))
        
        if not smtp_user:
            return {'success': False, 'error': 'SMTP not configured'}
        
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = smtp_user
        msg['To'] = to
        
        try:
            with smtplib.SMTP(smtp_host, smtp_port) as server:
                server.starttls()
                server.login(smtp_user, smtp_pass)
                server.send_message(msg)
            self._log('email', f"To {to}: {subject}", 'success')
            return {'success': True}
        except Exception as e:
            self._log('email', f"To {to}", f'error: {e}')
            return {'success': False, 'error': str(e)}
    
    def _log(self, channel: str, message: str, status: str):
        """Log notification."""
        log_file = self.logs_folder / f"notifications_{datetime.now().strftime('%Y-%m-%d')}.json"
        import json
        
        logs = []
        if log_file.exists():
            logs = json.loads(log_file.read_text())
        
        logs.append({
            'timestamp': datetime.now().isoformat(),
            'channel': channel,
            'message': message[:100],
            'status': status
        })
        
        log_file.write_text(json.dumps(logs, indent=2))


def main():
    parser = argparse.ArgumentParser(description='Notification Skill')
    parser.add_argument('--vault-path', default='..', help='Path to vault')
    parser.add_argument('--channel', required=True, 
                        choices=['slack', 'sms', 'push', 'email'])
    parser.add_argument('--message', help='Notification message')
    parser.add_argument('--to', help='Recipient (phone or email)')
    parser.add_argument('--title', help='Notification title')
    parser.add_argument('--subject', help='Email subject')
    parser.add_argument('--body', help='Email body')
    parser.add_argument('--urgent', action='store_true', help='Mark as urgent')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("📬 NOTIFICATION SKILL")
    print("=" * 60)
    
    skill = NotificationSkill(args.vault_path)
    
    if args.channel == 'slack':
        result = skill.send_slack(args.message, urgent=args.urgent)
    
    elif args.channel == 'sms':
        if not args.to:
            print("❌ --to required for SMS")
            return
        result = skill.send_sms(args.to, args.message)
    
    elif args.channel == 'push':
        title = args.title or 'AI Employee Alert'
        result = skill.send_push(title, args.message, priority=1 if args.urgent else 0)
    
    elif args.channel == 'email':
        if not all([args.to, args.subject, args.body]):
            print("❌ --to, --subject, and --body required for email")
            return
        result = skill.send_email(args.to, args.subject, args.body)
    
    else:
        print(f"❌ Unknown channel: {args.channel}")
        return
    
    if result['success']:
        print(f"✅ Notification sent via {args.channel}!")
    else:
        print(f"❌ Failed: {result.get('error', 'Unknown error')}")


if __name__ == '__main__':
    main()
```

## Usage Examples

### Urgent System Alert

```bash
python notification_skill.py --vault-path .. --channel slack \
  --message "🚨 Server CPU at 95%! Immediate attention required." \
  --urgent
```

### Payment Reminder SMS

```bash
python notification_skill.py --vault-path .. --channel sms \
  --to +1234567890 \
  --message "Reminder: Invoice #1234 ($500) is 5 days overdue. Please pay today."
```

### Daily Summary Push

```bash
python notification_skill.py --vault-path .. --channel push \
  --title "Daily Summary" \
  --message "Today: 5 tasks completed, $2,500 revenue, 3 pending approvals"
```

## Notification Templates

### Payment Received
```
✅ Payment Received!

Client: ABC Corp
Amount: $1,500.00
Invoice: #1234
```

### Low Balance Alert
```
⚠️ Low Balance Warning

Current Balance: $500
Minimum Threshold: $1,000
Action: Transfer funds needed
```

### Deadline Reminder
```
⏰ Deadline Tomorrow

Task: Submit quarterly report
Time: 5:00 PM
Status: 80% complete
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "Slack webhook not configured" | Set SLACK_WEBHOOK_URL env var |
| "Twilio not configured" | Set Twilio credentials |
| SMS not delivered | Verify phone number format (+1234567890) |
| Push not received | Check Pushover user key |

## Related Skills

- `bank-watcher` - Alert on low balance
- `approval-workflow-v2` - Notify on pending approvals
- `scheduler` - Schedule daily summaries

---

*Skill Version: 1.0 | Last Updated: 2026-03-14 | Silver Tier*
