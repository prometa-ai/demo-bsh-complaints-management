import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
print(f"API key exists: {api_key is not None}")
print(f"API key length: {len(api_key) if api_key else 'None'}")

try:
    # Clear any proxy settings that might interfere
    for env_var in list(os.environ.keys()):
        if 'proxy' in env_var.lower() or 'proxy' in os.environ.get(env_var, '').lower():
            print(f"Removing proxy environment variable: {env_var}={os.environ[env_var]}")
            del os.environ[env_var]
    
    print("Importing OpenAI...")
    from openai import OpenAI
    import openai
    print(f"OpenAI version: {openai.__version__}")
    
    # Create client without proxy settings
    print("Creating OpenAI client...")
    client = OpenAI(api_key=api_key)
    print("Client created successfully")
    
    # Test chat completions only
    print("Testing chat completions...")
    chat_response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Say hello!"}
        ],
        max_tokens=5
    )
    print(f"Chat response: {chat_response.choices[0].message.content}")
    
    print("\nOpenAI client is working correctly.")
    sys.exit(0)  # Success
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)  # Error 