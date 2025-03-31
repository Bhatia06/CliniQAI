# CliniQAI - Adverse Drug Reaction (ADR) Reporting System

CliniQAI is an integrated healthcare system for reporting, analyzing, and predicting adverse drug reactions using advanced AI models. The system consists of multiple interconnected components that work together to provide a comprehensive solution for healthcare professionals and patients.

## System Overview

CliniQAI consists of three main components:

1. **Patient Portal** - A web application where patients can report adverse drug reactions
2. **Doctor Portal** - A web application for healthcare professionals to analyze patient reports
3. **AI Model** - A biomedical chatbot that provides drug interaction analysis and predictions

All components share a common data source (`adr_reports.csv`) to ensure information is synchronized across the system.

## Project Structure

```
CliniQAI/
├── app-starter/              # Main application launcher
│   ├── main.py               # Orchestrates the startup of all components
│   └── templates/            # Dashboard templates
│
├── patient-portal/           # Patient-facing web application
│   ├── app.py                # Flask application for patient portal
│   ├── server.py             # Data handling server
│   ├── templates/            # HTML templates
│   └── data/                 # Directory for patient ID counter
│      └── patient_id_counter.txt  # Counter for patient IDs
│
├── doctor-portal/            # Doctor-facing web application
│   ├── app.py                # Flask application for doctor portal
│   ├── data_server.py        # Data processing server
│   └── templates/            # HTML templates
│
├── AI_MODEL/                 # AI-powered analysis tools
│   └── biomedical_chatbot/   # Drug interaction analysis model
│       ├── app.py            # Flask application for AI model
│       ├── ml_model.py       # Machine learning model implementation
│       ├── synthetic_data.py # Data generation for testing
│       ├── requirements.txt  # Dependencies
│       ├── start.bat         # Windows startup script
│       └── start.sh          # Linux/Mac startup script
│
└── adr_reports.csv           # Central database for all ADR reports
```

## System Requirements

- **Python 3.8+** (Python 3.10+ recommended)
- Required Python packages (installed via requirements.txt files)
- Modern web browser (Chrome, Firefox, Edge, etc.)
- Windows, macOS, or Linux operating system

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/CliniQAI.git
   cd CliniQAI
   ```

2. Install dependencies for each component:
   ```
   # For the biomedical chatbot
   cd AI_MODEL/biomedical_chatbot
   pip install -r requirements.txt
   
   # For the patient portal
   cd ../../patient-portal
   pip install -r requirements.txt
   
   # For the doctor portal
   cd ../doctor-portal
   pip install -r requirements.txt
   
   # Return to root directory
   cd ..
   ```

## Running the Application

### Method 1: Using the App Starter (Recommended)

The App Starter launches all components simultaneously and provides a central dashboard:

```
cd app-starter
python main.py
```

This will start all three components and launch the main dashboard at http://localhost:8080.

### Method 2: Running Components Individually

You can also run each component separately:

1. **Start the Patient Portal**:
   ```
   cd patient-portal
   python app.py
   ```
   Access at http://localhost:8083

2. **Start the Doctor Portal**:
   ```
   cd doctor-portal
   python app.py
   ```
   Access at http://localhost:8082

3. **Start the AI Model**:
   ```
   cd AI_MODEL/biomedical_chatbot
   python app.py
   ```
   Access at http://localhost:8084

### On Windows (Alternative)

For Windows users, the biomedical chatbot provides a convenient batch file:

```
# Navigate to the biomedical chatbot directory
cd AI_MODEL/biomedical_chatbot

# Run the batch file
start.bat
```

## How to Use

### 1. Patient Portal

The Patient Portal allows patients to:
- Submit new adverse drug reaction reports
- View previously submitted reports
- Track their unique patient ID

To submit a report:
1. Access the patient portal at http://localhost:8083
2. Fill out the form with details about the drug, medical condition, adverse reaction, etc.
3. Submit the form to generate a unique patient ID and store the report

### 2. Doctor Portal

The Doctor Portal allows healthcare professionals to:
- Search for specific drug-condition combinations
- View patient-reported adverse reactions
- Analyze patterns and correlations
- Access the AI model for prediction when no matches are found
- Add new drug reports with comprehensive information

To analyze data:
1. Access the doctor portal at http://localhost:8082
2. Use the search functionality to find specific drug-condition combinations
3. Review matching records and analysis
4. If no matches are found, a link to the AI model will be provided

### 3. AI Model / Biomedical Chatbot

The AI model provides:
- Drug interaction analysis
- Adverse reaction prediction
- Access to a comprehensive medical condition database

To use the AI model:
1. Access directly at http://localhost:8084 or through the Doctor Portal
2. Enter information about the patient, current medications, and drug to analyze
3. Receive detailed analysis of potential adverse reactions

## Data Management

The system uses a centralized `adr_reports.csv` file to store all adverse drug reaction reports. This file is accessed and updated by both the patient and doctor portals, ensuring all components have access to the same data.

## Troubleshooting

- **Port Conflicts**: If any of the ports (8080, 8082, 8083, 8084) are already in use, you may need to modify the port numbers in the respective app.py files.
- **Missing Dependencies**: Ensure all requirements are installed using the requirements.txt files.
- **File Permissions**: Make sure the application has write access to the data directory.

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Contributing

Contributions are welcome! Please submit a pull request or open an issue for any enhancements or bug fixes.
