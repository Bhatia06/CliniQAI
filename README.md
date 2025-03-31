# CliniQAI: Adverse Drug Reaction (ADR) Management System

<div align="center">
  <img src="https://img.shields.io/badge/Python-3.8%2B-blue?style=for-the-badge&logo=python">
  <img src="https://img.shields.io/badge/Flask-2.0.1-green?style=for-the-badge&logo=flask">
  <img src="https://img.shields.io/badge/Machine%20Learning-Enabled-brightgreen?style=for-the-badge&logo=scikit-learn">
  <img src="https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge">
</div>

<div align="center">
  <p><strong>An Intelligent Healthcare System for reporting, analyzing and predicting Adverse Drug Reactions</strong></p>
</div>

## 🌟 Overview

CliniQAI is a comprehensive healthcare platform that integrates patient reporting, physician analysis, and AI-powered predictions of adverse drug reactions (ADRs). The system features:

- 🏥 **Doctor Portal**: Advanced interface for healthcare professionals to analyze ADR reports
- 👤 **Patient Portal**: User-friendly interface for patients to report adverse reactions
- 🤖 **AI Module**: Intelligent prediction system for drug interactions and adverse effects
- 🔄 **Centralized Data Management**: Synchronized information across all system components

## 📋 Table of Contents

- [Features](#-features)
- [System Architecture](#-system-architecture)
- [Installation](#-installation)
- [Usage Guide](#-usage-guide)
- [Project Structure](#-project-structure)
- [API Documentation](#-api-documentation)
- [Development](#-development)
- [Contributing](#-contributing)
- [License](#-license)

## ✨ Features

### Doctor Portal
- Comprehensive search of patient-reported ADRs
- Analysis of drug-condition relationships
- Statistics and visualizations of ADR patterns
- Direct integration with AI predictions for novel drug combinations

### Patient Portal
- Simple reporting interface for adverse reactions
- Tracking of submitted reports
- Unique patient ID system
- Privacy-focused design

### AI Module
- Machine learning model for predicting drug interactions
- Analysis of patient-specific risk factors
- Comprehensive medication and condition database
- Real-time prediction of potential adverse effects

## 🏗️ System Architecture

CliniQAI uses a modular architecture with three main components connected through a central launcher:

```
┌─────────────────┐      ┌──────────────────┐       ┌─────────────────┐
│   Doctor Portal │      │  Patient Portal  │      │     AI Model    │
│   (Port 8082)   │      │   (Port 8083)    │      │   (Port 8084)   │
└────────┬────────┘      └────────┬─────────┘      └────────┬────────┘
         │                        │                         │
         │                        │                         │
         └────────────────┬───────┴──────────────────┬──────┘
                          │                          │
                          ▼                          ▼
                ┌────────────────────┐      ┌────────────────────┐
                │    App Starter     │      │  Shared Data File  │
                │    (Port 8080)     │      │  (adr_reports.csv) │
                └────────────────────┘      └────────────────────┘
```

The system uses Flask for all web interfaces and RESTful APIs, with data shared through a common CSV file.

## 🚀 Installation

### Prerequisites
- Python 3.8 or higher
- Git (for cloning the repository)
- Modern web browser

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/CliniQAI.git
   cd CliniQAI
   ```

2. **Easy Setup (Recommended)**
   
   Simply run the included startup script:

   ```
   run.bat
   ```

   This script will automatically:
   - Create a virtual environment
   - Install all required dependencies
   - Start the application components
   
3. **Access the application**
   - Main Dashboard: http://localhost:8080
   - Doctor Portal: http://localhost:8082
   - Patient Portal: http://localhost:8083
   - AI Model: http://localhost:8084

4. **Manual Setup (Alternative)**

   If you prefer to set up manually:

   ```bash
   # Create and activate a virtual environment
   python -m venv venv
   venv\Scripts\activate

   # Install dependencies
   pip install -r requirements.txt

   # Start the application
   cd app-starter
   python main.py
   ```

## 📘 Usage Guide

### Doctor Portal

1. Navigate to http://localhost:8082
2. Use the search interface to find drug-condition combinations
3. View detailed analysis of matching records
4. For novel combinations, follow the AI model link for predictions
5. Add new drug reports with the submission form

### Patient Portal

1. Navigate to http://localhost:8083
2. Fill out the form with information about your adverse reaction
3. Submit the form to receive a unique patient ID
4. View your submitted reports at the bottom of the page

### AI Model

1. Navigate to http://localhost:8084
2. Enter patient information (age, weight)
3. Select current medications and pre-existing conditions
4. Enter the drug to analyze
5. Submit to receive AI-powered prediction of potential adverse reactions

## 📁 Project Structure

```
CliniQAI/
├── app-starter/              # Main application launcher
│   ├── main.py               # Orchestrates startup of components
│   └── templates/            # Main dashboard interface
│
├── patient-portal/           # Patient-facing application
│   ├── app.py                # Flask server for patient portal
│   ├── server.py             # Data handling
│   ├── templates/            # HTML templates
│   └── data/                 # Patient ID tracking
│
├── doctor-portal/            # Healthcare professional interface
│   ├── app.py                # Flask server for doctor portal
│   ├── data_server.py        # Data analysis functions
│   └── templates/            # HTML templates
│
├── AI_MODEL/                 # Machine learning component
│   └── biomedical_chatbot/   # Drug interaction prediction
│       ├── app.py            # Flask server for AI model
│       ├── ml_model.py       # ML model implementation
│       ├── synthetic_data.py # Data generation for model
│       ├── requirements.txt  # ML-specific dependencies
│       ├── templates/        # HTML templates
│       └── static/           # CSS, JS and static files
│
├── requirements.txt          # Project dependencies
├── .gitignore                # Git ignore file
├── adr_reports.csv           # Shared data file
└── README.md                 # This documentation
```

## 🔌 API Documentation

### Patient Portal API

- `GET /api/reports` - Retrieve all submitted reports
- `POST /api/reports` - Submit a new adverse reaction report

### Doctor Portal API

- `GET /api/search` - Search for drug-condition combinations
- `GET /api/drugs` - Get list of all drugs in the database
- `POST /api/drugs/add` - Add a new drug report
- `GET /api/conditions` - Get list of all medical conditions

### AI Model API

- `POST /api/analyze` - Analyze drug interactions and predict adverse reactions
- `GET /api/medications` - Get list of all medications
- `GET /api/conditions` - Get list of all medical conditions

## 👨‍💻 Development

### Setting Up Development Environment

1. Fork the repository
2. Clone your fork
3. Create a new branch for your feature
4. Make your changes
5. Run tests
6. Submit a pull request

### Coding Standards

- Follow PEP 8 style guide for Python code
- Use descriptive variable and function names
- Comment complex logic
- Write tests for new features

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the project
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👏 Acknowledgments

- **Cursor AI**: This project was developed with the assistance of [Cursor AI](https://cursor.com/), which provided code suggestions, refactoring help, and documentation guidance. We acknowledge and appreciate this AI assistance in our development process.

---

<div align="center">
  <p align="center">
    Made with ❤️ by the Cryptic Hunters:<br>
    <a href="https://github.com/yuv294">@yuv294</a> • 
    <a href="https://github.com/sathwikhbhat">@sathwikhbhat</a> • 
    <a href="https://github.com/Bhatia06">@Bhatia06</a> • 
    <a href="https://github.com/adigocrazy">@AdiGoCrazy</a>
  </p>
  <p align="center">
    <sub>© 2025 CliniQAI. All rights reserved.</sub>
  </p>
</div>
