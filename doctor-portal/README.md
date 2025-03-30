# Doctor Portal

## Overview
The Doctor Portal is a web application designed to assist healthcare professionals in searching for drug-condition combinations and retrieving relevant medical information. The application is built using Flask for the backend and a modern frontend framework.

## Project Structure
```
doctor-portal
├── backend
│   ├── app.py                # Main entry point of the Flask application
│   ├── data
│   │   └── adr_reports.csv    # CSV data containing drug and medical condition records
│   ├── static                # Directory for serving static files (CSS, JS, images)
│   └── templates             # Directory for HTML templates
├── frontend
│   ├── public                # Directory for public assets (e.g., index.html)
│   └── src                   # Source code for the frontend application
├── requirements.txt          # Lists dependencies for the Flask application
└── README.md                 # Documentation for the project
```

## Setup Instructions

1. **Clone the Repository**
   ```
   git clone <repository-url>
   cd doctor-portal
   ```

2. **Install Dependencies**
   It is recommended to use a virtual environment. You can create one using:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

   Then install the required packages:
   ```
   pip install -r requirements.txt
   ```

3. **Run the Application**
   Navigate to the `backend` directory and run the Flask application:
   ```
   python app.py
   ```

   The application will be accessible at `http://localhost:8082`.

## Usage
- **Search for Drug-Condition Combinations**
  Use the `/api/search` endpoint to search for specific drug-condition combinations by providing the necessary query parameters.

- **Retrieve Unique Drug Names**
  Access the `/api/drugs` endpoint to get a list of all unique drug names available in the dataset.

- **Retrieve Unique Medical Conditions**
  Use the `/api/conditions` endpoint to obtain a list of unique medical conditions.

## Contributing
Contributions are welcome! Please submit a pull request or open an issue for any enhancements or bug fixes.

## License
This project is licensed under the MIT License. See the LICENSE file for more details.