# CoordMCP Makefile
# Development commands for CoordMCP
# Works on Unix-like systems (Linux, macOS, WSL)

.PHONY: help install dev test test-unit test-integration test-all clean build release lint format docs

# Detect OS
ifeq ($(OS),Windows_NT)
    PYTHON = python
    PYTEST = pytest
    RM = del /Q
    RMDIR = rmdir /S /Q
    SEP = \
else
    PYTHON = python3
    PYTEST = pytest
    RM = rm -f
    RMDIR = rm -rf
    SEP = /
endif

# Default target
help:
	@echo "CoordMCP Development Commands"
	@echo "============================="
	@echo ""
	@echo "Setup:"
	@echo "  make install      - Install dependencies"
	@echo "  make dev          - Install in development mode"
	@echo ""
	@echo "Testing:"
	@echo "  make test         - Run all tests"
	@echo "  make test-unit    - Run unit tests only"
	@echo "  make test-integration - Run integration tests only"
	@echo ""
	@echo "Development:"
	@echo "  make run          - Run the server"
	@echo "  make clean        - Clean build artifacts"
	@echo "  make build        - Build package for PyPI"
	@echo "  make release      - Full release process (clean, test, build)"
	@echo ""
	@echo "Code Quality:"
	@echo "  make lint         - Run linter"
	@echo "  make format       - Format code"
	@echo ""
	@echo "PyPI Release:"
	@echo "  make pypi-test    - Upload to Test PyPI"
	@echo "  make pypi-release - Upload to Production PyPI"
	@echo ""
	@echo "Platform-specific:"
	@echo "  Windows: Use 'make clean' or run Python cleanup manually"
	@echo "  Unix:    Use 'make clean'"

# Setup
install:
	$(PYTHON) -m pip install -e .

dev:
	$(PYTHON) -m pip install -e ".[dev]"

# Testing
test: test-all

test-all:
	$(PYTHON) -m pytest src/tests/ -v

test-unit:
	$(PYTHON) -m pytest src/tests/unit/ -v -m unit

test-integration:
	$(PYTHON) -m pytest src/tests/integration/ -v -m integration

test-e2e:
	$(PYTHON) -m pytest src/tests/e2e/ -v -m e2e

# Development
run:
	$(PYTHON) -m coordmcp.main

run-dev:
	COORDMCP_LOG_LEVEL=DEBUG $(PYTHON) -m coordmcp.main

# Cross-platform clean
clean:
	@echo "Cleaning build artifacts..."
	$(RM) -rf build/ dist/ *.egg-info/
	$(RM) -rf src/coordmcp.egg-info/
	@find . -type d -name "__pycache__" -exec $(RMDIR) {} + 2>/dev/null || true
	@find . -name "*.pyc" -delete 2>/dev/null || true
	@find . -name "*.pyo" -delete 2>/dev/null || true
	@$(RMDIR) .pytest_cache 2>/dev/null || true
	@echo "Clean complete."

# Build package
build: clean
	@echo "Building package..."
	$(PYTHON) -m build
	@echo "Build complete. Check dist/ directory."

# Verify build
verify:
	@echo "Verifying package..."
	@echo ""
	@echo "Package contents:"
	ls -la dist/

# Full release process
release: clean test build verify
	@echo ""
	@echo "=========================================="
	@echo "Release package ready in dist/"
	@echo "=========================================="
	@echo ""
	@echo "Next steps:"
	@echo "  1. Test with: make pypi-test"
	@echo "  2. Release with: make pypi-release"
	@echo ""

# PyPI Uploads
pypi-test: build
	@echo "Uploading to Test PyPI..."
	$(PYTHON) -m twine upload --repository testpypi dist/*
	@echo ""
	@echo "Test installation:"
	@echo "  pip install --index-url https://test.pypi.org/simple/ coordmcp"

pypi-release: build
	@echo "Uploading to Production PyPI..."
	$(PYTHON) -m twine upload dist/*
	@echo ""
	@echo "Installation:"
	@echo "  pip install coordmcp"

# Code quality
lint:
	@echo "Running linter..."
	@which flake8 > /dev/null 2>&1 && flake8 src/coordmcp/ || echo "flake8 not installed. Install with: pip install flake8"

format:
	@echo "Formatting code..."
	@which black > /dev/null 2>&1 && black src/coordmcp/ || echo "black not installed. Install with: pip install black"

format-check:
	@echo "Checking code formatting..."
	@which black > /dev/null 2>&1 && black --check src/coordmcp/ || echo "black not installed"

# Type checking
typecheck:
	@echo "Running type checker..."
	@which mypy > /dev/null 2>&1 && mypy src/coordmcp/ || echo "mypy not installed. Install with: pip install mypy"

# Security check
security:
	@echo "Running security check..."
	@which bandit > /dev/null 2>&1 && bandit -r src/coordmcp/ || echo "bandit not installed. Install with: pip install bandit"

# Documentation
docs:
	@echo "Documentation is in docs/ directory"
	@ls -la docs/

# Data management
clean-data:
	$(RMDIR) ~/.coordmcp/data/*
	@echo "Data directory cleaned"

view-logs:
	@cat ~/.coordmcp/logs/coordmcp.log 2>/dev/null || echo "No logs found"

# Version bump (manual)
bump-version:
	@echo "Current version:"
	@git describe --tags --abbrev=0 2>/dev/null || echo "No tags yet"
	@echo ""
	@echo "To bump version:"
	@echo "  git tag v0.1.1"
	@echo "  git push origin v0.1.1"

# Install release dependencies
install-release:
	$(PYTHON) -m pip install build twine

# Help for Windows users
windows-help:
	@echo "For Windows users:"
	@echo "  Use PowerShell or CMD with Python commands:"
	@echo "  python -m coordmcp.main"
	@echo "  python -m build"
	@echo ""
	@echo "Or use Git Bash/WSL to run Makefile commands"
