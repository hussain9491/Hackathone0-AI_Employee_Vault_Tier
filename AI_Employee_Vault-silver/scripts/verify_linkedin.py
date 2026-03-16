"""
Playwright Verification Script for LinkedIn

Tests if Playwright can properly launch and interact with LinkedIn.
Use this to debug LinkedIn automation issues.

Usage:
    python verify_linkedin.py --session-path path/to/session
"""

import sys
import time
from pathlib import Path

try:
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
except ImportError:
    print("❌ Playwright not installed. Run:")
    print("   pip install playwright")
    print("   playwright install chromium")
    sys.exit(1)


def verify_playwright():
    """Verify Playwright installation and basic functionality."""
    print("\n" + "=" * 60)
    print("PLAYWRIGHT VERIFICATION TEST")
    print("=" * 60)
    
    # Test 1: Check installation
    print("\n✓ Test 1: Playwright imported successfully")
    
    # Test 2: Launch browser
    print("\n✓ Test 2: Launching Chromium browser...")
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            print("✓ Browser launched successfully")
            
            # Test 3: Create page
            page = browser.new_page()
            print("✓ Page created successfully")
            
            # Test 4: Navigate to LinkedIn
            print("\n✓ Test 3: Navigating to LinkedIn...")
            try:
                page.goto('https://www.linkedin.com/', timeout=30000)
                print("✓ LinkedIn loaded successfully")
                
                # Check page title
                title = page.title()
                print(f"✓ Page title: {title}")
                
                # Test 5: Check for login state
                print("\n✓ Test 4: Checking login state...")
                try:
                    page.wait_for_selector('.global-nav', timeout=5000)
                    print("✓ User appears to be logged in (found navigation)")
                except PlaywrightTimeout:
                    print("⚠ User not logged in (no navigation found)")
                    print("  → Run: python linkedin_poster.py --login")
                
                # Test 6: Check for common elements
                print("\n✓ Test 5: Checking for page elements...")
                
                # Check for login form
                login_form = page.query_selector('#session_key')
                if login_form:
                    print("  ✓ Login form found (not logged in)")
                
                # Check for feed
                feed = page.query_selector('[aria-label="Feed"]')
                if feed:
                    print("  ✓ Feed section found (logged in)")
                
                # Check for post button
                post_btn = page.query_selector('[aria-label="Start a post"]')
                if post_btn:
                    print("  ✓ 'Start a post' button found")
                else:
                    print("  ⚠ 'Start a post' button not found")
                
            except Exception as e:
                print(f"✗ Error loading LinkedIn: {e}")
                
            browser.close()
            print("\n✓ Browser closed successfully")
            
    except Exception as e:
        print(f"✗ Error launching browser: {e}")
        print("\nTroubleshooting:")
        print("1. Reinstall Playwright: pip install --upgrade playwright")
        print("2. Reinstall browsers: playwright install chromium")
        print("3. Check if Chromium is blocked by antivirus")
        return False
    
    print("\n" + "=" * 60)
    print("VERIFICATION COMPLETE")
    print("=" * 60)
    print("\n✓ Playwright is working correctly!")
    print("\nNext steps:")
    print("1. If not logged in: python linkedin_poster.py --login")
    print("2. To create a post: python linkedin_poster.py --post \"Your content\"")
    print("3. To debug visually: python linkedin_poster.py --post \"Content\" --visible")
    return True


def verify_session(session_path: str):
    """Verify existing LinkedIn session."""
    print("\n" + "=" * 60)
    print("SESSION VERIFICATION")
    print("=" * 60)
    
    session_dir = Path(session_path)
    
    if not session_dir.exists():
        print(f"\n✗ Session directory not found: {session_dir}")
        print("  → Run: python linkedin_poster.py --login")
        return False
    
    # Check for session files
    session_files = list(session_dir.glob('*'))
    if not session_files:
        print(f"\n✗ Session directory is empty: {session_dir}")
        print("  → Run: python linkedin_poster.py --login")
        return False
    
    print(f"\n✓ Session directory exists: {session_dir}")
    print(f"✓ Found {len(session_files)} session files")
    
    # Test session with browser
    print("\n✓ Testing session with browser...")
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch_persistent_context(
                user_data_dir=str(session_dir),
                headless=True
            )
            
            page = browser.pages[0] if browser.pages else browser.new_page()
            page.goto('https://www.linkedin.com/', timeout=30000)
            time.sleep(3)
            
            # Check if logged in
            try:
                page.wait_for_selector('.global-nav', timeout=5000)
                print("✓ Session is valid - user is logged in!")
            except PlaywrightTimeout:
                print("✗ Session expired - user not logged in")
                print("  → Run: python linkedin_poster.py --login")
            
            browser.close()
            
    except Exception as e:
        print(f"✗ Error testing session: {e}")
        return False
    
    return True


def main():
    parser = argparse.ArgumentParser(description='Verify LinkedIn Playwright setup')
    parser.add_argument(
        '--session-path',
        help='Path to LinkedIn session folder to verify'
    )
    
    args = parser.parse_args()
    
    # Run basic verification
    verify_playwright()
    
    # Verify session if path provided
    if args.session_path:
        print("\n")
        verify_session(args.session_path)


if __name__ == '__main__':
    import argparse
    main()
