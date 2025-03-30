from flask import Flask, request, jsonify, render_template
import os
import csv
import datetime
import json

app = Flask(__name__)

# Configuration
CSV_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "adr_reports.csv")
PATIENT_ID_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "patient_id_counter.txt")

# Initialize patient ID counter
if not os.path.exists(PATIENT_ID_FILE):
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
            row_data = [
                timestamp,
                data.get('drug_name', ''),
                data.get('medical_condition', ''),
                data.get('adverse_reaction', ''),
                data.get('severity', ''),
                '0',  # confidence
                data.get('cause_of_administration', ''),
                data.get('gender', ''),
                patient_id,
                data.get('current_medication', 'Not specified')
            ]

            file_exists = os.path.isfile(CSV_FILE) and os.path.getsize(CSV_FILE) > 0

            with open(CSV_FILE, 'a', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                if not file_exists:
                    writer.writerow(['timestamp', 'drug_name', 'medical_condition', 'adverse_reaction', 'severity', 
                                     'confidence', 'cause_of_administration', 'gender', 'patient_id', 'current_medication'])
                writer.writerow(row_data)

            return jsonify({'success': True, 'patient_id': patient_id})

        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(port=8083, debug=True)