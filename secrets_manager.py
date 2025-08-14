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
        # Get the secret value from Secret Manager
        secret_value = get_secret(secret_manager_key)
        if secret_value:
            try:
                # Try to parse as JSON first (for secrets like prod-prmt-demo)
                secret_data = json.loads(secret_value)
                if 'BSH_OPENAI_API_KEY' in secret_data:
                    os.environ['OPENAI_API_KEY'] = secret_data['BSH_OPENAI_API_KEY']
                    print(f"Loaded BSH_OPENAI_API_KEY from {secret_manager_key} secret")
                    return
                else:
                    print(f"BSH_OPENAI_API_KEY not found in {secret_manager_key} secret")
            except json.JSONDecodeError:
                # If not JSON, treat as direct API key
                os.environ['OPENAI_API_KEY'] = secret_value
                print(f"Loaded OpenAI API key directly from {secret_manager_key} secret")
                return
        else:
            print(f"Failed to load secret {secret_manager_key} from Secret Manager")
            print("Will use local environment variable if available")
                
    except Exception as e:
        print(f"Error loading secrets: {e}")
        print("Will use local environment variable if available")

if __name__ == "__main__":
    load_secrets_to_env() 
