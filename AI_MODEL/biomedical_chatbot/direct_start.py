import subprocess
import sys
import os
import time
from pathlib import Path

# Get the directory containing this script
SCRIPT_DIR = Path(__file__).parent.absolute()
print(f"Script directory: {SCRIPT_DIR}")

# Ensure necessary packages are installed
print("Installing required packages...")
subprocess.run([
    sys.executable, "-m", "pip", "install", 
    "flask", "flask-cors", "joblib", "numpy", "pandas", "scikit-learn"
], check=True)

# Set the working directory to the script directory to ensure relative paths work
os.chdir(SCRIPT_DIR)
print(f"Changed working directory to: {os.getcwd()}")

# Run the app.py file
print("Starting AI chatbot...")
subprocess.run([sys.executable, "app.py"]) 