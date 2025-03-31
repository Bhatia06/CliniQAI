@echo off
color a
cls
title CliniQAI - Adverse Drug Reaction Management System

:: Set environment variable to indicate that the AI Model will be started by run.bat
set CLINIQA_AI_STARTED=1

:: Remove any leftover files from previous runs
if exist cleanup.bat del /f cleanup.bat >nul 2>&1
if exist cleanup_chatbot.bat del /f cleanup_chatbot.bat >nul 2>&1
if exist cleanup_doctor.bat del /f cleanup_doctor.bat >nul 2>&1
if exist ai_model.lock del /f ai_model.lock >nul 2>&1
if exist ai_bypass.py del /f ai_bypass.py >nul 2>&1
if exist ai_chatbot_log.txt del /f ai_chatbot_log.txt >nul 2>&1

:: Initial cleanup - check for running instances and kill them if necessary
echo Checking for running CliniQAI instances...

:: Kill all Python processes that might be related to CliniQAI
for /f "tokens=2" %%p in ('tasklist /fi "imagename eq python.exe" /fo list ^| find "PID:"') do (
    wmic process where "ProcessID=%%p" get CommandLine 2>nul | find "app-starter\main.py" >nul 2>&1
    if %ERRORLEVEL% equ 0 (
        echo Killing CliniQAI process (PID: %%p)
        taskkill /F /PID %%p >nul 2>&1
    )
    
    wmic process where "ProcessID=%%p" get CommandLine 2>nul | find "AI_MODEL\biomedical_chatbot" >nul 2>&1
    if %ERRORLEVEL% equ 0 (
        echo Killing AI model process (PID: %%p)
        taskkill /F /PID %%p >nul 2>&1
    )
    
    wmic process where "ProcessID=%%p" get CommandLine 2>nul | find "doctor-portal\app.py" >nul 2>&1
    if %ERRORLEVEL% equ 0 (
        echo Killing Doctor portal process (PID: %%p)
        taskkill /F /PID %%p >nul 2>&1
    )
    
    wmic process where "ProcessID=%%p" get CommandLine 2>nul | find "patient-portal\app.py" >nul 2>&1
    if %ERRORLEVEL% equ 0 (
        echo Killing Patient portal process (PID: %%p)
        taskkill /F /PID %%p >nul 2>&1
    )
)

:: Kill processes using the application ports
for %%p in (8080 8082 8083 8084) do (
    for /f "tokens=5" %%a in ('netstat -ano ^| find ":%%p" ^| find "LISTENING"') do (
        echo Killing process on port %%p (PID: %%a)
        taskkill /F /PID %%a >nul 2>&1
    )
)

:: Remove any existing lock file
if exist ai_model.lock (
    del /f ai_model.lock >nul 2>&1
)

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
echo Checking Python version...
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

:: Also install AI model specific requirements
if not exist venv\Lib\site-packages\joblib (
    echo Installing AI model dependencies...
    pip install -r AI_MODEL\biomedical_chatbot\requirements.txt
    
    if %ERRORLEVEL% neq 0 (
        echo WARNING: Failed to install AI model dependencies
        echo The AI chatbot may not function correctly.
        echo.
    else
        echo AI model dependencies installed successfully.
    echo.
    )
)

:: Check if AI model file exists
if not exist AI_MODEL\biomedical_chatbot\drug_interaction_model.joblib (
    echo WARNING: AI model file not found at AI_MODEL\biomedical_chatbot\drug_interaction_model.joblib
    echo The AI chatbot will use rule-based predictions only.
    echo.
)

cls
echo CliniQAI - Adverse Drug Reaction Management System
echo ===================================================
echo.
echo Starting all system components...
echo.

:: Start the Doctor Portal in the background
echo Starting Doctor Portal (http://localhost:8082)...
cd doctor-portal
start /b "" cmd /c "set CLINIQA_AI_STARTED=1 && python app.py > nul 2>&1"
cd ..
echo Doctor Portal started.

:: Start the Patient Portal in the background
echo Starting Patient Portal (http://localhost:8083)...
cd patient-portal
start /b "" cmd /c "python app.py > nul 2>&1"
cd ..
echo Patient Portal started.

:: Start the AI Chatbot in the background with output to file for debugging
echo Starting AI Chatbot (http://localhost:8084)...
cd AI_MODEL\biomedical_chatbot
start /b "" cmd /c "python app.py > ..\..\ai_chatbot_log.txt 2>&1"
cd ..\..
echo AI Chatbot started.

:: Wait longer for the AI Model to initialize and start listening
echo Waiting for AI Chatbot to initialize...
timeout /t 5 /nobreak > nul

:: Check if AI Model started successfully
netstat -ano | find ":8084" | find "LISTENING" > nul
if %ERRORLEVEL% neq 0 (
    echo WARNING: AI Chatbot may not have started properly. Check ai_chatbot_log.txt for details.
)

:: Give services time to properly initialize
echo Waiting for all services to finish starting...
echo This may take a moment...
timeout /t 5 /nobreak > nul

:: Start the main dashboard (will stay in foreground)
echo Starting Main Dashboard (http://localhost:8080)...
echo.

:: Start the main app and wait
cd app-starter
start /b "" cmd /c "set CLINIQA_AI_STARTED=1 && python main.py > nul 2>&1"
cd ..

:: Give the main app a moment to start
timeout /t 2 /nobreak > nul

echo.
echo The main dashboard will be launched in a browser window.
echo DO NOT CLOSE THIS WINDOW WHILE USING CliniQAI.

timeout /t 2 /nobreak > nul

echo.
echo All system components are running:
echo  - Main Dashboard: http://localhost:8080
echo  - Doctor Portal: http://localhost:8082
echo  - Patient Portal: http://localhost:8083
echo  - AI Chatbot: http://localhost:8084

timeout /t 2 /nobreak > nul

echo.
echo =================================================
echo ===  PRESS ANY KEY TO START THE APPLICATION   ===
echo =================================================
pause >nul

:: Now open the browser after everything is ready
echo Opening browser to dashboard...

timeout /t 2 /nobreak > nul

start "" http://localhost:8080

echo.
echo =====================================================
echo ===  PRESS ANY KEY TO SHUTDOWN THE APPLICATION    ===
echo =====================================================
pause >nul

echo.
echo CliniQAI has been stopped. Thank you for using our system.
echo Performing final cleanup of any remaining processes...

:: Manually perform cleanup
echo Cleaning up CliniQAI processes...

:: Kill all Python processes again to ensure clean exit
for /f "tokens=2" %%p in ('tasklist /fi "imagename eq python.exe" /fo list ^| find "PID:"') do (
    wmic process where "ProcessID=%%p" get CommandLine 2>nul | find "app-starter\main.py" >nul 2>&1
    if %ERRORLEVEL% equ 0 (
        echo Killing CliniQAI process (PID: %%p)
        taskkill /F /PID %%p >nul 2>&1
    )
    
    wmic process where "ProcessID=%%p" get CommandLine 2>nul | find "AI_MODEL\biomedical_chatbot" >nul 2>&1
    if %ERRORLEVEL% equ 0 (
        echo Killing AI model process (PID: %%p)
        taskkill /F /PID %%p >nul 2>&1
    )
    
    wmic process where "ProcessID=%%p" get CommandLine 2>nul | find "doctor-portal\app.py" >nul 2>&1
    if %ERRORLEVEL% equ 0 (
        echo Killing Doctor portal process (PID: %%p)
        taskkill /F /PID %%p >nul 2>&1
    )
    
    wmic process where "ProcessID=%%p" get CommandLine 2>nul | find "patient-portal\app.py" >nul 2>&1
    if %ERRORLEVEL% equ 0 (
        echo Killing Patient portal process (PID: %%p)
        taskkill /F /PID %%p >nul 2>&1
    )
)

:: Kill processes using the application ports again
for %%p in (8080 8082 8083 8084) do (
    for /f "tokens=5" %%a in ('netstat -ano ^| find ":%%p" ^| find "LISTENING"') do (
        echo Killing process on port %%p (PID: %%a)
        taskkill /F /PID %%a >nul 2>&1
    )
)

echo.
echo All CliniQAI processes have been terminated.
echo.

:: Clean up any Python cache files that may slow down the application
echo Removing Python cache files...
if exist AI_MODEL\biomedical_chatbot\__pycache__ rmdir /s /q AI_MODEL\biomedical_chatbot\__pycache__ >nul 2>&1
if exist doctor-portal\__pycache__ rmdir /s /q doctor-portal\__pycache__ >nul 2>&1
if exist patient-portal\__pycache__ rmdir /s /q patient-portal\__pycache__ >nul 2>&1
if exist app-starter\__pycache__ rmdir /s /q app-starter\__pycache__ >nul 2>&1

:: Clean up any temporary files
if exist cleanup.bat del /f cleanup.bat >nul 2>&1
if exist ai_model.lock del /f ai_model.lock >nul 2>&1
if exist ai_chatbot_log.txt type ai_chatbot_log.txt && del /f ai_chatbot_log.txt >nul 2>&1

:: Reset environment variable
set CLINIQA_AI_STARTED=

:: Deactivate virtual environment
call venv\Scripts\deactivate.bat

exit /b
