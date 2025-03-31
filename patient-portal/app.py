from flask import Flask, request, jsonify, render_template
import os
import csv
import datetime
from pathlib import Path

app = Flask(__name__)

# Configuration
ROOT_DIR = Path(__file__).parent.parent
CSV_FILE = ROOT_DIR / 'adr_reports.csv'
PATIENT_ID_FILE = Path(__file__).parent / 'data' / 'patient_id_counter.txt'

# Initialize patient ID counter
if not os.path.exists(PATIENT_ID_FILE):
    os.makedirs(os.path.dirname(PATIENT_ID_FILE), exist_ok=True)
    with open(PATIENT_ID_FILE, 'w') as f:
        f.write('2000')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/reports', methods=['GET', 'POST'])
def reports():
    if request.method == 'GET':
        reports = []
        if os.path.exists(CSV_FILE):
            with open(CSV_FILE, 'r', newline='', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    reports.append(row)
        reports.reverse()
        return jsonify({'reports': reports})

    if request.method == 'POST':
        data = request.get_json()
        try:
            with open(PATIENT_ID_FILE, 'r') as f:
                patient_id_counter = int(f.read().strip())
            patient_id = f"PTD_{patient_id_counter}"

            with open(PATIENT_ID_FILE, 'w') as f:
                f.write(str(patient_id_counter + 1))

            timestamp = datetime.datetime.now().strftime("%d-%m-%Y %H:%M")
            row_data = {
                'timestamp': timestamp,
                'drug_name': data.get('drug_name', '').strip().title(),
                'medical_condition': data.get('medical_condition', ''),
                'adverse_reaction': data.get('adverse_reaction', ''),
                'severity': data.get('severity', ''),
                'confidence': '0',
                'cause_of_administration': data.get('cause_of_administration', ''),
                'gender': data.get('gender', ''),
                'patient_id': patient_id,
                'current_medication': data.get('current_medication', 'Not specified')
            }

            file_exists = os.path.isfile(CSV_FILE) and os.path.getsize(CSV_FILE) > 0

            with open(CSV_FILE, 'a', newline='', encoding='utf-8') as file:
                writer = csv.DictWriter(file, fieldnames=row_data.keys())
                if not file_exists:
                    writer.writeheader()
                writer.writerow(row_data)

            return jsonify({'success': True, 'patient_id': patient_id})

        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(port=8083, debug=True)