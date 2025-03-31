import http.server
import socketserver
import os
import webbrowser
import json
import csv
import time
from pathlib import Path
from urllib.parse import urlparse, parse_qs

# Configuration
PORT = 8085
DIRECTORY = "templates"
DATA_FILE = "../adr_reports.csv"  # Path to main directory

# Validate and resolve the DATA_FILE path
try:
    data_file_path = os.path.abspath(DATA_FILE)
    print(f"Absolute data file path: {data_file_path}")
    data_dir = os.path.dirname(data_file_path)
    if not os.path.exists(data_dir):
        print(f"Warning: Data directory does not exist: {data_dir}")
        print("Will create directory when needed")
except Exception as e:
    print(f"Error resolving data file path: {e}")

# Cache variables
csv_cache = {
    'data': [],
    'last_modified': 0,
    'unique_drugs': [],
    'unique_conditions': []
}

# Make sure the directory exists
dir_path = Path(DIRECTORY)
if not dir_path.exists():
    print(f"Creating directory {DIRECTORY}...")
    os.makedirs(dir_path, exist_ok=True)

# Preload the data cache at startup
def preload_data_cache():
    try:
        print("Preloading data cache...")
        get_cached_data()
        print("Data cache preloaded successfully")
    except Exception as e:
        print(f"Error preloading data cache: {str(e)}")

# Function to refresh cache if needed
def get_cached_data():
    global csv_cache
    
    try:
        # If file doesn't exist, initialize empty cache
        if not os.path.exists(DATA_FILE):
            print("Data file does not exist, returning empty data set")
            return {'data': [], 'unique_drugs': [], 'unique_conditions': []}
            
        # Check if file has been modified since last cache
        try:
            file_modified_time = os.path.getmtime(DATA_FILE)
        except Exception as e:
            print(f"Error getting file modification time: {str(e)}")
            return csv_cache  # Return existing cache on error
        
        # If file modified time is newer than our cached version, refresh the cache
        if file_modified_time > csv_cache['last_modified']:
            print("Refreshing CSV cache...")
            
            csv_data = []
            unique_drugs = set()
            unique_conditions = set()
            
            try:
                # Print the full resolved path for debugging
                full_path = os.path.abspath(DATA_FILE)
                print(f"Loading data from: {full_path}")
                
                with open(DATA_FILE, 'r', newline='', encoding='utf-8') as file:
                    reader = csv.DictReader(file)
                    for row in reader:
                        # Skip empty rows
                        if not any(row.values()):
                            continue
                            
                        csv_data.append(row)
                        
                        # Build unique sets for dropdown options
                        drug = row.get('drug_name', '').strip()
                        if drug:
                            unique_drugs.add(drug)
                            
                        condition = row.get('medical_condition', '').strip()
                        if condition and condition.lower() != 'n/a' and condition.lower() != 'none':
                            unique_conditions.add(condition)
                
                # Update cache
                csv_cache = {
                    'data': csv_data,
                    'last_modified': file_modified_time,
                    'unique_drugs': sorted(list(unique_drugs)),
                    'unique_conditions': sorted(list(unique_conditions))
                }
                print(f"Cache refreshed. Found {len(csv_data)} records, {len(unique_drugs)} unique drugs, {len(unique_conditions)} unique conditions")
                
                # Print the first few records for debugging
                if csv_data:
                    print("Sample data (first record):")
                    for key, value in csv_data[0].items():
                        print(f"  {key}: {value}")
                else:
                    print("WARNING: No data was loaded from the CSV file")
            except Exception as e:
                print(f"Error reading CSV file: {str(e)}")
                # Continue with old cache if available, or return empty if not
                if not csv_cache['data']:
                    return {'data': [], 'unique_drugs': [], 'unique_conditions': []}
        else:
            print("Cache is current, no refresh needed")
            
        return csv_cache
    except Exception as e:
        print(f"Unexpected error refreshing cache: {str(e)}")
        return {'data': [], 'unique_drugs': [], 'unique_conditions': []}

# Enhanced HTTP server that can handle API requests
class DoctorPortalHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)
    
    def do_GET(self):
        # Parse URL query parameters
        url_parts = urlparse(self.path)
        
        # API endpoint to search for drug-condition combinations
        if url_parts.path == '/api/search':
            query_params = parse_qs(url_parts.query)
            drug_name = query_params.get('drug', [''])[0].lower().strip()
            medical_condition = query_params.get('condition', [''])[0].lower().strip()
            current_medication = query_params.get('current_medication', [''])[0].lower().strip()
            
            print(f"Search request received - Drug: '{drug_name}', Condition: '{medical_condition}', Medication: '{current_medication}'")
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            # Validate input
            if not drug_name and not medical_condition:
                print("Search rejected: Missing required parameters")
                self.wfile.write(json.dumps({
                    'success': False,
                    'message': 'Either drug name or symptoms are required for search',
                    'results': []
                }).encode())
                return
            
            # Get cached data
            cached_data = get_cached_data()
            
            if not cached_data['data']:
                print("Search returned no results: No data available in cache")
                self.wfile.write(json.dumps({
                    'success': True,
                    'message': 'No data available for search',
                    'count': 0,
                    'results': []
                }).encode())
                return
            
            # Search for matching records
            results = []
            total_drug_count = 0
            
            print("Debug: Starting search with parameters:")
            print(f"  - Drug: '{drug_name}'")
            print(f"  - Condition: '{medical_condition}'")
            print(f"  - Medication: '{current_medication}'")
            print(f"  - Total records to search: {len(cached_data['data'])}")
            
            for idx, row in enumerate(cached_data['data']):
                row_drug = row.get('drug_name', '').lower().strip()
                row_symptoms = row.get('medical_condition', '').lower().strip()
                row_medication = row.get('current_medication', '').lower().strip()
                
                print(f"\nDebug - Record #{idx+1}:")
                print(f"  Drug: '{row_drug}'")
                print(f"  Symptoms: '{row_symptoms}'")
                print(f"  Medication: '{row_medication}'")
                
                # Count total occurrences of the drug if drug name was provided
                drug_match = True
                if drug_name:
                    if row_drug == drug_name:
                        total_drug_count += 1
                    else:
                        drug_match = False
                
                # Skip this record if drug doesn't match
                if not drug_match:
                    continue
                    
                # Check for partial symptoms match in comma-separated list
                symptoms_match = True
                if medical_condition:
                    # Reset to false when a condition is provided and needs to be matched
                    symptoms_match = False
                    
                    # Convert to lowercase for comparison
                    row_symptoms_lower = row_symptoms.lower()
                    medical_condition_lower = medical_condition.lower()
                    
                    print(f"Comparing '{medical_condition_lower}' with '{row_symptoms_lower}'")
                    
                    # Skip empty or placeholder conditions
                    if row_symptoms_lower in ['none', 'n/a', 'not specified', 'not applicable', '']:
                        print(f"Skipping placeholder value: '{row_symptoms}'")
                        continue
                    
                    # Simplest matching logic: direct substring match
                    if medical_condition_lower in row_symptoms_lower:
                        symptoms_match = True
                        print(f"MATCHED (condition in symptoms): '{medical_condition_lower}' is in '{row_symptoms_lower}'")
                    elif row_symptoms_lower in medical_condition_lower:
                        symptoms_match = True
                        print(f"MATCHED (symptoms in condition): '{row_symptoms_lower}' is in '{medical_condition_lower}'")
                    
                    # If no direct match, try matching individual words if there are multiple conditions
                    if not symptoms_match and ',' in row_symptoms:
                        conditions = [c.strip().lower() for c in row_symptoms.split(',')]
                        for condition in conditions:
                            if medical_condition_lower in condition or condition in medical_condition_lower:
                                symptoms_match = True
                                print(f"MATCHED (in list): '{medical_condition_lower}' matches with '{condition}'")
                                break
                
                # Check medication match if current_medication is provided
                medication_match = True
                if current_medication:
                    medication_match = False
                    if ',' in row_medication:
                        row_medication_list = [m.strip() for m in row_medication.split(',')]
                        medication_match = any(current_medication in m or m in current_medication for m in row_medication_list)
                    else:
                        medication_match = current_medication in row_medication or row_medication in current_medication
                
                # Add to results if all criteria match
                if drug_match and symptoms_match and medication_match:
                    results.append({
                        'timestamp': row.get('timestamp', ''),
                        'drug_name': row.get('drug_name', ''),
                        'medical_condition': row.get('medical_condition', ''),
                        'adverse_reaction': row.get('adverse_reaction', ''),
                        'severity': row.get('severity', ''),
                        'confidence': row.get('confidence', '0.0'),
                        'cause_of_administration': row.get('cause_of_administration', 'Not specified'),
                        'gender': row.get('gender', 'Not specified'),
                        'patient_id': row.get('patient_id', 'Not assigned'),
                        'current_medication': row.get('current_medication', 'Not specified')
                    })
            
            # Calculate percentage of matching results
            match_percentage = 0
            if total_drug_count > 0:
                match_percentage = round((len(results) * 100) / total_drug_count, 2)
            
            print(f"Search completed: Found {len(results)} matches out of {total_drug_count} drug instances ({match_percentage}%)")
            
            response = {
                'success': True,
                'count': len(results),
                'total_drug_count': total_drug_count,
                'match_percentage': match_percentage,
                'results': results
            }
            
            if len(results) == 0:
                response['message'] = 'No matching records found for this drug, symptoms, and medication combination.'
            
            self.wfile.write(json.dumps(response).encode())
            return
        
        # API endpoint to get all unique drug names
        elif self.path == '/api/drugs':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            cached_data = get_cached_data()
            
            self.wfile.write(json.dumps({
                'success': True,
                'drugs': cached_data['unique_drugs']
            }).encode())
            return
        
        # API endpoint to get all unique medical conditions
        elif self.path == '/api/conditions':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            cached_data = get_cached_data()
            
            self.wfile.write(json.dumps({
                'success': True,
                'conditions': cached_data['unique_conditions']
            }).encode())
            return
        
        # Default to serving static files
        return super().do_GET()
    
    def end_headers(self):
        # Add CORS headers to all responses
        try:
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        except Exception as e:
            print(f"Error adding CORS headers: {str(e)}")
        # Call parent implementation to finish sending headers
        super().end_headers()
    
    def do_OPTIONS(self):
        # Handle CORS preflight requests
        try:
            self.send_response(200)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.end_headers()
            print("OPTIONS request handled (CORS preflight)")
        except Exception as e:
            print(f"Error handling OPTIONS request: {str(e)}")
            self.send_response(500)
            self.end_headers()

print(f"Starting Doctor Portal server at http://localhost:{PORT}")
print(f"Serving files from {os.path.abspath(DIRECTORY)}")
print(f"Reading data from {os.path.abspath(DATA_FILE)}")
print("Press Ctrl+C to stop the server")

# Open browser
webbrowser.open(f"http://localhost:{PORT}")

# Preload the data cache before starting the server
preload_data_cache()

# Start server
with socketserver.TCPServer(("", PORT), DoctorPortalHandler) as httpd:
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.") 