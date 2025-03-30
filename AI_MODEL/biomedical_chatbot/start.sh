#!/bin/bash
echo "Biomedical Chatbot - Startup Script"
echo "==================================="

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Check if the virtual environment exists
if [ ! -d "venv" ]; then
    echo "Setting up virtual environment and installing dependencies."
    echo "This may take a few minutes..."
    python3 setup.py
    
    if [ $? -ne 0 ]; then
        echo "Failed to set up the environment. Please check the error messages above."
        exit 1
    fi
else
    echo "Virtual environment found."
fi

# Activate the virtual environment and run the app
echo "Starting the Biomedical Chatbot application..."
source venv/bin/activate && python app.py

# This part will be reached when the app is stopped
echo "Application stopped." 