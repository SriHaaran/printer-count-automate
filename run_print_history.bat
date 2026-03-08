@echo off

REM ============================================
REM Ricoh Printer History Scraper
REM ============================================

REM Get current project directory
SET PROJECT_DIR=%~dp0

REM Define folders
SET VENV_DIR=%PROJECT_DIR%venv
SET LOG_DIR=%PROJECT_DIR%logs

REM Create logs folder if not exists
IF NOT EXIST "%LOG_DIR%" (
    mkdir "%LOG_DIR%"
)

REM Build log filename (daily log)
SET LOGFILE=%LOG_DIR%\scraper_%DATE:~-4,4%-%DATE:~4,2%-%DATE:~7,2%.log

echo ========================================== >> "%LOGFILE%"
echo START %DATE% %TIME% >> "%LOGFILE%"
echo ========================================== >> "%LOGFILE%"

REM Move into project directory
cd /d "%PROJECT_DIR%"

REM Activate Python virtual environment
call "%VENV_DIR%\Scripts\activate.bat"

REM Run scraper
python app.py >> "%LOGFILE%" 2>&1

echo END %DATE% %TIME% >> "%LOGFILE%"
echo. >> "%LOGFILE%"