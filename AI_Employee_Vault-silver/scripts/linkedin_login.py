"""
LinkedIn Interactive Login Script

Opens LinkedIn in a visible browser for manual login.
Saves the session for automated posting later.

Usage:
    python linkedin_login.py --session-path path/to/save/session
"""

import sys
import time
from pathlib import Path

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("❌ Playwright not installed. Run:")
    print("   pip install playwright")
    print("   playwright install chromium")
    sys.exit(1)


def login_linkedin(session_path: str):
    """
    Open LinkedIn in visible browser for manual login.
    
    Args:
        session_path: Path to save browser session
    """
    session_dir = Path(session_path)
    session_dir.mkdir(parents=True, exist_ok=True)
    
    print("\n" + "=" * 60)
    print("LINKEDIN LOGIN - VISIBLE BROWSER")
    print("=" * 60)
    print(f"\nSession will be saved to: {session_dir}")
    print("\nInstructions:")
    print("1. Login to LinkedIn in the browser window")
    print("2. Wait for your feed/home page to fully load")
    print("3. Scroll through your feed a bit (helps save session)")
    print("4. Close the browser window when done")
    print("5. This script will verify the session\n")
    
    try:
        with sync_playwright() as p:
            # Launch visible browser with persistent context
            print("Launching browser...")
            browser = p.chromium.launch_persistent_context(
                user_data_dir=str(session_dir),
                headless=False,  # Visible browser
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--no-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-gpu'
                ]
            )
            
            page = browser.pages[0] if browser.pages else browser.new_page()
            
            # Navigate to LinkedIn
            print("Navigating to LinkedIn...")
            page.goto('https://www.linkedin.com/', timeout=60000)
            
            print("\n👉 LOGIN TO LINKEDIN IN THE BROWSER")
            print("👉 After logging in, wait for your feed to load")
            print("👉 Then press Enter here to save the session\n")
            
            # Wait for user to complete login
            input("Press Enter after you've logged in and see your feed...")
            
            # Take a screenshot to verify
            screenshot_path = session_dir / 'login_verification.png'
            page.screenshot(path=str(screenshot_path))
            print(f"✓ Screenshot saved: {screenshot_path}")
            
            # Try to navigate to feed to verify login
            try:
                page.goto('https://www.linkedin.com/feed/', timeout=30000)
                time.sleep(3)
                
                # Check for various logged-in indicators
                indicators = {
                    'Navigation bar': page.query_selector('.global-nav'),
                    'Feed section': page.query_selector('[aria-label="Feed"]'),
                    'Start post button': page.query_selector('[aria-label="Start a post"]'),
                    'Messaging icon': page.query_selector('[aria-label="Messaging"]'),
                    'Notifications icon': page.query_selector('[aria-label="Notifications"]'),
                }
                
                print("\n" + "=" * 60)
                print("SESSION VERIFICATION")
                print("=" * 60)
                
                found_count = 0
                for name, element in indicators.items():
                    if element:
                        print(f"✓ Found: {name}")
                        found_count += 1
                    else:
                        print(f"✗ Not found: {name}")
                
                if found_count >= 2:
                    print("\n✅ LOGIN SUCCESSFUL!")
                    print(f"✓ Session saved to: {session_dir}")
                    print("\nYou can now use:")
                    print("  python linkedin_poster.py --post \"Your content\"")
                else:
                    print("\n⚠️  Login may not have completed")
                    print("  Try running the script again")
                    
            except Exception as e:
                print(f"\n⚠️  Could not verify login: {e}")
            
            # Close browser
            browser.close()
            print("\n✓ Browser closed")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False
    
    return True


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='LinkedIn Login Helper')
    parser.add_argument(
        '--session-path',
        default='../AI_Employee_Vault/.obsidian/linkedin_session',
        help='Path to save browser session'
    )
    
    args = parser.parse_args()
    
    success = login_linkedin(args.session_path)
    
    if success:
        print("\n" + "=" * 60)
        print("NEXT STEPS")
        print("=" * 60)
        print("\n1. Test your session:")
        print("   python verify_linkedin.py --session-path", args.session_path)
        print("\n2. Create a post:")
        print("   python linkedin_poster.py --post \"Your post content\"")
        print("\n3. Post with visible browser (debug mode):")
        print("   python linkedin_poster.py --post \"Content\" --visible")
    else:
        print("\n⚠️  Login did not complete successfully")
        print("   Try running the script again")


if __name__ == '__main__':
    main()
