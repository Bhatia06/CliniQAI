from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import os
import traceback
import joblib
import numpy as np
from pathlib import Path
import sys

# Import the process manager
try:
    from process_manager import initialize
    
    # Initialize the process manager
    # If another instance is already running, this will exit
    if not initialize():
        print("Another instance of the AI Model is already running. Exiting.")
        sys.exit(0)
        
    print("Process manager initialized successfully")
except Exception as e:
    print(f"Error initializing process manager: {e}")
    print(traceback.format_exc())

# Print Python and current directory information
print(f"Python version: {sys.version}")
print(f"Current directory: {os.getcwd()}")

try:
    from synthetic_data import (
        generate_synthetic_data,
        generate_feature_vector,
        generate_adverse_reactions,
        ALL_MEDICATIONS,
        ALL_CONDITIONS
    )
    print("Successfully imported synthetic_data module")
except Exception as e:
    print(f"Error importing synthetic_data: {e}")
    print(traceback.format_exc())
    sys.exit(1)

app = Flask(__name__)
CORS(app)

# Use an absolute path for the model file
CURRENT_DIR = Path(__file__).parent.absolute()
MODEL_PATH = CURRENT_DIR / 'drug_interaction_model.joblib'
model_data = None

print(f"Looking for model at: {MODEL_PATH}")

try:
    if os.path.exists(MODEL_PATH):
        print(f"Loading model from {MODEL_PATH}...")
        model_data = joblib.load(MODEL_PATH)
        print("Model loaded successfully!")
    else:
        print(f"Model file {MODEL_PATH} not found. Using rule-based predictions only.")
except Exception as e:
    print(f"Error loading model: {e}")
    print(traceback.format_exc())
    print("Will use rule-based predictions only.")

@app.route('/')
def home():
    """Render the main application page"""
    return render_template('index.html')

@app.route('/api/analyze', methods=['POST'])
def analyze_medications():
    """
    Analyze potential adverse drug reactions
    
    Takes patient data including current medications, drug to check,
    pre-existing conditions, age, and weight to predict potential
    adverse reactions.
    
    Returns:
        JSON with analysis results or error message
    """
    try:
        data = request.get_json()
        
        # Extract patient information
        current_medications = data.get('current_medications', [])
        drug_to_use = data.get('drug_to_use', '')
        preexisting_conditions = data.get('preexisting_conditions', [])
        
        # Extract and validate age
        try:
            age = int(data.get('age', 0))
            if age < 1 or age > 120:
                return jsonify({
                    'success': False,
                    'error': 'Age must be between 1 and 120 years'
                }), 400
        except (ValueError, TypeError):
            return jsonify({
                'success': False,
                'error': 'Invalid age value'
            }), 400
        
        # Extract and validate weight
        try:
            weight = float(data.get('weight', 0.0))
            if weight < 1 or weight > 300:
                return jsonify({
                    'success': False,
                    'error': 'Weight must be between 1 and 300 kg'
                }), 400
        except (ValueError, TypeError):
            return jsonify({
                'success': False,
                'error': 'Invalid weight value'
            }), 400
        
        # Run rule-based prediction
        analysis = rule_based_prediction(
            current_medications=current_medications,
            drug_to_use=drug_to_use,
            preexisting_conditions=preexisting_conditions,
            age=age,
            weight=weight
        )

        return jsonify({
            'success': True,
            'analysis': analysis
        })

    except Exception as e:
        print(f"Error in API: {str(e)}")
        print(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

def rule_based_prediction(current_medications, drug_to_use, preexisting_conditions, age, weight):
    """
    Use rule-based approach to predict adverse reactions
    
    Args:
        current_medications: List of medications the patient is currently taking
        drug_to_use: Drug being checked for potential adverse reactions
        preexisting_conditions: List of patient's pre-existing medical conditions
        age: Patient's age in years
        weight: Patient's weight in kilograms
        
    Returns:
        Dictionary with adverse reactions and patient information
    """
    adverse_reactions = generate_adverse_reactions(
        current_medications, 
        drug_to_use, 
        preexisting_conditions, 
        age, 
        weight
    )
    
    return {
        'adverse_reactions': adverse_reactions,
        'medication_info': {
            'drug_to_use': drug_to_use,
            'current_medications': current_medications,
            'preexisting_conditions': preexisting_conditions
        },
        'patient_info': {
            'age': age,
            'weight': weight
        }
    }

@app.route('/api/medications', methods=['GET'])
def get_medications():
    """
    API endpoint to get list of available medications
    
    Returns:
        JSON with list of medication names
    """
    return jsonify({
        'success': True,
        'medications': sorted(ALL_MEDICATIONS)
    })

@app.route('/api/conditions', methods=['GET'])
def get_conditions():
    """
    API endpoint to get list of available medical conditions
    
    Returns:
        JSON with list of condition names
    """
    return jsonify({
        'success': True,
        'conditions': sorted(ALL_CONDITIONS)
    })

if __name__ == '__main__':
    # Start the Flask server without debug mode to prevent auto-restart
    app.run(debug=False, port=8084, host='0.0.0.0') 