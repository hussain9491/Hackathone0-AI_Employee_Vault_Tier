# AI Employee Vault - Scripts

This folder contains watcher scripts for the AI Employee system.

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the Filesystem Watcher

```bash
cd scripts
python filesystem_watcher.py ..
```

The `..` refers to the parent folder (the vault root).

### 3. Test the Watcher

1. Keep the watcher running in a terminal
2. Drop any file into the `Inbox` folder
3. Watch as an action file is created in `Needs_Action`

## Available Watchers

### Filesystem Watcher (Bronze Tier)

Monitors the `Inbox` folder for new files and creates action files.

```bash
python filesystem_watcher.py /path/to/vault
```
qwen
**Options:**
- `--drop-folder /custom/path` - Use a custom drop folder
- `--interval 5` - Check interval in seconds

### Gmail Watcher (Silver Tier)

Monitors Gmail for unread/important emails.

Requires Google API credentials setup.

### WhatsApp Watcher (Silver Tier)

Monitors WhatsApp Web for messages containing keywords.

Requires Playwright and browser setup.

## Architecture

All watchers inherit from `base_watcher.py` which provides:
- Logging to `/Logs` folder
- Processed item tracking (avoids duplicates)
- Standard run loop
- Error handling

## Stopping the Watcher

Press `Ctrl+C` to stop the watcher gracefully.

## Logs

Watcher logs are saved to `/Logs/watcher_YYYYMMDD.log`
