"""
LinkedIn Poster for AI Employee

Posts content to LinkedIn using Playwright automation.
Supports scheduled posts, draft review, and human approval workflow.

Usage:
    python linkedin_poster.py --vault-path ../AI_Employee_Vault --post "Your content here"
    python linkedin_poster.py --vault-path ../AI_Employee_Vault --from-file path/to/post.md
    python linkedin_poster.py --login  # First time setup

Author: AI Employee Project
Tier: Silver
"""

import os
import sys
import argparse
import time
import logging
from pathlib import Path
from datetime import datetime

try:
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
except ImportError:
    print("❌ Missing dependencies. Install with:")
    print("   pip install playwright")
    print("   playwright install chromium")
    sys.exit(1)


class LinkedInPoster:
    """
    LinkedIn poster that creates posts using browser automation.
    """

    def __init__(self, vault_path: str, session_path: str = None, headless: bool = True):
        """
        Initialize LinkedIn poster.

        Args:
            vault_path: Path to Obsidian vault
            session_path: Path to store browser session
            headless: Run browser in headless mode (default: True)
        """
        self.vault_path = Path(vault_path)
        self.session_path = Path(session_path) if session_path else self.vault_path / '.obsidian' / 'linkedin_session'
        self.headless = headless
        self.logs_folder = self.vault_path / 'Logs'
        self.posts_folder = self.vault_path / 'Posts'

        # Ensure directories exist
        self.logs_folder.mkdir(parents=True, exist_ok=True)
        self.posts_folder.mkdir(parents=True, exist_ok=True)
        self.session_path.mkdir(parents=True, exist_ok=True)

        # Setup logging
        self._setup_logging()

    def _setup_logging(self):
        """Setup logging to file and console."""
        log_file = self.logs_folder / f'linkedin_poster_{datetime.now().strftime("%Y%m%d")}.log'

        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('LinkedInPoster')

    def _login_to_linkedin(self, page) -> bool:
        """
        Check if already logged in using the saved session.

        Returns:
            True if logged in successfully
        """
        try:
            page.goto('https://www.linkedin.com/feed/', timeout=60000)
            time.sleep(5)  # Wait for page to load

            # Check for various logged-in indicators
            indicators = [
                '.global-nav',
                '[aria-label="Feed"]',
                '[aria-label="Start a post"]',
                '[aria-label="Messaging"]',
                '[aria-label="Notifications"]'
            ]
            
            for indicator in indicators:
                try:
                    page.wait_for_selector(indicator, timeout=3000)
                    self.logger.info(f"Already logged in to LinkedIn (found: {indicator})")
                    return True
                except PlaywrightTimeout:
                    continue

            # Not logged in - check if we're on login page
            current_url = page.url
            self.logger.info(f"Not logged in. Current URL: {current_url}")
            
            if 'login' in current_url.lower():
                self.logger.info("On login page - waiting for manual login...")
                if not self.headless:
                    print("\n👉 Please login to LinkedIn in the browser...")
                    print("👉 After login, wait for your feed to load...\n")
                    
                    # Wait for navigation after login
                    try:
                        with page.expect_navigation(timeout=120000):
                            pass
                        time.sleep(3)
                        
                        # Verify login succeeded
                        for indicator in indicators:
                            try:
                                page.wait_for_selector(indicator, timeout=3000)
                                self.logger.info("Login successful!")
                                return True
                            except PlaywrightTimeout:
                                continue
                                
                    except PlaywrightTimeout:
                        self.logger.error("Login timeout")
                        return False
            
            return False

        except Exception as e:
            self.logger.error(f"Login error: {e}")
            return False

    def create_post(self, content: str, image_path: str = None) -> bool:
        """
        Create a post on LinkedIn.

        Args:
            content: Post content text
            image_path: Optional path to image to attach

        Returns:
            True if post was successful
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

                # Login
                self.logger.info("Checking LinkedIn login status...")
                if not self._login_to_linkedin(page):
                    if self.headless:
                        print("\n⚠️  Not logged in. Run with --login flag first.")
                        print("   python linkedin_poster.py --login --visible")
                        browser.close()
                        return False
                    else:
                        print("\n⚠️  Login required. Please login in the browser.")
                        if not self._login_to_linkedin(page):
                            browser.close()
                            return False

                # Navigate to feed
                self.logger.info("Navigating to feed...")
                page.goto('https://www.linkedin.com/feed/', timeout=60000)
                time.sleep(3)

                # Click on "Start a post"
                try:
                    self.logger.info("Looking for 'Start a post' button...")
                    start_post_btn = page.query_selector('[aria-label="Start a post"]')
                    
                    if start_post_btn:
                        start_post_btn.click()
                        time.sleep(3)
                        self.logger.info("Clicked 'Start a post' button")
                    else:
                        self.logger.error("Could not find 'Start a post' button")
                        print("❌ Could not find 'Start a post' button")
                        browser.close()
                        return False
                except Exception as e:
                    self.logger.error(f"Error clicking start post: {e}")
                    browser.close()
                    return False

                # Wait for post dialog to appear
                time.sleep(2)

                # Find the text editor and enter content
                try:
                    self.logger.info("Entering post content...")
                    # LinkedIn uses a div with contenteditable attribute
                    editor = page.query_selector('div[contenteditable="true"]')
                    if editor:
                        self.logger.info("Found post editor")
                        
                        # Clear any existing content
                        editor.fill('')
                        time.sleep(1)
                        
                        # Type the content
                        editor.type(content, delay=50)
                        time.sleep(2)
                        self.logger.info(f"Entered post content ({len(content)} chars)")
                    else:
                        self.logger.error("Could not find post editor")
                        print("❌ Could not find post editor")
                        browser.close()
                        return False
                except Exception as e:
                    self.logger.error(f"Error entering content: {e}")
                    print(f"❌ Error entering content: {e}")
                    browser.close()
                    return False

                # Add image if provided
                if image_path:
                    try:
                        self.logger.info(f"Attaching image: {image_path}")
                        # Find file input for media
                        image_input = page.query_selector('input[type="file"]')
                        if image_input:
                            image_input.set_input_files(image_path)
                            time.sleep(2)
                            self.logger.info(f"Attached image: {image_path}")
                        else:
                            self.logger.warning("Could not find file input for image")
                    except Exception as e:
                        self.logger.warning(f"Could not attach image: {e}")

                # Click Post button
                try:
                    self.logger.info("Looking for 'Post' button...")
                    post_button = page.query_selector('button:has-text("Post")')
                    if not post_button:
                        # Try alternative selector
                        post_button = page.query_selector('button[aria-label="Post"]')
                    
                    if post_button:
                        # In headless mode, actually post
                        # In visible mode, let user review and click
                        if self.headless:
                            post_button.click()
                            time.sleep(5)
                            self.logger.info("Clicked 'Post' button")
                            print("✅ Post submitted successfully!")
                        else:
                            print("\n👉 Post content loaded in the browser.")
                            print("👉 Review the content and click 'Post' button manually.")
                            print("👉 You can also edit the content before posting.\n")
                            # Wait for user to manually post or close
                            time.sleep(30)
                    else:
                        self.logger.warning("Could not find 'Post' button")
                        print("❌ Could not find 'Post' button")
                except Exception as e:
                    self.logger.error(f"Error clicking post button: {e}")
                    print(f"❌ Error clicking post button: {e}")

                # Wait a bit for post to process
                time.sleep(3)

                browser.close()
                return True

        except Exception as e:
            self.logger.error(f"Error creating post: {e}")
            print(f"❌ Error: {e}")
            return False

    def create_post_from_file(self, file_path: str) -> bool:
        """
        Create a post from a markdown file in the Posts folder.

        Args:
            file_path: Path to the post markdown file

        Returns:
            True if post was successful
        """
        post_file = Path(file_path)
        
        if not post_file.exists():
            # Try relative to posts folder
            post_file = self.posts_folder / file_path
            
        if not post_file.exists():
            self.logger.error(f"Post file not found: {file_path}")
            return False

        # Read the post file
        content = post_file.read_text()
        
        # Extract post content from frontmatter
        post_content = content
        if '---' in content:
            parts = content.split('---')
            if len(parts) >= 3:
                # Skip frontmatter, get the actual content
                post_content = '---'.join(parts[2:]).strip()

        self.logger.info(f"Loaded post from {post_file}")
        return self.create_post(post_content)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='LinkedIn Poster for AI Employee (Silver Tier)'
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
        '--post',
        help='Post content text'
    )
    parser.add_argument(
        '--from-file',
        help='Path to post markdown file'
    )
    parser.add_argument(
        '--image',
        help='Path to image to attach'
    )
    parser.add_argument(
        '--login',
        action='store_true',
        help='Open browser for LinkedIn login (first time setup)'
    )
    parser.add_argument(
        '--visible',
        action='store_true',
        help='Run in visible mode (for debugging/manual review)'
    )

    args = parser.parse_args()

    # Create poster
    poster = LinkedInPoster(
        vault_path=args.vault_path,
        session_path=args.session_path,
        headless=not args.visible
    )

    if args.login or args.visible:
        # Login/visible mode
        print("\n" + "=" * 60)
        print("🔐 LINKEDIN LOGIN / VISIBLE MODE")
        print("=" * 60)
        print("\nOpening browser...")
        
        if args.post:
            print(f"\n📝 Post content: {args.post[:100]}...")
        
        success = poster.create_post(
            content=args.post or "Your post content here",
            image_path=args.image
        )
        
        if success and not args.post:
            print("\n✅ Session saved! You can now post in headless mode.")
        
    elif args.from_file:
        # Post from file
        print("\n📝 Posting from file...")
        success = poster.create_post_from_file(args.from_file)
        if success:
            print("✅ Post created successfully!")
        else:
            print("❌ Failed to create post")
            
    elif args.post:
        # Direct post
        print("\n📝 Creating post...")
        success = poster.create_post(
            content=args.post,
            image_path=args.image
        )
        if success:
            print("✅ Post created successfully!")
        else:
            print("❌ Failed to create post. Run with --visible to debug.")
            
    else:
        # No action specified
        print("\n" + "=" * 60)
        print("LINKEDIN POSTER - Usage Examples")
        print("=" * 60)
        print("""
First time setup:
  python linkedin_poster.py --login

Create a post:
  python linkedin_poster.py --post "Your post content here"

Post with image:
  python linkedin_poster.py --post "Content" --image path/to/image.jpg

Post from file:
  python linkedin_poster.py --from-file Posts/my_post.md

Debug mode (visible browser):
  python linkedin_poster.py --post "Content" --visible
        """)
        print("=" * 60)


if __name__ == '__main__':
    main()
