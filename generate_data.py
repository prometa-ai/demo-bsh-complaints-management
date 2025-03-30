import json
import random
import getpass
import psycopg2
from datetime import datetime, timedelta
from faker import Faker

# Initialize Faker with English locale
fake = Faker('en_US')

# Define refrigerator problem types
refrigerator_problems = [
    "Not Cooling", 
    "Temperature Fluctuations", 
    "Ice Maker Issues", 
    "Excessive Frost", 
    "Water Leakage", 
    "Unusual Noise", 
    "Door Seal Problems", 
    "Display Issues", 
    "Automatic Defrost Problems", 
    "Compressor Problems",
    "Lighting Issues",
    "Bad Smell"
]

# Define detailed problem descriptions
problem_descriptions = [
    "The refrigerator has stopped cooling properly. The temperature inside is much higher than the setting indicates.",
    "The refrigerator temperature fluctuates significantly. Sometimes it's too cold and freezes the food, other times it's not cold enough.",
    "The ice maker is not producing ice or is producing unusually small or incomplete ice cubes.",
    "There is excessive frost buildup in the freezer section that doesn't defrost automatically.",
    "There is water leaking from the refrigerator, either inside or forming puddles on the floor.",
    "The refrigerator is making unusual noises like clicking, buzzing, or a loud hum that wasn't there before.",
    "The door seal appears to be worn, torn, or not sealing properly, making the door hard to close or allowing cold air to escape.",
    "The display panel is not working correctly. Either some segments don't light up or it shows incorrect information.",
    "The defrost system isn't working properly, causing ice buildup on the back wall of the refrigerator.",
    "The compressor seems to be running continuously, or it doesn't turn on at all.",
    "One or more lights inside the refrigerator are not working, even after replacing the bulbs.",
    "There is a bad smell inside the refrigerator even after cleaning it thoroughly."
]

# Define frequency options
frequency_options = ["Constant", "Intermittent", "Occasional", "Daily", "Weekly"]

# Define warranty status options
warranty_status_options = ["Active", "Expired", "Void"]

# Define preferred resolution options
preferred_resolution_options = ["Repair", "Replacement", "Refund", "Technical Assistance"]

# Define ventilation options
ventilation_options = ["Good", "Average", "Poor", "Unknown"]

# Service representative initial assessment templates
initial_assessment_templates = [
    "Customer's {problem_type} complaint was verified during the initial assessment. The {component} was tested and showed abnormal readings.",
    "Initial examination confirmed the {problem_type} as described by the customer. The {component} appears to be functioning below expected parameters.",
    "Diagnostic testing verified the customer's report of {problem_type}. When testing the {component}, found significant deviations from normal operation.",
    "Upon initial examination, the {problem_type} was confirmed. The {component} showed signs of {issue} which is likely causing the reported issue.",
    "Preliminary testing indicates that the customer's report of {problem_type} is accurate. The {component} is not performing within acceptable parameters."
]

# Service representative immediate actions taken templates
immediate_actions_templates = [
    "Performed a full system diagnostic test. Reset the control board and provided temporary settings to mitigate the issue until a full repair can be scheduled.",
    "Cleared the ice buildup and applied a temporary fix to improve the sealing. Adjusted the temperature settings to optimal levels based on ambient conditions.",
    "Checked all electrical connections and reseated them. Updated the firmware on the control panel and reset the system to factory settings.",
    "Cleaned the condenser coils and checked the refrigerant pressure. Performed a manual defrost cycle to clear any ice blockages.",
    "Inspected and cleaned the drain line to prevent further water leakage. Adjusted the leveling feet to ensure proper drainage."
]

# Service representative recommendations templates
recommendations_templates = [
    "Recommend scheduling a service appointment for a {component} replacement. This is covered under the warranty and should resolve the {problem_type} permanently.",
    "The unit requires a thorough maintenance service including cleaning of the {component} and recalibration of the temperature sensors. Will schedule a follow-up appointment.",
    "Based on the diagnosis, the {component} needs to be replaced. I've ordered the part and will schedule installation once it arrives.",
    "Recommend a complete service check of all systems. The {problem_type} appears to be caused by multiple factors that require extensive troubleshooting.",
    "The {component} is showing signs of failure and will need replacement soon. Recommend scheduling this service within the next 30 days to prevent complete failure."
]

def generate_random_date(start_date, end_date):
    """Generate a random date between start_date and end_date."""
    time_between_dates = end_date - start_date
    days_between_dates = time_between_dates.days
    random_number_of_days = random.randrange(days_between_dates)
    return start_date + timedelta(days=random_number_of_days)

def generate_complaint():
    """Generate a random complaint data structure."""
    # Generate dates
    current_date = datetime.now()
    purchase_date = generate_random_date(current_date - timedelta(days=1825), current_date - timedelta(days=30))
    warranty_expiration_date = purchase_date + timedelta(days=730)  # 2-year warranty
    problem_first_date = generate_random_date(purchase_date, current_date)
    complaint_date = generate_random_date(problem_first_date, current_date)
    
    # Randomly select 1-3 problems
    num_problems = random.randint(1, 3)
    selected_problems = random.sample(refrigerator_problems, num_problems)
    
    # Select one of the problems for detailed description
    main_problem_type = random.choice(selected_problems)
    main_problem_index = refrigerator_problems.index(main_problem_type)
    detailed_description = problem_descriptions[main_problem_index]
    
    # Randomly determine if a repair was attempted
    repair_attempted = random.choice([True, False])
    repair_details = ""
    if repair_attempted:
        repair_details = f"I tried to {random.choice(['reset the unit', 'clean the coils', 'adjust the temperature settings', 'defrost manually', 'check for loose connections'])}. It did not resolve the issue."
    
    # Determine warranty status based on dates
    if current_date < warranty_expiration_date:
        warranty_status = "Active"
    else:
        warranty_status = random.choice(["Expired", "Void"])
    
    # Generate random components
    components = ["compressor", "thermostat", "control board", "ice maker", "door seal", "condenser coils", "evaporator fan", "defrost timer"]
    component = random.choice(components)
    issue = random.choice(["wear", "malfunction", "damage", "failure", "misalignment"])
    
    # Generate service representative notes using templates
    initial_assessment = random.choice(initial_assessment_templates).format(
        problem_type=main_problem_type.lower(),
        component=component,
        issue=issue
    )
    
    immediate_actions_taken = random.choice(immediate_actions_templates)
    
    recommendations = random.choice(recommendations_templates).format(
        component=component,
        problem_type=main_problem_type.lower()
    )
    
    # Generate availability days (3-5 random weekdays)
    weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    availability_days = random.sample(weekdays, random.randint(3, 5))
    
    # Create the complaint data structure
    complaint = {
        "customerInformation": {
            "fullName": fake.name(),
            "address": fake.street_address(),
            "city": fake.city(),
            "stateProvince": fake.state(),
            "postalCode": fake.zipcode(),
            "phoneNumber": fake.phone_number(),
            "emailAddress": fake.email()
        },
        "productInformation": {
            "modelNumber": f"BSH-R{fake.random_int(min=1000, max=9999)}",
            "serialNumber": fake.uuid4().upper()[:12],
            "dateOfPurchase": purchase_date.isoformat(),
            "placeOfPurchase": random.choice(["Home Depot", "Best Buy", "Lowes", "Costco", "Amazon", "Walmart", "Target"])
        },
        "warrantyInformation": {
            "warrantyStatus": warranty_status,
            "warrantyExpirationDate": warranty_expiration_date.isoformat()
        },
        "complaintDetails": {
            "dateOfComplaint": complaint_date.isoformat(),
            "natureOfProblem": selected_problems,
            "detailedDescription": detailed_description,
            "problemFirstOccurrence": problem_first_date.isoformat(),
            "frequency": random.choice(frequency_options),
            "repairAttempted": repair_attempted,
            "repairDetails": repair_details if repair_attempted else ""
        },
        "environmentalConditions": {
            "roomTemperature": f"{random.randint(60, 85)}°F",
            "ventilation": random.choice(ventilation_options),
            "recentEnvironmentalChanges": random.choice([
                "Recently moved the refrigerator to a new location", 
                "No recent changes", 
                "Recent power outage", 
                "Changed room temperature settings", 
                "Remodeled kitchen"
            ])
        },
        "customerAcknowledgment": {
            "preferredResolution": random.choice(preferred_resolution_options),
            "availabilityForServiceVisit": availability_days,
            "additionalComments": random.choice([
                "Need this fixed as soon as possible", 
                "Prefer morning appointments", 
                "Please call before visiting", 
                "Already had a bad experience with previous repair attempts", 
                ""
            ])
        },
        "serviceRepresentativeNotes": {
            "initialAssessment": initial_assessment,
            "immediateActionsTaken": immediate_actions_taken,
            "recommendations": recommendations
        },
        "signatures": {
            "customerSignature": fake.name(),
            "customerSignatureDate": complaint_date.isoformat(),
            "serviceRepresentativeSignature": fake.name(),
            "serviceRepresentativeSignatureDate": complaint_date.isoformat()
        }
    }
    
    return complaint

def setup_database():
    """Create complaints table in the database if it doesn't exist."""
    username = getpass.getuser()
    
    try:
        conn = psycopg2.connect(
            host="localhost",
            user=username,
            database="bsh_english_complaints",
            port="5432"
        )
        cursor = conn.cursor()
        
        # Create complaints table if it doesn't exist
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS complaints (
            id SERIAL PRIMARY KEY,
            data JSONB NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("Database setup completed successfully.")
        return True
    except Exception as e:
        print(f"Error setting up database: {e}")
        return False

def generate_and_store_complaints(num_complaints=8773):
    """Generate and store random complaints in the database."""
    username = getpass.getuser()
    
    try:
        conn = psycopg2.connect(
            host="localhost",
            user=username,
            database="bsh_english_complaints",
            port="5432"
        )
        cursor = conn.cursor()
        
        # Clear existing data if any
        cursor.execute("TRUNCATE complaints RESTART IDENTITY")
        conn.commit()
        print(f"Cleared existing data. Generating {num_complaints} new complaints...")
        
        # Generate and insert complaints in batches
        batch_size = 100
        for i in range(0, num_complaints, batch_size):
            batch_end = min(i + batch_size, num_complaints)
            batch = [(json.dumps(generate_complaint()),) for _ in range(i, batch_end)]
            
            cursor.executemany(
                "INSERT INTO complaints (data) VALUES (%s)",
                batch
            )
            conn.commit()
            
            print(f"Progress: {batch_end}/{num_complaints} complaints generated ({batch_end/num_complaints*100:.1f}%)")
        
        cursor.close()
        conn.close()
        
        print(f"Successfully generated and stored {num_complaints} complaints.")
        return True
    except Exception as e:
        print(f"Error generating complaints: {e}")
        return False

if __name__ == "__main__":
    print("Setting up database...")
    if setup_database():
        print("Generating complaints data...")
        generate_and_store_complaints() 