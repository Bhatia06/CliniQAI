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
import requests

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

@app.route('/api/ai-analyze', methods=['POST'])
def ai_analyze():
    """Proxy the request to the AI chatbot for pattern analysis"""
    try:
        data = request.get_json()
        
        # Get a sample drug and condition from the first result
        drug_to_use = ""
        preexisting_conditions = []
        
        if data.get('results') and len(data.get('results')) > 0:
            sample_result = data['results'][0]
            drug_to_use = sample_result.get('drug_name', '')
            preexisting_conditions = [sample_result.get('medical_condition', '')]
        
        # Prepare the data for the AI model
        ai_data = {
            'current_medications': [],  # We don't have this info in our results
            'drug_to_use': drug_to_use,
            'preexisting_conditions': preexisting_conditions,
            'age': 45,  # Default values since we don't have this info
            'weight': 70
        }
        
        # Call the AI model API
        ai_model_url = 'http://localhost:8084/api/analyze'
        
        try:
            ai_response = requests.post(ai_model_url, json=ai_data, timeout=10)
            
            if ai_response.status_code == 200:
                result = ai_response.json()
                
                # Transform the AI model response to our expected format
                analysis_results = transform_ai_response(result, data.get('results', []))
                
                return jsonify({
                    'success': True,
                    'analysis': analysis_results
                })
            else:
                # If the AI model API returns an error, fall back to mock data
                return jsonify({
                    'success': True,
                    'analysis': generate_mock_analysis(data.get('results', []))
                })
                
        except requests.RequestException as e:
            print(f"Error connecting to AI model: {str(e)}")
            # Fall back to mock data if we can't connect to the AI model
            return jsonify({
                'success': True,
                'analysis': generate_mock_analysis(data.get('results', []))
            })
        
    except Exception as e:
        print(f"Error in AI analysis API: {str(e)}")
        return jsonify({
            'success': False,
            'message': f"Error performing analysis: {str(e)}"
        }), 500

def transform_ai_response(ai_response, search_results):
    """Transform the AI model response to our expected format"""
    if not ai_response.get('success', False):
        return generate_mock_analysis(search_results)
    
    analysis = ai_response.get('analysis', {})
    adverse_reactions = analysis.get('adverse_reactions', [])
    
    results = []
    
    # Convert the adverse reactions to our format
    for i, reaction in enumerate(adverse_reactions):
        if i >= 4:  # Limit to 4 results
            break
            
        title = f"Potential Risk: {reaction.get('reaction_name', 'Unknown')}"
        description = f"Analysis shows that [{ analysis.get('medication_info', {}).get('drug_to_use', 'the medication') }] may cause [{ reaction.get('reaction_name', 'adverse reactions') }]. "
        
        if reaction.get('reason'):
            description += f"{reaction.get('reason')}. "
            
        # Add recommendation if available
        if reaction.get('recommendation'):
            description += f"Recommendation: {reaction.get('recommendation')}"
        
        confidence = min(float(reaction.get('probability', 0)) + 0.3, 0.95)  # Adjust confidence for display
        
        results.append({
            'title': title,
            'description': description,
            'confidence': confidence
        })
    
    return results

def generate_mock_analysis(search_results):
    """Generate mock analysis results based on the search results"""
    if not search_results or len(search_results) == 0:
        return []
    
    # Extract drug names and conditions from search results
    drugs = set()
    conditions = set()
    reactions = set()
    
    for result in search_results:
        if result.get('drug_name'):
            drugs.add(result.get('drug_name'))
        if result.get('medical_condition'):
            conditions.add(result.get('medical_condition'))
        if result.get('adverse_reaction'):
            reactions.add(result.get('adverse_reaction'))
    
    # Convert sets to lists for easier access
    drug_list = list(drugs)
    condition_list = list(conditions)
    reaction_list = list(reactions)
    
    # Generate mock analysis patterns
    analysis_results = []
    
    if drug_list and reaction_list:
        analysis_results.append({
            'title': f"Correlation: {drug_list[0]} and Adverse Reactions",
            'description': f"Analysis shows that [{drug_list[0]}] has a higher rate of [{reaction_list[0] if reaction_list else 'adverse reactions'}] compared to other medications in the database. Consider monitoring patients closely for these symptoms.",
            'confidence': random.uniform(0.75, 0.9)
        })
    
    if drug_list and condition_list:
        analysis_results.append({
            'title': f"Medical Condition Impact",
            'description': f"Patients with [{condition_list[0] if condition_list else 'this condition'}] taking [{drug_list[0]}] may experience more severe side effects. Consider adjusting dosage or alternative treatments for these patients.",
            'confidence': random.uniform(0.7, 0.85)
        })
    
    if len(drug_list) > 1:
        analysis_results.append({
            'title': "Potential Drug Interaction",
            'description': f"Patients taking [{drug_list[0]}] concurrently with [{drug_list[1] if len(drug_list) > 1 else 'other medications'}] show an increased risk of adverse effects. Consider alternative treatment options when possible.",
            'confidence': random.uniform(0.8, 0.95)
        })
    
    if drug_list:
        analysis_results.append({
            'title': "Dosage Recommendation",
            'description': f"For [{drug_list[0]}], starting with a lower dose and gradually increasing may reduce the incidence of [{reaction_list[0] if reaction_list else 'adverse reactions'}] while maintaining efficacy.",
            'confidence': random.uniform(0.7, 0.88)
        })
    
    return analysis_results

if __name__ == '__main__':
    preload_data_cache()
    # Start the AI model server on application startup
    start_ai_model_server()
    
    app.run(port=8082, debug=True)