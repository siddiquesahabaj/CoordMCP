#!/usr/bin/env python3
"""
Script to clean up old CoordMCP data directories.

Run this after updating to the new workspace_path-based system.
"""

import os
import shutil
import sys
from pathlib import Path

def get_old_data_dirs():
    """Get list of old data directories to clean."""
    dirs = []
    
    # Global data dir in home
    home_dir = Path.home()
    global_data = home_dir / ".coordmcp" / "data"
    if global_data.exists():
        dirs.append(global_data)
    
    # Check for any project-specific data directories
    # Look for .coordmcp directories in common workspace locations
    common_workspaces = [
        Path.home() / "projects",
        Path.home() / "workspace",
        Path.home() / "code",
        Path.home() / "dev",
    ]
    
    for workspace in common_workspaces:
        if workspace.exists():
            for item in workspace.iterdir():
                if item.is_dir():
                    coordmcp_dir = item / ".coordmcp" / "data"
                    if coordmcp_dir.exists():
                        dirs.append(coordmcp_dir)
    
    return dirs


def clean_data_directory(data_dir: Path, dry_run: bool = True):
    """Clean a data directory."""
    if not data_dir.exists():
        print(f"  Directory does not exist: {data_dir}")
        return
    
    print(f"  {'Would delete' if dry_run else 'Deleting'}: {data_dir}")
    
    if not dry_run:
        try:
            shutil.rmtree(data_dir)
            print(f"  ✓ Deleted successfully")
        except Exception as e:
            print(f"  ✗ Error deleting: {e}")


def main():
    """Main cleanup function."""
    print("=" * 60)
    print("CoordMCP Data Cleanup Tool")
    print("=" * 60)
    print()
    print("This will clean up old CoordMCP data directories.")
    print("⚠️  WARNING: This will delete all existing project data!")
    print()
    
    # Check for --force flag
    dry_run = "--force" not in sys.argv
    
    if dry_run:
        print("Running in DRY RUN mode (no changes will be made)")
        print("Add --force to actually delete data")
        print()
    
    # Find old data directories
    old_dirs = get_old_data_dirs()
    
    if not old_dirs:
        print("No old data directories found.")
        return
    
    print(f"Found {len(old_dirs)} data directories:")
    for i, dir_path in enumerate(old_dirs, 1):
        print(f"  {i}. {dir_path}")
        # Show size
        try:
            total_size = sum(f.stat().st_size for f in dir_path.rglob('*') if f.is_file())
            size_mb = total_size / (1024 * 1024)
            print(f"     Size: {size_mb:.2f} MB")
        except:
            pass
    
    print()
    
    if dry_run:
        print("To actually delete these directories, run:")
        print("  python cleanup_data.py --force")
    else:
        print("Deleting data directories...")
        for dir_path in old_dirs:
            clean_data_directory(dir_path, dry_run=False)
        
        print()
        print("✓ Cleanup complete!")
        print()
        print("Note: You'll need to recreate projects with the new workspace_path field.")


if __name__ == "__main__":
    main()
