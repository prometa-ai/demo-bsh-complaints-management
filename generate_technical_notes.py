import random
import json
import psycopg2
from datetime import datetime, timedelta
import time
import getpass
from faker import Faker

# Set Faker to use English locale
fake = Faker('en_US')

# Technical problem diagnosis templates
fault_diagnosis_templates = [
    "The {problem_type} issue reported by the customer was examined. Tests on the {component} detected {issue}. Measurement values are {deviation}% outside the normal range.",
    "The {component} was thoroughly examined and a {issue} problem was found. This is causing the {problem_type} complaint.",
    "The {issue} accumulated in the device is affecting the {component} operation and is causing the {problem_type} complaint reported by the customer.",
    "Wear and {issue} were detected in the {component}. This is the main source of the reported {problem_type} problem.",
    "Measurements revealed that the {component} unit is not functioning properly due to {issue}."
]

# Root cause templates
root_cause_templates = [
    "The root cause of the problem is that the {component} is not working efficiently due to {issue}. This is likely due to {cause}.",
    "The {issue} on the {component} has occurred due to usage time and {cause}.",
    "The {issue} caused by {cause} has weakened the {component} system over time.",
    "An {issue} caused by {cause} was detected in the {component} part of the refrigerator.",
    "The fundamental cause is {cause}. This has created {issue} on the {component}."
]

# Solution templates
solution_templates = [
    "The {component} unit needs to be completely replaced. Additionally, {additional_action} is recommended.",
    "The {component} part needs {repair_action} for repair. I recommend {preventive_action} to prevent similar problems from recurring.",
    "The current {component} unit can be repaired with {repair_action}, but replacement would be more appropriate in the long term.",
    "The {component} should be replaced and {additional_action} performed. The customer was also informed about {usage_advice}.",
    "A new {component} should be ordered from the factory and installed. I also recommend {preventive_action}."
]

# Repair details templates
repair_templates = [
    "Applied {repair_action} to the {component}. The old part was completely removed, the new part was installed and tested.",
    "The device's {component} unit was disassembled, {repair_action} and reassembled. The system was restarted and tested.",
    "Performed {repair_action} on the {component}. All connections were checked.",
    "The faulty {component} was removed and replaced with a new one. {additional_action} was also performed.",
    "{repair_action} and {additional_action} procedures were performed on the {component}. The refrigerant level was also checked."
]

# Follow-up notes templates
followup_templates = [
    "Contact the customer within a week to check the operation of the {component}.",
    "Provide detailed information to the customer about {usage_advice} and check again within a month.",
    "Initiate the warranty process for the replaced {component} and enter the information into the system.",
    "Send a new user manual to the customer and provide telephone support regarding {usage_advice}.",
    "Investigate whether this problem is common in similar model devices and inform the production department."
]

# Component lists
components = [
    "Compressor", "Evaporator", "Condenser", "Thermostat", "Ice Maker", 
    "Door Seal", "Electronic Board", "Fan Motor", "Refrigerant System",
    "Humidity Control Unit", "Temperature Sensor", "Main Control Board", "Door Hinge"
]

# Issues
issues = [
    "wear", "aging", "rust", "disconnection", "short circuit",
    "blockage", "leakage", "calibration disorder", "mechanical failure",
    "electrical failure", "insufficient performance", "overheating", "abnormal noise"
]

# Causes
causes = [
    "normal wear and tear", "manufacturing defect", "improper use", "unsuitable environmental conditions",
    "power fluctuations", "shipping damage", "improper cleaning", "normal end of life",
    "previous incorrect repair", "use of incompatible parts", "overloading", "moisture and humidity"
]

# Repair actions
repair_actions = [
    "cleaning", "replacement", "calibration", "reprogramming",
    "soldering", "tightening", "welding", "insulation reinforcement", 
    "refrigerant addition", "connection renewal", "software update"
]

# Additional actions
additional_actions = [
    "general system cleaning", "checking all connections", "software update",
    "general inspection of other parts", "replacement of door seals", "sensor calibration",
    "resetting the device", "checking refrigerant level"
]

# Preventive actions
preventive_actions = [
    "regular cleaning", "using the device on level ground", "avoiding overloading",
    "using a voltage protector", "not leaving the door open for long periods", "maintaining appropriate ambient temperature",
    "keeping the ventilation behind the device clear", "not placing the device too close to the wall"
]

# Usage advice
usage_advice = [
    "regular cleaning", "energy saving", "proper food placement", "reducing door opening frequency",
    "frost control", "regular maintenance", "ambient temperature control", "protection against voltage fluctuations"
]

# Technician names
technician_names = [
    "John Smith", "Michael Johnson", "David Williams", "Sarah Brown", "Jessica Davis", 
    "Robert Miller", "James Wilson", "Mary Taylor", "Thomas Anderson", 
    "Charles Martin", "Daniel Thompson", "Mark White", "Kevin Harris", "Steven Clark"
]

# Function to generate a random date within a range
def random_date(start_date, end_date):
    time_between_dates = end_date - start_date
    days_between_dates = time_between_dates.days
    random_number_of_days = random.randrange(days_between_dates)
    return start_date + timedelta(days=random_number_of_days)

# Function to generate a technical note
def generate_technical_note(complaint_data):
    # Extract problem types from complaint
    problems = complaint_data.get('complaintDetails', {}).get('natureOfProblem', ['Cooling Issue'])
    problem_type = random.choice(problems) if problems else 'Cooling Issue'
    
    # Get random components for inspection (2-4 components)
    inspected_components = random.sample(components, k=random.randint(2, 4))
    
    # Random primary component that has the issue
    primary_component = random.choice(inspected_components)
    
    # Random issue
    issue = random.choice(issues)
    
    # Random cause
    cause = random.choice(causes)
    
    # Random repair action
    repair_action = random.choice(repair_actions)
    
    # Random additional action
    additional_action = random.choice(additional_actions)
    
    # Random preventive action
    preventive_action = random.choice(preventive_actions)
    
    # Random usage advice
    advice = random.choice(usage_advice)
    
    # Generate random dates
    complaint_date = datetime.fromisoformat(complaint_data.get('complaintDetails', {}).get('dateOfComplaint', datetime.now().isoformat()))
    visit_date = random_date(complaint_date, datetime.now())
    
    # Decide if parts were replaced (higher chance if issue is serious)
    parts_replaced = []
    if random.random() < 0.7:  # 70% chance to replace parts
        # 100% chance to replace the primary component
        parts_replaced.append(primary_component)
        
        # Small chance to replace additional components
        if random.random() < 0.3:  # 30% chance for each additional component
            for comp in inspected_components:
                if comp != primary_component and random.random() < 0.3:
                    parts_replaced.append(comp)
    
    # Decide if follow-up is required
    follow_up_required = random.random() < 0.4  # 40% chance to require follow-up
    
    # Select templates and fill them
    fault_diagnosis = random.choice(fault_diagnosis_templates).format(
        problem_type=problem_type,
        component=primary_component,
        issue=issue,
        deviation=random.randint(15, 50)
    )
    
    root_cause = random.choice(root_cause_templates).format(
        component=primary_component,
        issue=issue,
        cause=cause
    )
    
    solution_proposed = random.choice(solution_templates).format(
        component=primary_component,
        repair_action=repair_action,
        additional_action=additional_action,
        preventive_action=preventive_action,
        usage_advice=advice
    )
    
    repair_details = ""
    if parts_replaced:
        repair_details = random.choice(repair_templates).format(
            component=primary_component,
            repair_action=repair_action,
            additional_action=additional_action
        )
    
    follow_up_notes = ""
    if follow_up_required:
        follow_up_notes = random.choice(followup_templates).format(
            component=primary_component,
            usage_advice=advice
        )
    
    # Generate customer satisfaction (biased towards 3-5)
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

# Function to add technical notes to the database
def generate_and_store_technical_notes(num_notes=8773):
    username = getpass.getuser()
    
    try:
        # Connect to the database
        conn = psycopg2.connect(
            host="localhost",
            user=username,
            database="bsh_english_complaints",
            port="5432"
        )
        cursor = conn.cursor()
        
        # Get complaint count to make sure we don't exceed it
        cursor.execute("SELECT COUNT(*) FROM complaints")
        total_complaints = cursor.fetchone()[0]
        
        if num_notes > total_complaints:
            print(f"Requested notes ({num_notes}) exceeds total complaints ({total_complaints}). Using {total_complaints} instead.")
            num_notes = total_complaints
        
        # Get all complaint IDs
        cursor.execute("SELECT id, data FROM complaints ORDER BY id")
        all_complaints = cursor.fetchall()
        
        # Randomly select complaints for technical notes
        selected_complaints = random.sample(all_complaints, num_notes)
        
        # Check if technical_notes table exists, create if not
        cursor.execute("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_name = 'technical_notes'
        )
        """)
        
        table_exists = cursor.fetchone()[0]
        
        if not table_exists:
            cursor.execute("""
            CREATE TABLE technical_notes (
                id SERIAL PRIMARY KEY,
                complaint_id INTEGER REFERENCES complaints(id),
                data JSONB NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)
            conn.commit()
            print("Created technical_notes table.")
        
        # Clear existing technical notes if any
        cursor.execute("TRUNCATE technical_notes RESTART IDENTITY")
        conn.commit()
        print("Cleared existing technical notes.")
        
        # Generate and store technical notes
        start_time = time.time()
        batch_size = 100
        generated_count = 0
        
        for i in range(0, len(selected_complaints), batch_size):
            batch = selected_complaints[i:i + batch_size]
            notes_batch = []
            
            for complaint_id, complaint_data in batch:
                # Convert string to Python dict if needed
                if isinstance(complaint_data, str):
                    complaint_data_dict = json.loads(complaint_data)
                else:
                    complaint_data_dict = complaint_data
                
                note = generate_technical_note(complaint_data_dict)
                notes_batch.append((complaint_id, json.dumps(note)))
                generated_count += 1
            
            # Insert batch of notes
            cursor.executemany(
                "INSERT INTO technical_notes (complaint_id, data) VALUES (%s, %s)",
                notes_batch
            )
            conn.commit()
            
            # Print progress
            elapsed_time = time.time() - start_time
            print(f"Generated: {generated_count}/{num_notes} technical notes ({generated_count/num_notes*100:.1f}%) - Elapsed time: {elapsed_time:.2f}s")
        
        print(f"Successfully generated and saved {num_notes} technical notes in {time.time() - start_time:.2f} seconds")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    print("Starting generation of technical assessment notes for 8773 complaints...")
    generate_and_store_technical_notes(8773) 