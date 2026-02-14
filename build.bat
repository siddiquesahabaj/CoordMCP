@echo off
REM CoordMCP Build Script for Windows
REM This script provides build and release commands for Windows users

setlocal EnableDelayedExpansion

echo ===========================================
echo CoordMCP Windows Build Script
echo ===========================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Please install Python 3.10+
    exit /b 1
)

REM Parse command
if "%~1"=="" goto :help
if /i "%~1"=="help" goto :help
if /i "%~1"=="install" goto :install
if /i "%~1"=="dev" goto :dev
if /i "%~1"=="test" goto :test
if /i "%~1"=="clean" goto :clean
if /i "%~1"=="build" goto :build
if /i "%~1"=="release" goto :release
if /i "%~1"=="pypi-test" goto :pypi-test
if /i "%~1"=="pypi-release" goto :pypi-release
if /i "%~1"=="verify" goto :verify

echo Unknown command: %~1
goto :help

:help
echo Usage: build.bat [command]
echo.
echo Commands:
echo   install      - Install package
echo   dev          - Install in development mode
echo   test         - Run all tests
echo   clean        - Clean build artifacts
echo   build        - Build package for PyPI
echo   verify       - Verify package contents
echo   release      - Full release (clean, test, build)
echo   pypi-test    - Upload to Test PyPI
echo   pypi-release - Upload to Production PyPI
echo.
echo Examples:
echo   build.bat install
echo   build.bat build
echo   build.bat release
echo.
goto :eof

:install
echo Installing CoordMCP...
python -m pip install -e .
if errorlevel 1 (
    echo ERROR: Installation failed
    exit /b 1
)
echo SUCCESS: Installation complete
goto :eof

:dev
echo Installing CoordMCP in development mode...
python -m pip install -e ".[dev]"
if errorlevel 1 (
    echo ERROR: Development installation failed
    exit /b 1
)
echo SUCCESS: Development installation complete
goto :eof

:test
echo Running tests...
python -m pytest src/tests/ -v
if errorlevel 1 (
    echo ERROR: Tests failed
    exit /b 1
)
echo SUCCESS: All tests passed
goto :eof

:clean
echo Cleaning build artifacts...
python scripts/cleanup.py
if errorlevel 1 (
    echo ERROR: Cleanup failed
    exit /b 1
)
echo SUCCESS: Cleanup complete
goto :eof

:build
echo Building package...
call :clean
python -m build
if errorlevel 1 (
    echo ERROR: Build failed
    exit /b 1
)
echo.
echo SUCCESS: Package built successfully
echo Check the dist/ directory for the built packages
goto :eof

:verify
echo Verifying package...
if not exist "dist\*.whl" (
    echo ERROR: No wheel file found. Run 'build.bat build' first.
    exit /b 1
)
echo.
echo Package contents:
dir dist\ /b
echo.
echo SUCCESS: Package verified
goto :eof

:release
echo Running full release process...
call :clean
call :test
if errorlevel 1 exit /b 1
call :build
if errorlevel 1 exit /b 1
call :verify
echo.
echo ===========================================
echo RELEASE PACKAGE READY
echo ===========================================
echo.
echo Next steps:
echo   1. Test with: build.bat pypi-test
echo   2. Release with: build.bat pypi-release
echo.
goto :eof

:pypi-test
echo Uploading to Test PyPI...
if not exist "dist\*.whl" (
    echo ERROR: No package found. Run 'build.bat build' first.
    exit /b 1
)
python -m twine upload --repository testpypi dist\*
if errorlevel 1 (
    echo ERROR: Upload to Test PyPI failed
    exit /b 1
)
echo.
echo SUCCESS: Uploaded to Test PyPI
echo Test installation with:
echo   pip install --index-url https://test.pypi.org/simple/ coordmcp
goto :eof

:pypi-release
echo ===========================================
echo WARNING: Uploading to PRODUCTION PyPI
echo ===========================================
echo.
echo This will publish the package to the production PyPI repository.
echo This action cannot be undone easily.
echo.
set /p confirm="Are you sure you want to continue? (yes/no): "
if /i not "!confirm!"=="yes" (
    echo Cancelled.
    goto :eof
)

if not exist "dist\*.whl" (
    echo ERROR: No package found. Run 'build.bat build' first.
    exit /b 1
)

python -m twine upload dist\*
if errorlevel 1 (
    echo ERROR: Upload to PyPI failed
    exit /b 1
)
echo.
echo SUCCESS: Package published to PyPI
echo Users can now install with: pip install coordmcp
goto :eof

:eof
echo.
