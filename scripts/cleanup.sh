#!/bin/bash
# Production Cleanup Script for CoordMCP
# Run this before releasing to PyPI

echo "=========================================="
echo "CoordMCP Production Cleanup Script"
echo "=========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Step 1: Cleaning Python cache files...${NC}"
# Remove all __pycache__ directories
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
# Remove all .pyc and .pyo files
find . -type f -name "*.pyc" -delete 2>/dev/null
find . -type f -name "*.pyo" -delete 2>/dev/null
# Remove .pytest_cache
rm -rf .pytest_cache 2>/dev/null
rm -rf src/tests/__pycache__ 2>/dev/null
echo -e "${GREEN}✓ Python cache cleaned${NC}"
echo ""

echo -e "${YELLOW}Step 2: Cleaning build artifacts...${NC}"
# Remove old build artifacts, keep only latest
if [ -d "dist" ]; then
    cd dist
    # Keep only the 2 most recent versions (wheel and sdist)
    ls -t *.whl | tail -n +3 | xargs -r rm -f
    ls -t *.tar.gz | tail -n +3 | xargs -r rm -f
    cd ..
fi
# Remove build directory
rm -rf build/ 2>/dev/null
# Remove egg-info directories
rm -rf src/*.egg-info/ 2>/dev/null
rm -rf *.egg-info/ 2>/dev/null
echo -e "${GREEN}✓ Build artifacts cleaned${NC}"
echo ""

echo -e "${YELLOW}Step 3: Checking for sensitive files...${NC}"
# Check for .env files
if find . -name ".env" -type f 2>/dev/null | grep -q .; then
    echo -e "${RED}⚠️  Found .env files:${NC}"
    find . -name ".env" -type f
    echo -e "${YELLOW}Make sure these are in .gitignore and not in the package${NC}"
fi

# Check for venv directories
if [ -d "venv" ] || [ -d ".venv" ] || [ -d "env" ]; then
    echo -e "${YELLOW}⚠️  Found virtual environment directories (these should not be in the package)${NC}"
fi
echo -e "${GREEN}✓ Sensitive files check complete${NC}"
echo ""

echo -e "${YELLOW}Step 4: Verifying package structure...${NC}"
# Check that essential files exist
required_files=(
    "README.md"
    "LICENSE"
    "pyproject.toml"
    "MANIFEST.in"
    "src/coordmcp/__init__.py"
    "src/coordmcp/main.py"
)

all_present=true
for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        echo -e "${RED}❌ Missing required file: $file${NC}"
        all_present=false
    fi
done

if [ "$all_present" = true ]; then
    echo -e "${GREEN}✓ All required files present${NC}"
fi
echo ""

echo -e "${YELLOW}Step 5: Building package for verification...${NC}"
python -m build --quiet 2>&1 | tail -5
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Package builds successfully${NC}"
else
    echo -e "${RED}❌ Package build failed${NC}"
fi
echo ""

echo -e "${YELLOW}Step 6: Checking package contents...${NC}"
# List what's in the wheel
if [ -f "dist"/*.whl ]; then
    wheel_file=$(ls -t dist/*.whl | head -1)
    echo "Checking contents of: $(basename $wheel_file)"
    unzip -l "$wheel_file" | grep -E "coordmcp/|\.dist-info" | head -20
fi
echo ""

echo "=========================================="
echo -e "${GREEN}Cleanup Complete!${NC}"
echo "=========================================="
echo ""
echo "Your package is ready for production release!"
echo ""
echo "Next steps:"
echo "  1. Review the changes: git status"
echo "  2. Commit cleanup: git add -A && git commit -m 'chore: Clean up for production release'"
echo "  3. Tag release: git tag v0.1.0"
echo "  4. Push: git push origin main && git push origin v0.1.0"
echo "  5. Build: python -m build"
echo "  6. Upload to PyPI: twine upload dist/*"
echo ""
echo "For detailed release instructions, see: docs/RELEASE.md"
