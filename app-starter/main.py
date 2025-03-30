from flask import Flask, render_template, redirect
import subprocess
import os
import threading
import time
import signal
import sys
import socket

app = Flask(__name__)

# Paths to the other Flask applications - Updated to use absolute paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
DOCTOR_APP_PATH = os.path.join(PROJECT_ROOT, "doctor-portal", "app.py")
PATIENT_APP_PATH = os.path.join(PROJECT_ROOT, "patient-portal", "app.py")
AI_MODEL_PATH = r"C:\Users\divya\OneDrive\Desktop\CRYPTIC_HUNTERS\AI_MODEL\biomedical_chatbot\app.py"
AI_MODEL_PORT = 8084

# Process objects to keep track of the subprocesses
doctor_process = None
patient_process = None
ai_model_process = None

def start_doctor_app():
    """Start the doctor portal Flask app"""
    global doctor_process
    doctor_dir = os.path.dirname(DOCTOR_APP_PATH)
    doctor_process = subprocess.Popen(
        [sys.executable, DOCTOR_APP_PATH],
        cwd=doctor_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    print(f"Started Doctor Portal (PID: {doctor_process.pid})")

def start_patient_app():
    """Start the patient portal Flask app"""
    global patient_process
    patient_dir = os.path.dirname(PATIENT_APP_PATH)
    patient_process = subprocess.Popen(
        [sys.executable, PATIENT_APP_PATH],
        cwd=patient_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    print(f"Started Patient Portal (PID: {patient_process.pid})")

def start_ai_model():
    """Start the AI model Flask app"""
    global ai_model_process
    
    # Check if the AI model is already running on port 8084
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('127.0.0.1', AI_MODEL_PORT))
    if result == 0:
        print(f"AI Model already running on port {AI_MODEL_PORT}")
        sock.close()
        return
    sock.close()
    
    ai_model_dir = os.path.dirname(AI_MODEL_PATH)
    ai_model_process = subprocess.Popen(
        [sys.executable, AI_MODEL_PATH],
        cwd=ai_model_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        # Use creationflags on Windows to prevent new console window
        creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
    )
    print(f"Started AI Model (PID: {ai_model_process.pid})")

def start_portals():
    """Start both portal applications and AI model in separate threads"""
    doctor_thread = threading.Thread(target=start_doctor_app)
    patient_thread = threading.Thread(target=start_patient_app)
    ai_model_thread = threading.Thread(target=start_ai_model)
    
    doctor_thread.daemon = True
    patient_thread.daemon = True
    ai_model_thread.daemon = True
    
    doctor_thread.start()
    patient_thread.start()
    ai_model_thread.start()
    
    # Give the apps a moment to start
    time.sleep(2)
    
    # Print startup message
    print("\n==== Healthcare AI System ====")
    print("Main dashboard running on: http://localhost:8080")
    print("Doctor portal running on: http://localhost:8082")
    print("Patient portal running on: http://localhost:8083")
    print(f"AI Model running on: http://localhost:{AI_MODEL_PORT}")
    print("===============================\n")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/doctor-portal')
def doctor_portal():
    # Redirect to the doctor portal application
    return redirect('http://localhost:8082/')

@app.route('/patient-portal')
def patient_portal():
    # Redirect to the patient portal application
    return redirect('http://localhost:8083/')

@app.route('/ai-model')
def ai_model():
    # Redirect to the AI model application
    return redirect(f'http://localhost:{AI_MODEL_PORT}/')

def cleanup_processes():
    """Terminate the subprocesses when the main app exits"""
    if doctor_process:
        print(f"Stopping Doctor Portal (PID: {doctor_process.pid})")
        doctor_process.terminate()
    
    if patient_process:
        print(f"Stopping Patient Portal (PID: {patient_process.pid})")
        patient_process.terminate()
        
    if ai_model_process:
        print(f"Stopping AI Model (PID: {ai_model_process.pid})")
        ai_model_process.terminate()

def signal_handler(sig, frame):
    """Handle Ctrl+C and other termination signals"""
    print("\nShutting down Healthcare AI System...")
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
        app.run(host='0.0.0.0', port=8080, debug=False)
    finally:
        # Make sure to clean up processes when the app exits
        cleanup_processes()