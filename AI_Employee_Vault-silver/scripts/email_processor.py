"""
Email Processor with Approval Workflow for AI Employee

This script:
1. Detects notification-type emails (one-way, no reply needed) → moves to Rejected/
2. Detects real emails (need reply) → creates plan, drafts reply → moves to Pending_Approval/
3. Waits for human approval (move to Approved/)
4. Sends email reply when approved

Usage:
    python email_processor.py --vault-path ../AI_Employee_Vault
    python email_processor.py --vault-path .. --send-approved

Author: AI Employee Project
Tier: Silver
"""

import os
import sys
import argparse
import smtplib
import json
import re
from pathlib import Path
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


class EmailProcessor:
    """
    Process emails with classification and approval workflow.
    """
    
    # Notification patterns (one-way, no reply needed)
    NOTIFICATION_PATTERNS = [
        r'no-reply',
        r'noreply',
        r'do-not-reply',
        r'automated',
        r'notification',
        r'verification code',
        r'confirm your',
        r'activate your',
        r'welcome to',
        r'your account',
        r'password reset',
        r'security alert',
        r'newsletter',
        r'subscription',
        r'unsubscribe',
        r'gamma',
        r'whatsapp.*code',
        r'otp',
        r'one time',
    ]
    
    # Real email patterns (conversation, needs reply)
    REAL_EMAIL_PATTERNS = [
        r'^(hi|hello|hey|greetings)',
        r'^(dear|mr\.|ms\.|dr\.)',
        r'\?(question mark)?',
        r'(are you|will you|can you|could you)',
        r'(please|kindly)',
        r'(regards|sincerely|best)',
        r'(thanks|thank you)',
        r'(job|work|project|meeting)',
        r'(coming|joining|attending)',
    ]
    
    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.needs_action = self.vault_path / 'Needs_Action'
        self.pending_approval = self.vault_path / 'Pending_Approval'
        self.approved = self.vault_path / 'Approved'
        self.rejected = self.vault_path / 'Rejected'
        self.drafts = self.vault_path / 'Drafts'
        self.plans_folder = self.vault_path / 'Plans'
        self.logs_folder = self.vault_path / 'Logs'
        
        # Ensure folders exist
        for folder in [self.pending_approval, self.approved, self.rejected, 
                       self.drafts, self.plans_folder, self.logs_folder]:
            folder.mkdir(parents=True, exist_ok=True)
        
        # Setup logging
        self._setup_logging()
    
    def _setup_logging(self):
        """Setup logging."""
        self.log_file = self.logs_folder / f'email_processor_{datetime.now().strftime("%Y%m%d")}.log'
    
    def _log(self, message: str):
        """Write to log file."""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"{timestamp} - {message}\n"
        print(log_entry.strip())
        
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry)
    
    def is_notification(self, email_content: str, subject: str, from_email: str) -> bool:
        """
        Check if email is a notification (one-way, no reply needed).
        
        Args:
            email_content: Full email content
            subject: Email subject
            from_email: Sender email address
            
        Returns:
            True if notification, False if real email
        """
        text_to_check = f"{from_email} {subject} {email_content}".lower()
        
        # Check notification patterns
        for pattern in self.NOTIFICATION_PATTERNS:
            if re.search(pattern, text_to_check, re.IGNORECASE):
                return True
        
        # Check if from address is a no-reply
        if 'no-reply' in from_email or 'noreply' in from_email:
            return True
        
        return False
    
    def is_real_email(self, email_content: str, subject: str, from_email: str) -> bool:
        """
        Check if email is a real conversation (needs reply).
        
        Args:
            email_content: Full email content
            subject: Email subject
            from_email: Sender email address
            
        Returns:
            True if real email, False if notification
        """
        text_to_check = f"{subject} {email_content}".lower()
        
        # Check real email patterns
        for pattern in self.REAL_EMAIL_PATTERNS:
            if re.search(pattern, text_to_check, re.IGNORECASE):
                return True
        
        # Check if email has questions
        if '?' in text_to_check:
            return True
        
        # Check if email is short and personal (likely conversation)
        words = text_to_check.split()
        if len(words) < 50 and not self.is_notification(email_content, subject, from_email):
            return True
        
        return False
    
    def classify_email(self, filepath: Path) -> dict:
        """
        Classify an email action file.
        
        Args:
            filepath: Path to email action file
            
        Returns:
            Dict with classification results
        """
        content = filepath.read_text(encoding='utf-8')
        
        # Extract metadata
        from_email = ''
        subject = ''
        preview = ''
        
        for line in content.split('\n'):
            if line.startswith('from:'):
                from_email = line.split(':', 1)[1].strip().strip('"')
            elif line.startswith('subject:'):
                subject = line.split(':', 1)[1].strip().strip('"')
            elif line.startswith('## Email Preview'):
                preview = content.split('## Email Preview')[1].split('##')[0].strip()
        
        # Classify
        is_notification = self.is_notification(content, subject, from_email)
        is_real = self.is_real_email(content, subject, from_email)
        
        result = {
            'filepath': filepath,
            'from': from_email,
            'subject': subject,
            'is_notification': is_notification,
            'is_real_email': is_real,
            'classification': 'notification' if is_notification else 'real_email'
        }
        
        self._log(f"Classified: {filepath.name} → {result['classification']}")
        
        return result
    
    def move_to_rejected(self, filepath: Path, reason: str):
        """
        Move notification email to Rejected folder.
        
        Args:
            filepath: Path to email action file
            reason: Reason for rejection
        """
        content = filepath.read_text(encoding='utf-8')
        
        # Add rejection note
        new_content = content.replace(
            '---\n*Created by Gmail Watcher*',
            f'''---
*Created by Gmail Watcher*

## Rejection Note

**Reason:** {reason}
**Classified as:** Notification (no reply needed)
**Processed:** {datetime.now().isoformat()}
'''
        )
        
        # Move to Rejected
        dest = self.rejected / filepath.name
        dest.write_text(new_content, encoding='utf-8')
        filepath.unlink()
        
        self._log(f"Moved to Rejected: {filepath.name} - {reason}")
    
    def create_plan_and_draft(self, filepath: Path) -> Path:
        """
        Create plan and draft reply for real email.
        
        Args:
            filepath: Path to email action file
            
        Returns:
            Path to draft file in Drafts/
        """
        content = filepath.read_text(encoding='utf-8')
        
        # Extract email info
        from_email = ''
        subject = ''
        preview = ''
        
        for line in content.split('\n'):
            if line.startswith('from:'):
                from_email = line.split(':', 1)[1].strip().strip('"')
            elif line.startswith('subject:'):
                subject = line.split(':', 1)[1].strip().strip('"')
            elif line.startswith('## Email Preview'):
                preview = content.split('## Email Preview')[1].split('##')[0].strip()
        
        # Extract sender name
        sender_name = from_email.split('<')[0].strip().strip('"') if '<' in from_email else from_email.split('@')[0]
        
        # Create plan
        plan_content = f'''---
type: email_response_plan
created: {datetime.now().isoformat()}
status: pending_draft
email_from: "{from_email}"
email_subject: "{subject}"
---

# Email Response Plan

**Email From:** {from_email}
**Subject:** {subject}
**Created:** {datetime.now().strftime('%Y-%m-%d %H:%M')}

## Analysis

This is a real conversation email that requires a response.

## Response Strategy

1. Acknowledge the sender's message
2. Answer any questions
3. Provide relevant information
4. End with professional closing

## Draft Reply Location

Draft created in: `Drafts/DRAFT_{filepath.stem}.md`

## Next Steps

- [ ] Qwen to write draft reply
- [ ] Human review draft
- [ ] Move to Approved/ to send
- [ ] Move to Rejected/ to discard

---
*Generated by Email Processor*
'''
        
        # Save plan
        plan_filename = f"PLAN_{filepath.stem}_{datetime.now().strftime('%Y%m%d_%H%M')}.md"
        plan_path = self.plans_folder / plan_filename
        plan_path.write_text(plan_content, encoding='utf-8')
        
        self._log(f"Created plan: {plan_path.name}")
        
        # Create draft file
        draft_path = self.create_draft_reply(filepath, from_email, subject, preview, sender_name)
        
        return draft_path
    
    def create_draft_reply(self, filepath: Path, from_email: str, 
                           subject: str, preview: str, sender_name: str) -> Path:
        """
        Create draft reply in Drafts folder.
        
        Args:
            filepath: Path to email action file
            from_email: Sender email
            subject: Email subject
            preview: Email preview
            sender_name: Sender name
            
        Returns:
            Path to draft file
        """
        timestamp = datetime.now()
        filename = f"DRAFT_{filepath.stem}_{timestamp.strftime('%Y%m%d_%H%M')}.md"
        draft_path = self.drafts / filename
        
        content = f'''---
type: email_draft
to: "{from_email}"
subject: "Re: {subject}"
created: {timestamp.isoformat()}
status: needs_qwen_draft
priority: high
---

# Email Draft Reply

**To:** {sender_name} <{from_email}>
**Subject:** Re: {subject}
**Created:** {timestamp.strftime('%Y-%m-%d %H:%M')}
**Status:** 🟡 Awaiting Qwen Draft

## Original Email

{preview}

## Draft Reply

---

Dear {sender_name},

[QWEN: Please write an appropriate response to this email]

Key points to address:
- Acknowledge their message
- Answer any questions they asked
- Provide next steps if applicable

Best regards,
AI Employee

---

## Instructions for Qwen

1. Read the original email preview above
2. Write a professional, helpful response
3. Address any questions or concerns
4. Keep it concise and friendly
5. Update status to: `status: draft_ready`

## Human Review

- [ ] Review Qwen's draft
- [ ] Edit if needed
- [ ] Move to Pending_Approval/ when ready

---
*Created by Email Processor - Silver Tier*
'''
        
        draft_path.write_text(content, encoding='utf-8')
        
        self._log(f"Created draft: {draft_path.name}")
        
        return draft_path
    
    def create_approval_request(self, filepath: Path, from_email: str, 
                                 subject: str, preview: str) -> Path:
        """
        Create approval request for email reply.
        
        Args:
            filepath: Path to email action file
            from_email: Sender email
            subject: Email subject
            preview: Email preview
            
        Returns:
            Path to approval request file
        """
        timestamp = datetime.now()
        filename = f"APPROVAL_EMAIL_{subject.replace(' ', '_')[:30]}_{timestamp.strftime('%Y%m%d_%H%M')}.md"
        approval_path = self.pending_approval / filename
        
        # Extract sender name
        sender_name = from_email.split('<')[0].strip().strip('"') if '<' in from_email else from_email.split('@')[0]
        
        content = f"""---
type: email_approval_request
action: send_email_reply
to: "{from_email}"
subject: "Re: {subject}"
created: {timestamp.isoformat()}
expires: {(timestamp + timedelta(hours=24)).isoformat()}
priority: high
status: pending
---

# Email Reply Approval Request

**To:** {sender_name} <{from_email}>
**Subject:** Re: {subject}
**Created:** {timestamp.strftime('%Y-%m-%d %H:%M')}

## Original Email

{preview}

## Draft Reply

---

Dear {sender_name},

Thank you for your email regarding "{subject}".

[AI: Please draft an appropriate response based on the email content]

Key points to address:
- Acknowledge their message
- Answer any questions they asked
- Provide next steps if applicable

Best regards,
AI Employee

---

## To Approve

1. Review and edit the draft reply above
2. Move this file to `/Approved` folder
3. The reply will be sent automatically

## To Reject

1. Move this file to `/Rejected` folder
2. Or add a note explaining why

## Notes

_Add any notes or edits to the draft above_

---
*Expires in 24 hours if not approved*
*Created by Email Processor - Silver Tier*
"""
        
        approval_path.write_text(content, encoding='utf-8')
        
        self._log(f"Created approval request: {approval_path.name}")
        
        return approval_path
    
    def process_pending_emails(self) -> dict:
        """
        Process all pending email action files.

        Returns:
            Dict with processing results
        """
        results = {
            'total': 0,
            'notifications': 0,
            'real_emails': 0,
            'errors': 0
        }

        # Find all email action files
        email_files = list(self.needs_action.glob('EMAIL_*.md'))

        self._log(f"Found {len(email_files)} email action files to process")

        for filepath in email_files:
            try:
                results['total'] += 1

                # Classify email
                classification = self.classify_email(filepath)

                if classification['is_notification']:
                    # Move to rejected
                    self.move_to_rejected(
                        filepath,
                        "Automated notification - no reply needed"
                    )
                    results['notifications'] += 1
                else:
                    # Create plan and approval request
                    self.create_plan_and_draft(filepath)

                    # Move original to Needs_Action (keep for reference)
                    # The approval request is in Pending_Approval
                    results['real_emails'] += 1

            except Exception as e:
                self._log(f"Error processing {filepath.name}: {e}")
                results['errors'] += 1

        # Check for Qwen-completed drafts and move to Pending_Approval
        self.move_completed_drafts_to_pending_approval()

        return results

    def move_completed_drafts_to_pending_approval(self):
        """
        Move drafts with status 'draft_ready' from Drafts/ to Pending_Approval/.
        This is called after Qwen writes email replies.
        """
        drafts_ready = list(self.drafts.glob('DRAFT_*.md'))
        moved_count = 0

        for draft_path in drafts_ready:
            content = draft_path.read_text(encoding='utf-8')
            if 'status: draft_ready' in content:
                # Move to Pending_Approval
                dest_path = self.pending_approval / draft_path.name
                dest_path.write_text(content, encoding='utf-8')
                draft_path.unlink()
                self._log(f"Moved to Pending_Approval: {draft_path.name}")
                moved_count += 1

        if moved_count > 0:
            self._log(f"Total drafts moved to Pending_Approval: {moved_count}")
    
    def check_approved_emails(self) -> list:
        """
        Check for approved email replies ready to send.
        
        Returns:
            List of approved email files
        """
        approved_files = []
        
        for filepath in self.approved.glob('APPROVAL_EMAIL_*.md'):
            content = filepath.read_text(encoding='utf-8')
            if 'type: email_approval_request' in content:
                approved_files.append(filepath)
        
        return approved_files
    
    def send_approved_email(self, filepath: Path) -> dict:
        """
        Send an approved email reply.
        
        Args:
            filepath: Path to approved approval request
            
        Returns:
            Dict with send result
        """
        content = filepath.read_text(encoding='utf-8')
        
        # Extract email details
        to_email = ''
        subject = ''
        body = ''
        
        for line in content.split('\n'):
            if line.startswith('to:'):
                to_email = line.split(':', 1)[1].strip().strip('"')
            elif line.startswith('subject:'):
                subject = line.split(':', 1)[1].strip().strip('"')
            elif line.startswith('## Draft Reply'):
                body = content.split('## Draft Reply')[1].split('##')[0].strip()
                # Remove the separator lines
                body = '\n'.join(line for line in body.split('\n') 
                                if not line.startswith('---'))
        
        if not to_email or not subject:
            return {'success': False, 'error': 'Missing email details'}
        
        # Get SMTP credentials
        smtp_user = os.environ.get('SMTP_USER')
        smtp_pass = os.environ.get('SMTP_PASS')
        smtp_host = os.environ.get('SMTP_HOST', 'smtp.gmail.com')
        smtp_port = int(os.environ.get('SMTP_PORT', 587))
        
        if not smtp_user:
            # Try to get from credentials
            creds_path = Path('.qwen/credentials.json')
            if creds_path.exists():
                # For Gmail, use the credentials
                self._log("SMTP not configured, logging email for manual send")
                return {
                    'success': False, 
                    'error': 'SMTP not configured - email logged for manual send',
                    'to': to_email,
                    'subject': subject,
                    'body': body
                }
        
        # Send email
        try:
            msg = MIMEMultipart()
            msg['From'] = smtp_user
            msg['To'] = to_email
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain'))
            
            with smtplib.SMTP(smtp_host, smtp_port) as server:
                server.starttls()
                server.login(smtp_user, smtp_pass)
                server.send_message(msg)
            
            # Log success
            self._log(f"Email sent to {to_email}: {subject}")
            
            # Update approval file
            new_content = content + f'''

---
## Execution Log

**Status:** ✅ SENT
**Sent At:** {datetime.now().isoformat()}
**To:** {to_email}
**Subject:** {subject}
'''
            filepath.write_text(new_content, encoding='utf-8')
            
            # Move to Done
            done_folder = self.vault_path / 'Done'
            done_folder.mkdir(parents=True, exist_ok=True)
            done_path = done_folder / f"SENT_{filepath.name}"
            done_path.write_text(new_content, encoding='utf-8')
            filepath.unlink()
            
            return {'success': True, 'to': to_email, 'subject': subject}
            
        except Exception as e:
            self._log(f"Error sending email: {e}")
            return {'success': False, 'error': str(e)}


def main():
    parser = argparse.ArgumentParser(description='Email Processor with Approval Workflow')
    parser.add_argument('--vault-path', default='..', help='Path to vault')
    parser.add_argument('--process', action='store_true', help='Process pending emails')
    parser.add_argument('--send-approved', action='store_true', help='Send approved emails')
    parser.add_argument('--classify-only', action='store_true', help='Only classify, don\'t move')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("📧 EMAIL PROCESSOR WITH APPROVAL WORKFLOW")
    print("=" * 60)
    
    processor = EmailProcessor(args.vault_path)
    
    if args.send_approved:
        # Send approved emails
        print("\n📤 Checking for approved emails...")
        approved = processor.check_approved_emails()
        
        if approved:
            print(f"   Found {len(approved)} approved emails")
            for filepath in approved:
                print(f"\n   Sending: {filepath.name}")
                result = processor.send_approved_email(filepath)
                if result['success']:
                    print(f"   ✅ Sent to {result['to']}")
                else:
                    print(f"   ⚠️  {result['error']}")
        else:
            print("   No approved emails waiting")
    
    elif args.classify_only:
        # Just classify
        print("\n🔍 Classifying emails...")
        email_files = list(processor.needs_action.glob('EMAIL_*.md'))
        
        for filepath in email_files:
            classification = processor.classify_email(filepath)
            emoji = "📬" if classification['is_real_email'] else "🤖"
            print(f"   {emoji} {filepath.name}: {classification['classification']}")
    
    else:
        # Process pending emails (default)
        print("\n📋 Processing pending emails...")
        results = processor.process_pending_emails()
        
        print(f"\n📊 Results:")
        print(f"   Total processed: {results['total']}")
        print(f"   🤖 Notifications (moved to Rejected): {results['notifications']}")
        print(f"   📬 Real emails (approval created): {results['real_emails']}")
        print(f"   ❌ Errors: {results['errors']}")
        
        print(f"\n📁 Approval requests saved to: {processor.pending_approval}")
        print(f"📝 Plans saved to: {processor.plans_folder}")


if __name__ == '__main__':
    main()
