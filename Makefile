# CoordMCP Makefile
# Development commands for CoordMCP

.PHONY: help install dev test test-unit test-integration test-all lint format clean run docs

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
	@echo "  make lint         - Run linter"
	@echo "  make format       - Format code"
	@echo ""
	@echo "Examples:"
	@echo "  make example-basic      - Run basic example"
	@echo "  make example-multi      - Run multi-agent example"
	@echo "  make example-arch       - Run architecture example"
	@echo "  make example-context    - Run context switching example"

# Setup
install:
	pip install -e .

dev:
	pip install -e ".[dev]"

# Testing
test: test-all

test-all:
	python -m pytest src/tests/ -v

test-unit:
	python -m pytest src/tests/unit/ -v

test-integration:
	python -m pytest src/tests/integration/ -v

# Individual test suites
test-unit-memory:
	python -m pytest src/tests/unit/test_memory/ -v

test-unit-context:
	python -m pytest src/tests/unit/test_context/ -v

test-unit-architecture:
	python -m pytest src/tests/unit/test_architecture/ -v

test-full:
	python src/tests/integration/test_full_integration.py

# Development
run:
	python -m coordmcp.main

run-dev:
	COORDMCP_LOG_LEVEL=DEBUG python -m coordmcp.main

clean:
	# Clean Python cache files
	python -c "import shutil, pathlib, sys; [shutil.rmtree(p) for p in pathlib.Path('.').rglob('__pycache__') if p.is_dir()]; [p.unlink() for p in pathlib.Path('.').rglob('*.py[co]') if p.is_file()]; sys.exit(0)" 2>/dev/null || true
	# Clean build artifacts
	rm -rf build/ dist/ *.egg-info/
	# Clean pytest cache
	rm -rf .pytest_cache/ src/tests/.pytest_cache/

# Examples
example-basic:
	python examples/basic_project_setup.py

example-multi:
	python examples/multi_agent_workflow.py

example-arch:
	python examples/architecture_recommendation.py

example-context:
	python examples/context_switching.py

# Code quality (if tools are installed)
lint:
	@echo "Running linter..."
	@which flake8 > /dev/null 2>&1 && flake8 src/coordmcp/ || echo "flake8 not installed"

format:
	@echo "Formatting code..."
	@which black > /dev/null 2>&1 && black src/coordmcp/ || echo "black not installed"

# Data management
clean-data:
	rm -rf ~/.coordmcp/data/*
	@echo "Data directory cleaned"

view-logs:
	@cat ~/.coordmcp/logs/coordmcp.log 2>/dev/null || echo "No logs found"

# Documentation
docs:
	@echo "Documentation is in docs/ directory"
	@ls -la docs/

# Release
build:
	python -m build

# Help for Windows users (PowerShell)
windows-help:
	@echo "For Windows PowerShell, use:"
	@echo "  python -m coordmcp.main"
	@echo "  python src/tests/test_memory_system.py"
