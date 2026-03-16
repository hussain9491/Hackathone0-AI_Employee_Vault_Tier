---
name: linkedin-poster
description: |
  Automatically post to LinkedIn for business lead generation. Uses Playwright for
  browser automation. Includes approval workflow before posting. Use for automated
  social media presence and lead generation.
---

# LinkedIn Auto Poster Skill

Automatically post to LinkedIn for business lead generation.

## Installation

```bash
pip install playwright
playwright install chromium
```

## ⚠️ Important Notice

**LinkedIn Terms of Service:** Automation may violate LinkedIn's User Agreement.

**Safe Usage:**
- ✅ Post 1-2 times per day maximum
- ✅ Original content only
- ✅ Human review before posting
- ❌ Don't spam or auto-comment

## Quick Reference

### Start LinkedIn Poster

```bash
# Create and schedule post
python AI_Employee_Vault/scripts/linkedin_poster.py --vault-path AI_Employee_Vault --action create

# Post with approval
python AI_Employee_Vault/scripts/linkedin_poster.py --vault-path AI_Employee_Vault --action post --file "post.md"

# Check scheduled posts
python AI_Employee_Vault/scripts/linkedin_poster.py --vault-path AI_Employee_Vault --action list
```

### With Qwen

```bash
# Create LinkedIn post
qwen "Use the linkedin-poster skill to create a post about our new service"

# Schedule post
qwen "Schedule the LinkedIn post for tomorrow at 9 AM"

# Post after approval
qwen "Post the approved LinkedIn content"
```

## Setup: LinkedIn Login

### Step 1: Install Dependencies

```bash
pip install playwright
playwright install chromium
```

### Step 2: First Login

```bash
cd AI_Employee_Vault/scripts
python linkedin_poster.py --vault-path .. --action login
```

Opens browser for LinkedIn login. Session saved for future posts.

## Workflow: LinkedIn Posting

```
1. Qwen creates post content
         ↓
2. Saves to Pending_Approval/LinkedIn_*.md
         ↓
3. User reviews and approves (moves to Approved/)
         ↓
4. LinkedIn poster executes
         ↓
5. Logs post to Logs/linkedin_posts.json
```

## LinkedIn Poster Implementation

```python
# AI_Employee_Vault/scripts/linkedin_poster.py
from playwright.sync_api import sync_playwright
from pathlib import Path
from datetime import datetime
import json
import argparse

class LinkedInPoster:
    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.session_path = self.vault_path / '.obsidian' / 'linkedin_session'
        self.session_path.mkdir(parents=True, exist_ok=True)
        self.log_file = self.vault_path / 'Logs' / 'linkedin_posts.json'
    
    def login(self):
        """Login to LinkedIn and save session."""
        with sync_playwright() as p:
            browser = p.chromium.launch_persistent_context(
                user_data_dir=str(self.session_path),
                headless=False  # Visible for login
            )
            page = browser.pages[0] if browser.pages else browser.new_page()
            page.goto('https://www.linkedin.com/login')
            print("🔐 Login to LinkedIn in the browser...")
            print("Close browser when logged in.")
            input("Press Enter after login complete...")
            browser.close()
        print("✅ Session saved!")
    
    def create_post(self, content: str, topic: str = 'general') -> Path:
        """Create a post draft for approval."""
        timestamp = datetime.now()
        filename = f"LINKEDIN_{topic}_{timestamp.strftime('%Y%m%d')}.md"
        filepath = self.vault_path / 'Pending_Approval' / filename
        
        content_md = f'''---
type: linkedin_post
topic: {topic}
created: {timestamp.isoformat()}
status: pending
scheduled: null
---

# LinkedIn Post Draft

**Created:** {timestamp.strftime('%Y-%m-%d %H:%M')}
**Topic:** {topic}

## Post Content

{content}

## Hashtags

#Business #AI #Automation #Technology

## To Approve

Move this file to /Approved folder to schedule for posting.

## To Reject

Move to /Rejected or delete.

## Notes

_Add any context or images to include_
'''
        filepath.write_text(content_md)
        return filepath
    
    def post(self, content: str) -> dict:
        """Post to LinkedIn."""
        result = {'success': False, 'error': None, 'url': None}
        
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch_persistent_context(
                    user_data_dir=str(self.session_path),
                    headless=True
                )
                page = browser.pages[0] if browser.pages else browser.new_page()
                
                # Go to LinkedIn
                page.goto('https://www.linkedin.com/', timeout=60000)
                page.wait_for_load_state('networkidle')
                
                # Check if logged in
                if 'login' in page.url:
                    result['error'] = 'Not logged in. Run --action login first'
                    browser.close()
                    return result
                
                # Click "Start a post"
                try:
                    page.click('[aria-label="Start a post"]', timeout=5000)
                except:
                    # Alternative selector
                    page.goto('https://www.linkedin.com/feed/')
                    page.wait_for_selector('[aria-label="Start a post"]')
                    page.click('[aria-label="Start a post"]')
                
                # Wait for post dialog
                page.wait_for_selector('[role="dialog"]', timeout=5000)
                
                # Find editor and type content
                editor = page.locator('[role="textbox"]').first
                editor.fill(content[:3000])  # LinkedIn character limit
                
                # Click Post button
                page.click('button:has-text("Post")', timeout=5000)
                page.wait_for_load_state('networkidle')
                
                result['success'] = True
                result['url'] = page.url
                
                browser.close()
                
        except Exception as e:
            result['error'] = str(e)
        
        # Log post
        self._log_post(content, result)
        return result
    
    def _log_post(self, content: str, result: dict):
        """Log post to file."""
        logs = []
        if self.log_file.exists():
            logs = json.loads(self.log_file.read_text())
        
        logs.append({
            'date': datetime.now().isoformat(),
            'content': content[:200],
            'success': result['success'],
            'error': result.get('error'),
            'url': result.get('url')
        })
        self.log_file.write_text(json.dumps(logs, indent=2))


def main():
    parser = argparse.ArgumentParser(description='LinkedIn Auto Poster')
    parser.add_argument('--vault-path', default='..', help='Path to vault')
    parser.add_argument('--action', required=True, 
                        choices=['login', 'create', 'post', 'list'])
    parser.add_argument('--content', help='Post content')
    parser.add_argument('--topic', default='general', help='Post topic')
    parser.add_argument('--file', help='Post file to publish')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("💼 LINKEDIN AUTO POSTER")
    print("=" * 60)
    
    poster = LinkedInPoster(args.vault_path)
    
    if args.action == 'login':
        poster.login()
    
    elif args.action == 'create':
        if not args.content:
            print("❌ --content required for create action")
            return
        filepath = poster.create_post(args.content, args.topic)
        print(f"✅ Post draft created: {filepath}")
    
    elif args.action == 'post':
        if args.file:
            filepath = Path(args.vault_path) / 'Approved' / args.file
            content = filepath.read_text()
            # Extract content from markdown
            lines = content.split('\n')
            post_content = '\n'.join(lines[lines.index('## Post Content')+2:lines.index('## Hashtags')])
        elif args.content:
            post_content = args.content
        else:
            print("❌ --file or --content required")
            return
        
        print("📤 Posting to LinkedIn...")
        result = poster.post(post_content)
        
        if result['success']:
            print(f"✅ Posted successfully!")
            if result['url']:
                print(f"🔗 {result['url']}")
        else:
            print(f"❌ Error: {result['error']}")
    
    elif args.action == 'list':
        if poster.log_file.exists():
            logs = json.loads(poster.log_file.read_text())
            print(f"\n📊 Recent Posts ({len(logs)} total):")
            for log in logs[-5:]:
                status = "✅" if log['success'] else "❌"
                print(f"{status} {log['date'][:10]}: {log['content'][:50]}...")
        else:
            print("No posts logged yet")


if __name__ == '__main__':
    main()
```

## Output Format

Post draft in `Pending_Approval/`:

```markdown
---
type: linkedin_post
topic: ai_automation
created: 2026-03-14T10:30:00
status: pending
---

# LinkedIn Post Draft

**Created:** 2026-03-14 10:30
**Topic:** AI Automation

## Post Content

Excited to announce our new AI Employee system! 🚀

Automate your business tasks with our Digital FTE solution. Save 85% on operational costs while working 24/7.

#AI #Automation #Business #Technology

## Hashtags

#Business #AI #Automation #Technology

## To Approve

Move this file to /Approved folder to schedule for posting.
```

## Best Practices

### Posting Schedule

| Frequency | Risk Level | Recommendation |
|-----------|------------|----------------|
| 1-2 posts/day | Low | ✅ Safe |
| 3-5 posts/day | Medium | ⚠️ Use caution |
| 5+ posts/day | High | ❌ Don't do this |

### Content Guidelines

- ✅ Original content only
- ✅ Add value to network
- ✅ Include relevant hashtags
- ✅ Human review before posting
- ❌ Don't spam connections
- ❌ Don't auto-comment on posts

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "Not logged in" | Run `--action login` first |
| "Post button not found" | LinkedIn UI changed, update selectors |
| Session expired | Re-run login action |
| Post failed | Check character limit (3000 max) |

## Related Skills

- `email-mcp` - Email post notifications
- `approval-workflow-v2` - Approve posts
- `scheduler` - Schedule posts

---

*Skill Version: 1.0 | Last Updated: 2026-03-14 | Silver Tier | ⚠️ Use Responsibly*
