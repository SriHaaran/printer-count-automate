@echo off

REM ============================================
REM Initial setup for Ricoh Printer Scraper
REM ============================================

SET PROJECT_DIR=%~dp0

cd /d "%PROJECT_DIR%"

echo Creating virtual environment...
python -m venv venv

echo Activating virtual environment...
call "%PROJECT_DIR%venv\Scripts\activate.bat"

echo Installing Python packages...
pip install --upgrade pip
pip install -r requirements.txt

echo Installing Playwright browser...
python -m playwright install

echo.
echo ============================================
echo Setup completed.
echo Please make sure:
echo 1. Python is installed
echo 2. MS Access ODBC driver is installed
echo 3. .env paths are correct
echo ============================================

pause