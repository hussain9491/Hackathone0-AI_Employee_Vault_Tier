"""
Simple LinkedIn Poster - Direct Post Script

This script opens a visible browser, lets you login, and then helps you post.
More reliable than session-based approach for LinkedIn.

Usage:
    python linkedin_post_simple.py --post "Your content here"
"""

import sys
import time
import argparse
from pathlib import Path

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("❌ Playwright not installed. Run:")
    print("   pip install playwright")
    print("   playwright install chromium")
    sys.exit(1)


def post_to_linkedin(content: str, session_path: str, visible: bool = True):
    """
    Post to LinkedIn using visible browser.
    
    Args:
        content: Post content
        session_path: Path to save session
        visible: Show browser (always True for reliability)
    """
    session_dir = Path(session_path)
    session_dir.mkdir(parents=True, exist_ok=True)
    
    print("\n" + "=" * 60)
    print("LINKEDIN POSTER - DIRECT MODE")
    print("=" * 60)
    print(f"\n📝 Post content: {content[:100]}{'...' if len(content) > 100 else ''}")
    print("\n📁 Session: {session_dir}")
    
    try:
        with sync_playwright() as p:
            # Launch visible browser
            print("\n🚀 Launching browser...")
            browser = p.chromium.launch_persistent_context(
                user_data_dir=str(session_dir),
                headless=False,  # Always visible for reliability
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--no-sandbox',
                    '--disable-dev-shm-usage'
                ]
            )
            
            page = browser.pages[0] if browser.pages else browser.new_page()
            
            # Navigate to LinkedIn
            print("📍 Navigating to LinkedIn...")
            page.goto('https://www.linkedin.com/', timeout=60000)
            time.sleep(3)
            
            # Check if logged in
            print("🔍 Checking login status...")
            logged_in = False
            
            indicators = [
                '.global-nav',
                '[aria-label="Feed"]',
                '[aria-label="Start a post"]'
            ]
            
            for indicator in indicators:
                try:
                    if page.query_selector(indicator):
                        print(f"✓ Logged in (found: {indicator})")
                        logged_in = True
                        break
                except:
                    pass
            
            if not logged_in:
                print("\n" + "=" * 60)
                print("NOT LOGGED IN")
                print("=" * 60)
                print("\n👉 Please login to LinkedIn in the browser window")
                print("👉 After login, wait for your feed to load")
                print("👉 The script will continue automatically\n")
                
                # Wait for login
                max_wait = 120  # 2 minutes
                wait_interval = 5
                waited = 0
                
                while waited < max_wait:
                    time.sleep(wait_interval)
                    waited += wait_interval
                    
                    # Check if logged in now
                    for indicator in indicators:
                        try:
                            if page.query_selector(indicator):
                                print(f"✓ Login detected after {waited}s!")
                                logged_in = True
                                break
                        except:
                            pass
                    
                    if logged_in:
                        break
                    
                    if waited % 30 == 0:
                        print(f"  ...waiting for login ({waited}s/{max_wait}s)")
                
                if not logged_in:
                    print("\n⚠️  Login timeout. Please try again.")
                    browser.close()
                    return False
            
            # Navigate to feed
            print("\n📍 Navigating to feed...")
            page.goto('https://www.linkedin.com/feed/', timeout=60000)
            time.sleep(3)
            
            # Click "Start a post"
            print("\n📝 Clicking 'Start a post'...")
            start_post_btn = page.query_selector('[aria-label="Start a post"]')

            if not start_post_btn:
                print("❌ Could not find 'Start a post' button")
                print("👉 You may need to scroll down to see the post box")
                browser.close()
                return False

            start_post_btn.click()
            time.sleep(3)

            # Enter content - wait for editor
            print("✏️  Entering post content...")
            try:
                # Wait for editor to appear
                page.wait_for_selector('div[contenteditable="true"]', timeout=10000)
                time.sleep(2)
                
                editor = page.query_selector('div[contenteditable="true"]')
                if editor:
                    print("✓ Found post editor")
                    # Clear and type
                    editor.fill('')
                    time.sleep(1)
                    editor.type(content, delay=30)
                    time.sleep(2)
                    print(f"✓ Content entered ({len(content)} characters)")
                else:
                    print("❌ Could not find post editor after waiting")
                    browser.close()
                    return False
            except Exception as e:
                print(f"❌ Error with editor: {e}")
                # Take screenshot
                page.screenshot(path='debug_simple_poster.png')
                print("📸 Screenshot saved to: debug_simple_poster.png")
                browser.close()
                return False
            
            # Show the post for review
            print("\n" + "=" * 60)
            print("POST READY FOR REVIEW")
            print("=" * 60)
            print("\n👉 The post content is now in the LinkedIn post editor")
            print("👉 You can edit it manually if needed")
            print("👉 Click the 'Post' button when ready")
            print("\n⏱️  Browser will close in 60 seconds...")
            
            # Wait for user to post manually
            time.sleep(60)
            
            browser.close()
            print("\n✓ Browser closed")
            print("\n✅ Done! Check your LinkedIn profile to verify the post.")
            
            return True
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    parser = argparse.ArgumentParser(description='Simple LinkedIn Poster')
    parser.add_argument(
        '--post',
        required=True,
        help='Post content'
    )
    parser.add_argument(
        '--session-path',
        default='../AI_Employee_Vault/.obsidian/linkedin_session',
        help='Path to save session'
    )
    
    args = parser.parse_args()
    
    success = post_to_linkedin(
        content=args.post,
        session_path=args.session_path
    )
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
