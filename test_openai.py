import os
import openai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get the API key
api_key = os.getenv("OPENAI_API_KEY")
print(f"API key exists: {api_key is not None}")

try:
    # Initialize OpenAI client
    from openai import OpenAI
    client = OpenAI(api_key=api_key)
    
    # Make a simple test call
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello, are you working?"}
        ],
        max_tokens=20
    )
    
    # Print the response
    print(f"OpenAI API test successful!")
    print(f"Response: {response.choices[0].message.content}")
    
except Exception as e:
    print(f"Error testing OpenAI API: {e}")
    import traceback
    traceback.print_exc() 