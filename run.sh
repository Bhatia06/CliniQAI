#!/bin/bash

echo "CliniQAI - Adverse Drug Reaction Management System"
echo "=================================================="
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3.8 or higher from your package manager or https://www.python.org/downloads/"
    echo
    exit 1
fi

# Display Python version
python3 --version
echo

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to create virtual environment"
        echo "Please make sure you have the venv module installed."
        echo
        exit 1
    fi
    
    echo "Virtual environment created successfully."
    echo
fi

# Activate virtual environment and install dependencies
echo "Activating virtual environment..."
source venv/bin/activate

if [ $? -ne 0 ]; then
    echo "ERROR: Failed to activate virtual environment"
    echo
    exit 1
fi

# Check if dependencies are installed
if [ ! -d "venv/lib/python"*"/site-packages/flask" ]; then
    echo "Installing dependencies..."
    pip install -r requirements.txt
    
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to install dependencies"
        echo
        exit 1
    fi
    
    echo "Dependencies installed successfully."
    echo
fi

# Start the application
echo "Starting CliniQAI..."
echo
echo "Once the application is running, you can access it at:"
echo
echo "Main Dashboard: http://localhost:8080"
echo "Doctor Portal: http://localhost:8082"
echo "Patient Portal: http://localhost:8083"
echo "AI Model: http://localhost:8084"
echo
echo "Press Ctrl+C to stop the application when finished."
echo

cd app-starter
python main.py

# This will be reached when the application is stopped
echo
echo "CliniQAI has been stopped."
echo 