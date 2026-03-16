"""
Base Watcher Module for AI Employee

All watcher scripts inherit from BaseWatcher class.
Provides common functionality for monitoring and creating action files.
"""

import time
import logging
from pathlib import Path
from abc import ABC, abstractmethod
from datetime import datetime


class BaseWatcher(ABC):
    """
    Abstract base class for all watcher scripts.
    
    Watchers run continuously, monitoring various inputs and creating
    actionable .md files in the Needs_Action folder for Claude to process.
    """
    
    def __init__(self, vault_path: str, check_interval: int = 60):
        """
        Initialize the watcher.
        
        Args:
            vault_path: Path to the Obsidian vault root
            check_interval: Seconds between checks (default: 60)
        """
        self.vault_path = Path(vault_path)
        self.needs_action = self.vault_path / 'Needs_Action'
        self.check_interval = check_interval
        
        # Ensure directories exist
        self.vault_path.mkdir(parents=True, exist_ok=True)
        self.needs_action.mkdir(parents=True, exist_ok=True)
        
        # Setup logging
        self._setup_logging()
        
        # Track processed items to avoid duplicates
        self.processed_ids = set()
        
    def _setup_logging(self):
        """Setup logging to file and console."""
        log_dir = self.vault_path / 'Logs'
        log_dir.mkdir(parents=True, exist_ok=True)
        
        log_file = log_dir / f'watcher_{datetime.now().strftime("%Y%m%d")}.log'
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(self.__class__.__name__)
    
    @abstractmethod
    def check_for_updates(self) -> list:
        """
        Check for new items to process.
        
        Returns:
            List of new items (format depends on watcher type)
        """
        pass
    
    @abstractmethod
    def create_action_file(self, item) -> Path:
        """
        Create a .md action file in Needs_Action folder.
        
        Args:
            item: Item to process (format depends on watcher type)
            
        Returns:
            Path to created action file
        """
        pass
    
    def run(self):
        """
        Main run loop. Continuously checks for updates and creates action files.
        """
        self.logger.info(f'Starting {self.__class__.__name__}')
        self.logger.info(f'Vault path: {self.vault_path}')
        self.logger.info(f'Check interval: {self.check_interval}s')
        
        try:
            while True:
                try:
                    items = self.check_for_updates()
                    for item in items:
                        self.create_action_file(item)
                except Exception as e:
                    self.logger.error(f'Error checking for updates: {e}')
                
                time.sleep(self.check_interval)
        except KeyboardInterrupt:
            self.logger.info(f'{self.__class__.__name__} stopped by user')
        except Exception as e:
            self.logger.error(f'Fatal error: {e}')
            raise


def load_processed_ids(vault_path: str, watcher_name: str) -> set:
    """
    Load previously processed IDs from disk to avoid duplicates after restart.
    
    Args:
        vault_path: Path to the Obsidian vault
        watcher_name: Name of the watcher (for unique state file)
        
    Returns:
        Set of processed IDs
    """
    state_file = Path(vault_path) / 'Logs' / f'{watcher_name}_state.txt'
    if state_file.exists():
        return set(state_file.read_text().strip().split('\n'))
    return set()


def save_processed_ids(vault_path: str, watcher_name: str, processed_ids: set):
    """
    Save processed IDs to disk for persistence across restarts.
    
    Args:
        vault_path: Path to the Obsidian vault
        watcher_name: Name of the watcher
        processed_ids: Set of processed IDs to save
    """
    state_file = Path(vault_path) / 'Logs' / f'{watcher_name}_state.txt'
    state_file.parent.mkdir(parents=True, exist_ok=True)
    state_file.write_text('\n'.join(processed_ids))
