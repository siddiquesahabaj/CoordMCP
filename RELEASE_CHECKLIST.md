# Production Release Checklist for CoordMCP

This document outlines the complete process for releasing CoordMCP to production (PyPI).

## ✅ Pre-Release Checklist

### 1. Code Quality
- [ ] All tests pass (`python -m pytest src/tests/ -v`)
- [ ] No critical bugs or security issues
- [ ] Documentation is up to date (README, API docs)
- [ ] CHANGELOG.md updated with version changes

### 2. Version Management
- [ ] Version number updated in `pyproject.toml` (if not using setuptools-scm)
- [ ] Git tag created (`git tag v0.1.0`)
- [ ] All changes committed and pushed

### 3. Cleanup Completed
The following files should be removed/cleaned before release:

#### ✅ Already Cleaned (via scripts/cleanup.sh):
- [x] Python cache files (`__pycache__`, `*.pyc`, `*.pyo`)
- [x] Old build artifacts in `dist/` (kept only latest 2 versions)
- [x] `build/` directory
- [x] `*.egg-info/` directories
- [x] `.pytest_cache/`

#### ⚠️ Files to Review:
- [ ] `venv/` or `.venv/` - Should be in `.gitignore`, not in package
- [ ] `.env` files - Should NOT be in package (add to `.gitignore`)
- [ ] `docs/` - Already excluded via MANIFEST.in ✅
- [ ] `tests/` - Already excluded via MANIFEST.in ✅
- [ ] `examples/` - Decide: include or exclude?
- [ ] `.github/` - Already excluded via MANIFEST.in ✅

### 4. Required Files Present
Ensure these files exist and are properly configured:
- [x] `README.md` - Comprehensive documentation
- [x] `LICENSE` - MIT License
- [x] `pyproject.toml` - Package configuration
- [x] `MANIFEST.in` - Controls what files are included
- [x] `src/coordmcp/__init__.py` - Package init with version
- [x] `src/coordmcp/main.py` - Entry point
- [x] `src/coordmcp/__main__.py` - Module execution support

### 5. Package Contents Review
Run this to see what's in your package:
```bash
python -m build
unzip -l dist/coordmcp-*.whl
```

Should include:
- ✅ `coordmcp/` directory with all Python files
- ✅ `coordmcp-*.dist-info/` with metadata
- ✅ Should NOT include: tests, docs, .git, venv

## 🚀 Release Process

### Step 1: Final Cleanup
```bash
# Run the cleanup script
bash scripts/cleanup.sh

# Or manually:
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -type f -name "*.pyc" -delete 2>/dev/null
rm -rf build/ *.egg-info/ .pytest_cache/
```

### Step 2: Update Version (if using manual versioning)
```bash
# If NOT using setuptools-scm, update version in pyproject.toml
# With setuptools-scm, version comes from git tags
```

### Step 3: Create Git Tag
```bash
# Commit any final changes
git add -A
git commit -m "chore: Prepare for v0.1.0 release"

# Create annotated tag
git tag -a v0.1.0 -m "Release version 0.1.0"

# Push to remote
git push origin main
git push origin v0.1.0
```

### Step 4: Build Package
```bash
# Clean old builds
rm -rf dist/ build/ *.egg-info/

# Build wheel and sdist
python -m build

# Verify builds
ls -lh dist/
# Should see:
# coordmcp-0.1.0-py3-none-any.whl
# coordmcp-0.1.0.tar.gz
```

### Step 5: Test Installation
```bash
# Create fresh virtual environment
python -m venv test_env
source test_env/bin/activate  # Windows: test_env\Scripts\activate

# Install from wheel
pip install dist/coordmcp-0.1.0-py3-none-any.whl

# Test commands
coordmcp --version
python -m coordmcp --version

# Verify tools are available
python -c "from coordmcp.tools.memory_tools import create_project; print('✓ Import successful')"

# Clean up test environment
deactivate
rm -rf test_env/
```

### Step 6: Upload to Test PyPI (Recommended First)
```bash
# Install twine if not already installed
pip install twine

# Upload to Test PyPI
twine upload --repository testpypi dist/*

# Test installation from Test PyPI
pip install --index-url https://test.pypi.org/simple/ coordmcp
```

### Step 7: Upload to Production PyPI
```bash
# Upload to real PyPI
twine upload dist/*

# Enter your PyPI credentials when prompted
# Username: __token__
# Password: <your-pypi-api-token>
```

### Step 8: Verify PyPI Release
```bash
# Wait a few minutes for PyPI to update

# Install from PyPI
pip install coordmcp

# Test
coordmcp --version
```

## 📋 Files Status Summary

### ✅ Files INCLUDED in Package (via MANIFEST.in):
- README.md
- LICENSE
- CHANGELOG.md
- SECURITY.md
- CONTRIBUTING.md
- All Python files in src/coordmcp/

### ✅ Files EXCLUDED from Package (via MANIFEST.in):
- docs/**
- tests/**
- .github/**
- .gitignore
- .env files
- Makefile
- venv/**
- __pycache__/
- *.pyc, *.pyo

### ⚠️ DECISION NEEDED:
- `examples/` - Currently excluded. Should examples be included?
- `QUICK_REFERENCE.md` - Currently excluded. Include for users?
- `SYSTEM_PROMPT.md` - Currently excluded. Include for agent setup?

To include additional files, edit `MANIFEST.in`:
```
include QUICK_REFERENCE.md
include SYSTEM_PROMPT.md
recursive-include examples *.py *.md
```

## 🔒 Security Checklist

Before releasing:
- [ ] No `.env` files with secrets in the package
- [ ] No hardcoded API keys or passwords
- [ ] No personal/development configuration files
- [ ] LICENSE file present and correct
- [ ] README doesn't contain sensitive information

## 📊 Post-Release Checklist

After releasing to PyPI:
- [ ] Package installs successfully from PyPI
- [ ] Version number is correct
- [ ] All entry points work (`coordmcp`, `python -m coordmcp`)
- [ ] Documentation is accessible
- [ ] GitHub release notes created
- [ ] Announcement made (Twitter, Discord, etc.)

## 🆘 Troubleshooting

### "File already exists on PyPI"
```bash
# You cannot overwrite files on PyPI
# Option 1: Use a new version number
# Option 2: Delete the release on PyPI (not recommended for production)
```

### "Invalid distribution"
```bash
# Clean and rebuild
rm -rf dist/ build/ *.egg-info/
python -m build
```

### "Missing files in package"
```bash
# Check MANIFEST.in
# Rebuild after editing
cat MANIFEST.in
python -m build
unzip -l dist/*.whl
```

## 📞 Support

If you encounter issues:
- Check PyPI documentation: https://packaging.python.org/
- TestPyPI: https://test.pypi.org/
- twine documentation: https://twine.readthedocs.io/

## 🎉 Success!

Once all checks pass, your package is live on PyPI and ready for users to install with:
```bash
pip install coordmcp
```

Congratulations on your release! 🚀
