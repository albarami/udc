"""Direct Anthropic API test"""
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("ANTHROPIC_API_KEY")
print(f"API Key loaded: {api_key[:15]}...{api_key[-4:]}")
print(f"Key length: {len(api_key)}")

try:
    import anthropic
    
    client = anthropic.Anthropic(api_key=api_key)
    
    # Try to list models or make a simple request
    print("\nTrying simple message with claude-3-haiku-20240307...")
    message = client.messages.create(
        model="claude-3-haiku-20240307",
        max_tokens=100,
        messages=[
            {"role": "user", "content": "Say hello"}
        ]
    )
    
    print(f"\nSUCCESS! Response: {message.content[0].text}")
    
except Exception as e:
    print(f"\nERROR: {e}")
    print("\nTrying to get account info...")
    import requests
    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01"
    }
    response = requests.get("https://api.anthropic.com/v1/messages", headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text[:500]}")

