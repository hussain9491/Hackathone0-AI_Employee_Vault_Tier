# LinkedIn Automation for AI Employee

This folder contains scripts for automating LinkedIn interactions using Playwright.

## 📁 Available Scripts

| Script | Purpose | Mode |
|--------|---------|------|
| `linkedin_login.py` | Login and save session | Interactive |
| `linkedin_post_simple.py` | Create posts (recommended) | Interactive |
| `linkedin_poster.py` | Full-featured poster | Headless/Visible |
| `linkedin_watcher.py` | Monitor connections/messages | Background |
| `verify_linkedin.py` | Test setup and session | Diagnostic |

## 🚀 Quick Start

### Step 1: Install Dependencies

```bash
pip install playwright
playwright install chromium
```

### Step 2: Login to LinkedIn

```bash
cd scripts
python linkedin_login.py
```

This opens a browser window:
1. Login to LinkedIn
2. Wait for your feed to load
3. Press Enter in the terminal

### Step 3: Create a Post

**Recommended (Simple Mode):**
```bash
python linkedin_post_simple.py --post "Your post content here"
```

This opens a visible browser, you review and click Post manually.

**Advanced (Headless Mode):**
```bash
python linkedin_poster.py --post "Your content" --visible
```

## 📝 Usage Examples

### Create a Post (Visible Browser)
```bash
python linkedin_post_simple.py --post "Excited to share our new AI Employee project! #automation #AI"
```

### Create a Post with Image
```bash
python linkedin_poster.py --post "Check out our latest update!" --image path/to/image.jpg --visible
```

### Monitor LinkedIn (Background)
```bash
python linkedin_watcher.py --vault-path ../AI_Employee_Vault
```

This watches for:
- New connection requests
- New messages
- Creates action files in `Needs_Action/` folder

### Verify Setup
```bash
python verify_linkedin.py --session-path ..\.obsidian\linkedin_session
```

## 🔧 Troubleshooting

### Issue: "Not logged in" error

**Solution:** Re-login with visible browser
```bash
python linkedin_login.py
```

### Issue: Session expires quickly

LinkedIn sessions can expire. Solutions:
1. Use `linkedin_post_simple.py` - logs in each time
2. Login frequently to keep session fresh
3. Don't close browser abruptly after login

### Issue: "Start a post" button not found

**Causes:**
- Not logged in
- Page didn't load fully
- LinkedIn changed UI

**Solutions:**
```bash
# Try visible mode to see what's happening
python linkedin_poster.py --post "test" --visible

# Or use simple mode
python linkedin_post_simple.py --post "test"
```

### Issue: Browser doesn't open

**Check:**
1. Playwright installed: `pip show playwright`
2. Chromium installed: `playwright install chromium`
3. Antivirus not blocking

## 📂 File Structure

```
scripts/
├── linkedin_login.py         # Login helper
├── linkedin_post_simple.py   # Simple poster (recommended)
├── linkedin_poster.py        # Full-featured poster
├── linkedin_watcher.py       # Monitor for messages
├── verify_linkedin.py        # Diagnostic tool
└── README_LINKEDIN.md        # This file
```

## 🔐 Session Storage

Sessions are saved in:
```
AI_Employee_Vault/.obsidian/linkedin_session/
```

This folder contains browser cookies and local storage.

**Important:** 
- Keep this folder secure
- Don't share it
- Delete if compromised

## 🤖 Integration with AI Employee

### Workflow: Watch → Process → Post

1. **Watcher** monitors LinkedIn for messages/connections
2. Creates action files in `Needs_Action/`
3. **Qwen** processes and drafts responses
4. **Poster** publishes approved content

### Example: Automated Posting

```bash
# 1. Start watcher (background)
python linkedin_watcher.py

# 2. Qwen processes action files in Needs_Action/

# 3. Post approved content
python linkedin_post_simple.py --post "Content from Qwen"
```

## ⚠️ Important Notes

1. **LinkedIn Terms of Service**: Be aware that automation may violate LinkedIn's ToS. Use responsibly.

2. **Rate Limiting**: Don't post too frequently. LinkedIn may flag your account.

3. **Session Fragility**: LinkedIn sessions expire. Be prepared to re-login.

4. **Visible Mode Recommended**: For reliability, use `--visible` flag to see what's happening.

## 📞 Support

If you encounter issues:

1. Run diagnostic: `python verify_linkedin.py --session-path ..\.obsidian\linkedin_session`
2. Check logs in: `AI_Employee_Vault/Logs/`
3. Try visible mode to see what's happening
4. Re-login if session expired

## 🎯 Best Practices

1. **Always test** with a short post first
2. **Use visible mode** when debugging
3. **Don't automate sensitive actions** (password changes, etc.)
4. **Review posts manually** before publishing
5. **Keep sessions private** and secure

---

*AI Employee Project - Silver Tier*
*LinkedIn Automation Scripts*
