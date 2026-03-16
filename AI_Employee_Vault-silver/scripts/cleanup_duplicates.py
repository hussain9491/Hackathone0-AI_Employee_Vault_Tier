#!/usr/bin/env python3
"""
Cleanup duplicate PLAN_ and DRAFT_EMAIL_ files.
Keeps only the latest version of each unique email.
"""

import os
import re
from pathlib import Path
from collections import defaultdict


def extract_email_id(filename: str) -> str:
    """Extract the unique email ID from filename."""
    # Pattern: PLAN_EMAIL_<email_id>_<timestamp>.md or DRAFT_EMAIL_<email_id>_<timestamp>.md
    match = re.search(r'(?:PLAN|DRAFT)_EMAIL_(.+?)_\d{8}_\d{4}\.md$', filename)
    if match:
        return match.group(1)
    return None


def cleanup_folder(folder_path: Path, prefix: str) -> tuple:
    """
    Remove duplicate files, keeping only the latest.
    
    Returns:
        Tuple of (kept_count, deleted_count, deleted_files)
    """
    # Group files by email ID
    files_by_id = defaultdict(list)
    
    for filepath in folder_path.glob(f'{prefix}*.md'):
        email_id = extract_email_id(filepath.name)
        if email_id:
            files_by_id[email_id].append(filepath)
    
    kept = 0
    deleted = 0
    deleted_files = []
    
    for email_id, files in files_by_id.items():
        if len(files) > 1:
            # Sort by filename (timestamp is in filename, so alphabetical = chronological)
            files.sort(key=lambda f: f.name, reverse=True)
            
            # Keep the latest (first after sorting)
            kept_file = files[0]
            kept += 1
            
            # Delete the rest
            for old_file in files[1:]:
                old_file.unlink()
                deleted += 1
                deleted_files.append(old_file.name)
        else:
            kept += 1
    
    return kept, deleted, deleted_files


def main():
    vault_path = Path(__file__).parent.parent
    
    plans_folder = vault_path / 'Plans'
    pending_folder = vault_path / 'Pending_Approval'
    
    print("=" * 60)
    print("🧹 CLEANUP DUPLICATES")
    print("=" * 60)
    
    # Cleanup Plans folder
    print(f"\n📁 Plans Folder: {plans_folder}")
    print("-" * 60)
    kept, deleted, deleted_files = cleanup_folder(plans_folder, 'PLAN_EMAIL')
    print(f"   ✅ Kept: {kept} files")
    print(f"   🗑️  Deleted: {deleted} duplicates")
    if deleted_files:
        print("   Deleted files:")
        for f in deleted_files[:10]:  # Show first 10
            print(f"      - {f}")
        if len(deleted_files) > 10:
            print(f"      ... and {len(deleted_files) - 10} more")
    
    # Cleanup Pending_Approval folder
    print(f"\n📁 Pending_Approval Folder: {pending_folder}")
    print("-" * 60)
    kept, deleted, deleted_files = cleanup_folder(pending_folder, 'DRAFT_EMAIL')
    print(f"   ✅ Kept: {kept} files")
    print(f"   🗑️  Deleted: {deleted} duplicates")
    if deleted_files:
        print("   Deleted files:")
        for f in deleted_files[:10]:  # Show first 10
            print(f"      - {f}")
        if len(deleted_files) > 10:
            print(f"      ... and {len(deleted_files) - 10} more")
    
    print("\n" + "=" * 60)
    print("✨ Cleanup complete!")
    print("=" * 60)


if __name__ == '__main__':
    main()
