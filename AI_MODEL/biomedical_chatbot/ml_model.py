import json
from typing import List, Dict, Any
import os
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.multioutput import MultiOutputClassifier
from sklearn.model_selection import train_test_split
import joblib
from collections import Counter

from synthetic_data import (
    generate_synthetic_data, 
    generate_feature_vector,
    generate_adverse_reactions,
    ALL_MEDICATIONS,
    ALL_CONDITIONS,
    ALL_ADVERSE_REACTIONS,
    INTERACTION_DICT,
    CONDITION_INTERACTION_DICT
)

class DrugInteractionPredictor:
    def __init__(self, model_path=None):
        """Initialize the drug interaction predictor"""
        self.is_trained = False
        self.reaction_mlb = MultiLabelBinarizer()
        self.severity_mlb = MultiLabelBinarizer()
        self.reaction_classifier = None
        self.severity_classifier = None
        
        if model_path and os.path.exists(model_path):
            self.load_model(model_path)
        
    def prepare_data(self, X, y):
        """Prepare data for training the ML model"""
        # Extract reactions and severities
        reactions = [sample['reactions'] for sample in y]
        severities = [sample['severities'] for sample in y]
        
        # Transform multi-label targets
        reactions_binary = self.reaction_mlb.fit_transform(reactions)
        severities_binary = self.severity_mlb.fit_transform(severities)
        
        return np.array(X), reactions_binary, severities_binary
    
    def train(self, num_samples=5000, train_size=0.8, random_state=42):
        """Train the drug interaction predictor on synthetic data"""
        print(f"Generating {num_samples} synthetic training samples...")
        # Generate synthetic data
        data = generate_synthetic_data(num_samples)
        
        # Prepare features and targets
        X = []
        y = []
        
        for sample in data:
            # Generate feature vector
            features = generate_feature_vector(
                sample['current_medications'],
                sample['pre_existing_conditions'],
                sample['drug_to_check'],
                sample['age'],
                sample['weight']
            )
            
            # Extract target variables (adverse reactions)
            reactions = [r['reaction'] for r in sample['adverse_reactions']]
            severities = [r['severity'] for r in sample['adverse_reactions']]
            
            # Add to dataset
            X.append(features)
            y.append({'reactions': reactions, 'severities': severities})
        
        # Prepare data for training
        X_array, reactions_binary, severities_binary = self.prepare_data(X, y)
        
        # Split into training and validation sets
        X_train, X_val, y_reactions_train, y_reactions_val, y_severities_train, y_severities_val = train_test_split(
            X_array, reactions_binary, severities_binary, 
            train_size=train_size, 
            random_state=random_state
        )
        
        print("Training reaction prediction model...")
        # Train reaction prediction model
        self.reaction_classifier = MultiOutputClassifier(
            GradientBoostingClassifier(n_estimators=100, random_state=random_state)
        )
        self.reaction_classifier.fit(X_train, y_reactions_train)
        
        print("Training severity prediction model...")
        # Train severity prediction model
        self.severity_classifier = MultiOutputClassifier(
            RandomForestClassifier(n_estimators=100, random_state=random_state)
        )
        self.severity_classifier.fit(X_train, y_severities_train)
        
        # Calculate validation accuracy
        reaction_acc = self.reaction_classifier.score(X_val, y_reactions_val)
        severity_acc = self.severity_classifier.score(X_val, y_severities_val)
        
        print(f"Validation accuracy - Reactions: {reaction_acc:.4f}, Severities: {severity_acc:.4f}")
        
        self.is_trained = True
        return self
    
    def predict(self, current_medications: List[str], drug_to_use: str, 
                preexisting_conditions: List[str], age: int, weight: float) -> Dict[str, Any]:
        """Predict potential adverse drug reactions using ML model and rule-based approach"""
        # Check if model is trained
        if not self.is_trained:
            print("Model not trained, using rule-based prediction only.")
            return self.rule_based_prediction(current_medications, drug_to_use, preexisting_conditions, age, weight)
        
        try:
            # Generate feature vector
            features = generate_feature_vector(
                current_medications,
                preexisting_conditions,
                drug_to_use,
                age,
                weight
            )
            
            # Make predictions with ML model
            reaction_pred = self.reaction_classifier.predict([features])[0]
            
            # Get probabilities
            reaction_probs = []
            try:
                reaction_probs = self.reaction_classifier.predict_proba([features])
            except Exception as e:
                print(f"Warning: Error getting prediction probabilities: {e}")
            
            # Get most likely reactions with probabilities
            reaction_probs_dict = {}
            
            # Fall back to rule-based if ML prediction fails
            if len(reaction_probs) == 0 or reaction_pred.shape[0] == 0:
                print("ML prediction failed, falling back to rule-based only")
                return self.rule_based_prediction(current_medications, drug_to_use, preexisting_conditions, age, weight)
            
            # Get predicted reactions if possible
            try:
                predicted_reactions = self.reaction_mlb.inverse_transform(reaction_pred.reshape(1, -1))[0]
            except Exception as e:
                print(f"Warning: Could not transform reactions: {e}")
                predicted_reactions = []
            
            # Process probabilities if available
            if len(reaction_probs) > 0:
                for i, estimator_probs in enumerate(reaction_probs):
                    if i < len(self.reaction_classifier.estimators_) and len(estimator_probs[0]) > 1:
                        try:
                            label = self.reaction_mlb.classes_[i]
                            prob = estimator_probs[0][1]  # Probability of positive class
                            if prob > 0.3:  # Threshold for considering a reaction
                                reaction_probs_dict[label] = prob
                        except Exception as e:
                            print(f"Warning: Error processing probability for class {i}: {e}")
            
            # Sort by probability
            sorted_reactions = sorted(reaction_probs_dict.items(), key=lambda x: x[1], reverse=True)
            
            # Combine with rule-based predictions for better results
            rule_pred = self.rule_based_prediction(current_medications, drug_to_use, preexisting_conditions, age, weight)
            
            # Combine ML predictions with rule-based predictions
            combined_reactions = []
            
            # Add high-probability ML predictions
            for reaction, prob in sorted_reactions[:5]:  # Top 5 ML predictions
                if prob > 0.5:  # Higher threshold for final selection
                    severity = 'HIGH' if prob > 0.7 else 'MEDIUM'
                    combined_reactions.append({
                        'reaction': reaction,
                        'probability': f"{prob:.2f}",
                        'severity': severity,
                        'source': 'ML prediction',
                        'mechanism': 'Statistical pattern from training data',
                        'type': 'ML-predicted'
                    })
            
            # Add rule-based predictions
            for reaction in rule_pred['adverse_reactions']:
                # Check if we already have this reaction
                if not any(r.get('reaction') == reaction.get('reaction') for r in combined_reactions):
                    reaction['source'] = 'Rule-based'
                    combined_reactions.append(reaction)
            
            # Organize by severity
            high_severity = [r for r in combined_reactions if r.get('severity') == 'HIGH']
            medium_severity = [r for r in combined_reactions if r.get('severity') == 'MEDIUM']
            low_severity = [r for r in combined_reactions if r.get('severity') == 'LOW']
            
            organized_reactions = high_severity + medium_severity + low_severity
            
            return {
                'adverse_reactions': organized_reactions,
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
        except Exception as e:
            print(f"Error in ML prediction: {e}")
            # Fall back to rule-based prediction
            return self.rule_based_prediction(current_medications, drug_to_use, preexisting_conditions, age, weight)
    
    def rule_based_prediction(self, current_medications: List[str], drug_to_use: str, 
                             preexisting_conditions: List[str], age: int, weight: float) -> Dict[str, Any]:
        """Use rule-based approach to predict adverse reactions"""
        return {
            'adverse_reactions': generate_adverse_reactions(current_medications, drug_to_use, preexisting_conditions, age, weight)
        }
    
    def save_model(self, model_path: str):
        """Save the trained model to disk"""
        if not self.is_trained:
            raise ValueError("Model must be trained before saving")
        
        model_data = {
            'reaction_classifier': self.reaction_classifier,
            'severity_classifier': self.severity_classifier,
            'reaction_mlb': self.reaction_mlb,
            'severity_mlb': self.severity_mlb
        }
        
        joblib.dump(model_data, model_path)
        print(f"Model saved to {model_path}")
    
    def load_model(self, model_path: str):
        """Load a trained model from disk"""
        try:
            model_data = joblib.load(model_path)
            
            self.reaction_classifier = model_data['reaction_classifier']
            self.severity_classifier = model_data['severity_classifier']
            self.reaction_mlb = model_data['reaction_mlb']
            self.severity_mlb = model_data['severity_mlb']
            
            self.is_trained = True
            print(f"Model loaded from {model_path}")
        except Exception as e:
            print(f"Error loading model: {e}")
            self.is_trained = False 