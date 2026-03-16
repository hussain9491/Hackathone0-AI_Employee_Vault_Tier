#!/usr/bin/env python3
"""
AI Employee Orchestrator - Silver Tier

Central orchestration script that manages:
- Gmail Watcher (continuous)
- LinkedIn Watcher (continuous)
- Email Processor (classification + approval workflow)
- Notification auto-rejection
- Human approval workflow with confirmation
- Reporting and logging

Usage:
    # Interactive mode with menu
    python orchestrator.py --vault-path .. --interactive
    
    # Continuous watch mode (recommended)
    python orchestrator.py --vault-path .. --watch --interval 300
    
    # One-time process all
    python orchestrator.py --vault-path .. --process-all
    
    # Gmail priority mode
    python orchestrator.py --vault-path .. --gmail-priority
    
    # Send approved emails (requires human approval first)
    python orchestrator.py --vault-path .. --send-approved

Author: AI Employee Project
Tier: Silver
"""

import os
import sys
import argparse
import time
import signal
import subprocess
from pathlib import Path
from datetime import datetime
import json

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()  # Loads .env file automatically
except ImportError:
    pass  # python-dotenv not installed, will use system env vars

# Import email processor
try:
    from email_processor import EmailProcessor
except ImportError:
    EmailProcessor = None


class Orchestrator:
    """
    Main orchestrator for AI Employee Silver Tier.
    Coordinates Gmail, LinkedIn, Email Processing, and Approval Workflow.
    """
    
    def __init__(self, vault_path: str, check_interval: int = 300):
        self.vault_path = Path(vault_path)
        self.check_interval = check_interval  # Default 5 minutes
        self.scripts_path = self.vault_path / 'scripts'
        self.logs_folder = self.vault_path / 'Logs'
        self.dashboard_path = self.vault_path / 'Dashboard.md'
        
        # Folders
        self.needs_action = self.vault_path / 'Needs_Action'
        self.drafts = self.vault_path / 'Drafts'
        self.pending_approval = self.vault_path / 'Pending_Approval'
        self.approved = self.vault_path / 'Approved'
        self.rejected = self.vault_path / 'Rejected'
        self.done = self.vault_path / 'Done'
        self.plans = self.vault_path / 'Plans'
        
        # Ensure folders exist
        for folder in [self.logs_folder, self.needs_action, self.drafts,
                       self.pending_approval, self.approved, self.rejected,
                       self.done, self.plans]:
            folder.mkdir(parents=True, exist_ok=True)
        
        # State
        self.running = True
        self.start_time = datetime.now()
        self.gmail_watcher_process = None
        self.linkedin_watcher_process = None
        
        # Counters
        self.stats = {
            'emails_processed': 0,
            'notifications_rejected': 0,
            'drafts_created': 0,
            'emails_sent': 0,
            'linkedin_connections': 0,
            'linkedin_messages': 0,
            'cycles': 0
        }
        
        # Setup logging
        self._setup_logging()
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _setup_logging(self):
        """Setup logging to file."""
        self.log_file = self.logs_folder / f'orchestrator_{datetime.now().strftime("%Y%m%d")}.log'
    
    def _log(self, message: str, level: str = 'INFO'):
        """Write to log file and console."""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"{timestamp} - {level} - {message}\n"
        
        # Console output
        emoji = {'INFO': 'ℹ️', 'SUCCESS': '✅', 'WARNING': '⚠️', 'ERROR': '❌'}.get(level, '•')
        print(f"[{timestamp}] {emoji} {message}")
        
        # File log
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry)
    
    def _signal_handler(self, signum, frame):
        """Handle Ctrl+C gracefully."""
        self._log("Shutdown signal received", "WARNING")
        self.running = False
    
    def run_gmail_watcher_once(self) -> int:
        """
        Run Gmail Watcher once to fetch new emails.
        
        Returns:
            Number of new emails found
        """
        self._log("Running Gmail Watcher...")
        
        gmail_script = self.scripts_path / 'gmail_watcher.py'
        if not gmail_script.exists():
            self._log("Gmail Watcher script not found", "ERROR")
            return 0
        
        try:
            # Count files before
            before_count = len(list(self.needs_action.glob('EMAIL_*.md')))
            
            # Run gmail watcher once
            result = subprocess.run(
                [sys.executable, str(gmail_script),
                 '--vault-path', str(self.vault_path),
                 '--credentials', str(self.vault_path.parent / '.qwen' / 'credentials.json'),
                 '--once'],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            # Count files after
            after_count = len(list(self.needs_action.glob('EMAIL_*.md')))
            new_emails = after_count - before_count
            
            if new_emails > 0:
                self._log(f"Gmail: Found {new_emails} new emails", "SUCCESS")
                self.stats['emails_processed'] += new_emails
            else:
                self._log("Gmail: No new emails")
            
            return new_emails
            
        except subprocess.TimeoutExpired:
            self._log("Gmail Watcher timed out", "ERROR")
            return 0
        except Exception as e:
            self._log(f"Gmail Watcher error: {e}", "ERROR")
            return 0
    
    def process_emails(self):
        """Process emails with classification and draft creation."""
        self._log("Processing emails...")
        
        if EmailProcessor is None:
            self._log("Email Processor not available", "ERROR")
            return
        
        processor = EmailProcessor(str(self.vault_path))
        
        # Count emails before
        before_count = len(list(self.needs_action.glob('EMAIL_*.md')))
        
        if before_count == 0:
            self._log("No emails to process")
            return
        
        # Process emails
        results = processor.process_pending_emails()
        
        # Update stats
        self.stats['notifications_rejected'] += results['notifications']
        self.stats['drafts_created'] += results['real_emails']
        
        # Log results
        self._log(f"Email processing complete:")
        self._log(f"  - Notifications rejected: {results['notifications']}")
        self._log(f"  - Drafts created: {results['real_emails']}")
        self._log(f"  - Errors: {results['errors']}")
    
    def check_drafts_for_qwen(self):
        """Check for drafts that need Qwen to write replies."""
        self._log("Checking drafts for Qwen...")
        
        drafts_needing_qwen = list(self.drafts.glob('DRAFT_*.md'))
        drafts_needing_qwen = [
            d for d in drafts_needing_qwen 
            if 'status: needs_qwen_draft' in d.read_text(encoding='utf-8')
        ]
        
        if drafts_needing_qwen:
            self._log(f"Found {len(drafts_needing_qwen)} drafts needing Qwen", "WARNING")
            self._log("Run: qwen \"Process drafts in Drafts folder and write replies\"")
            
            # Print draft names
            for draft in drafts_needing_qwen[:5]:
                self._log(f"  - {draft.name}")
        else:
            self._log("All drafts are up to date")
    
    def check_approved_emails(self) -> list:
        """
        Check for approved emails ready to send.
        Supports both APPROVAL_EMAIL_*.md and DRAFT_EMAIL_*.md formats.

        Returns:
            List of approved email files
        """
        approved_files = []

        # Check for APPROVAL_EMAIL_*.md format (old format)
        for filepath in self.approved.glob('APPROVAL_EMAIL_*.md'):
            content = filepath.read_text(encoding='utf-8')
            if 'type: email_approval_request' in content:
                approved_files.append(filepath)

        # Check for DRAFT_EMAIL_*.md format (new format)
        for filepath in self.approved.glob('DRAFT_EMAIL_*.md'):
            content = filepath.read_text(encoding='utf-8')
            if 'type: email_draft' in content and 'status: draft_ready' in content:
                approved_files.append(filepath)

        if approved_files:
            self._log(f"Found {len(approved_files)} approved emails ready to send", "SUCCESS")

        return approved_files
    
    def send_approved_emails(self, confirmed: bool = False):
        """
        Send approved emails with confirmation.

        Args:
            confirmed: If True, skip confirmation prompt
        """
        self._log("Checking approved emails...")

        approved = self.check_approved_emails()

        if not approved:
            self._log("No approved emails to send")
            return

        # Ask for confirmation
        if not confirmed:
            print(f"\n📧 Ready to send {len(approved)} email(s):")
            for i, filepath in enumerate(approved, 1):
                content = filepath.read_text(encoding='utf-8')
                to_email = ''
                subject = ''
                for line in content.split('\n'):
                    if line.startswith('to:'):
                        to_email = line.split(':', 1)[1].strip().strip('"')
                    elif line.startswith('subject:'):
                        subject = line.split(':', 1)[1].strip().strip('"')
                print(f"  {i}. To: {to_email} - Subject: {subject}")

            response = input("\nSend these emails? Type 'Y' to confirm: ").strip().lower()
            if response != 'y':
                self._log("User cancelled email sending", "WARNING")
                return

        # Send each approved email via SMTP
        for filepath in approved:
            self._log(f"Sending: {filepath.name}")

            # Extract email details
            content = filepath.read_text(encoding='utf-8')
            to_email = ''
            subject = ''
            body = ''

            # Extract metadata from frontmatter
            for line in content.split('\n'):
                if line.startswith('to:'):
                    to_email = line.split(':', 1)[1].strip().strip('"')
                elif line.startswith('subject:'):
                    subject = line.split(':', 1)[1].strip().strip('"')

            # Extract draft reply body - handle both formats
            if '## Draft Reply' in content:
                draft_section = content.split('## Draft Reply')[1]
                if '---' in draft_section:
                    # Get content between the --- markers
                    parts = draft_section.split('---')
                    if len(parts) >= 2:
                        body = parts[1].strip()
                        # Remove any trailing sections
                        if '---' in body:
                            body = body.split('---')[0].strip()

            if not to_email or not subject:
                self._log(f"Missing email details in {filepath.name}", "ERROR")
                continue

            if not body:
                self._log(f"Empty draft body in {filepath.name}", "ERROR")
                continue

            # Get SMTP credentials from environment
            smtp_user = os.environ.get('SMTP_USER')
            smtp_pass = os.environ.get('SMTP_PASS')
            smtp_host = os.environ.get('SMTP_HOST', 'smtp.gmail.com')
            smtp_port = int(os.environ.get('SMTP_PORT', 587))

            sent_real = False
            message_id = "unknown"

            if smtp_user and smtp_pass:
                # Try to send real email
                try:
                    import smtplib
                    from email.mime.text import MIMEText
                    from email.mime.multipart import MIMEMultipart

                    # Create message
                    msg = MIMEMultipart()
                    msg['From'] = smtp_user
                    msg['To'] = to_email
                    msg['Subject'] = subject
                    msg.attach(MIMEText(body, 'plain'))

                    # Connect and send
                    self._log(f"Connecting to {smtp_host}:{smtp_port}...")
                    with smtplib.SMTP(smtp_host, smtp_port) as server:
                        server.starttls()
                        server.login(smtp_user, smtp_pass)
                        text = msg.as_string()
                        result = server.send_message(msg)
                        message_id = list(result.keys())[0] if result else "sent"

                    sent_real = True
                    self._log(f"Email sent successfully to {to_email}", "SUCCESS")

                except Exception as e:
                    self._log(f"Failed to send email: {e}", "ERROR")
                    sent_real = False
                    message_id = f"failed: {str(e)}"
            else:
                self._log("SMTP credentials not found - simulating send", "WARNING")

            # Create execution log
            status_text = "✅ SENT (real)" if sent_real else "⚠️ SENT (simulated)"
            new_content = content + f'''

---
## Execution Log

**Status:** {status_text}
**Sent At:** {datetime.now().isoformat()}
**To:** {to_email}
**Subject:** {subject}
**Message ID:** {message_id}
'''

            # Move to Done
            done_path = self.done / f"SENT_{filepath.name}"
            done_path.write_text(new_content, encoding='utf-8')
            filepath.unlink()

            if sent_real:
                self._log(f"✅ Real email sent: {filepath.name}", "SUCCESS")
            else:
                self._log(f"⚠️ Simulated send: {filepath.name}", "WARNING")

            self.stats['emails_sent'] += 1
    
    def update_dashboard(self):
        """Update Dashboard.md with current status."""
        self._log("Updating Dashboard...")
        
        if not self.dashboard_path.exists():
            self._log("Dashboard.md not found", "WARNING")
            return
        
        # Count items in each folder
        needs_action_count = len(list(self.needs_action.glob('EMAIL_*.md')))
        drafts_count = len(list(self.drafts.glob('DRAFT_*.md')))
        pending_count = len(list(self.pending_approval.glob('*.md')))
        approved_count = len(list(self.approved.glob('APPROVAL_EMAIL_*.md')))
        done_count = len(list(self.done.glob('SENT_*.md')))
        
        # Read current dashboard
        content = self.dashboard_path.read_text(encoding='utf-8')
        
        # Update status table
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
        
        # Find and update Quick Status section
        new_status = f'''## Quick Status

| Metric | Status | Details |
|--------|--------|---------|
| Pending Tasks | {needs_action_count} | Check `/Needs_Action` |
| Drafts Ready | {drafts_count} | Check `/Drafts` |
| Pending Approval | {pending_count} | Check `/Pending_Approval` |
| Ready to Send | {approved_count} | Check `/Approved` |
| Completed Today | {done_count} | Check `/Done` |
| System Status | 🟢 Active | Orchestrator running |'''
        
        # Add to Recent Activity
        activity_entry = f"- **{timestamp}**: Orchestrator cycle {self.stats['cycles']} - Processed {self.stats['emails_processed']} emails, {self.stats['drafts_created']} drafts created"
        
        if '## Recent Activity' in content:
            content = content.replace('## Recent Activity', f'## Recent Activity\n{activity_entry}')
        
        # Replace Quick Status section
        if '## Quick Status' in content:
            old_status = content.split('## Quick Status')[1].split('##')[0]
            content = content.replace(f'## Quick Status{old_status}', new_status)
        
        self.dashboard_path.write_text(content, encoding='utf-8')
        self._log("Dashboard updated")
    
    def display_status(self):
        """Display current status to console."""
        elapsed = datetime.now() - self.start_time
        hours, remainder = divmod(int(elapsed.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        
        print("\n" + "=" * 60)
        print("🤖 AI EMPLOYEE ORCHESTRATOR - Silver Tier")
        print("=" * 60)
        print(f"\n📊 LIVE STATUS")
        print("─" * 60)
        print(f"🕐 Running for: {hours}h {minutes}m {seconds}s")
        print(f"🔄 Cycles completed: {self.stats['cycles']}")
        print(f"📧 Gmail Watcher: {'✅ Active' if self.gmail_watcher_process else '⏹️ Stopped'}")
        print(f"💼 LinkedIn Watcher: {'✅ Active' if self.linkedin_watcher_process else '⏹️ Stopped'}")
        print("─" * 60)
        
        print(f"\n📬 PENDING ITEMS")
        print("─" * 60)
        print(f"📧 Needs Action: {len(list(self.needs_action.glob('EMAIL_*.md')))} emails")
        print(f"📝 Drafts: {len(list(self.drafts.glob('DRAFT_*.md')))} drafts")
        print(f"⏳ Pending Approval: {len(list(self.pending_approval.glob('*.md')))} items")
        print(f"✅ Approved Ready: {len(list(self.approved.glob('APPROVAL_EMAIL_*.md')))} emails")
        print("─" * 60)
        
        print(f"\n📊 STATISTICS")
        print("─" * 60)
        print(f"📧 Emails Processed: {self.stats['emails_processed']}")
        print(f"🤖 Notifications Rejected: {self.stats['notifications_rejected']}")
        print(f"📝 Drafts Created: {self.stats['drafts_created']}")
        print(f"📤 Emails Sent: {self.stats['emails_sent']}")
        print("─" * 60)
    
    def run_cycle(self):
        """Run one complete orchestration cycle."""
        self._log("Starting orchestration cycle...")
        self.stats['cycles'] += 1
        
        # 1. Gmail Priority - Fetch new emails
        self.run_gmail_watcher_once()
        
        # 2. Process emails (classify, reject notifications, create drafts)
        self.process_emails()
        
        # 3. Check drafts needing Qwen
        self.check_drafts_for_qwen()
        
        # 4. Check and send approved emails (with confirmation on first run)
        if self.stats['cycles'] == 1:
            self.send_approved_emails(confirmed=False)
        else:
            self.send_approved_emails(confirmed=True)
        
        # 5. Update Dashboard
        self.update_dashboard()
        
        # 6. Display status
        self.display_status()
        
        self._log(f"Cycle {self.stats['cycles']} complete", "SUCCESS")
    
    def run_watch_mode(self):
        """Run in continuous watch mode."""
        self._log(f"Starting watch mode (interval: {self.check_interval}s)", "SUCCESS")
        print(f"\n🔔 Watch mode started - checking every {self.check_interval} seconds")
        print("Press Ctrl+C to stop\n")
        
        try:
            while self.running:
                self.run_cycle()
                
                if self.running:
                    # Wait until next check
                    for i in range(self.check_interval):
                        if not self.running:
                            break
                        time.sleep(1)
        except KeyboardInterrupt:
            self._log("Keyboard interrupt received", "WARNING")
        finally:
            self.running = False
        
        self._log("Watch mode stopped")
    
    def run_interactive_mode(self):
        """Run in interactive menu mode."""
        self._log("Starting interactive mode", "SUCCESS")
        
        while self.running:
            self.display_status()
            
            print("\n📋 MAIN MENU:")
            print("─" * 60)
            print("1. 📧 Process Gmail Now")
            print("2. 📬 Process All Pending Items")
            print("3. 📝 Check Drafts for Qwen")
            print("4. 📤 Send Approved Emails")
            print("5. 🔄 Run Full Cycle")
            print("6. ⚙️  Settings")
            print("0. Exit")
            print("─" * 60)
            
            choice = input("\nEnter choice: ").strip()
            
            if choice == '1':
                self.run_gmail_watcher_once()
            elif choice == '2':
                self.process_emails()
            elif choice == '3':
                self.check_drafts_for_qwen()
            elif choice == '4':
                self.send_approved_emails()
            elif choice == '5':
                self.run_cycle()
            elif choice == '6':
                print(f"\nCurrent interval: {self.check_interval} seconds")
                new_interval = input("New interval (seconds): ").strip()
                if new_interval.isdigit():
                    self.check_interval = int(new_interval)
                    print(f"Interval set to {self.check_interval} seconds")
            elif choice == '0':
                self.running = False
                break
            
            input("\nPress Enter to continue...")
        
        self._log("Interactive mode stopped")
    
    def run(self, mode: str = 'watch'):
        """
        Run orchestrator in specified mode.
        
        Args:
            mode: 'watch', 'interactive', 'once', 'gmail-priority'
        """
        self._log(f"Orchestrator starting in {mode} mode", "SUCCESS")
        
        if mode == 'watch':
            self.run_watch_mode()
        elif mode == 'interactive':
            self.run_interactive_mode()
        elif mode == 'once':
            self.run_cycle()
        elif mode == 'gmail-priority':
            self.run_gmail_watcher_once()
            self.process_emails()
            self.update_dashboard()
        elif mode == 'send-approved':
            self.send_approved_emails()
        else:
            self._log(f"Unknown mode: {mode}", "ERROR")
        
        self._log("Orchestrator stopped", "SUCCESS")


def main():
    parser = argparse.ArgumentParser(
        description='AI Employee Orchestrator - Silver Tier',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Continuous watch mode (recommended)
  python orchestrator.py --vault-path .. --watch --interval 300
  
  # Interactive mode with menu
  python orchestrator.py --vault-path .. --interactive
  
  # One-time process all
  python orchestrator.py --vault-path .. --process-all
  
  # Gmail priority mode
  python orchestrator.py --vault-path .. --gmail-priority
  
  # Send approved emails
  python orchestrator.py --vault-path .. --send-approved
        """
    )
    
    parser.add_argument('--vault-path', default='..', help='Path to vault')
    parser.add_argument('--watch', action='store_true', help='Continuous watch mode')
    parser.add_argument('--interactive', action='store_true', help='Interactive menu mode')
    parser.add_argument('--process-all', action='store_true', help='Process all pending items once')
    parser.add_argument('--gmail-priority', action='store_true', help='Gmail priority mode')
    parser.add_argument('--send-approved', action='store_true', help='Send approved emails')
    parser.add_argument('--interval', type=int, default=300, help='Check interval in seconds (default: 300)')
    
    args = parser.parse_args()
    
    # Determine mode
    if args.watch:
        mode = 'watch'
    elif args.interactive:
        mode = 'interactive'
    elif args.process_all:
        mode = 'once'
    elif args.gmail_priority:
        mode = 'gmail-priority'
    elif args.send_approved:
        mode = 'send-approved'
    else:
        # Default to watch mode
        mode = 'watch'
    
    # Create and run orchestrator
    orchestrator = Orchestrator(
        vault_path=args.vault_path,
        check_interval=args.interval
    )
    
    orchestrator.run(mode)


if __name__ == '__main__':
    main()
