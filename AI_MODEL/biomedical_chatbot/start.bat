@echo off
echo Biomedical Chatbot - Startup Script
echo ===================================

:: Check if Python is installed
where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo Python is not installed or not in PATH. Please install Python 3.8 or higher.
    pause
    exit /b
)

:: Check if the virtual environment exists
if not exist venv (
    echo Setting up virtual environment and installing dependencies.
    echo This may take a few minutes...
    python setup.py
    
    if %ERRORLEVEL% neq 0 (
        echo Failed to set up the environment. Please check the error messages above.
        pause
        exit /b
    )
) else (
    echo Virtual environment found.
)

:: Activate the virtual environment and run the app
echo Starting the Biomedical Chatbot application...
call venv\Scripts\activate && python app.py

:: This part will be reached when the app is stopped
echo Application stopped.
pause 