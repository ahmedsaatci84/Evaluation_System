"""Quick test to verify AI chatbot endpoint is working"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'EvaluationProject.settings')
import django
django.setup()

from evaluation_app.ai_service import EvaluationAI

print("Testing AI Service Directly...")
print("=" * 50)

ai = EvaluationAI()
print(f"AI Available: {ai.is_available()}")

if ai.is_available():
    print("\n✅ AI is ready!")
    print("\nTesting chatbot response...")
    response = ai.chatbot_response("Hello")
    print(f"Response: {response[:200]}...")
else:
    print("\n❌ AI is not available")
    print("This shouldn't happen - we verified it works!")
    
    # Debug
    print("\nDebug info:")
    import ollama
    try:
        models = ollama.list()
        print(f"Models found: {[m.model for m in models.models]}")
    except Exception as e:
        print(f"Error listing models: {e}")
