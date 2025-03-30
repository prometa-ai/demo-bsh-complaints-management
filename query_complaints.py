import psycopg2
import json
import getpass
import pandas as pd
from collections import Counter
from tabulate import tabulate as tabulate_func
import matplotlib.pyplot as plt
import sys

def connect_to_db():
    """Connect to the PostgreSQL database."""
    username = getpass.getuser()
    conn = psycopg2.connect(
        host="localhost",
        user=username,
        database="bsh_complaints",
        port="5432"
    )
    return conn

def get_complaint_count():
    """Get the total number of complaints in the database."""
    conn = connect_to_db()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM complaints")
    count = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return count

def get_problem_distribution():
    """Get the distribution of complaint types."""
    conn = connect_to_db()
    cursor = conn.cursor()
    
    # This query uses PostgreSQL jsonb functionality to unnest the array of problems
    cursor.execute("""
    SELECT jsonb_array_elements_text(data->'complaintDetails'->'natureOfProblem') as problem_type,
           COUNT(*) as count
    FROM complaints
    GROUP BY problem_type
    ORDER BY count DESC
    """)
    
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return results

def get_warranty_status_distribution():
    """Get distribution of warranty statuses."""
    conn = connect_to_db()
    cursor = conn.cursor()
    
    cursor.execute("""
    SELECT data->'warrantyInformation'->>'warrantyStatus' as status,
           COUNT(*) as count
    FROM complaints
    GROUP BY status
    ORDER BY count DESC
    """)
    
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return results

def search_complaints(search_term, limit=10):
    """Search complaints containing a specific term in the detailed description."""
    conn = connect_to_db()
    cursor = conn.cursor()
    
    cursor.execute("""
    SELECT id, data->'customerInformation'->>'fullName' as customer_name,
           data->'complaintDetails'->>'detailedDescription' as description
    FROM complaints
    WHERE data->'complaintDetails'->>'detailedDescription' ILIKE %s
    LIMIT %s
    """, (f'%{search_term}%', limit))
    
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return results

def get_sample_complaints(limit=5):
    """Get a sample of complaints."""
    conn = connect_to_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, data FROM complaints ORDER BY id LIMIT %s", (limit,))
    results = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return results

def get_complaints_by_problem(problem_type, limit=10):
    """Get complaints with a specific problem type."""
    conn = connect_to_db()
    cursor = conn.cursor()
    
    cursor.execute("""
    SELECT id, data->'customerInformation'->>'fullName' as customer_name,
           data->'productInformation'->>'modelNumber' as model,
           data->'complaintDetails'->>'detailedDescription' as description
    FROM complaints
    WHERE data->'complaintDetails'->'natureOfProblem' @> %s::jsonb
    LIMIT %s
    """, (json.dumps([problem_type]), limit))
    
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return results

def print_menu():
    """Print the main menu options."""
    print("\n=== BSH Customer Complaints Management System ===")
    print("1. Summary Statistics")
    print("2. Problem Type Distribution")
    print("3. Warranty Status Distribution")
    print("4. Search Complaints")
    print("5. View Sample Complaints")
    print("6. Get Complaints by Problem Type")
    print("7. Exit")
    
    choice = input("\nEnter your choice (1-7): ")
    return choice

def main():
    """Main function to run the menu-driven interface."""
    try:
        import matplotlib
        import pandas
    except ImportError:
        print("Installing required packages...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "matplotlib", "pandas", "tabulate"])
        
    while True:
        choice = print_menu()
        
        if choice == '1':
            count = get_complaint_count()
            print(f"\nTotal Complaints: {count}")
            
        elif choice == '2':
            problems = get_problem_distribution()
            print("\nProblem Type Distribution:")
            print(tabulate_func(problems, headers=["Problem Type", "Count"], tablefmt="grid"))
            
            # Plot distribution
            problem_types, counts = zip(*problems)
            plt.figure(figsize=(12, 6))
            plt.bar(problem_types, counts)
            plt.xlabel('Problem Type')
            plt.ylabel('Count')
            plt.title('Distribution of Problem Types')
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            plt.savefig('problem_distribution.png')
            print("Chart saved as 'problem_distribution.png'")
            
        elif choice == '3':
            warranty_stats = get_warranty_status_distribution()
            print("\nWarranty Status Distribution:")
            print(tabulate_func(warranty_stats, headers=["Status", "Count"], tablefmt="grid"))
            
            # Plot distribution
            statuses, counts = zip(*warranty_stats)
            plt.figure(figsize=(8, 6))
            plt.pie(counts, labels=statuses, autopct='%1.1f%%')
            plt.title('Warranty Status Distribution')
            plt.savefig('warranty_distribution.png')
            print("Chart saved as 'warranty_distribution.png'")
            
        elif choice == '4':
            term = input("\nEnter search term: ")
            results = search_complaints(term)
            if results:
                print("\nSearch Results:")
                for id, name, desc in results:
                    print(f"ID: {id} | Customer: {name}")
                    print(f"Description: {desc[:100]}...")
                    print("-" * 80)
            else:
                print("No matching complaints found.")
                
        elif choice == '5':
            samples = get_sample_complaints()
            print("\nSample Complaints:")
            for id, data in samples:
                print(f"\nID: {id}")
                print(f"Customer: {data['customerInformation']['fullName']}")
                print(f"Product: {data['productInformation']['modelNumber']}")
                print(f"Problem: {', '.join(data['complaintDetails']['natureOfProblem'])}")
                print(f"Description: {data['complaintDetails']['detailedDescription'][:100]}...")
                print("-" * 80)
                
        elif choice == '6':
            problems = get_problem_distribution()
            print("\nAvailable Problem Types:")
            for i, (problem, count) in enumerate(problems, 1):
                print(f"{i}. {problem} ({count} complaints)")
                
            try:
                idx = int(input("\nEnter the number of the problem type: ")) - 1
                if 0 <= idx < len(problems):
                    problem_type = problems[idx][0]
                    results = get_complaints_by_problem(problem_type)
                    
                    print(f"\nComplaints for problem type: {problem_type}")
                    for id, name, model, desc in results:
                        print(f"ID: {id} | Customer: {name} | Model: {model}")
                        print(f"Description: {desc[:100]}...")
                        print("-" * 80)
                else:
                    print("Invalid selection.")
            except ValueError:
                print("Please enter a valid number.")
                
        elif choice == '7':
            print("\nExiting BSH Customer Complaints Management System. Goodbye!")
            break
            
        else:
            print("\nInvalid choice. Please try again.")
            
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    main() 