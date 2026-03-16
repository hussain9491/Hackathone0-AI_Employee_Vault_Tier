"""
File System Watcher for AI Employee

Monitors a drop folder for new files and creates action files in Needs_Action.
This is the simplest watcher to implement and test for Bronze tier.

Usage:
    python filesystem_watcher.py /path/to/your/vault

Or with custom drop folder:
    python filesystem_watcher.py /path/to/your/vault --drop-folder /path/to/drop
"""

import sys
import shutil
import argparse
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileCreatedEvent

from base_watcher import BaseWatcher, load_processed_ids, save_processed_ids


class DropFolderHandler(FileSystemEventHandler):
    """
    Handles file system events in the drop folder.
    Creates action files when new files are detected.
    """
    
    def __init__(self, vault_path: str, drop_folder: str):
        """
        Initialize the handler.
        
        Args:
            vault_path: Path to the Obsidian vault
            drop_folder: Path to the drop folder to monitor
        """
        self.vault_path = Path(vault_path)
        self.drop_folder = Path(drop_folder)
        self.needs_action = self.vault_path / 'Needs_Action'
        self.processed_files = set()
        
        # Ensure directories exist
        self.needs_action.mkdir(parents=True, exist_ok=True)
        
    def on_created(self, event):
        """
        Called when a file or directory is created.
        
        Args:
            event: File system event
        """
        if event.is_directory:
            return
        
        source = Path(event.src_path)
        
        # Skip if already processed
        if str(source) in self.processed_files:
            return
        
        # Skip temporary files
        if source.name.startswith('~$') or source.suffix in ['.tmp', '.swp']:
            return
        
        print(f'\n📁 New file detected: {source.name}')
        
        # Copy file to Needs_Action
        dest = self.needs_action / f'FILE_{source.name}'
        try:
            shutil.copy2(source, dest)
            print(f'  Copied to: {dest}')
        except Exception as e:
            print(f'  Error copying file: {e}')
            return
        
        # Create metadata file
        meta_path = self.create_metadata(source, dest)
        print(f'  Created metadata: {meta_path.name}')
        
        self.processed_files.add(str(source))
    
    def create_metadata(self, source: Path, dest: Path) -> Path:
        """
        Create a metadata .md file for the dropped file.
        
        Args:
            source: Original file path
            dest: Destination file path in Needs_Action
            
        Returns:
            Path to created metadata file
        """
        from datetime import datetime
        
        meta_path = dest.with_suffix('.md')
        
        content = f'''---
type: file_drop
original_name: {source.name}
size: {source.stat().st_size}
dropped_at: {datetime.now().isoformat()}
status: pending
---

# File Dropped for Processing

**Original File:** `{source.name}`  
**Size:** {self._format_size(source.stat().st_size)}  
**Dropped:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Suggested Actions

- [ ] Review file content
- [ ] Process or take action
- [ ] Move to /Done when complete

## Notes

_Add your notes here_
'''
        meta_path.write_text(content)
        return meta_path
    
    def _format_size(self, size_bytes: int) -> str:
        """Format file size in human-readable format."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} TB"


class FilesystemWatcher(BaseWatcher):
    """
    Filesystem-based watcher using watchdog library.
    Monitors a drop folder for new files.
    """
    
    def __init__(self, vault_path: str, drop_folder: str = None, check_interval: int = 5):
        """
        Initialize the filesystem watcher.
        
        Args:
            vault_path: Path to the Obsidian vault
            drop_folder: Path to drop folder (default: vault/Inbox)
            check_interval: Check interval in seconds
        """
        super().__init__(vault_path, check_interval)
        
        self.drop_folder = Path(drop_folder) if drop_folder else self.vault_path / 'Inbox'
        self.drop_folder.mkdir(parents=True, exist_ok=True)
        
        # Load processed files from disk
        self.processed_files = load_processed_ids(vault_path, 'filesystem_watcher')
        
    def check_for_updates(self) -> list:
        """
        This method is not used for watchdog-based watcher.
        The Observer runs in background and calls the handler directly.
        
        Returns:
            Empty list (watchdog handles events asynchronously)
        """
        return []
    
    def create_action_file(self, item) -> Path:
        """
        Not used for watchdog-based watcher.
        
        Args:
            item: Item to process
            
        Returns:
            None
        """
        pass
    
    def run(self):
        """
        Run the filesystem watcher using watchdog Observer.
        """
        self.logger.info(f'Starting {self.__class__.__name__}')
        self.logger.info(f'Vault path: {self.vault_path}')
        self.logger.info(f'Drop folder: {self.drop_folder}')
        
        event_handler = DropFolderHandler(str(self.vault_path), str(self.drop_folder))
        
        observer = Observer()
        observer.schedule(event_handler, str(self.drop_folder), recursive=False)
        observer.start()
        
        self.logger.info(f'Watching for new files in: {self.drop_folder}')
        print(f'\n✅ Filesystem watcher started')
        print(f'📁 Drop folder: {self.drop_folder}')
        print(f'📝 Action files will be created in: {self.needs_action}')
        print('\nPress Ctrl+C to stop...\n')
        
        try:
            while True:
                # Save processed files periodically for persistence
                save_processed_ids(str(self.vault_path), 'filesystem_watcher', 
                                   event_handler.processed_files)
                import time
                time.sleep(60)
        except KeyboardInterrupt:
            observer.stop()
            self.logger.info(f'{self.__class__.__name__} stopped by user')
        except Exception as e:
            observer.stop()
            self.logger.error(f'Fatal error: {e}')
            raise
        
        observer.join()


def main():
    """Main entry point for the filesystem watcher."""
    parser = argparse.ArgumentParser(
        description='File System Watcher for AI Employee'
    )
    parser.add_argument(
        'vault_path',
        help='Path to your Obsidian vault'
    )
    parser.add_argument(
        '--drop-folder',
        help='Path to drop folder (default: vault/Inbox)'
    )
    parser.add_argument(
        '--interval',
        type=int,
        default=5,
        help='Check interval in seconds (default: 5)'
    )
    
    args = parser.parse_args()
    
    watcher = FilesystemWatcher(
        vault_path=args.vault_path,
        drop_folder=args.drop_folder,
        check_interval=args.interval
    )
    watcher.run()


if __name__ == '__main__':
    main()
