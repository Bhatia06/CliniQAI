import json
import random
import pandas as pd
import numpy as np
from typing import List, Dict, Any

# Synthetic medical data with more comprehensive lists
medications = [
    # Cardiovascular
    "Metformin", "Lisinopril", "Amlodipine", "Atorvastatin", "Aspirin",
    "Metoprolol", "Hydrochlorothiazide", "Warfarin", "Clopidogrel", "Nitroglycerin",
    # Anti-inflammatory
    "Ibuprofen", "Naproxen", "Prednisone", "Methotrexate", "Sulfasalazine",
    # Gastrointestinal
    "Omeprazole", "Ranitidine", "Metoclopramide", "Lansoprazole", "Pantoprazole",
    # Psychiatric
    "Sertraline", "Fluoxetine", "Amitriptyline", "Venlafaxine", "Bupropion",
    # Diabetes
    "Insulin", "Glimepiride", "Pioglitazone", "Sitagliptin", "Dapagliflozin",
    # Thyroid
    "Levothyroxine", "Methimazole", "Propylthiouracil",
    # Pain Management
    "Acetaminophen", "Tramadol", "Gabapentin", "Pregabalin", "Duloxetine"
]

conditions = [
    # Cardiovascular
    "Hypertension", "Heart Disease", "Atrial Fibrillation", "Heart Failure", "Coronary Artery Disease",
    # Metabolic
    "Type 2 Diabetes", "Hyperlipidemia", "Obesity", "Metabolic Syndrome", "Thyroid Disorder",
    # Respiratory
    "Asthma", "COPD", "Sleep Apnea", "Bronchitis", "Emphysema",
    # Gastrointestinal
    "GERD", "IBS", "Crohn's Disease", "Ulcerative Colitis", "Liver Disease",
    # Musculoskeletal
    "Arthritis", "Osteoporosis", "Fibromyalgia", "Rheumatoid Arthritis", "Osteoarthritis",
    # Mental Health
    "Depression", "Anxiety", "Bipolar Disorder", "PTSD", "Insomnia",
    # Other
    "Kidney Disease", "Migraine", "Epilepsy", "Cancer", "HIV/AIDS"
]

# Drug interactions and their effects
drug_interactions = {
    ('warfarin', 'aspirin'): {
        'effect': 'Increased risk of bleeding',
        'severity': 'HIGH'
    },
    ('lisinopril', 'spironolactone'): {
        'effect': 'Dangerous increase in blood potassium levels',
        'severity': 'HIGH'
    },
    ('metformin', 'furosemide'): {
        'effect': 'Reduced blood sugar control',
        'severity': 'MEDIUM'
    },
    ('simvastatin', 'clarithromycin'): {
        'effect': 'Increased risk of muscle damage',
        'severity': 'HIGH'
    },
    ('omeprazole', 'clopidogrel'): {
        'effect': 'Reduced effectiveness of blood clot prevention',
        'severity': 'HIGH'
    },
    ('fluoxetine', 'tramadol'): {
        'effect': 'Increased risk of serotonin syndrome',
        'severity': 'HIGH'
    },
    ('amiodarone', 'levofloxacin'): {
        'effect': 'Increased risk of irregular heartbeat',
        'severity': 'HIGH'
    },
    ('methotrexate', 'ibuprofen'): {
        'effect': 'Increased methotrexate toxicity',
        'severity': 'HIGH'
    },
    ('digoxin', 'verapamil'): {
        'effect': 'Increased risk of digoxin toxicity',
        'severity': 'HIGH'
    },
    ('lithium', 'hydrochlorothiazide'): {
        'effect': 'Increased risk of lithium toxicity',
        'severity': 'HIGH'
    },
    ('carbamazepine', 'simvastatin'): {
        'effect': 'Reduced effectiveness of simvastatin',
        'severity': 'MEDIUM'
    },
    ('ciprofloxacin', 'insulin'): {
        'effect': 'Blood sugar fluctuations',
        'severity': 'MEDIUM'
    },
    ('prednisone', 'ibuprofen'): {
        'effect': 'Increased risk of stomach ulcers',
        'severity': 'MEDIUM'
    },
    ('levothyroxine', 'calcium'): {
        'effect': 'Reduced thyroid medication absorption',
        'severity': 'MEDIUM'
    },
    ('metronidazole', 'alcohol'): {
        'effect': 'Severe nausea and vomiting',
        'severity': 'MEDIUM'
    },
    ('alprazolam', 'alcohol'): {
        'effect': 'Dangerous increase in sedation',
        'severity': 'HIGH'
    },
    ('sildenafil', 'nitroglycerin'): {
        'effect': 'Dangerous drop in blood pressure',
        'severity': 'HIGH'
    },
    ('potassium', 'lisinopril'): {
        'effect': 'Dangerous increase in potassium levels',
        'severity': 'HIGH'
    },
    ('amoxicillin', 'allopurinol'): {
        'effect': 'Increased risk of skin rash',
        'severity': 'MEDIUM'
    },
    ('sertraline', 'aspirin'): {
        'effect': 'Increased risk of bleeding',
        'severity': 'MEDIUM'
    },
    ('cyclosporine', 'simvastatin'): {
        'effect': 'Increased risk of muscle breakdown',
        'severity': 'HIGH'
    },
    ('diltiazem', 'simvastatin'): {
        'effect': 'Increased risk of muscle pain and damage',
        'severity': 'HIGH'
    },
    ('rifampin', 'warfarin'): {
        'effect': 'Reduced blood-thinning effect',
        'severity': 'HIGH'
    },
    ('phenytoin', 'omeprazole'): {
        'effect': 'Altered phenytoin levels',
        'severity': 'MEDIUM'
    },
    ('acetaminophen', 'alcohol'): {
        'effect': 'Increased risk of liver damage',
        'severity': 'HIGH'
    }
}

# Define common medications by category
MEDICATIONS = {
    'antihypertensives': ['lisinopril', 'losartan', 'amlodipine', 'hydrochlorothiazide', 'metoprolol', 'valsartan'],
    'anticoagulants': ['warfarin', 'apixaban', 'rivaroxaban', 'dabigatran', 'heparin', 'clopidogrel'],
    'antidiabetics': ['metformin', 'insulin', 'glipizide', 'sitagliptin', 'empagliflozin', 'liraglutide'],
    'statins': ['atorvastatin', 'simvastatin', 'rosuvastatin', 'pravastatin', 'lovastatin'],
    'antibiotics': ['amoxicillin', 'azithromycin', 'ciprofloxacin', 'doxycycline', 'levofloxacin', 'metronidazole'],
    'nsaids': ['ibuprofen', 'naproxen', 'celecoxib', 'diclofenac', 'aspirin'],
    'antidepressants': ['sertraline', 'fluoxetine', 'escitalopram', 'duloxetine', 'venlafaxine', 'bupropion'],
    'antipsychotics': ['quetiapine', 'risperidone', 'aripiprazole', 'olanzapine', 'haloperidol'],
    'anticonvulsants': ['levetiracetam', 'lamotrigine', 'phenytoin', 'carbamazepine', 'valproic acid'],
    'ppis': ['omeprazole', 'pantoprazole', 'esomeprazole', 'lansoprazole'],
    'corticosteroids': ['prednisone', 'hydrocortisone', 'budesonide', 'fluticasone', 'dexamethasone'],
    'bronchodilators': ['albuterol', 'tiotropium', 'salmeterol', 'formoterol', 'ipratropium'],
    'opioids': ['tramadol', 'oxycodone', 'morphine', 'hydrocodone', 'fentanyl'],
    'other': ['levothyroxine', 'alprazolam', 'gabapentin', 'sildenafil', 'montelukast', 'digoxin']
}

# Flatten the medications list
ALL_MEDICATIONS = [med for category in MEDICATIONS.values() for med in category]

# Define common conditions by system
CONDITIONS = {
    'cardiovascular': ['hypertension', 'coronary artery disease', 'congestive heart failure', 'atrial fibrillation', 'history of stroke', 'peripheral vascular disease'],
    'respiratory': ['asthma', 'chronic obstructive pulmonary disease', 'pulmonary fibrosis', 'sleep apnea', 'bronchitis'],
    'endocrine': ['diabetes type 1', 'diabetes type 2', 'hypothyroidism', 'hyperthyroidism', 'obesity'],
    'gastrointestinal': ['gastroesophageal reflux disease', 'peptic ulcer disease', 'irritable bowel syndrome', 'Crohn disease', 'ulcerative colitis', 'liver cirrhosis'],
    'neurological': ['migraine', 'epilepsy', 'Parkinson disease', 'multiple sclerosis', 'neuropathy'],
    'psychiatric': ['depression', 'anxiety disorder', 'bipolar disorder', 'schizophrenia', 'PTSD'],
    'renal': ['chronic kidney disease', 'kidney stones', 'renal failure', 'nephrotic syndrome'],
    'hepatic': ['fatty liver disease', 'hepatitis', 'liver cirrhosis', 'portal hypertension'],
    'musculoskeletal': ['rheumatoid arthritis', 'osteoarthritis', 'osteoporosis', 'fibromyalgia', 'gout'],
    'other': ['anemia', 'chronic pain', 'eczema', 'psoriasis', 'glaucoma', 'cataract']
}

# Flatten the conditions list
ALL_CONDITIONS = [condition for category in CONDITIONS.values() for condition in category]

# Define potential adverse reactions by system
ADVERSE_REACTIONS = {
    'cardiovascular': ['hypotension', 'hypertension', 'tachycardia', 'bradycardia', 'arrhythmia', 'QT prolongation', 'myocardial infarction', 'edema'],
    'respiratory': ['bronchospasm', 'cough', 'shortness of breath', 'respiratory depression', 'pulmonary edema'],
    'gastrointestinal': ['nausea', 'vomiting', 'diarrhea', 'constipation', 'GI bleeding', 'pancreatitis', 'liver damage'],
    'neurological': ['headache', 'dizziness', 'seizures', 'drowsiness', 'insomnia', 'peripheral neuropathy', 'confusion'],
    'dermatological': ['rash', 'itching', 'photosensitivity', 'Stevens-Johnson syndrome', 'angioedema'],
    'renal': ['acute kidney injury', 'electrolyte imbalance', 'fluid retention', 'urinary retention'],
    'hematological': ['bleeding', 'thrombocytopenia', 'neutropenia', 'anemia', 'thrombotic events'],
    'endocrine': ['hyperglycemia', 'hypoglycemia', 'thyroid dysfunction', 'adrenal suppression'],
    'musculoskeletal': ['muscle pain', 'rhabdomyolysis', 'tendonitis', 'joint pain', 'fractures'],
    'psychiatric': ['depression', 'anxiety', 'hallucinations', 'mood changes', 'suicidal ideation']
}

# Flatten the adverse reactions list
ALL_ADVERSE_REACTIONS = [reaction for category in ADVERSE_REACTIONS.values() for reaction in category]

# Define known drug interactions
DRUG_INTERACTIONS = [
    # Format: (drug1, drug2, effect, severity, mechanism)
    ('warfarin', 'aspirin', 'increased risk of bleeding', 'HIGH', 'additive anticoagulant effects'),
    ('warfarin', 'ibuprofen', 'increased risk of bleeding', 'HIGH', 'additive anticoagulant effects'),
    ('warfarin', 'ciprofloxacin', 'increased warfarin effect', 'HIGH', 'inhibition of warfarin metabolism'),
    ('warfarin', 'amiodarone', 'increased warfarin effect', 'HIGH', 'inhibition of warfarin metabolism'),
    ('lisinopril', 'spironolactone', 'hyperkalemia', 'HIGH', 'potassium retention'),
    ('lisinopril', 'potassium supplements', 'hyperkalemia', 'HIGH', 'potassium retention'),
    ('lisinopril', 'ibuprofen', 'reduced antihypertensive effect', 'MEDIUM', 'prostaglandin inhibition'),
    ('metformin', 'hydrochlorothiazide', 'reduced blood glucose control', 'MEDIUM', 'increased insulin resistance'),
    ('metformin', 'contrast media', 'lactic acidosis', 'HIGH', 'reduced metformin clearance'),
    ('simvastatin', 'erythromycin', 'increased risk of rhabdomyolysis', 'HIGH', 'inhibition of simvastatin metabolism'),
    ('simvastatin', 'clarithromycin', 'increased risk of rhabdomyolysis', 'HIGH', 'inhibition of simvastatin metabolism'),
    ('simvastatin', 'amiodarone', 'increased risk of myopathy', 'HIGH', 'inhibition of simvastatin metabolism'),
    ('simvastatin', 'diltiazem', 'increased risk of myopathy', 'MEDIUM', 'inhibition of simvastatin metabolism'),
    ('digoxin', 'amiodarone', 'increased digoxin levels', 'HIGH', 'reduced digoxin clearance'),
    ('digoxin', 'verapamil', 'increased digoxin levels', 'HIGH', 'reduced digoxin clearance'),
    ('theophylline', 'ciprofloxacin', 'increased theophylline levels', 'HIGH', 'inhibition of theophylline metabolism'),
    ('clopidogrel', 'omeprazole', 'reduced clopidogrel effectiveness', 'MEDIUM', 'inhibition of clopidogrel activation'),
    ('methotrexate', 'ibuprofen', 'increased methotrexate toxicity', 'HIGH', 'reduced methotrexate clearance'),
    ('lithium', 'hydrochlorothiazide', 'increased lithium levels', 'HIGH', 'reduced lithium clearance'),
    ('fluoxetine', 'tramadol', 'serotonin syndrome', 'HIGH', 'increased serotonin levels'),
    ('fluoxetine', 'sumatriptan', 'serotonin syndrome', 'HIGH', 'increased serotonin levels'),
    ('sildenafil', 'nitroglycerin', 'severe hypotension', 'HIGH', 'additive vasodilatory effects'),
    ('rifampin', 'oral contraceptives', 'reduced contraceptive effectiveness', 'HIGH', 'increased contraceptive metabolism'),
    ('carbamazepine', 'oral contraceptives', 'reduced contraceptive effectiveness', 'HIGH', 'increased contraceptive metabolism'),
    ('carbamazepine', 'valproic acid', 'altered anticonvulsant levels', 'MEDIUM', 'enzyme induction'),
    ('phenytoin', 'valproic acid', 'altered anticonvulsant levels', 'MEDIUM', 'enzyme induction'),
    ('alprazolam', 'alcohol', 'increased sedation', 'HIGH', 'additive CNS depression'),
    ('oxycodone', 'alcohol', 'respiratory depression', 'HIGH', 'additive CNS depression'),
    ('levothyroxine', 'calcium', 'reduced levothyroxine absorption', 'MEDIUM', 'binding in GI tract'),
    ('ciprofloxacin', 'antacids', 'reduced ciprofloxacin absorption', 'MEDIUM', 'binding in GI tract'),
    ('tetracycline', 'antacids', 'reduced tetracycline absorption', 'MEDIUM', 'binding in GI tract'),
    ('metronidazole', 'alcohol', 'disulfiram-like reaction', 'MEDIUM', 'inhibition of aldehyde dehydrogenase'),
    ('acetaminophen', 'alcohol', 'increased hepatotoxicity', 'HIGH', 'enhanced toxic metabolite production'),
    ('prednisone', 'ibuprofen', 'increased GI bleeding risk', 'MEDIUM', 'additive GI irritation'),
    ('allopurinol', 'amoxicillin', 'increased risk of rash', 'MEDIUM', 'unknown mechanism'),
    ('cyclosporine', 'simvastatin', 'increased statin toxicity', 'HIGH', 'inhibition of statin metabolism'),
]

# Create a dictionary of drug-condition interactions
DRUG_CONDITION_INTERACTIONS = [
    # Format: (drug, condition, effect, severity)
    ('metformin', 'renal failure', 'lactic acidosis', 'HIGH'),
    ('metformin', 'liver cirrhosis', 'lactic acidosis', 'HIGH'),
    ('nsaids', 'peptic ulcer disease', 'GI bleeding', 'HIGH'),
    ('nsaids', 'kidney stones', 'worsening renal function', 'MEDIUM'),
    ('nsaids', 'hypertension', 'increased blood pressure', 'MEDIUM'),
    ('nsaids', 'congestive heart failure', 'fluid retention', 'HIGH'),
    ('warfarin', 'liver cirrhosis', 'increased bleeding risk', 'HIGH'),
    ('statins', 'liver disease', 'hepatotoxicity', 'HIGH'),
    ('fluoroquinolones', 'epilepsy', 'seizures', 'HIGH'),
    ('beta-blockers', 'asthma', 'bronchospasm', 'HIGH'),
    ('beta-blockers', 'diabetes', 'masked hypoglycemia symptoms', 'MEDIUM'),
    ('ace-inhibitors', 'renal artery stenosis', 'acute kidney injury', 'HIGH'),
    ('thiazide diuretics', 'gout', 'gout flare', 'MEDIUM'),
    ('corticosteroids', 'diabetes', 'hyperglycemia', 'MEDIUM'),
    ('corticosteroids', 'osteoporosis', 'increased fracture risk', 'MEDIUM'),
    ('ssris', 'bleeding disorders', 'increased bleeding risk', 'HIGH'),
    ('antipsychotics', 'Parkinson disease', 'worsening parkinsonism', 'HIGH'),
    ('anticholinergics', 'glaucoma', 'increased intraocular pressure', 'HIGH'),
    ('anticholinergics', 'prostatic hyperplasia', 'urinary retention', 'MEDIUM'),
    ('opioids', 'sleep apnea', 'respiratory depression', 'HIGH'),
    ('benzodiazepines', 'sleep apnea', 'respiratory depression', 'HIGH'),
    ('potassium', 'renal failure', 'hyperkalemia', 'HIGH'),
    ('allopurinol', 'renal failure', 'hypersensitivity reactions', 'HIGH')
]

# Map drug categories to drug names
DRUG_CATEGORIES = {}
for category, drugs in MEDICATIONS.items():
    for drug in drugs:
        DRUG_CATEGORIES[drug] = category

# Convert interactions to dictionary for faster lookup
INTERACTION_DICT = {}
for drug1, drug2, effect, severity, mechanism in DRUG_INTERACTIONS:
    if drug1 not in INTERACTION_DICT:
        INTERACTION_DICT[drug1] = {}
    if drug2 not in INTERACTION_DICT:
        INTERACTION_DICT[drug2] = {}
    
    INTERACTION_DICT[drug1][drug2] = {
        'effect': effect,
        'severity': severity,
        'mechanism': mechanism
    }
    
    # Also store the reverse interaction
    INTERACTION_DICT[drug2][drug1] = {
        'effect': effect,
        'severity': severity,
        'mechanism': mechanism
    }

# Create a dictionary of drug-condition interactions
CONDITION_INTERACTION_DICT = {}
for drug, condition, effect, severity in DRUG_CONDITION_INTERACTIONS:
    if drug not in CONDITION_INTERACTION_DICT:
        CONDITION_INTERACTION_DICT[drug] = {}
    
    CONDITION_INTERACTION_DICT[drug][condition] = {
        'effect': effect,
        'severity': severity
    }

# Map drug categories to specific drugs
for category, drugs in MEDICATIONS.items():
    for drug_cond, cond, effect, severity in DRUG_CONDITION_INTERACTIONS:
        if drug_cond in category or drug_cond == category:
            for drug in drugs:
                if drug not in CONDITION_INTERACTION_DICT:
                    CONDITION_INTERACTION_DICT[drug] = {}
                CONDITION_INTERACTION_DICT[drug][cond] = {
                    'effect': effect,
                    'severity': severity
                }

def generate_synthetic_data(num_samples=1000):
    """Generate synthetic training data for drug interaction prediction"""
    data = []
    
    for _ in range(num_samples):
        # Randomly select 1-4 current medications
        num_current_meds = random.randint(1, 4)
        current_medications = random.sample(ALL_MEDICATIONS, num_current_meds)
        
        # Randomly select 1-3 pre-existing conditions
        num_conditions = random.randint(1, 3)
        pre_existing_conditions = random.sample(ALL_CONDITIONS, num_conditions)
        
        # Randomly select a drug to check
        drug_to_check = random.choice(ALL_MEDICATIONS)
        
        # Determine age with realistic distribution
        # Higher probability of elderly patients (more likely to have multiple medications)
        age_group = random.choices(
            ["adult", "elderly", "very_elderly"], 
            weights=[0.5, 0.3, 0.2], 
            k=1
        )[0]
        
        if age_group == "adult":
            age = random.randint(18, 64)
        elif age_group == "elderly":
            age = random.randint(65, 85)
        else:  # very_elderly
            age = random.randint(86, 100)
        
        # Determine weight with realistic distribution based on age
        # Use normal distribution around average weights for different age groups
        if age < 65:
            # Adult: mean weight ~70kg with standard deviation 15kg
            weight = max(1, min(200, round(random.normalvariate(70.0, 15.0), 1)))
        else:
            # Elderly: slightly lower mean weight ~65kg with standard deviation 12kg
            weight = max(1, min(200, round(random.normalvariate(65.0, 12.0), 1)))
        
        # Generate actual adverse reactions
        adverse_reactions = generate_adverse_reactions(current_medications, drug_to_check, pre_existing_conditions, age, weight)
        
        # Create sample
        sample = {
            'current_medications': current_medications,
            'pre_existing_conditions': pre_existing_conditions,
            'drug_to_check': drug_to_check,
            'age': age,
            'weight': weight,
            'adverse_reactions': adverse_reactions
        }
        
        data.append(sample)
    
    return data

def generate_feature_vector(medications, conditions, drug, age, weight):
    """Generate a feature vector for ML model"""
    # Initialize feature vector
    features = []
    
    # Age features
    features.append(age / 100.0)  # Normalize age
    
    # Weight feature
    features.append(weight / 200.0)  # Normalize weight
    
    # One-hot encode medications
    med_features = [1 if med in medications else 0 for med in ALL_MEDICATIONS]
    features.extend(med_features)
    
    # One-hot encode the drug to check
    drug_features = [1 if drug == med else 0 for med in ALL_MEDICATIONS]
    features.extend(drug_features)
    
    # One-hot encode conditions
    condition_features = [1 if cond in conditions else 0 for cond in ALL_CONDITIONS]
    features.extend(condition_features)
    
    # Calculate number of medications
    features.append(len(medications) / 10.0)  # Normalize
    
    # Calculate number of conditions
    features.append(len(conditions) / 10.0)  # Normalize
    
    return features

def generate_adverse_reactions(current_medications, drug_to_check, pre_existing_conditions, age, weight):
    """Generate adverse reactions based on drug interactions and conditions"""
    adverse_reactions = []
    
    # Check drug-drug interactions
    for current_med in current_medications:
        if current_med in INTERACTION_DICT and drug_to_check in INTERACTION_DICT[current_med]:
            interaction = INTERACTION_DICT[current_med][drug_to_check]
            adverse_reactions.append({
                'reaction': interaction['effect'],
                'severity': interaction['severity'],
                'mechanism': interaction['mechanism'],
                'type': 'drug-drug',
                'trigger': f"{current_med} + {drug_to_check}"
            })
    
    # Check drug-condition interactions
    if drug_to_check in CONDITION_INTERACTION_DICT:
        for condition in pre_existing_conditions:
            if condition in CONDITION_INTERACTION_DICT[drug_to_check]:
                interaction = CONDITION_INTERACTION_DICT[drug_to_check][condition]
                adverse_reactions.append({
                    'reaction': interaction['effect'],
                    'severity': interaction['severity'],
                    'mechanism': 'Condition specific risk',
                    'type': 'drug-condition',
                    'trigger': f"{drug_to_check} with {condition}"
                })
    
    # Check age-related risks (based on real medical knowledge)
    if age > 65:
        # Evidence-based elderly-specific risks
        if drug_to_check in ['alprazolam', 'diazepam', 'zolpidem', 'lorazepam', 'clonazepam']:
            # Benzodiazepines and sleep medications have higher risks in elderly
            adverse_reactions.append({
                'reaction': 'confusion and increased fall risk',
                'severity': 'HIGH',
                'mechanism': 'Age-related pharmacokinetic changes',
                'type': 'drug-age',
                'trigger': f"Age > 65 with {drug_to_check}"
            })
        elif drug_to_check in ['ibuprofen', 'naproxen', 'diclofenac', 'aspirin']:
            # NSAIDs have increased GI bleeding risk in elderly
            adverse_reactions.append({
                'reaction': 'increased gastrointestinal bleeding risk',
                'severity': 'HIGH',
                'mechanism': 'Age-related GI vulnerability',
                'type': 'drug-age',
                'trigger': f"Age > 65 with {drug_to_check}"
            })
        elif drug_to_check in ['warfarin', 'apixaban', 'rivaroxaban', 'dabigatran']:
            # Anticoagulants have increased bleeding risk in elderly
            adverse_reactions.append({
                'reaction': 'increased bleeding risk',
                'severity': 'HIGH',
                'mechanism': 'Age-related pharmacokinetic changes',
                'type': 'drug-age',
                'trigger': f"Age > 65 with {drug_to_check}"
            })
        elif drug_to_check in ['amlodipine', 'lisinopril', 'losartan', 'hydrochlorothiazide']:
            # Antihypertensives can cause more orthostatic hypotension in elderly
            adverse_reactions.append({
                'reaction': 'increased risk of orthostatic hypotension',
                'severity': 'MEDIUM',
                'mechanism': 'Age-related cardiovascular changes',
                'type': 'drug-age',
                'trigger': f"Age > 65 with {drug_to_check}"
            })
    
    # Check weight-related risks
    # Low body weight can lead to overdose risk for certain drugs
    if weight < 50:
        if any(drug in ['digoxin', 'warfarin', 'phenytoin', 'vancomycin', 'aminoglycosides'] 
               for drug in [drug_to_check] + current_medications):
            adverse_reactions.append({
                'reaction': 'potential overdose risk',
                'severity': 'HIGH',
                'mechanism': 'Low body weight resulting in altered drug distribution volume',
                'type': 'drug-weight',
                'trigger': f"Low weight ({weight} kg) with {drug_to_check}"
            })
        elif drug_to_check in ['hydrochlorothiazide', 'furosemide']:
            adverse_reactions.append({
                'reaction': 'increased risk of electrolyte imbalance',
                'severity': 'MEDIUM',
                'mechanism': 'Low body weight with diuretic use',
                'type': 'drug-weight',
                'trigger': f"Low weight ({weight} kg) with {drug_to_check}"
            })
    
    # Check specific drug category risks with conditions (evidence-based)
    drug_category = None
    for category, drugs in MEDICATIONS.items():
        if drug_to_check in drugs:
            drug_category = category
            break
    
    # Real-life evidence-based category-condition interactions
    if drug_category == 'nsaids' and any('kidney' in cond.lower() for cond in pre_existing_conditions):
        adverse_reactions.append({
            'reaction': 'acute kidney injury',
            'severity': 'HIGH',
            'mechanism': 'NSAIDs reduce renal blood flow in compromised kidneys',
            'type': 'category-condition',
            'trigger': f"NSAID use with kidney disease"
        })
    elif drug_category == 'statins' and any('liver' in cond.lower() for cond in pre_existing_conditions):
        adverse_reactions.append({
            'reaction': 'hepatotoxicity',
            'severity': 'HIGH',
            'mechanism': 'Impaired statin metabolism with liver disease',
            'type': 'category-condition',
            'trigger': f"Statin use with liver disease"
        })
    elif drug_category == 'antidiabetics' and any('kidney' in cond.lower() for cond in pre_existing_conditions):
        adverse_reactions.append({
            'reaction': 'hypoglycemia',
            'severity': 'HIGH',
            'mechanism': 'Reduced clearance of insulin or oral hypoglycemics',
            'type': 'category-condition',
            'trigger': f"Antidiabetic use with kidney disease"
        })
    
    # If no specific interactions found, return common side effects based on real data
    if not adverse_reactions:
        # Get the drug category
        category = drug_category or 'other'
        
        # Common evidence-based side effects by drug category
        side_effects = {
            'antihypertensives': [
                {'reaction': 'dizziness', 'severity': 'MEDIUM'},
                {'reaction': 'fatigue', 'severity': 'LOW'},
                {'reaction': 'cough (specifically with ACE inhibitors)', 'severity': 'MEDIUM'}
            ],
            'anticoagulants': [
                {'reaction': 'bruising', 'severity': 'LOW'},
                {'reaction': 'nosebleeds', 'severity': 'MEDIUM'},
                {'reaction': 'bleeding gums', 'severity': 'MEDIUM'}
            ],
            'antidiabetics': [
                {'reaction': 'hypoglycemia', 'severity': 'MEDIUM'},
                {'reaction': 'nausea', 'severity': 'LOW'},
                {'reaction': 'vitamin B12 deficiency (with long-term metformin)', 'severity': 'MEDIUM'}
            ],
            'statins': [
                {'reaction': 'muscle pain (myalgia)', 'severity': 'MEDIUM'},
                {'reaction': 'liver enzyme elevation', 'severity': 'MEDIUM'},
                {'reaction': 'headache', 'severity': 'LOW'}
            ],
            'antibiotics': [
                {'reaction': 'diarrhea', 'severity': 'MEDIUM'},
                {'reaction': 'nausea', 'severity': 'LOW'},
                {'reaction': 'rash', 'severity': 'MEDIUM'}
            ],
            'nsaids': [
                {'reaction': 'stomach upset', 'severity': 'MEDIUM'},
                {'reaction': 'heartburn', 'severity': 'MEDIUM'},
                {'reaction': 'hypertension', 'severity': 'MEDIUM'}
            ],
            'antidepressants': [
                {'reaction': 'sexual dysfunction', 'severity': 'MEDIUM'},
                {'reaction': 'dry mouth', 'severity': 'LOW'},
                {'reaction': 'weight changes', 'severity': 'MEDIUM'}
            ],
            'other': [
                {'reaction': 'headache', 'severity': 'LOW'},
                {'reaction': 'nausea', 'severity': 'LOW'},
                {'reaction': 'dizziness', 'severity': 'MEDIUM'}
            ]
        }
        
        # Add 1-2 common side effects
        num_side_effects = random.randint(1, 2)
        if category in side_effects:
            selected_effects = random.sample(side_effects[category], min(num_side_effects, len(side_effects[category])))
        else:
            selected_effects = random.sample(side_effects['other'], min(num_side_effects, len(side_effects['other'])))
        
        for effect in selected_effects:
            adverse_reactions.append({
                'reaction': effect['reaction'],
                'severity': effect['severity'],
                'mechanism': 'Known side effect based on clinical data',
                'type': 'common-effect',
                'trigger': drug_to_check
            })
    
    return adverse_reactions

def create_training_dataset(num_samples=5000):
    """Create a training dataset for the ML model"""
    data = generate_synthetic_data(num_samples)
    
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
    
    return X, y

def save_synthetic_data(data, filename="synthetic_medical_data.json"):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)

if __name__ == "__main__":
    data = generate_synthetic_data(100)
    save_synthetic_data(data) 