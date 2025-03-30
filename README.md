# BSH Customer Complaints Management System

A comprehensive system for managing customer complaints about refrigerators, integrating technical assessment notes and AI analysis.

## Features

- **Unified Complaint View**: All complaint information, technical notes, and AI analysis in a single view
- **Complaint Management**: Track customer complaints, warranty status, and product information
- **Technical Assessment**: Record technical notes, error codes, faulty parts, and repair details
- **AI Analysis**: Get an AI-generated quality analysis based on complaint and technical assessment data
- **Statistical Dashboard**: Visualize complaint trends, common issues, and warranty status

## Installation

1. Clone the repository:
   ```
   git clone [repository-url]
   cd bsh_customer_complaints_management_v1
   ```

2. Create a virtual environment and install dependencies:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Configure the environment variables:
   ```
   cp .env.example .env
   ```
   Edit `.env` and add your OpenAI API key if you want to use the AI analysis feature.

4. Initialize the database:
   ```
   python setup_database.py
   ```

5. Run the application:
   ```
   python app.py
   ```

6. Open your browser and go to:
   ```
   http://127.0.0.1:5001
   ```

## Usage

### Complaint Management
- View all complaints on the Complaints page
- Add new complaints through the form
- View detailed information about individual complaints

### Technical Assessment
- Add technical notes to complaints after service visits
- Record error codes, faulty parts, repairs performed, and customer satisfaction

### Unified View
- Access the unified view from any complaint page
- See all complaint details and technical notes in one place
- View the AI-generated quality analysis for complaints with technical notes

### Statistics
- View trends and patterns on the Statistics page
- Analyze common issues and warranty status distribution
- Track complaint volumes over time

## AI Analysis Integration

The system includes an AI feature that analyzes complaints and technical notes to provide:

1. Final opinion on the case
2. Detailed reasoning based on provided information
3. Specific recommendations for further action

To enable this feature, you need an OpenAI API key in the `.env` file.

## Dependencies

- Flask: Web framework
- SQLite/PostgreSQL: Database
- OpenAI: AI analysis
- Matplotlib: Chart generation
- Bootstrap: Frontend styling

## Project Structure

- `generate_and_store_data.py` - Script to generate synthetic customer complaints data and store it in PostgreSQL
- `query_complaints.py` - Menu-driven interface to query and analyze the complaints data
- `README.md` - This documentation file

## Data Structure

Each complaint is stored as a JSON document with the following structure:

```json
{
  "customerInformation": {
    "fullName": "",
    "address": "",
    "city": "",
    "stateProvince": "",
    "postalCode": "",
    "phoneNumber": "",
    "emailAddress": ""
  },
  "productInformation": {
    "modelNumber": "",
    "serialNumber": "",
    "dateOfPurchase": "",
    "placeOfPurchase": ""
  },
  "warrantyInformation": {
    "warrantyStatus": "",
    "warrantyExpirationDate": ""
  },
  "complaintDetails": {
    "dateOfComplaint": "",
    "natureOfProblem": [],
    "detailedDescription": "",
    "problemFirstOccurrence": "",
    "frequency": "",
    "repairAttempted": "",
    "repairDetails": ""
  },
  "environmentalConditions": {
    "roomTemperature": "",
    "ventilation": "",
    "recentEnvironmentalChanges": ""
  },
  "customerAcknowledgment": {
    "preferredResolution": "",
    "availabilityForServiceVisit": [],
    "additionalComments": ""
  },
  "serviceRepresentativeNotes": {
    "initialAssessment": "",
    "immediateActionsTaken": "",
    "recommendations": ""
  },
  "signatures": {
    "customerSignature": "",
    "customerSignatureDate": "",
    "serviceRepresentativeSignature": "",
    "serviceRepresentativeSignatureDate": ""
  }
}
```

## Setup and Installation

### Prerequisites

- Python 3.8 or higher
- PostgreSQL
- Required Python packages: `faker`, `psycopg2-binary`, `pandas`, `matplotlib`, `tabulate`

### Generating Synthetic Data

To generate 10,000 synthetic customer complaints and store them in PostgreSQL:

```