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
    
    if not check_port_available(AI_MODEL_PORT):
        logger.warning(f"AI Model already running on port {AI_MODEL_PORT}")
        return True
        
    try:
        # Use the direct start script path instead
        ai_model_dir = os.path.join(PROJECT_ROOT, "AI_MODEL", "biomedical_chatbot")
        direct_start_path = os.path.join(ai_model_dir, "direct_start.py")
        
        logger.debug(f"AI Model directory: {ai_model_dir}")
        logger.debug(f"Direct start script: {direct_start_path}")
        
        # Verify the directory exists
        if not os.path.exists(ai_model_dir):
            logger.error(f"AI Model directory {ai_model_dir} does not exist")
            return False
        
        # Create the direct_start.py file if it doesn't exist yet
        if not os.path.exists(direct_start_path):
            logger.info("Creating direct start script...")
            with open(direct_start_path, 'w') as f:
                f.write('''import subprocess
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
''')
            logger.info("Direct start script created successfully")
            
        # List the contents of the biomedical_chatbot directory for debugging
        logger.debug("Contents of AI Model directory:")
        try:
            for item in os.listdir(ai_model_dir):
                logger.debug(f"  - {item}")
        except Exception as e:
            logger.error(f"Error listing directory: {str(e)}")
            
        try:
            logger.info(f"Attempting to start AI Model using Python: {sys.executable}")
            
            # Start the direct_start.py script
            if os.name == 'nt':  # Windows
                # On Windows, use 'start' command to open in a new window
                ai_model_process = subprocess.Popen(
                    f'start cmd /c "cd {ai_model_dir} && {sys.executable} direct_start.py"',
                    shell=True
                )
            else:  # Linux/Mac
                # Use gnome-terminal or open a new terminal window
                try:
                    ai_model_process = subprocess.Popen(
                        ["gnome-terminal", "--", sys.executable, direct_start_path],
                        cwd=ai_model_dir
                    )
                except FileNotFoundError:
                    # Fallback to regular subprocess if gnome-terminal is not available
                    ai_model_process = subprocess.Popen(
                        [sys.executable, direct_start_path],
                        cwd=ai_model_dir
                    )
            
            # Give it a moment to start
            time.sleep(2)
            
            logger.info(f"Started AI Model launcher")
            logger.info(f"AI Model should be accessible at http://localhost:{AI_MODEL_PORT}")
            return True
            
        except Exception as e:
            logger.error(f"Error starting AI Model: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return False
    except Exception as e:
        logger.error(f"Error in AI Model startup: {str(e)}")
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
    
    if doctor_process:
        logger.info(f"Stopping Doctor Portal (PID: {doctor_process.pid})")
        try:
            doctor_process.terminate()
        except Exception as e:
            logger.error(f"Error terminating Doctor Portal: {str(e)}")
    
    if patient_process:
        logger.info(f"Stopping Patient Portal (PID: {patient_process.pid})")
        try:
            patient_process.terminate()
        except Exception as e:
            logger.error(f"Error terminating Patient Portal: {str(e)}")
        
    if ai_model_process:
        logger.info(f"Stopping AI Model (PID: {ai_model_process.pid})")
        try:
            ai_model_process.terminate()
        except Exception as e:
            logger.error(f"Error terminating AI Model: {str(e)}")
    
    logger.info("Cleanup completed")

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