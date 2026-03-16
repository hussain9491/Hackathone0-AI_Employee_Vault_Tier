"""
Debug script to find LinkedIn post editor selectors.
Opens LinkedIn, clicks 'Start a post', and finds the correct editor.
"""

import time
from playwright.sync_api import sync_playwright

def debug_linkedin_editor():
    with sync_playwright() as p:
        # Launch browser visibly
        browser = p.chromium.launch_persistent_context(
            user_data_dir=r"C:\Users\user1542\Documents\GitHub\H-0-Q4\AI_Employee_Vault\.obsidian\linkedin_session",
            headless=False,
            args=['--disable-blink-features=AutomationControlled']
        )
        
        page = browser.pages[0] if browser.pages else browser.new_page()
        
        # Go to LinkedIn
        print("Going to LinkedIn...")
        page.goto('https://www.linkedin.com/feed/')
        time.sleep(5)
        
        # Check if logged in
        start_post = page.query_selector('[aria-label="Start a post"]')
        if not start_post:
            print("Please log in to LinkedIn in the browser window...")
            while not start_post:
                time.sleep(2)
                start_post = page.query_selector('[aria-label="Start a post"]')
        
        print("Clicking 'Start a post'...")
        start_post.click()
        time.sleep(5)
        
        # Take screenshot
        page.screenshot(path='debug_post_dialog.png')
        print("Screenshot saved to: debug_post_dialog.png")
        
        # Find all contenteditable elements
        print("\n=== Searching for editor selectors ===\n")
        
        selectors_to_try = [
            'div[contenteditable="true"]',
            '.ProseMirror',
            '.rich-text-input__contenteditable',
            '[aria-label="What do you want to share?"]',
            'div[aria-label="What do you want to share?"]',
            '.share-box-feed-entry__editor',
            '.editor-composer-editor',
            'div[role="textbox"]',
            '.artdeco-editable',
            '#editable-posting-textbox',
            'div.ember-view[contenteditable="true"]',
            '.share-box-feed-entry__dialog .ProseMirror',
            '[data-id="post-textbox"]',
            '.share-box-feed-entry__popover .ProseMirror',
        ]
        
        found = False
        for selector in selectors_to_try:
            try:
                element = page.query_selector(selector)
                if element:
                    print(f"✅ FOUND: {selector}")
                    tag = element.evaluate('el => el.tagName')
                    classes = element.evaluate('el => el.className')
                    placeholder = element.evaluate('el => el.getAttribute("aria-label")')
                    print(f"   Tag: {tag}, Class: {classes}, Aria-label: {placeholder}")
                    found = True
                    # Try to interact with it
                    try:
                        element.fill('Test')
                        print("   ✅ Successfully filled with test text!")
                        element.fill('')
                        print("   ✅ Successfully cleared!")
                    except Exception as e:
                        print(f"   ⚠️ Could not interact: {e}")
                else:
                    print(f"❌ Not found: {selector}")
            except Exception as e:
                print(f"⚠️ Error checking {selector}: {e}")
        
        if not found:
            print("\n=== Dumping ALL contenteditable elements ===\n")
            editable_elements = page.query_selector_all('[contenteditable="true"]')
            for i, el in enumerate(editable_elements):
                tag = el.evaluate('el => el.tagName')
                classes = el.evaluate('el => el.className')
                aria_label = el.evaluate('el => el.getAttribute("aria-label")')
                parent_class = el.evaluate('el => el.parentElement?.className')
                print(f"{i+1}. Tag: {tag}, Class: {classes}")
                print(f"   Aria-label: {aria_label}")
                print(f"   Parent class: {parent_class}")
        
        print("\n👉 Browser window is open for inspection")
        print("👉 Check debug_post_dialog.png for visual reference")
        print("\nPress Ctrl+C to exit\n")
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nExiting...")
            browser.close()

if __name__ == '__main__':
    print("=" * 60)
    print("LINKEDIN EDITOR DEBUGGER")
    print("=" * 60)
    debug_linkedin_editor()
