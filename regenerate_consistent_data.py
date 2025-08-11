import random
import json
import sqlite3
from datetime import datetime, timedelta
import time
import getpass
from faker import Faker

# Set Faker to use English locale
fake = Faker('en_US')

# Problem categories
refrigerator_problems = [
    "Temperature Control Issues",
    "Cooling Problems",
    "Freezing Issues",
    "Ice Maker Failure",
    "Water Dispenser Problem",
    "Noise Issues",
    "Door Seal Damage",
    "Defrost System Failure",
    "Lighting Issues",
    "Digital Panel Malfunction",
    "Compressor Problems",
    "Refrigerant Leak"
]

# Problem descriptions
problem_descriptions = [
    "The refrigerator is not maintaining the set temperature. It's either too warm or too cold.",
    "The refrigerator compartment is not cooling properly. Food is spoiling faster than it should.",
    "Items in the freezer are not freezing completely or are thawing unexpectedly.",
    "The ice maker is not producing ice or is producing ice that has an off taste or odor.",
    "The water dispenser is leaking, not dispensing water, or dispensing water that has an off taste.",
    "The refrigerator is making unusual noises such as clicking, buzzing, or rattling sounds.",
    "The door seal appears damaged or is not creating a proper seal when the door is closed.",
    "There is excessive frost buildup in the freezer compartment that is not being removed by the defrost cycle.",
    "One or more lights inside the refrigerator are not working, even after replacing the bulbs.",
    "The digital display panel is not functioning properly, showing errors, or not responding to controls.",
    "The compressor is running constantly or not running at all, affecting the cooling performance.",
    "There appears to be a refrigerant leak as evidenced by poor cooling and possibly a hissing sound."
]

# Component lists mapped to problems
component_mapping = {
    "Temperature Control Issues": ["Temperature Sensor", "Thermostat", "Main Control Board"],
    "Cooling Problems": ["Compressor", "Condenser", "Refrigerant System"],
    "Freezing Issues": ["Evaporator", "Thermostat", "Refrigerant System"],
    "Ice Maker Failure": ["Ice Maker", "Water Inlet Valve", "Temperature Sensor"],
    "Water Dispenser Problem": ["Water Inlet Valve", "Water Filter", "Dispenser Control Board"],
    "Noise Issues": ["Compressor", "Fan Motor", "Condenser"],
    "Door Seal Damage": ["Door Seal", "Door Hinge", "Door Alignment System"],
    "Defrost System Failure": ["Defrost Timer", "Defrost Heater", "Defrost Sensor"],
    "Lighting Issues": ["LED Lighting System", "Light Bulb", "Electronic Board"],
    "Digital Panel Malfunction": ["Main Control Board", "Display Panel", "Electronic Board"],
    "Compressor Problems": ["Compressor", "Start Relay", "Overload Protector"],
    "Refrigerant Leak": ["Refrigerant System", "Condenser", "Compressor"]
}

# Issue patterns mapped to problems
issue_mapping = {
    "Temperature Control Issues": ["calibration disorder", "sensor failure", "electrical failure"],
    "Cooling Problems": ["insufficient performance", "blockage", "mechanical failure"],
    "Freezing Issues": ["calibration disorder", "leakage", "insufficient performance"],
    "Ice Maker Failure": ["mechanical failure", "blockage", "electrical failure"],
    "Water Dispenser Problem": ["blockage", "leakage", "mechanical failure"],
    "Noise Issues": ["abnormal noise", "mechanical failure", "wear"],
    "Door Seal Damage": ["wear", "aging", "mechanical failure"],
    "Defrost System Failure": ["electrical failure", "insufficient performance", "sensor failure"],
    "Lighting Issues": ["short circuit", "electrical failure", "burn out"],
    "Digital Panel Malfunction": ["electronic failure", "short circuit", "software issue"],
    "Compressor Problems": ["overheating", "mechanical failure", "electrical failure"],
    "Refrigerant Leak": ["leakage", "aging", "mechanical failure"]
}

# Frequency options
frequency_options = ["Continuous", "Intermittent", "Periodic", "Random", "Only when..."]

# Ventilation options
ventilation_options = ["Good", "Poor", "Partially Blocked"]

# Preferred resolution options
preferred_resolution_options = ["Repair", "Replacement", "Refund", "Partial Refund", "Extended Warranty", "Technical Support"]

# Initial assessment templates for customer service
initial_assessment_templates = [
    "Upon initial examination, the {problem_type} was confirmed. The {component} showed signs of {issue} which is likely causing the reported issue.",
    "Initial diagnosis indicates that the {problem_type} is due to a {issue} in the {component}.",
    "The {problem_type} was verified during the initial assessment. Signs of {issue} in the {component} were observed.",
    "Initial inspection confirms customer report of {problem_type}. The {component} appears to be experiencing {issue}."
]

# Immediate actions taken templates
immediate_actions_templates = [
    "Cleaned the condenser coils and checked the refrigerant pressure. Performed a manual defrost cycle to clear any ice blockages.",
    "Reset the main control board and checked all electrical connections. Updated firmware to the latest version.",
    "Adjusted the temperature settings and cleared any blockages in the vent system. Checked for proper airflow.",
    "Inspected the compressor and cooling system for any obvious leaks or damages. Tested all operational modes.",
    "Checked the door seals for proper alignment and cleaned all gaskets. Verified that doors close and seal properly."
]

# Recommendations templates for customer service
recommendations_templates = [
    "The {component} is showing signs of failure and will need replacement soon. Recommend scheduling this service within the next 30 days to prevent complete failure.",
    "Based on the assessment, we recommend a full service maintenance to address the {problem_type} and prevent future issues.",
    "The {component} needs immediate replacement to resolve the {problem_type}. Parts have been ordered and will arrive in 3-5 business days.",
    "While a temporary fix has been applied, we recommend a complete system diagnostic to identify any underlying issues causing the {problem_type}.",
    "Regular maintenance every 6 months is recommended to prevent future {problem_type} issues. We can schedule the next service appointment now."
]

# Technician names
technician_names = [
    "John Smith", "Michael Johnson", "David Williams", "Sarah Brown", "Jessica Davis", 
    "Robert Miller", "James Wilson", "Mary Taylor", "Thomas Anderson", 
    "Charles Martin", "Daniel Thompson", "Mark White", "Kevin Harris", "Steven Clark"
]

# Function to generate a random date within a range
def random_date(start_date, end_date):
    """Generate a random date between start_date and end_date."""
    time_between_dates = end_date - start_date
    days_between_dates = time_between_dates.days
    random_number_of_days = random.randrange(max(1, days_between_dates))
    return start_date + timedelta(days=random_number_of_days)

def generate_country_specific_data(country):
    """Generate customer data specific to a country."""
    # Map country names to valid Faker locales
    locale_map = {
        "United States": "en_US",
        "Canada": "en_CA",
        "United Kingdom": "en_GB",
        "Germany": "de_DE",
        "France": "fr_FR"
    }
    locale = locale_map.get(country, "en_US")
    faker = Faker(locale)
    
    # Generate a name format appropriate for the country
    name = faker.name()
    
    # Generate address information
    address = faker.street_address()
    city = faker.city()
    
    # Generate postal code
    postal_code = faker.postcode()
    
    # Generate phone number
    phone = faker.phone_number()
    
    # Generate email (with ASCII-only domain)
    name_part = ''.join(c for c in name.lower() if c.isalnum())[:8]
    email = f"{name_part}{random.randint(1, 999)}@example.com"
    
    return {
        "fullName": name,
        "address": address,
        "city": city,
        "stateProvince": faker.state() if country in ["United States"] else "",
        "postalCode": postal_code,
        "phoneNumber": phone,
        "emailAddress": email
    }

def generate_consistent_complaint():
    """Generate a random complaint data structure that will be consistent with technical notes."""
    
    # Generate dates
    current_date = datetime.now()
    purchase_date = random_date(current_date - timedelta(days=1825), current_date - timedelta(days=30))
    warranty_expiration_date = purchase_date + timedelta(days=730)  # 2-year warranty
    problem_first_date = random_date(purchase_date, current_date)
    complaint_date = random_date(problem_first_date, current_date)
    
    # Randomly select 1-3 problems, but ensure they are logically related
    main_problem_index = random.randint(0, len(refrigerator_problems) - 1)
    main_problem_type = refrigerator_problems[main_problem_index]
    
    # Determine selected problems - make sure they're related
    if random.random() < 0.7:  # 70% chance for multiple problems
        num_problems = random.randint(2, 3)
        selected_problems = [main_problem_type]
        
        # Add related problems (e.g., cooling and temperature might be related)
        related_indices = []
        if main_problem_index in [0, 1, 2]:  # Temperature, Cooling, Freezing - related
            related_indices.extend([0, 1, 2])
        elif main_problem_index in [3, 4]:  # Ice Maker, Water Dispenser - related
            related_indices.extend([3, 4])
        elif main_problem_index in [5, 10]:  # Noise and Compressor - related
            related_indices.extend([5, 10])
        
        # Remove the main problem index from related indices to avoid duplicates
        if main_problem_index in related_indices:
            related_indices.remove(main_problem_index)
        
        # If we have related problems, add them
        if related_indices:
            for _ in range(min(num_problems - 1, len(related_indices))):
                idx = random.choice(related_indices)
                selected_problems.append(refrigerator_problems[idx])
                related_indices.remove(idx)
        else:
            # If no logical relation, just add random problems
            available_indices = list(range(len(refrigerator_problems)))
            available_indices.remove(main_problem_index)
            for _ in range(num_problems - 1):
                if not available_indices:
                    break
                idx = random.choice(available_indices)
                selected_problems.append(refrigerator_problems[idx])
                available_indices.remove(idx)
    else:
        selected_problems = [main_problem_type]
    
    # Get detailed description for the main problem
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
    
    # Get components relevant to the main problem
    component = random.choice(component_mapping.get(main_problem_type, ["Compressor", "Thermostat", "Control Board"]))
    issue = random.choice(issue_mapping.get(main_problem_type, ["wear", "malfunction", "failure"]))
    
    # Generate service representative notes using templates
    initial_assessment = random.choice(initial_assessment_templates).format(
        problem_type=main_problem_type.lower(),
        component=component.lower(),
        issue=issue
    )
    
    immediate_actions_taken = random.choice(immediate_actions_templates)
    
    recommendations = random.choice(recommendations_templates).format(
        component=component.lower(),
        problem_type=main_problem_type.lower()
    )
    
    # Generate availability days (3-5 random weekdays)
    weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    availability_days = random.sample(weekdays, random.randint(3, 5))
    
    # Create the complaint data structure
    complaint = {
        "customerInformation": generate_country_specific_data("United States"),
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
    
    return complaint, main_problem_type, component, issue

def generate_consistent_technical_note(complaint_data, main_problem_type, main_component, main_issue):
    """Generate a technical note that's consistent with the complaint."""
    
    # Extract problem details
    problems = complaint_data.get('complaintDetails', {}).get('natureOfProblem', [main_problem_type])
    
    # Get components based on the main problem type
    relevant_components = component_mapping.get(main_problem_type, ["Compressor", "Thermostat", "Control Board"])
    
    # Ensure the main component is included
    if main_component not in relevant_components:
        relevant_components.append(main_component)
    
    # Get a few more components to inspect (1-3 additional)
    additional_components = random.sample(
        [c for c in set(sum(component_mapping.values(), [])) if c != main_component],
        k=min(3, random.randint(1, 3))
    )
    inspected_components = [main_component] + additional_components
    
    # Get issues related to the main problem
    relevant_issues = issue_mapping.get(main_problem_type, ["wear", "malfunction", "failure"])
    
    # Ensure the main issue is included
    if main_issue not in relevant_issues:
        relevant_issues.append(main_issue)
    
    # Random cause
    causes = ["normal wear and tear", "manufacturing defect", "improper use", "unsuitable environmental conditions",
             "power fluctuations", "shipping damage", "improper cleaning", "normal end of life",
             "previous incorrect repair", "use of incompatible parts", "overloading", "moisture and humidity"]
    cause = random.choice(causes)
    
    # Repair actions
    repair_actions = ["cleaning", "replacement", "calibration", "reprogramming",
                     "soldering", "tightening", "welding", "insulation reinforcement", 
                     "refrigerant addition", "connection renewal", "software update"]
    repair_action = random.choice(repair_actions)
    
    # Additional actions
    additional_actions = ["general system cleaning", "checking all connections", "software update",
                         "general inspection of other parts", "replacement of door seals", "sensor calibration",
                         "resetting the device", "checking refrigerant level"]
    additional_action = random.choice(additional_actions)
    
    # Generate visit date
    complaint_date = datetime.fromisoformat(complaint_data.get('complaintDetails', {}).get('dateOfComplaint', datetime.now().isoformat()))
    visit_date = random_date(complaint_date, datetime.now())
    
    # Decide if parts were replaced
    parts_replaced = []
    if random.random() < 0.7:  # 70% chance to replace parts
        parts_replaced.append(main_component)
        
        # Small chance to replace additional components
        if random.random() < 0.3:
            parts_replaced.extend(random.sample(additional_components, k=random.randint(
                0, min(2, len(additional_components))
            )))
    
    # Create diagnosis text
    fault_diagnosis = f"The {main_problem_type} issue reported by the customer was examined. Tests on the {main_component} detected {main_issue}. Measurement values are {random.randint(15, 50)}% outside the normal range."
    
    # Create root cause text
    root_cause = f"The root cause of the problem is that the {main_component} is not working efficiently due to {main_issue}. This is likely due to {cause}."
    
    # Create solution text
    solution_proposed = f"The {main_component} unit needs to be completely replaced. Additionally, {additional_action} is recommended."
    
    # Create repair details text
    repair_details = ""
    if parts_replaced:
        repair_details = f"Applied {repair_action} to the {main_component}. The old part was completely removed, the new part was installed and tested."
    
    # Decide if follow-up is required
    follow_up_required = random.random() < 0.4
    
    # Create follow-up notes
    follow_up_notes = ""
    if follow_up_required:
        follow_up_notes = f"Contact the customer within a week to check the operation of the {main_component}."
    
    # Generate satisfaction (weighted towards higher scores)
    satisfaction_weights = {1: 0.05, 2: 0.1, 3: 0.2, 4: 0.35, 5: 0.3}
    satisfaction = random.choices(
        population=list(satisfaction_weights.keys()),
        weights=list(satisfaction_weights.values()),
        k=1
    )[0]
    
    # Create technical note data
    technical_note = {
        "technicianName": random.choice(technician_names),
        "visitDate": visit_date.isoformat(),
        "technicalAssessment": {
            "componentInspected": inspected_components,
            "faultDiagnosis": fault_diagnosis,
            "rootCause": root_cause,
            "solutionProposed": solution_proposed
        },
        "partsReplaced": parts_replaced,
        "repairDetails": repair_details,
        "followUpRequired": follow_up_required,
        "followUpNotes": follow_up_notes,
        "customerSatisfaction": str(satisfaction)
    }
    
    return technical_note

def create_special_case_angela_best():
    """Create the special case for Angela Best with lighting issues vs fan motor problems."""
    
    # Generate dates
    current_date = datetime.now()
    purchase_date = random_date(current_date - timedelta(days=1825), current_date - timedelta(days=30))
    warranty_expiration_date = purchase_date + timedelta(days=730)  # 2-year warranty
    problem_first_date = random_date(purchase_date, current_date)
    complaint_date = random_date(problem_first_date, current_date)
    
    # Create Angela Best's complaint with the lighting issue
    complaint = {
        "customerInformation": generate_country_specific_data("Germany"),
        "productInformation": {
            "modelNumber": "BSH-R8480",
            "serialNumber": fake.uuid4().upper()[:12],
            "dateOfPurchase": purchase_date.isoformat(),
            "placeOfPurchase": random.choice(["Home Depot", "Best Buy", "Lowes", "Costco", "Amazon", "Walmart", "Target"])
        },
        "warrantyInformation": {
            "warrantyStatus": "Expired",
            "warrantyExpirationDate": warranty_expiration_date.isoformat()
        },
        "complaintDetails": {
            "dateOfComplaint": complaint_date.isoformat(),
            "natureOfProblem": ["Lighting Issues"],
            "detailedDescription": "One or more lights inside the refrigerator are not working, even after replacing the bulbs.",
            "problemFirstOccurrence": problem_first_date.isoformat(),
            "frequency": "Intermittent",
            "repairAttempted": True,
            "repairDetails": "I tried to check for loose connections. It did not resolve the issue."
        },
        "environmentalConditions": {
            "roomTemperature": f"{random.randint(60, 85)}°F",
            "ventilation": "Poor",
            "recentEnvironmentalChanges": "Changed room temperature settings"
        },
        "customerAcknowledgment": {
            "preferredResolution": "Repair",
            "availabilityForServiceVisit": random.sample(["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"], k=random.randint(3, 5)),
            "additionalComments": "Prefer morning appointments"
        },
        "serviceRepresentativeNotes": {
            "initialAssessment": "Upon initial examination, the lighting issues was confirmed. The defrost timer showed signs of wear which is likely causing the reported issue.",
            "immediateActionsTaken": "Cleaned the condenser coils and checked the refrigerant pressure. Performed a manual defrost cycle to clear any ice blockages.",
            "recommendations": "The defrost timer is showing signs of failure and will need replacement soon. Recommend scheduling this service within the next 30 days to prevent complete failure."
        },
        "signatures": {
            "customerSignature": fake.name(),
            "customerSignatureDate": complaint_date.isoformat(),
            "serviceRepresentativeSignature": fake.name(),
            "serviceRepresentativeSignatureDate": complaint_date.isoformat()
        }
    }
    
    # Create technical note for fan motor issue
    visit_date = random_date(datetime.fromisoformat(complaint_date.isoformat()), datetime.now())
    
    technical_note = {
        "technicianName": "Michael Johnson",
        "visitDate": visit_date.isoformat(),
        "technicalAssessment": {
            "componentInspected": ["Condenser", "Thermostat", "Fan Motor"],
            "faultDiagnosis": "Measurements revealed that the Fan Motor unit is not functioning properly due to calibration disorder.",
            "rootCause": "An calibration disorder caused by moisture and humidity was detected in the Fan Motor part of the refrigerator.",
            "solutionProposed": "The Fan Motor should be replaced and general system cleaning performed. The customer was also informed about regular cleaning."
        },
        "partsReplaced": [],
        "repairDetails": "",
        "followUpRequired": False,
        "followUpNotes": "",
        "customerSatisfaction": "2"
    }
    
    return complaint, technical_note

def regenerate_database():
    """Regenerate the database with consistent complaints and technical notes."""
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    db_path = os.getenv("DB_PATH", "bsh_complaints.db")
    
    try:
        # Ensure directory exists (only if path has a directory component)
        db_dir = os.path.dirname(db_path)
        if db_dir:  # Only create directory if there's a directory path
            os.makedirs(db_dir, exist_ok=True)
        
        # Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Clear existing data
        cursor.execute("DELETE FROM technical_notes")
        cursor.execute("DELETE FROM complaints")
        cursor.execute("DELETE FROM sqlite_sequence WHERE name IN ('complaints', 'technical_notes')")
        conn.commit()
        
        print("Cleared existing data. Generating new data...")
        
        # Generate complaints (fewer to speed up testing)
        num_complaints = 2000
        special_complaint_id = None
        
        # Generate and insert complaints
        for i in range(1, num_complaints + 1):
            if i % 100 == 0:
                print(f"Generated {i} complaints...")
            
            # Generate a consistent complaint and relevant data
            complaint, problem_type, component, issue = generate_consistent_complaint()
            
            # Insert the complaint
            cursor.execute(
                "INSERT INTO complaints (data) VALUES (?)",
                (json.dumps(complaint),)
            )
            complaint_id = cursor.lastrowid
            
            # Add a technical note for about 70% of complaints
            if random.random() < 0.7:
                tech_note = generate_consistent_technical_note(complaint, problem_type, component, issue)
                cursor.execute(
                    "INSERT INTO technical_notes (complaint_id, data) VALUES (?, ?)",
                    (complaint_id, json.dumps(tech_note))
                )
                
            if i % 100 == 0:
                conn.commit()  # Commit in batches for better performance
        
        # Generate the special Angela Best case
        angela_complaint, angela_tech_note = create_special_case_angela_best()
        
        cursor.execute(
            "INSERT INTO complaints (data) VALUES (?)",
            (json.dumps(angela_complaint),)
        )
        angela_complaint_id = cursor.lastrowid
        special_complaint_id = angela_complaint_id
        
        cursor.execute(
            "INSERT INTO technical_notes (complaint_id, data) VALUES (?, ?)",
            (angela_complaint_id, json.dumps(angela_tech_note))
        )
        
        conn.commit()
        
        print(f"Successfully regenerated database with {num_complaints + 1} complaints and technical notes.")
        print(f"Special case 'Angela Best' created with ID: {special_complaint_id}")
        
        cursor.close()
        conn.close()
        
        return True
    except Exception as e:
        print(f"Error regenerating database: {e}")
        return False

if __name__ == "__main__":
    regenerate_database() 
