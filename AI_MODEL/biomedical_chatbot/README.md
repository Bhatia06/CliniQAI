# Biomedical Chatbot

An AI-powered biomedical chatbot for analyzing drug interactions and providing medical information.

## Features

- Drug interaction analysis
- Adverse reaction prediction
- Medical condition database
- API for integrating with healthcare applications

## Requirements

- Python 3.8 or higher
- Required Python packages listed in `requirements.txt`

## Quick Start

### Windows

Simply double-click the `start.bat` file, which will:
1. Check if Python is installed
2. Set up a virtual environment if needed
3. Install all dependencies from requirements.txt
4. Start the application

### macOS/Linux

1. Make the start script executable:
```bash
chmod +x start.sh
```

2. Run the script:
```bash
./start.sh
```

The script will set up everything automatically and start the application.

## Manual Installation

If you prefer to set up manually:

1. Clone the repository:

```bash
git clone <repository-url>
cd <repository-directory>/AI_MODEL/biomedical_chatbot
```

2. Create a virtual environment:

```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

1. Start the application:

```bash
python app.py
```

2. Access the application in your browser:

```
http://localhost:8084
```

## API Endpoints

- `GET /api/medications` - Get list of available medications
- `GET /api/conditions` - Get list of available medical conditions
- `POST /api/analyze` - Analyze medications, conditions, and potential interactions

## Integration

This application is designed to integrate with the Healthcare AI System, which includes:

- Doctor Portal (http://localhost:8082)
- Patient Portal (http://localhost:8083)
- Main Dashboard (http://localhost:8080)

## Development

To set up a development environment:

1. Clone the repository
2. Run `python setup.py` to create a virtual environment and install dependencies
3. Make your changes
4. Test thoroughly before submitting changes

## Notes for Deployment

- The application is configured to run on port 8084
- CORS is enabled for cross-domain requests
- Environment variables can be set in a `.env` file 