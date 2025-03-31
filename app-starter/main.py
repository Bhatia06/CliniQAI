from flask import Flask, render_template, redirect
import subprocess
import os
import threading
import time
import signal
import sys
import socket
import logging
from pathlib import Path
import queue
import datetime
import csv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('cliniqai.log')
    ]
)
logger = logging.getLogger('CliniQAI')

app = Flask(__name__)

# Paths to the other Flask applications - Using relative paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
DOCTOR_APP_PATH = os.path.join(PROJECT_ROOT, "doctor-portal", "app.py")
PATIENT_APP_PATH = os.path.join(PROJECT_ROOT, "patient-portal", "app.py")
AI_MODEL_PATH = os.path.join(PROJECT_ROOT, "AI_MODEL", "biomedical_chatbot", "app.py")

# Data file paths
DATA_FILE = os.path.join(PROJECT_ROOT, "adr_reports.csv")
PATIENT_DATA_DIR = os.path.join(PROJECT_ROOT, "patient-portal", "data")
PATIENT_ID_FILE = os.path.join(PATIENT_DATA_DIR, "patient_id_counter.txt")

# Configuration for ports
MAIN_PORT = 8080
DOCTOR_PORT = 8082
PATIENT_PORT = 8083
AI_MODEL_PORT = 8084

# Lock file to prevent multiple AI model instances
AI_MODEL_LOCK_FILE = os.path.join(PROJECT_ROOT, "ai_model.lock")

# Process objects to keep track of the subprocesses
doctor_process = None
patient_process = None
ai_model_process = None

def ensure_data_directories():
    """Create necessary data directories and files if they don't exist"""
    logger.info("Checking data directories...")
    
    # Ensure patient portal data directory exists
    if not os.path.exists(PATIENT_DATA_DIR):
        logger.info(f"Creating patient data directory: {PATIENT_DATA_DIR}")
        os.makedirs(PATIENT_DATA_DIR, exist_ok=True)
    
    # Ensure patient ID counter file exists
    if not os.path.exists(PATIENT_ID_FILE):
        logger.info(f"Creating patient ID counter file: {PATIENT_ID_FILE}")
        with open(PATIENT_ID_FILE, 'w') as f:
            f.write('2000')
    
    # Ensure ADR reports CSV file exists with proper headers
    if not os.path.exists(DATA_FILE):
        logger.info(f"Creating ADR reports file: {DATA_FILE}")
        with open(DATA_FILE, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                'timestamp', 'drug_name', 'medical_condition', 'adverse_reaction', 
                'severity', 'confidence', 'cause_of_administration', 'gender', 
                'patient_id', 'current_medication'
            ])
        logger.info("Created ADR reports file with headers")
    
    logger.info("Data directories check completed")

def check_port_available(port):
    """Check if a port is available for use"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('127.0.0.1', port))
    sock.close()
    return result != 0

def read_process_output(process, output_queue, name):
    """Read output from a process and put it in a queue"""
    logger.info(f"Started output reader for {name}")
    try:
        for line in iter(process.stdout.readline, ''):
            if line:
                output_queue.put((name, "stdout", line.strip()))
        for line in iter(process.stderr.readline, ''):
            if line:
                output_queue.put((name, "stderr", line.strip()))
    except Exception as e:
        logger.error(f"Error reading {name} process output: {str(e)}")
    logger.debug(f"Output reader for {name} has stopped")

def start_doctor_app():
    """Start the doctor portal Flask app"""
    global doctor_process
    
    if not check_port_available(DOCTOR_PORT):
        logger.warning(f"Port {DOCTOR_PORT} is already in use, Doctor Portal might not start correctly")
    
    try:
        doctor_dir = os.path.dirname(DOCTOR_APP_PATH)
        
        if not os.path.exists(DOCTOR_APP_PATH):
            logger.error(f"Doctor Portal app file not found at: {DOCTOR_APP_PATH}")
            return False
            
        doctor_process = subprocess.Popen(
            [sys.executable, DOCTOR_APP_PATH],
            cwd=doctor_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        logger.info(f"Started Doctor Portal (PID: {doctor_process.pid})")
        return True
    except Exception as e:
        logger.error(f"Error starting Doctor Portal: {str(e)}")
        return False

def start_patient_app():
    """Start the patient portal Flask app"""
    global patient_process
    
    if not check_port_available(PATIENT_PORT):
        logger.warning(f"Port {PATIENT_PORT} is already in use, Patient Portal might not start correctly")
    
    try:
        patient_dir = os.path.dirname(PATIENT_APP_PATH)
        
        if not os.path.exists(PATIENT_APP_PATH):
            logger.error(f"Patient Portal app file not found at: {PATIENT_APP_PATH}")
            return False
            
        patient_process = subprocess.Popen(
            [sys.executable, PATIENT_APP_PATH],
            cwd=patient_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        logger.info(f"Started Patient Portal (PID: {patient_process.pid})")
        return True
    except Exception as e:
        logger.error(f"Error starting Patient Portal: {str(e)}")
        return False

def start_ai_model():
    """Start the AI model Flask app"""
    global ai_model_process
    
    # Check if the AI model is being started by run.bat
    if os.environ.get('CLINIQA_AI_STARTED') == '1':
        logger.info("AI Model is being started by run.bat, skipping startup in app-starter")
        return True
    
    # First, ensure no AI Model instances are running
    logger.info("Checking for existing AI Model instances...")
    
    # Check for lock file
    if os.path.exists(AI_MODEL_LOCK_FILE):
        try:
            with open(AI_MODEL_LOCK_FILE, 'r') as f:
                pid = f.read().strip()
                logger.info(f"Found AI Model lock file with PID: {pid}")
                
                # Check if process with this PID exists
                try:
                    if os.name == 'nt':  # Windows
                        check_cmd = f"tasklist /FI \"PID eq {pid}\" /FO CSV"
                        result = subprocess.run(check_cmd, shell=True, capture_output=True, text=True)
                        if f'"{pid}"' in result.stdout:
                            logger.info(f"Found existing AI Model process with PID {pid}")
                            # Try to reuse the existing process
                            if not check_port_available(AI_MODEL_PORT):
                                logger.info("AI Model port is already in use, reusing existing instance")
                                return True
                    else:
                        # Unix
                        try:
                            os.kill(int(pid), 0)  # Send signal 0 to check if process exists
                            logger.info(f"Found existing AI Model process with PID {pid}")
                            # Try to reuse the existing process
                            if not check_port_available(AI_MODEL_PORT):
                                logger.info("AI Model port is already in use, reusing existing instance")
                                return True
                        except ProcessLookupError:
                            logger.info(f"No process with PID {pid} exists")
                except Exception as e:
                    logger.error(f"Error checking process existence: {str(e)}")
        except Exception as e:
            logger.error(f"Error reading AI Model lock file: {str(e)}")
    
    try:
        # Kill any existing instances of the AI Model
        if os.name == 'nt':  # Windows
            # Find and kill all Python processes with biomedical_chatbot in the command line
            cmd = 'wmic process where "name=\'python.exe\' and commandline like \'%biomedical_chatbot%\'" get processid /format:csv'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            # Extract PIDs from the output
            killed_count = 0
            if result.stdout:
                for line in result.stdout.splitlines():
                    if 'ProcessId' not in line and line.strip():
                        try:
                            pid = line.strip().split(',')[-1]
                            if pid:
                                logger.info(f"Killing existing AI Model process (PID: {pid})")
                                subprocess.run(f"taskkill /F /PID {pid}", shell=True)
                                killed_count += 1
                        except Exception as e:
                            logger.error(f"Error parsing or killing AI Model process: {str(e)}")
            
            if killed_count > 0:
                logger.info(f"Killed {killed_count} existing AI Model instances")
                # Give processes time to fully terminate
                time.sleep(2)
        else:
            # Unix approach
            cmd = "ps aux | grep biomedical_chatbot | grep -v grep | awk '{print $2}'"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            # Extract PIDs from the output
            killed_count = 0
            if result.stdout:
                for pid in result.stdout.splitlines():
                    if pid.strip():
                        logger.info(f"Killing existing AI Model process (PID: {pid})")
                        try:
                            os.kill(int(pid), signal.SIGKILL)
                            killed_count += 1
                        except Exception as e:
                            logger.error(f"Error killing AI Model process {pid}: {str(e)}")
            
            if killed_count > 0:
                logger.info(f"Killed {killed_count} existing AI Model instances")
                # Give processes time to fully terminate
                time.sleep(2)
    except Exception as e:
        logger.error(f"Error checking for existing AI Model instances: {str(e)}")
    
    # Also check if the port is in use
    if not check_port_available(AI_MODEL_PORT):
        logger.warning(f"AI Model port {AI_MODEL_PORT} is still in use, attempting to kill the process...")
        try:
            # Try to find and kill the process using the port
            if os.name == 'nt':  # Windows
                result = subprocess.run(
                    f'for /f "tokens=5" %p in (\'netstat -ano ^| find ":{AI_MODEL_PORT}" ^| find "LISTENING"\') do taskkill /F /PID %p',
                    shell=True, capture_output=True, text=True
                )
                logger.info(f"Killed existing AI Model process using port {AI_MODEL_PORT}: {result.stdout}")
            else:
                result = subprocess.run(
                    f"lsof -i :{AI_MODEL_PORT} | grep LISTEN | awk '{{print $2}}' | xargs kill -9",
                    shell=True, capture_output=True, text=True
                )
                logger.info(f"Killed existing AI Model process using port {AI_MODEL_PORT}: {result.stdout}")
            
            # Give it a moment to terminate
            time.sleep(2)
        except Exception as e:
            logger.error(f"Error killing existing AI Model process: {str(e)}")
        
    try:
        # Start the AI model directly
        ai_model_dir = os.path.join(PROJECT_ROOT, "AI_MODEL", "biomedical_chatbot")
        app_path = os.path.join(ai_model_dir, "app.py")
        
        logger.debug(f"AI Model directory: {ai_model_dir}")
        logger.debug(f"AI Model app path: {app_path}")
        
        # Verify the directory exists
        if not os.path.exists(ai_model_dir):
            logger.error(f"AI Model directory {ai_model_dir} does not exist")
            return False
            
        if not os.path.exists(app_path):
            logger.error(f"AI Model app file not found at: {app_path}")
            return False
        
        # Start the AI model directly as a subprocess
        logger.info(f"Starting AI Model using Python: {sys.executable}")
        
        ai_model_process = subprocess.Popen(
            [sys.executable, app_path],
            cwd=ai_model_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Give it a moment to start
        time.sleep(2)
        
        logger.info(f"Started AI Model (PID: {ai_model_process.pid})")
        logger.info(f"AI Model should be accessible at http://localhost:{AI_MODEL_PORT}")
        
        # Start output reader for the AI model
        ai_output_queue = queue.Queue()
        ai_thread = threading.Thread(
            target=read_process_output, 
            args=(ai_model_process, ai_output_queue, "AI Model")
        )
        ai_thread.daemon = True
        ai_thread.start()
        
        # Create the lock file with the PID
        try:
            with open(AI_MODEL_LOCK_FILE, 'w') as f:
                f.write(str(ai_model_process.pid))
            logger.info(f"Created AI Model lock file with PID: {ai_model_process.pid}")
        except Exception as e:
            logger.error(f"Error creating AI Model lock file: {str(e)}")
        
        return True
            
    except Exception as e:
        logger.error(f"Error starting AI Model: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return False

def start_portals():
    """Start all portal applications and AI model in separate threads"""
    output_queue = queue.Queue()
    
    # Log the startup
    logger.info("=" * 60)
    logger.info(f"  CliniQAI System Startup - {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 60)
    logger.info(f"Python version: {sys.version}")
    logger.info(f"Current directory: {os.getcwd()}")
    logger.info(f"Project root: {PROJECT_ROOT}")
    
    # Ensure data directories exist
    ensure_data_directories()
    
    # Start all components
    doctor_success = start_doctor_app()
    patient_success = start_patient_app()
    ai_model_success = start_ai_model()
    
    # Start output readers for doctor and patient portals
    if doctor_success and doctor_process:
        doctor_thread = threading.Thread(
            target=read_process_output, 
            args=(doctor_process, output_queue, "Doctor Portal")
        )
        doctor_thread.daemon = True
        doctor_thread.start()
    
    if patient_success and patient_process:
        patient_thread = threading.Thread(
            target=read_process_output, 
            args=(patient_process, output_queue, "Patient Portal")
        )
        patient_thread.daemon = True
        patient_thread.start()
    
    # Print startup message
    logger.info("\n")
    logger.info("==== Healthcare AI System ====")
    logger.info(f"Main dashboard running on: http://localhost:{MAIN_PORT}")
    
    if doctor_success:
        logger.info(f"Doctor portal running on: http://localhost:{DOCTOR_PORT}")
    else:
        logger.warning("Doctor portal failed to start")
        
    if patient_success:
        logger.info(f"Patient portal running on: http://localhost:{PATIENT_PORT}")
    else:
        logger.warning("Patient portal failed to start")
        
    if ai_model_success:
        logger.info(f"AI Model running on: http://localhost:{AI_MODEL_PORT}")
    else:
        logger.warning("AI Model failed to start")
        
    logger.info("===============================\n")
    
    # Start a thread to monitor and log process output
    def monitor_output():
        while True:
            try:
                name, stream_type, line = output_queue.get(timeout=1)
                if stream_type == "stderr":
                    logger.error(f"[{name}] {line}")
                else:
                    logger.debug(f"[{name}] {line}")
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Error in output monitor: {str(e)}")
                break
    
    monitor_thread = threading.Thread(target=monitor_output)
    monitor_thread.daemon = True
    monitor_thread.start()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/doctor-portal')
def doctor_portal():
    # Redirect to the doctor portal application
    return redirect(f'http://localhost:{DOCTOR_PORT}/')

@app.route('/patient-portal')
def patient_portal():
    # Redirect to the patient portal application
    return redirect(f'http://localhost:{PATIENT_PORT}/')

@app.route('/ai-model')
def ai_model():
    # Redirect to the AI model application
    return redirect(f'http://localhost:{AI_MODEL_PORT}/')

def cleanup_processes():
    """Terminate the subprocesses when the main app exits"""
    logger.info("Cleaning up processes...")
    
    # First, try to terminate processes gracefully
    processes = [
        (doctor_process, "Doctor Portal"),
        (patient_process, "Patient Portal"),
        (ai_model_process, "AI Model")
    ]
    
    for process, name in processes:
        if process:
            logger.info(f"Stopping {name} (PID: {process.pid})")
            try:
                process.terminate()
                # Give it some time to terminate gracefully
                try:
                    process.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    logger.warning(f"{name} did not terminate gracefully, forcing kill...")
                    process.kill()
            except Exception as e:
                logger.error(f"Error terminating {name}: {str(e)}")
                try:
                    # Force kill if terminate doesn't work
                    process.kill()
                except:
                    pass
    
    # Special handling for AI Model - find and kill ALL instances that might be running
    # This is necessary because the AI Model might spawn additional processes
    logger.info("Performing specialized AI Model cleanup...")
    try:
        if os.name == 'nt':  # Windows
            # Use more direct approach to find and kill ALL AI Model processes
            cmd = 'wmic process where "name=\'python.exe\' and commandline like \'%biomedical_chatbot%\'" get processid /format:csv'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            # Extract PIDs from the output
            if result.stdout:
                for line in result.stdout.splitlines():
                    if 'ProcessId' not in line and line.strip():
                        try:
                            pid = line.strip().split(',')[-1]
                            if pid:
                                logger.info(f"Killing additional AI Model process (PID: {pid})")
                                subprocess.run(f"taskkill /F /PID {pid}", shell=True)
                        except Exception as e:
                            logger.error(f"Error parsing or killing AI Model process: {str(e)}")
        else:
            # Unix approach
            cmd = "ps aux | grep biomedical_chatbot | grep -v grep | awk '{print $2}'"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            # Extract PIDs from the output
            if result.stdout:
                for pid in result.stdout.splitlines():
                    if pid.strip():
                        logger.info(f"Killing additional AI Model process (PID: {pid})")
                        try:
                            os.kill(int(pid), signal.SIGKILL)
                        except Exception as e:
                            logger.error(f"Error killing AI Model process {pid}: {str(e)}")
    except Exception as e:
        logger.error(f"Error in specialized AI Model cleanup: {str(e)}")
    
    # Check for any remaining processes on the ports we're using
    try:
        for port in [MAIN_PORT, DOCTOR_PORT, PATIENT_PORT, AI_MODEL_PORT]:
            if os.name == 'nt':  # Windows
                cmd = f'for /f "tokens=5" %a in (\'netstat -ano ^| find ":{port}" ^| find "LISTENING"\') do taskkill /F /PID %a'
                subprocess.run(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            else:
                cmd = f"lsof -i :{port} | grep LISTEN | awk '{{print $2}}' | xargs kill -9"
                subprocess.run(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception as e:
        logger.error(f"Error killing remaining processes: {str(e)}")
    
    # Check for Python processes related to this app
    try:
        if os.name == 'nt':  # Windows
            # Kill any remaining Python processes related to the app
            cmd = 'for /f "tokens=2" %p in (\'tasklist /fi "imagename eq python.exe" /fo list ^| find "PID:"\') do (' + \
                  'wmic process where "ProcessID=%p" get CommandLine | find "app-starter\\main.py" > nul && taskkill /F /PID %p & ' + \
                  'wmic process where "ProcessID=%p" get CommandLine | find "AI_MODEL\\biomedical_chatbot" > nul && taskkill /F /PID %p & ' + \
                  'wmic process where "ProcessID=%p" get CommandLine | find "doctor-portal\\app.py" > nul && taskkill /F /PID %p & ' + \
                  'wmic process where "ProcessID=%p" get CommandLine | find "patient-portal\\app.py" > nul && taskkill /F /PID %p)'
            subprocess.run(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception as e:
        logger.error(f"Error in final process cleanup: {str(e)}")
    
    # Remove the AI Model lock file
    try:
        if os.path.exists(AI_MODEL_LOCK_FILE):
            os.remove(AI_MODEL_LOCK_FILE)
            logger.info("Removed AI Model lock file")
    except Exception as e:
        logger.error(f"Error removing AI Model lock file: {str(e)}")
    
    logger.info("All processes have been cleaned up")

def signal_handler(sig, frame):
    """Handle Ctrl+C and other termination signals"""
    logger.info("\nShutting down Healthcare AI System...")
    cleanup_processes()
    sys.exit(0)

if __name__ == '__main__':
    # Register the signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Start the portal applications
    start_portals()
    
    try:
        # Run the main Flask app
        app.run(host='0.0.0.0', port=MAIN_PORT, debug=False)
    except Exception as e:
        logger.error(f"Error in main app: {str(e)}")
    finally:
        # Make sure to clean up processes when the app exits
        cleanup_processes()