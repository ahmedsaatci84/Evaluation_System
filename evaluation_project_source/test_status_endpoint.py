"""Test the AI status endpoint"""
import requests
import json

try:
    response = requests.get('http://127.0.0.1:8000/ai/status/')
    data = response.json()
    
    print("AI Status Endpoint Response:")
    print("=" * 50)
    print(json.dumps(data, indent=2))
    print("=" * 50)
    
    if data.get('available'):
        print("✅ AI is available and ready to use!")
    else:
        print("❌ AI is showing as unavailable")
        print("   This is unexpected - we verified it works!")
        
except Exception as e:
    print(f"Could not connect to server: {e}")
    print("\nMake sure Django server is running:")
    print("  python manage.py runserver")
