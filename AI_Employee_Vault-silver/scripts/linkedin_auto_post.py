"""
LinkedIn Auto-Poster for AI Employee

Automatically posts approved content from the Approved/ folder to LinkedIn.
Part of the Qwen integration workflow.

Usage:
    python linkedin_auto_post.py --vault-path ../AI_Employee_Vault
    
Workflow:
    1. Watches Approved/ folder for LINKEDIN_POST_*.md files
    2. Extracts post content
    3. Posts to LinkedIn
    4. Moves file to Done/ on success
    5. Logs result

Author: AI Employee Project
Tier: Silver
"""

import os
import sys
import argparse
import time
import logging
import shutil
from pathlib import Path
from datetime import datetime

try:
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
except ImportError:
    print("❌ Missing dependencies. Install with:")
    print("   pip install playwright")
    print("   playwright install chromium")
    sys.exit(1)


class LinkedInAutoPoster:
    """
    Automated LinkedIn poster that processes approved files.
    """

    def __init__(self, vault_path: str, session_path: str = None,
                 check_interval: int = 60, headless: bool = False):
        """
        Initialize auto poster.

        Args:
            vault_path: Path to Obsidian vault
            session_path: Path to browser session
            check_interval: Seconds between checks (default: 60)
            headless: Run browser in headless mode (default: False for reliability)
        """
        self.vault_path = Path(vault_path)
        self.session_path = Path(session_path) if session_path else self.vault_path / '.obsidian' / 'linkedin_session'
        self.check_interval = check_interval
        self.headless = headless

        # Folders
        self.needs_action = self.vault_path / 'Needs_Action'
        self.approved = self.vault_path / 'Approved'
        self.done = self.vault_path / 'Done'
        self.logs_folder = self.vault_path / 'Logs'

        # Ensure directories exist
        for folder in [self.needs_action, self.approved, self.done, self.logs_folder]:
            folder.mkdir(parents=True, exist_ok=True)
        self.session_path.mkdir(parents=True, exist_ok=True)

        # Setup logging
        self._setup_logging()

        # Track processed files
        self.processed_files = set()

    def _setup_logging(self):
        """Setup logging to file and console."""
        log_file = self.logs_folder / f'linkedin_auto_post_{datetime.now().strftime("%Y%m%d")}.log'

        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('LinkedInAutoPoster')

    def _login_to_linkedin(self, page) -> bool:
        """Check if logged in to LinkedIn."""
        try:
            page.goto('https://www.linkedin.com/feed/', timeout=60000)
            time.sleep(5)

            # Check for logged-in indicators
            indicators = [
                '.global-nav',
                '[aria-label="Feed"]',
                '[aria-label="Start a post"]'
            ]

            for indicator in indicators:
                try:
                    page.wait_for_selector(indicator, timeout=3000)
                    self.logger.info(f"Logged in (found: {indicator})")
                    return True
                except PlaywrightTimeout:
                    continue

            self.logger.warning("Not logged in")
            return False

        except Exception as e:
            self.logger.error(f"Login check failed: {e}")
            return False

    def _extract_post_content(self, file_path: Path) -> dict:
        """
        Extract post content from markdown file.

        Returns:
            Dict with content, image_path, and metadata
        """
        content = file_path.read_text(encoding='utf-8')

        # Parse frontmatter
        metadata = {}
        post_content = content

        if '---' in content:
            parts = content.split('---')
            if len(parts) >= 3:
                # Parse frontmatter
                frontmatter = parts[1].strip()
                for line in frontmatter.split('\n'):
                    if ':' in line:
                        key, value = line.split(':', 1)
                        metadata[key.strip()] = value.strip().strip('"')

                # Get actual content (after frontmatter)
                post_content = '---'.join(parts[2:]).strip()

        # Extract only the main post content (between Post Content section and Hashtags/Media)
        lines = post_content.split('\n')
        clean_lines = []
        in_post_content = False
        
        for line in lines:
            # Skip markdown headers
            if line.startswith('# LinkedIn Post Draft'):
                continue
            # Start capturing after "Post Content" header
            if '## Post Content' in line or '## Post Content (Improved' in line:
                in_post_content = True
                continue
            # Stop at Hashtags, Media, or Workflow sections
            if line.startswith('## Hashtags') or line.startswith('## Media') or line.startswith('## Workflow'):
                in_post_content = False
                break
            # Only add lines from the post content section
            if in_post_content:
                # Skip markdown headers but keep the content
                if not line.startswith('#'):
                    clean_lines.append(line)
        
        # If we didn't find the Post Content section, use the fallback method
        if not clean_lines:
            clean_lines = []
            for line in lines:
                if not line.startswith('#'):
                    clean_lines.append(line)
        
        post_content = '\n'.join(clean_lines).strip()

        # Check for image path in metadata
        image_path = None
        if 'image_path' in metadata:
            image_path = Path(metadata['image_path'])
            if not image_path.exists():
                image_path = None

        return {
            'content': post_content,
            'image_path': image_path,
            'metadata': metadata
        }

    def _create_post(self, content: str, image_path: str = None) -> bool:
        """
        Create a post on LinkedIn.

        Returns:
            True if successful
        """
        try:
            with sync_playwright() as p:
                # Launch browser
                browser = p.chromium.launch_persistent_context(
                    user_data_dir=str(self.session_path),
                    headless=self.headless,
                    args=[
                        '--disable-blink-features=AutomationControlled',
                        '--no-sandbox',
                        '--disable-dev-shm-usage'
                    ]
                )

                page = browser.pages[0] if browser.pages else browser.new_page()

                # Check login
                if not self._login_to_linkedin(page):
                    self.logger.error("Not logged in to LinkedIn")
                    browser.close()
                    return False

                # Navigate to feed
                page.goto('https://www.linkedin.com/feed/', timeout=60000)
                time.sleep(3)

                # Click "Start a post" - try multiple selectors
                start_post_btn = None
                selectors = [
                    '[aria-label="Start a post"]',
                    '[aria-label="Create a post"]',
                    'button:has-text("Start a post")',
                    '.share-box-feed-entry__trigger'
                ]
                
                for selector in selectors:
                    start_post_btn = page.query_selector(selector)
                    if start_post_btn:
                        self.logger.info(f"Found post button with: {selector}")
                        break
                
                if not start_post_btn:
                    self.logger.error("Could not find 'Start a post' button")
                    # Take screenshot for debugging
                    page.screenshot(path='debug_linkedin_start.png')
                    browser.close()
                    return False

                start_post_btn.click()
                time.sleep(3)

                # Wait for post dialog and enter content
                try:
                    self.logger.info("Waiting for post editor...")
                    # Wait for editor to appear with proper timeout
                    page.wait_for_selector('div[contenteditable="true"]', timeout=10000)
                    time.sleep(2)
                    
                    # Get editor and fill content
                    editor = page.query_selector('div[contenteditable="true"]')
                    if editor:
                        self.logger.info("Found post editor")
                        # Clear any existing content
                        editor.fill('')
                        time.sleep(1)
                        # Type content slowly to simulate human
                        editor.type(content, delay=30)
                        time.sleep(2)
                        self.logger.info(f"Entered post content ({len(content)} chars)")
                    else:
                        raise Exception("Editor not found after wait")
                        
                except Exception as e:
                    self.logger.error(f"Error with editor: {e}")
                    page.screenshot(path='debug_linkedin_editor.png')
                    # Fallback: try keyboard navigation
                    self.logger.info("Trying keyboard fallback...")
                    for _ in range(3):
                        page.keyboard.press('Tab')
                    time.sleep(1)
                    page.keyboard.type(content, delay=30)
                    time.sleep(2)

                # Add image if provided
                if image_path and Path(image_path).exists():
                    try:
                        image_input = page.query_selector('input[type="file"]')
                        if image_input:
                            image_input.set_input_files(image_path)
                            time.sleep(2)
                            self.logger.info(f"Attached image: {image_path}")
                    except Exception as e:
                        self.logger.warning(f"Could not attach image: {e}")

                # Click Post button
                post_button = page.query_selector('button:has-text("Post")')
                if not post_button:
                    post_button = page.query_selector('button[aria-label="Post"]')

                if post_button:
                    if self.headless:
                        # Auto-post in headless mode
                        post_button.click()
                        time.sleep(5)
                        self.logger.info("Posted automatically")
                    else:
                        # Visible mode - wait for manual confirmation
                        self.logger.info("Post ready for manual review")
                        print("\n👉 Post loaded in browser")
                        print("👉 Click 'Post' button manually")
                        time.sleep(30)
                else:
                    self.logger.warning("Could not find Post button")

                browser.close()
                return True

        except Exception as e:
            self.logger.error(f"Error creating post: {e}")
            return False

    def _process_approved_file(self, file_path: Path) -> bool:
        """
        Process a single approved file.

        Returns:
            True if successfully posted
        """
        self.logger.info(f"Processing: {file_path.name}")

        # Extract content
        post_data = self._extract_post_content(file_path)
        content = post_data['content']

        if not content or len(content) < 10:
            self.logger.error(f"No valid content in {file_path.name}")
            return False

        self.logger.info(f"Post content: {content[:100]}...")

        # Post to LinkedIn
        success = self._create_post(
            content=content,
            image_path=post_data['image_path']
        )

        if success:
            # Move to Done
            dest = self.done / file_path.name
            shutil.move(str(file_path), str(dest))
            self.logger.info(f"Moved to Done: {dest.name}")

            # Log success
            self._log_action(file_path.name, 'success', content)
        else:
            self.logger.error(f"Failed to post: {file_path.name}")
            self._log_action(file_path.name, 'failed', content)

        return success

    def _log_action(self, filename: str, status: str, content: str):
        """Log action to JSON log file."""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'file': filename,
            'status': status,
            'content_preview': content[:200]
        }

        log_file = self.logs_folder / f'linkedin_posts_{datetime.now().strftime("%Y%m")}.json'

        # Append to log file
        if log_file.exists():
            import json
            logs = json.loads(log_file.read_text())
            logs.append(log_entry)
            log_file.write_text(json.dumps(logs, indent=2))
        else:
            import json
            log_file.write_text(json.dumps([log_entry], indent=2))

    def check_and_post(self):
        """Check for approved files and post them."""
        # Find approved LinkedIn post files
        approved_files = list(self.approved.glob('LINKEDIN_POST_*.md'))

        if not approved_files:
            self.logger.debug("No approved files to process")
            return 0

        posted_count = 0

        for file_path in approved_files:
            if file_path.name in self.processed_files:
                continue

            success = self._process_approved_file(file_path)
            if success:
                posted_count += 1
                self.processed_files.add(file_path.name)

        return posted_count

    def run(self):
        """Main run loop."""
        self.logger.info('Starting LinkedIn Auto-Poster')
        self.logger.info(f'Vault path: {self.vault_path}')
        self.logger.info(f'Check interval: {self.check_interval}s')
        self.logger.info(f'Headless mode: {self.headless}')

        print("\n" + "=" * 60)
        print("LINKEDIN AUTO-POSTER")
        print("=" * 60)
        print(f"\n✅ Auto-Poster started")
        print(f"📁 Approved folder: {self.approved}")
        print(f"📝 Check interval: {self.check_interval} seconds")
        print(f"🔍 Monitoring for: LINKEDIN_POST_*.md files")
        print("\nPress Ctrl+C to stop...\n")

        try:
            while True:
                try:
                    posted = self.check_and_post()

                    if posted > 0:
                        print(f"   ✅ Posted {posted} file(s)")

                except Exception as e:
                    self.logger.error(f'Error in loop: {e}')

                time.sleep(self.check_interval)

        except KeyboardInterrupt:
            self.logger.info('Auto-Poster stopped by user')
            print("\n👋 Auto-Poster stopped")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='LinkedIn Auto-Poster for AI Employee'
    )
    parser.add_argument(
        '--vault-path',
        default='../AI_Employee_Vault',
        help='Path to Obsidian vault'
    )
    parser.add_argument(
        '--session-path',
        help='Path to browser session folder'
    )
    parser.add_argument(
        '--interval',
        type=int,
        default=60,
        help='Check interval in seconds (default: 60)'
    )
    parser.add_argument(
        '--headless',
        action='store_true',
        help='Run in headless mode (auto-post without review)'
    )
    parser.add_argument(
        '--once',
        action='store_true',
        help='Run once and exit (for testing)'
    )

    args = parser.parse_args()

    # Create auto poster
    poster = LinkedInAutoPoster(
        vault_path=args.vault_path,
        session_path=args.session_path,
        check_interval=args.interval,
        headless=args.headless
    )

    if args.once:
        # Test mode
        print("\n🧪 TEST MODE - Checking for approved files...")
        posted = poster.check_and_post()
        print(f"✅ Posted {posted} file(s)")
    else:
        # Continuous mode
        poster.run()


if __name__ == '__main__':
    main()
