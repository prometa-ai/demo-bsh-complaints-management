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
    
    if not project_id:
        raise ValueError("Project ID not found. Set GCP_PROJECT_ID environment variable.")
    
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
    """
    # Get the secret manager key from environment
    secret_manager_key = os.getenv('SECRET_MANAGER_KEY')
    
    if not secret_manager_key:
        print("No SECRET_MANAGER_KEY found, skipping secret loading")
        return
    
    try:
        # Parse the secret manager key (assuming it's JSON with secret mappings)
        secret_config = json.loads(secret_manager_key)
        
        for env_var, secret_id in secret_config.items():
            secret_value = get_secret(secret_id)
            if secret_value:
                os.environ[env_var] = secret_value
                print(f"Loaded secret for {env_var}")
            else:
                print(f"Failed to load secret for {env_var}")
                
    except json.JSONDecodeError:
        # If it's not JSON, treat it as a single secret ID
        # For example, if SECRET_MANAGER_KEY contains "BSH_OPENAI_API_KEY"
        secret_value = get_secret(secret_manager_key)
        if secret_value:
            os.environ['OPENAI_API_KEY'] = secret_value
            print("Loaded OpenAI API key from Secret Manager")
        else:
            print("Failed to load OpenAI API key from Secret Manager")
    
    except Exception as e:
        print(f"Error loading secrets: {e}")

if __name__ == "__main__":
    load_secrets_to_env() 