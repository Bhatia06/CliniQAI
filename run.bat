color a
cls
@echo off
echo CliniQAI - Adverse Drug Reaction Management System
echo ===================================================
echo.

:: Check if Python is installed
where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher from https://www.python.org/downloads/
    echo.
    pause
    exit /b
)

:: Display Python version
python --version
echo.

:: Check if virtual environment exists
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
    
    if %ERRORLEVEL% neq 0 (
        echo ERROR: Failed to create virtual environment
        echo Please make sure you have the venv module installed.
        echo.
        pause
        exit /b
    )
    
    echo Virtual environment created successfully.
    echo.
)

:: Activate virtual environment and install dependencies
echo Activating virtual environment...
call venv\Scripts\activate

if %ERRORLEVEL% neq 0 (
    echo ERROR: Failed to activate virtual environment
    echo.
    pause
    exit /b
)

:: Check if dependencies are installed
if not exist venv\Lib\site-packages\flask (
    echo Installing dependencies...
    pip install -r requirements.txt
    
    if %ERRORLEVEL% neq 0 (
        echo ERROR: Failed to install dependencies
        echo.
        pause
        exit /b
    )
    
    echo Dependencies installed successfully.
    echo.
)

:: Start the application
cls
echo Starting CliniQAI...
echo.
echo Once the application is running, you can access it at:
echo.
echo Main Dashboard: http://localhost:8080
echo Doctor Portal: http://localhost:8082
echo Patient Portal: http://localhost:8083
echo AI Model: http://localhost:8084
echo.
echo Press Ctrl+C to stop the application when finished.
echo.

cd app-starter
python main.py

:: This will be reached when the application is stopped
echo.
echo CliniQAI has been stopped.
echo.
pause 