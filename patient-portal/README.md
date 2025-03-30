# HealthcareAI Patient Portal

## Overview
The HealthcareAI Patient Portal is a web application built using Flask that allows users to submit and view adverse drug reaction reports. The application serves as a platform for healthcare professionals and patients to report and track drug-related side effects.

## Project Structure
```
HealthcareAI
├── patient-portal
│   ├── app.py                # Main entry point of the Flask application
│   ├── templates
│   │   └── index.html        # Frontend HTML structure
│   ├── static
│   │   ├── css               # CSS files for styling
│   │   ├── js                # JavaScript files for interactivity
│   │   └── images            # Image files used in the frontend
│   ├── data
│   │   ├── adr_reports.csv    # CSV file for storing adverse drug reaction reports
│   │   └── patient_id_counter.txt # File for tracking patient ID counter
│   └── README.md             # Documentation for the project
```

## Setup Instructions
1. **Clone the Repository**
   Clone this repository to your local machine using:
   ```
   git clone <repository-url>
   ```

2. **Navigate to the Project Directory**
   ```
   cd HealthcareAI/patient-portal
   ```

3. **Install Dependencies**
   Ensure you have Python installed, then install Flask and any other required packages:
   ```
   pip install Flask
   ```

4. **Run the Application**
   Start the Flask application by running:
   ```
   python app.py
   ```
   The application will be accessible at `http://localhost:8080`.

## Usage
- **Submitting Reports**: Users can submit adverse drug reaction reports through the frontend interface.
- **Viewing Reports**: Users can view previously submitted reports, which are stored in a CSV file.

## Contributing
Contributions are welcome! Please submit a pull request or open an issue for any enhancements or bug fixes.

## License
This project is licensed under the MIT License. See the LICENSE file for more details.