from flask import Flask, jsonify, render_template, request
import os
import csv
import subprocess
from pathlib import Path
import sys
import socket
import time
import datetime

app = Flask(__name__)

# Configuration
ROOT_DIR = Path(__file__).parent.parent
DATA_FILE = ROOT_DIR / 'adr_reports.csv'
AI_MODEL_PATH = ROOT_DIR / 'AI_MODEL' / 'biomedical_chatbot' / 'app.py'
AI_MODEL_PORT = 8084

# Cache variables
csv_cache = {
    'data': [],
    'last_modified': 0,
    'unique_drugs': [],
    'unique_conditions': []
}

# Preload the data cache at startup
def preload_data_cache():
    get_cached_data()

def start_ai_model_server():
    try:
        # Check if the AI model has already been started by run.bat
        if os.environ.get('CLINIQA_AI_STARTED') == '1':
            print("AI Model is being started by run.bat, skipping startup in doctor portal")
            return
            
        # Check if the AI model is already running on port 8084
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('127.0.0.1', AI_MODEL_PORT))
        if result == 0:
            print(f"AI Model already running on port {AI_MODEL_PORT}")
            sock.close()
            return
        sock.close()
        
        # Start the AI model - it will handle its own process management
        subprocess.Popen(
            [sys.executable, AI_MODEL_PATH], 
            cwd=os.path.dirname(AI_MODEL_PATH),
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
        )
        print(f"AI model server started on port {AI_MODEL_PORT}")
    except Exception as e:
        print(f"Error starting AI model server: {str(e)}")

def get_cached_data():
    global csv_cache
    
    try:
        file_modified_time = os.path.getmtime(DATA_FILE) if os.path.exists(DATA_FILE) else 0
        
        if not os.path.exists(DATA_FILE):
            csv_cache.update({
                'data': [],
                'last_modified': 0,
                'unique_drugs': [],
                'unique_conditions': []
            })
            return csv_cache
            
        if file_modified_time > csv_cache['last_modified']:
            csv_data = []
            unique_drugs = set()
            unique_conditions = set()
            
            with open(DATA_FILE, 'r', newline='', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    csv_data.append(row)
                    drug = row.get('drug_name', '').strip()
                    if drug:
                        unique_drugs.add(drug)
                    condition = row.get('medical_condition', '').strip()
                    if condition and condition.lower() != 'n/a':
                        unique_conditions.add(condition)
            
            csv_cache.update({
                'data': csv_data,
                'last_modified': file_modified_time,
                'unique_drugs': sorted(list(unique_drugs)),
                'unique_conditions': sorted(list(unique_conditions))
            })
            
        return csv_cache
    except Exception as e:
        print(f"Error refreshing cache: {str(e)}")
        return {'data': [], 'unique_drugs': [], 'unique_conditions': []}

def add_new_drug_report(drug_name, medical_condition, adverse_reaction, severity, cause, gender, current_medication):
    """Add a new drug report to the CSV file"""
    try:
        # Generate a unique patient ID
        patient_id = f"DOC_{int(time.time())}"
        timestamp = datetime.datetime.now().strftime("%d-%m-%Y %H:%M")
        
        new_row = {
            'timestamp': timestamp,
            'drug_name': drug_name.strip().title(),
            'medical_condition': medical_condition,
            'adverse_reaction': adverse_reaction,
            'severity': severity,
            'confidence': '0',
            'cause_of_administration': cause,
            'gender': gender,
            'patient_id': patient_id,
            'current_medication': current_medication or 'Not specified'
        }
        
        # Append to the CSV file
        with open(DATA_FILE, 'a', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=new_row.keys())
            if os.path.getsize(DATA_FILE) == 0:
                writer.writeheader()
            writer.writerow(new_row)
        
        # Update the cache
        cached_data = get_cached_data()
        cached_data['data'].append(new_row)
        if drug_name not in cached_data['unique_drugs']:
            cached_data['unique_drugs'].append(drug_name)
            cached_data['unique_drugs'].sort()
        
        return True
    except Exception as e:
        print(f"Error adding drug report: {str(e)}")
        return False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/search', methods=['GET'])
def search():
    drug_name = request.args.get('drug', '').lower().strip()
    medical_condition = request.args.get('condition', '').lower().strip()
    current_medication = request.args.get('current_medication', '').lower().strip()
    
    if not drug_name or not medical_condition:
        return jsonify({
            'success': False,
            'message': 'Both drug name and symptoms are required',
            'results': [],
            'show_ai_option': False
        })
    
    cached_data = get_cached_data()
    results = []
    total_drug_count = 0
    
    # Check if this is a new drug
    drug_in_list = False
    drug_name_titled = drug_name.title()
    for existing_drug in cached_data['unique_drugs']:
        if existing_drug.lower() == drug_name:
            drug_in_list = True
            drug_name_titled = existing_drug  # Use existing capitalization
            break
    
    for row in cached_data['data']:
        row_drug = row.get('drug_name', '').lower().strip()
        row_symptoms = row.get('medical_condition', '').lower().strip()
        row_medication = row.get('current_medication', '').lower().strip()
        
        if row_drug == drug_name:
            total_drug_count += 1
            symptoms_match = medical_condition in row_symptoms or row_symptoms in medical_condition
            medication_match = current_medication in row_medication or row_medication in current_medication
            
            if symptoms_match and medication_match:
                results.append(row)
    
    match_percentage = round((len(results) * 100) / total_drug_count, 2) if total_drug_count > 0 else 0
    show_ai_option = len(results) == 0
    
    response = {
        'success': True,
        'count': len(results),
        'total_drug_count': total_drug_count,
        'match_percentage': match_percentage,
        'results': results,
        'show_ai_option': show_ai_option,
        'ai_model_url': f'http://localhost:{AI_MODEL_PORT}' if show_ai_option else '',
        'drug_is_new': not drug_in_list
    }
    
    if len(results) == 0:
        response['message'] = 'No matching records found for this drug, symptoms, and medication combination.'
    
    return jsonify(response)

@app.route('/api/drugs', methods=['GET'])
def get_drugs():
    cached_data = get_cached_data()
    return jsonify({
        'success': True,
        'drugs': cached_data['unique_drugs']
    })

@app.route('/api/drugs/add', methods=['POST'])
def add_drug():
    """Add a new drug report"""
    try:
        data = request.get_json()
        drug_name = data.get('drug_name', '').strip()
        medical_condition = data.get('medical_condition', 'Not specified').strip()
        adverse_reaction = data.get('adverse_reaction', 'Not reported').strip()
        severity = data.get('severity', 'Mild').strip()
        cause = data.get('cause', 'Not specified').strip()
        gender = data.get('gender', 'Not specified').strip()
        current_medication = data.get('current_medication', '').strip()
        
        if not drug_name:
            return jsonify({
                'success': False,
                'message': 'Drug name is required'
            }), 400
        
        success = add_new_drug_report(
            drug_name, 
            medical_condition, 
            adverse_reaction, 
            severity, 
            cause, 
            gender, 
            current_medication
        )
        
        return jsonify({
            'success': success,
            'message': 'Drug report added successfully' if success else 'Failed to add drug report'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/api/conditions', methods=['GET'])
def get_conditions():
    cached_data = get_cached_data()
    return jsonify({
        'success': True,
        'conditions': cached_data['unique_conditions']
    })

if __name__ == '__main__':
    preload_data_cache()
    # Start the AI model server on application startup
    start_ai_model_server()
    
    app.run(port=8082)