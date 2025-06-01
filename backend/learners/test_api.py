import requests
from django.conf import settings
import json

def test_together_api():
    """Test the Together AI API connection"""
    headers = {
        "Authorization": f"Bearer {settings.TOGETHER_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": settings.TOGETHER_MODEL,
        "messages": [
            {"role": "user", "content": "Say hello!"}
        ],
        "temperature": 0.7,
        "max_tokens": 300,
        "stream": False
    }

    print("Testing Together AI API connection...")
    print(f"API URL: {settings.TOGETHER_API_URL}")
    print(f"Model: {settings.TOGETHER_MODEL}")
    print(f"API Key (first 8 chars): {settings.TOGETHER_API_KEY[:8]}...")

    try:
        response = requests.post(
            settings.TOGETHER_API_URL,
            json=payload,
            headers=headers,
            timeout=15
        )
        
        print(f"\nResponse Status: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print("\nSuccessful response:")
                print(json.dumps(data, indent=2))
            except json.JSONDecodeError as e:
                print(f"\nError decoding JSON response: {str(e)}")
                print(f"Raw response: {response.text}")
        else:
            print(f"\nError response ({response.status_code}):")
            print(response.text)
            
    except Exception as e:
        print(f"\nError making request: {str(e)}")

if __name__ == "__main__":
    test_together_api() 