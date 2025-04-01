from flask import Flask, jsonify, render_template, request
import os
import csv
import subprocess
from pathlib import Path
import sys
import socket
import time
import datetime
import json
import random

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
    'unique_conditions': [],
    'unique_reactions': []
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
                'unique_conditions': [],
                'unique_reactions': []
            })
            return csv_cache
            
        if file_modified_time > csv_cache['last_modified']:
            csv_data = []
            unique_drugs = set()
            unique_conditions = set()
            unique_reactions = set()
            
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
                    reaction = row.get('adverse_reaction', '').strip()
                    if reaction and reaction.lower() != 'n/a' and reaction.lower() != 'not reported':
                        unique_reactions.add(reaction)
            
            csv_cache.update({
                'data': csv_data,
                'last_modified': file_modified_time,
                'unique_drugs': sorted(list(unique_drugs)),
                'unique_conditions': sorted(list(unique_conditions)),
                'unique_reactions': sorted(list(unique_reactions))
            })
            
        return csv_cache
    except Exception as e:
        print(f"Error refreshing cache: {str(e)}")
        return {'data': [], 'unique_drugs': [], 'unique_conditions': [], 'unique_reactions': []}

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

@app.route('/api/search', methods=['POST'])
def search():
    try:
        data = request.get_json()
        drug_name = data.get('drug_name', '').lower().strip()
        adverse_reaction = data.get('adverse_reaction', '').lower().strip()
        medical_condition = data.get('medical_condition', '').lower().strip()
        date_range = data.get('date_range', 'all')
        
        cached_data = get_cached_data()
        results = []
        
        for row in cached_data['data']:
            row_drug = row.get('drug_name', '').lower().strip()
            row_reaction = row.get('adverse_reaction', '').lower().strip()
            row_condition = row.get('medical_condition', '').lower().strip()
            row_date = row.get('timestamp', '')
            
            # Filter by criteria
            if drug_name and drug_name not in row_drug:
                continue
            if adverse_reaction and adverse_reaction not in row_reaction:
                continue
            if medical_condition and medical_condition not in row_condition:
                continue
            
            # Filter by date range
            if date_range != 'all':
                try:
                    report_date = datetime.datetime.strptime(row_date, "%d-%m-%Y %H:%M")
                    current_date = datetime.datetime.now()
                    
                    if date_range == '1month' and (current_date - report_date).days > 30:
                        continue
                    elif date_range == '3months' and (current_date - report_date).days > 90:
                        continue
                    elif date_range == '6months' and (current_date - report_date).days > 180:
                        continue
                    elif date_range == '1year' and (current_date - report_date).days > 365:
                        continue
                except:
                    # If date parsing fails, include the record anyway
                    pass
            
            # Add matching result
            results.append({
                'id': row.get('patient_id', f"P{random.randint(10000, 99999)}"),
                'drug_name': row.get('drug_name', ''),
                'adverse_reaction': row.get('adverse_reaction', ''),
                'medical_condition': row.get('medical_condition', ''),
                'severity': row.get('severity', 'Unknown'),
                'date': row.get('timestamp', ''),
                'gender': row.get('gender', ''),
                'current_medication': row.get('current_medication', '')
            })
        
        return jsonify({
            'success': True,
            'count': len(results),
            'results': results
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e),
            'results': []
        }), 500

@app.route('/api/analyze', methods=['POST'])
def analyze():
    """Perform AI analysis on the search results"""
    try:
        # In a real application, this would call the AI model
        # Here we'll just return a successful response with placeholder data
        
        return jsonify({
            'success': True,
            'message': 'Analysis completed successfully',
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/api/drugs', methods=['GET'])
def get_drugs():
    cached_data = get_cached_data()
    return jsonify({
        'success': True,
        'drugs': cached_data['unique_drugs']
    })

@app.route('/api/reactions', methods=['GET'])
def get_reactions():
    cached_data = get_cached_data()
    return jsonify({
        'success': True,
        'reactions': cached_data['unique_reactions']
    })

@app.route('/api/conditions', methods=['GET'])
def get_conditions():
    cached_data = get_cached_data()
    return jsonify({
        'success': True,
        'conditions': cached_data['unique_conditions']
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

if __name__ == '__main__':
    preload_data_cache()
    # Start the AI model server on application startup
    start_ai_model_server()
    
    app.run(port=8082, debug=True)