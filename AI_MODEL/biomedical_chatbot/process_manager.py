"""
Process Manager for CliniQAI

This module handles process management for the AI model, ensuring only one instance
is running at a time using a lock file mechanism.
"""

import os
import sys
import socket
import signal
import subprocess
import atexit
from pathlib import Path

# Get project root directory
ROOT_DIR = Path(__file__).parent.parent.parent
LOCK_FILE = ROOT_DIR / 'ai_model.lock'
AI_MODEL_PORT = 8084

def is_port_in_use(port):
    """Check if a port is already in use."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def create_lock_file(pid):
    """Create a lock file with the given PID."""
    try:
        with open(LOCK_FILE, 'w') as f:
            f.write(str(pid))
        print(f"Created lock file with PID {pid}")
        return True
    except Exception as e:
        print(f"Error creating lock file: {e}")
        return False

def remove_lock_file():
    """Remove the lock file."""
    try:
        if os.path.exists(LOCK_FILE):
            os.remove(LOCK_FILE)
            print("Removed lock file")
        return True
    except Exception as e:
        print(f"Error removing lock file: {e}")
        return False

def check_lock_file():
    """Check if a lock file exists and if the process is still running."""
    if not os.path.exists(LOCK_FILE):
        return False
    
    try:
        with open(LOCK_FILE, 'r') as f:
            pid = f.read().strip()
            if not pid:
                return False
                
            print(f"Found lock file with PID {pid}")
            
            # Check if the process is still running
            if os.name == 'nt':  # Windows
                cmd = f"tasklist /FI \"PID eq {pid}\" /FO CSV"
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                if f'"{pid}"' in result.stdout:
                    # Process is running, check if it's using our port
                    if is_port_in_use(AI_MODEL_PORT):
                        print(f"AI Model already running on PID {pid}")
                        return True
            else:  # Unix
                try:
                    os.kill(int(pid), 0)  # Signal 0 is used to check if process exists
                    # Process is running, check if it's using our port
                    if is_port_in_use(AI_MODEL_PORT):
                        print(f"AI Model already running on PID {pid}")
                        return True
                except OSError:
                    pass
                    
            # Process is not running or not using our port
            remove_lock_file()
            return False
    except Exception as e:
        print(f"Error checking lock file: {e}")
        remove_lock_file()
        return False

def register_exit_handler():
    """Register exit handler to remove lock file on exit."""
    atexit.register(remove_lock_file)
    
    # Also register signal handlers
    if os.name != 'nt':  # Not needed on Windows
        signal.signal(signal.SIGTERM, lambda sig, frame: remove_lock_file())
        signal.signal(signal.SIGINT, lambda sig, frame: remove_lock_file())

def kill_existing_processes():
    """Kill any existing AI model processes."""
    try:
        if os.name == 'nt':  # Windows
            # Find and kill all Python processes with biomedical_chatbot in the command line
            cmd = 'wmic process where "name=\'python.exe\' and commandline like \'%biomedical_chatbot%\'" get processid /format:csv'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            # Extract PIDs from the output
            for line in result.stdout.splitlines():
                if 'ProcessId' not in line and line.strip():
                    try:
                        pid = line.strip().split(',')[-1]
                        if pid and pid != str(os.getpid()):  # Don't kill ourselves
                            print(f"Killing existing AI Model process (PID: {pid})")
                            subprocess.run(f"taskkill /F /PID {pid}", shell=True)
                    except Exception as e:
                        print(f"Error parsing or killing AI Model process: {e}")
        else:
            # Unix approach
            cmd = "ps aux | grep biomedical_chatbot | grep -v grep | awk '{print $2}'"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            # Extract PIDs from the output
            for pid in result.stdout.splitlines():
                if pid.strip() and pid.strip() != str(os.getpid()):  # Don't kill ourselves
                    print(f"Killing existing AI Model process (PID: {pid})")
                    try:
                        os.kill(int(pid), signal.SIGKILL)
                    except Exception as e:
                        print(f"Error killing AI Model process {pid}: {e}")
    except Exception as e:
        print(f"Error killing existing processes: {e}")

def initialize():
    """Initialize the process manager. Returns True if we should continue, False if we should exit."""
    # If port is already in use and lock file checks out, exit
    if is_port_in_use(AI_MODEL_PORT) and check_lock_file():
        print(f"AI Model is already running on port {AI_MODEL_PORT}")
        return False
    
    # Otherwise, ensure no existing processes are running and create a new lock file
    kill_existing_processes()
    create_lock_file(os.getpid())
    register_exit_handler()
    return True

if __name__ == "__main__":
    # Test the process manager
    if initialize():
        print("Process manager initialized successfully")
        print("Press Ctrl+C to exit")
        try:
            while True:
                pass
        except KeyboardInterrupt:
            print("Exiting...")
            remove_lock_file() 