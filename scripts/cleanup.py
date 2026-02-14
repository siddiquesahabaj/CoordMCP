#!/usr/bin/env python3
"""
Production Cleanup and Build Script for CoordMCP
Run this before releasing to PyPI

Usage:
    python scripts/cleanup.py
    python scripts/cleanup.py --build
    python scripts/cleanup.py --check
"""

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path


def get_project_root():
    """Get the project root directory."""
    return Path(__file__).parent.parent


def print_color(text, color):
    """Print colored text."""
    colors = {
        'red': '\033[91m',
        'green': '\033[92m',
        'yellow': '\033[93m',
        'blue': '\033[94m',
        'end': '\033[0m'
    }
    
    # Replace Unicode characters with ASCII equivalents for Windows
    if sys.platform == 'win32':
        text = text.replace('✓', '[OK]').replace('✗', '[X]').replace('⚠️', '[!]')
        print(text)
    else:
        print(f"{colors.get(color, '')}{text}{colors['end']}")


def clean_python_cache():
    """Step 1: Clean Python cache files."""
    print_color("Step 1: Cleaning Python cache files...", 'yellow')
    project_root = get_project_root()
    
    # Remove __pycache__ directories
    for pycache_dir in project_root.rglob('__pycache__'):
        if pycache_dir.is_dir():
            try:
                shutil.rmtree(pycache_dir)
            except Exception as e:
                print(f"  Warning: Could not remove {pycache_dir}: {e}")
    
    # Remove .pyc and .pyo files
    for ext in ['*.pyc', '*.pyo', '*.pyd']:
        for file in project_root.rglob(ext):
            try:
                file.unlink()
            except Exception as e:
                print(f"  Warning: Could not remove {file}: {e}")
    
    # Remove .pytest_cache
    pytest_cache = project_root / '.pytest_cache'
    if pytest_cache.exists():
        shutil.rmtree(pytest_cache)
    
    print_color("✓ Python cache cleaned", 'green')


def clean_build_artifacts():
    """Step 2: Clean build artifacts."""
    print_color("Step 2: Cleaning build artifacts...", 'yellow')
    project_root = get_project_root()
    
    # Clean dist directory (keep only latest 2 versions)
    dist_dir = project_root / 'dist'
    if dist_dir.exists():
        wheels = sorted(dist_dir.glob('*.whl'), key=lambda x: x.stat().st_mtime, reverse=True)
        tarballs = sorted(dist_dir.glob('*.tar.gz'), key=lambda x: x.stat().st_mtime, reverse=True)
        
        # Remove old versions
        for wheel in wheels[2:]:
            wheel.unlink()
            print(f"  Removed old wheel: {wheel.name}")
        
        for tarball in tarballs[2:]:
            tarball.unlink()
            print(f"  Removed old tarball: {tarball.name}")
    
    # Remove build directory
    build_dir = project_root / 'build'
    if build_dir.exists():
        shutil.rmtree(build_dir)
    
    # Remove egg-info directories
    for egg_info in project_root.rglob('*.egg-info'):
        if egg_info.is_dir():
            shutil.rmtree(egg_info)
    
    print_color("✓ Build artifacts cleaned", 'green')


def check_sensitive_files():
    """Step 3: Check for sensitive files."""
    print_color("Step 3: Checking for sensitive files...", 'yellow')
    project_root = get_project_root()
    
    # Check for .env files
    env_files = list(project_root.rglob('.env'))
    if env_files:
        print_color("⚠️  Found .env files:", 'red')
        for env_file in env_files:
            print(f"  - {env_file}")
        print_color("Make sure these are in .gitignore and not in the package", 'yellow')
    
    # Check for venv directories
    venv_dirs = ['venv', '.venv', 'env', 'ENV']
    found_venv = False
    for venv_name in venv_dirs:
        venv_path = project_root / venv_name
        if venv_path.exists():
            found_venv = True
            break
    
    if found_venv:
        print_color("⚠️  Found virtual environment directories (these should not be in the package)", 'yellow')
    
    print_color("✓ Sensitive files check complete", 'green')


def verify_package_structure():
    """Step 4: Verify package structure."""
    print_color("Step 4: Verifying package structure...", 'yellow')
    project_root = get_project_root()
    
    required_files = [
        "README.md",
        "LICENSE",
        "pyproject.toml",
        "MANIFEST.in",
        "src/coordmcp/__init__.py",
        "src/coordmcp/main.py",
    ]
    
    all_present = True
    for file in required_files:
        file_path = project_root / file
        if not file_path.exists():
            print_color(f"❌ Missing required file: {file}", 'red')
            all_present = False
    
    if all_present:
        print_color("✓ All required files present", 'green')
    
    return all_present


def build_package():
    """Step 5: Build package for verification."""
    print_color("Step 5: Building package for verification...", 'yellow')
    project_root = get_project_root()
    
    try:
        # Clean previous builds
        dist_dir = project_root / 'dist'
        if dist_dir.exists():
            shutil.rmtree(dist_dir)
        
        # Build the package
        result = subprocess.run(
            [sys.executable, '-m', 'build'],
            cwd=project_root,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print_color("✓ Package builds successfully", 'green')
            return True
        else:
            print_color("❌ Package build failed", 'red')
            print(result.stderr)
            return False
    except Exception as e:
        print_color(f"❌ Error building package: {e}", 'red')
        return False


def check_package_contents():
    """Step 6: Check package contents."""
    print_color("Step 6: Checking package contents...", 'yellow')
    project_root = get_project_root()
    dist_dir = project_root / 'dist'
    
    if not dist_dir.exists():
        print_color("No dist directory found. Run build first.", 'red')
        return
    
    wheels = list(dist_dir.glob('*.whl'))
    if not wheels:
        print_color("No wheel file found in dist/", 'red')
        return
    
    # Get the latest wheel
    latest_wheel = max(wheels, key=lambda x: x.stat().st_mtime)
    print(f"Checking contents of: {latest_wheel.name}")
    
    # List contents
    try:
        import zipfile
        with zipfile.ZipFile(latest_wheel, 'r') as zf:
            files = zf.namelist()
            print(f"\nTotal files: {len(files)}")
            print("\nTop-level directories:")
            top_dirs = set()
            for f in files:
                parts = f.split('/')
                if len(parts) > 0 and parts[0]:
                    top_dirs.add(parts[0])
            for d in sorted(top_dirs):
                print(f"  - {d}")
    except Exception as e:
        print(f"Error reading wheel: {e}")


def main():
    parser = argparse.ArgumentParser(description='CoordMCP Production Cleanup Script')
    parser.add_argument('--build', action='store_true', help='Build package after cleanup')
    parser.add_argument('--check', action='store_true', help='Only check package structure')
    args = parser.parse_args()
    
    print("=" * 50)
    print("CoordMCP Production Cleanup Script")
    print("=" * 50)
    print()
    
    if args.check:
        verify_package_structure()
        return
    
    # Run all cleanup steps
    clean_python_cache()
    print()
    
    clean_build_artifacts()
    print()
    
    check_sensitive_files()
    print()
    
    structure_ok = verify_package_structure()
    print()
    
    if args.build and structure_ok:
        build_package()
        print()
        check_package_contents()
        print()
    
    print("=" * 50)
    print_color("Cleanup Complete!", 'green')
    print("=" * 50)
    print()
    print("Your package is ready for production release!")
    print()
    print("Next steps:")
    print("  1. Review the changes: git status")
    print("  2. Commit cleanup: git add -A && git commit -m 'chore: Clean up for production release'")
    print("  3. Tag release: git tag v0.1.0")
    print("  4. Push: git push origin master && git push origin v0.1.0")
    print("  5. Build: python -m build")
    print("  6. Upload to PyPI: twine upload dist/*")
    print()


if __name__ == '__main__':
    main()
