import os
from google.cloud import secretmanager
import json

def get_secret(secret_id, project_id=None):
    """
    Get a secret from Google Secret Manager
    
    Args:
        secret_id (str): The ID of the secret
        project_id (str): The GCP project ID (optional, defaults to env var)
    
    Returns:
        str: The secret value
    """
    if not project_id:
        project_id = os.getenv('GCP_PROJECT_ID')
    
    if not project_id or project_id == 'your-project-id':
        print(f"Invalid project ID: {project_id}. Skipping secret loading.")
        return None
    
    try:
        # Create the Secret Manager client
        client = secretmanager.SecretManagerServiceClient()
        
        # Build the resource name of the secret version
        name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"
        
        # Access the secret version
        response = client.access_secret_version(request={"name": name})
        
        # Return the decoded payload
        return response.payload.data.decode("UTF-8")
    
    except Exception as e:
        print(f"Error accessing secret {secret_id}: {e}")
        return None

def load_secrets_to_env():
    """
    Load secrets from Secret Manager to environment variables
    Handles both individual secrets and JSON secrets with multiple variables
    """
    # Check if we already have OpenAI API key in environment
    existing_key = os.getenv('OPENAI_API_KEY')
    if existing_key and existing_key != 'your-openai-api-key-here':
        print("OpenAI API key already found in environment variables")
        return
    
    # Get the secret manager key from environment
    secret_manager_key = os.getenv('SECRET_MANAGER_KEY')
    
    if not secret_manager_key:
        print("No SECRET_MANAGER_KEY found, using local environment variables")
        return
    
    try:
        # For BSH_OPENAI_API_KEY, try to get from Secret Manager
        if secret_manager_key == "BSH_OPENAI_API_KEY":
            # First try to get from prod-prmt-demo secret (JSON format)
            prod_secret_value = get_secret("prod-prmt-demo")
            if prod_secret_value:
                try:
                    # Parse JSON and look for BSH_OPENAI_API_KEY
                    secret_data = json.loads(prod_secret_value)
                    if 'BSH_OPENAI_API_KEY' in secret_data:
                        os.environ['OPENAI_API_KEY'] = secret_data['BSH_OPENAI_API_KEY']
                        print("Loaded BSH_OPENAI_API_KEY from prod-prmt-demo secret")
                        return
                    else:
                        print("BSH_OPENAI_API_KEY not found in prod-prmt-demo secret")
                except json.JSONDecodeError:
                    print("prod-prmt-demo secret is not valid JSON")
            
            # If not found in prod-prmt-demo, try direct BSH_OPENAI_API_KEY secret
            secret_value = get_secret(secret_manager_key)
            if secret_value:
                os.environ['OPENAI_API_KEY'] = secret_value
                print("Loaded BSH_OPENAI_API_KEY from direct secret")
            else:
                print("Failed to load BSH_OPENAI_API_KEY from Secret Manager")
                print("Will use local environment variable if available")
        else:
            print(f"Unknown secret manager key: {secret_manager_key}")
                
    except Exception as e:
        print(f"Error loading secrets: {e}")
        print("Will use local environment variable if available")

if __name__ == "__main__":
    load_secrets_to_env() 
