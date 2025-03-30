import http.server
import socketserver
import os
import webbrowser
import json
import csv
import datetime
import random
import traceback

# Configuration
PORT = 8080
DIRECTORY = os.path.join(os.path.dirname(os.path.abspath(__file__)), "public")
CSV_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "adr_reports.csv")
PATIENT_ID_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "patient_id_counter.txt")

print(f"Starting server on port {PORT}")
print(f"Serving files from: {DIRECTORY}")
print(f"CSV file location: {CSV_FILE}")

# Initialize patient ID counter
if not os.path.exists(PATIENT_ID_FILE):
    try:
        with open(PATIENT_ID_FILE, 'w') as f:
            f.write('2000')
        print(f"Created new patient ID counter file at {PATIENT_ID_FILE}")
    except Exception as e:
        print(f"ERROR creating patient ID file: {str(e)}")
        print(f"Path attempted: {PATIENT_ID_FILE}")

# Create CSV file if it doesn't exist
if not os.path.exists(CSV_FILE):
    try:
        os.makedirs(os.path.dirname(CSV_FILE), exist_ok=True)
        with open(CSV_FILE, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['timestamp', 'drug_name', 'medical_condition', 'adverse_reaction', 'severity', 
                         'confidence', 'cause_of_administration', 'gender', 'patient_id', 'current_medication'])
            # No sample data will be added
            print("Created empty CSV file")
    except Exception as e:
        print(f"ERROR creating CSV file: {str(e)}")
        print(f"Path attempted: {CSV_FILE}")
else:
    print(f"CSV file exists at {CSV_FILE}")
    # Check if file is readable
    try:
        with open(CSV_FILE, 'r', newline='', encoding='utf-8') as file:
            reader = csv.reader(file)
            header = next(reader, None)
            if header:
                print(f"CSV header: {header}")
                row_count = sum(1 for _ in reader)
                print(f"CSV contains {row_count} rows of data")
            else:
                print("CSV file appears to be empty")
    except Exception as e:
        print(f"Error reading CSV file: {str(e)}")
        print(f"Path attempted: {CSV_FILE}")

class ADRHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)
    
    def log_message(self, format, *args):
        """Log messages with more detail for debugging"""
        print(f"{self.address_string()} - [{self.log_date_time_string()}] {format % args}")
    
    def do_GET(self):
        print(f"GET request: {self.path}")
        # Handle API request for reports
        if self.path == '/api/reports':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            try:
                # Read CSV file and convert to JSON
                reports = []
                if os.path.exists(CSV_FILE):
                    try:
                        with open(CSV_FILE, 'r', newline='', encoding='utf-8') as file:
                            print(f"Reading from CSV file: {CSV_FILE}")
                            reader = csv.DictReader(file)
                            for row in reader:
                                reports.append(row)
                            print(f"Read {len(reports)} reports from CSV file")
                    except Exception as e:
                        print(f"Error reading CSV file in API: {str(e)}")
                        reports = []
                else:
                    print(f"CSV file not found at: {CSV_FILE}")
                
                # Return reports (newest first)
                reports.reverse()
                json_data = json.dumps({'reports': reports})
                print(f"Sending {len(reports)} reports, data length: {len(json_data)} bytes")
                self.wfile.write(json_data.encode())
            except Exception as e:
                print(f"ERROR serving reports: {str(e)}")
                traceback.print_exc()
                # Return empty array with error
                error_response = json.dumps({'reports': [], 'error': str(e)})
                self.wfile.write(error_response.encode())
            return
            
        # Handle static files for all other requests - sanitize path to prevent directory traversal
        try:
            return super().do_GET()
        except Exception as e:
            print(f"Error serving static file: {str(e)}")
            self.send_response(404)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b"File not found")
    
    def do_POST(self):
        print(f"POST request: {self.path}")
        if self.path == '/api/reports':
            try:
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length).decode('utf-8')
                
                try:
                    # Parse the JSON data
                    data = json.loads(post_data)
                    print(f"Received POST data: {data}")
                    
                    # Generate a patient ID
                    try:
                        with open(PATIENT_ID_FILE, 'r') as f:
                            patient_id_counter = int(f.read().strip())
                    except Exception as e:
                        print(f"Error reading patient ID file: {e}")
                        patient_id_counter = 2000
                    
                    patient_id = f"PTD_{patient_id_counter}"
                    
                    # Increment patient ID counter
                    try:
                        with open(PATIENT_ID_FILE, 'w') as f:
                            f.write(str(patient_id_counter + 1))
                    except Exception as e:
                        print(f"Error updating patient ID counter: {e}")
                    
                    # Get current timestamp
                    timestamp = datetime.datetime.now().strftime("%d-%m-%Y %H:%M")
                    
                    # Prepare row data
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
                    
                    # Debug print the data being written
                    print(f"Writing to CSV: {row_data}")
                    
                    # Check if file exists and has headers
                    file_exists = os.path.isfile(CSV_FILE) and os.path.getsize(CSV_FILE) > 0
                    
                    # Append to CSV with proper encoding
                    try:
                        with open(CSV_FILE, 'a', newline='', encoding='utf-8') as file:
                            writer = csv.writer(file)
                            # Write header if file is new
                            if not file_exists:
                                writer.writerow(['timestamp', 'drug_name', 'medical_condition', 'adverse_reaction', 'severity', 
                                             'confidence', 'cause_of_administration', 'gender', 'patient_id', 'current_medication'])
                            # Write data row
                            writer.writerow(row_data)
                        
                        print(f"Saved new report to CSV with patient ID: {patient_id}")
                        
                        # Send success response
                        self.send_response(200)
                        self.send_header('Content-type', 'application/json')
                        self.send_header('Access-Control-Allow-Origin', '*')
                        self.end_headers()
                        self.wfile.write(json.dumps({
                            'success': True,
                            'patient_id': patient_id
                        }).encode())
                    except Exception as e:
                        print(f"ERROR writing to CSV: {str(e)}")
                        raise e
                    
                except json.JSONDecodeError as e:
                    print(f"ERROR parsing JSON: {str(e)}")
                    print(f"Invalid JSON data received: {post_data}")
                    raise e
                
            except Exception as e:
                print(f"ERROR processing submission: {str(e)}")
                traceback.print_exc()
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({
                    'success': False,
                    'error': str(e)
                }).encode())
            return
        
        # Default response for other POST requests
        self.send_response(404)
        self.end_headers()
        return
    
    def do_OPTIONS(self):
        print(f"OPTIONS request: {self.path}")
        try:
            self.send_response(200)
            self.end_headers()
            print("OPTIONS request handled (CORS preflight)")
        except Exception as e:
            print(f"Error handling OPTIONS request: {str(e)}")
            self.send_response(500)
            self.end_headers()

    def end_headers(self):
        # Add CORS headers to every response
        try:
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        except Exception as e:
            print(f"Error adding CORS headers: {str(e)}")
        super().end_headers()

# Start the server
print(f"Server running at http://localhost:{PORT}")
print(f"API endpoint: http://localhost:{PORT}/api/reports")

# Open the correct URL in browser
webbrowser.open(f"http://localhost:{PORT}")

# Create server
with socketserver.TCPServer(("", PORT), ADRHandler) as httpd:
    try:
        print("Server is running, press Ctrl+C to stop")
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        httpd.server_close() 