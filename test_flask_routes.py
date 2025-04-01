import requests
import time

def test_route(url, description):
    try:
        print(f"Testing {description} at {url}...")
        response = requests.get(url, timeout=5)
        print(f"Status code: {response.status_code}")
        if response.status_code == 200:
            print(f"Response content (first 100 chars): {response.text[:100]}...")
        else:
            print(f"Error response: {response.text}")
        return True
    except requests.exceptions.Timeout:
        print(f"Timeout occurred while accessing {url}")
        return False
    except requests.exceptions.RequestException as e:
        print(f"Error accessing {url}: {e}")
        return False

if __name__ == "__main__":
    # Test simple Flask app
    print("\n=== Testing Simple Flask App ===")
    test_route("http://127.0.0.1:5003/", "simple Flask app root")
    test_route("http://127.0.0.1:5003/test", "simple Flask app test route")
    
    # Test main Flask app
    print("\n=== Testing Main Flask App ===")
    test_route("http://127.0.0.1:5002/", "main Flask app root")
    test_route("http://127.0.0.1:5002/complaints", "complaints listing page")
    test_route("http://127.0.0.1:5002/statistics", "statistics page")
    
    print("\n=== Testing Batch Processing Endpoint ===")
    test_route("http://127.0.0.1:5002/batch_process_complaints", "batch processing endpoint") 