from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import os
import traceback
import joblib
import numpy as np
from pathlib import Path
import sys

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
    return render_template('index.html')

@app.route('/api/analyze', methods=['POST'])
def analyze_medications():
    try:
        data = request.get_json()
        
        # Extract patient information
        current_medications = data.get('current_medications', [])
        drug_to_use = data.get('drug_to_use', '')
        preexisting_conditions = data.get('preexisting_conditions', [])
        
        # Extract and validate age
        try:
            age = int(data.get('age', 0))
            if age < 1 or age > 100:
                return jsonify({
                    'success': False,
                    'error': 'Age must be between 1 and 100 years'
                }), 400
        except (ValueError, TypeError):
            return jsonify({
                'success': False,
                'error': 'Invalid age value'
            }), 400
        
        # Extract and validate weight
        try:
            weight = float(data.get('weight', 0.0))
            if weight < 1 or weight > 200:
                return jsonify({
                    'success': False,
                    'error': 'Weight must be between 1 and 200 kg'
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
    """Use rule-based approach to predict adverse reactions"""
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
    """API endpoint to get list of available medications"""
    return jsonify({
        'success': True,
        'medications': sorted(ALL_MEDICATIONS)
    })

@app.route('/api/conditions', methods=['GET'])
def get_conditions():
    """API endpoint to get list of available conditions"""
    return jsonify({
        'success': True,
        'conditions': sorted(ALL_CONDITIONS)
    })

if __name__ == '__main__':
    app.run(debug=True, port=8084, host='0.0.0.0') 