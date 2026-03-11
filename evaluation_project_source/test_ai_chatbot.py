"""
Test script for AI chatbot functionality
Run this to verify Ollama and the chatbot are working correctly
"""
import sys
import os

# Add project to path
sys.path.insert(0, os.path.dirname(__file__))

def test_ollama_connection():
    """Test if Ollama is running and models are available"""
    print("=" * 50)
    print("Testing Ollama Connection...")
    print("=" * 50)
    
    try:
        import ollama
        print("✓ Ollama module imported successfully")
    except ImportError:
        print("✗ Ollama module not found. Install with: pip install ollama")
        return False
    
    try:
        models = ollama.list()
        print(f"✓ Ollama service is running")
        
        # Handle new ollama response format (ListResponse object)
        if hasattr(models, 'models'):
            model_names = [m.model for m in models.models]
        else:
            model_names = [m['name'] for m in models.get('models', [])]
            
        if model_names:
            print(f"✓ Available models: {', '.join(model_names)}")
        else:
            print("✗ No models found. Download one with: ollama pull llama3.2")
            return False
            
        return True
    except Exception as e:
        print(f"✗ Cannot connect to Ollama service: {e}")
        print("  Make sure Ollama is installed and running.")
        print("  Start it with: ollama serve")
        return False


def test_ai_service():
    """Test the EvaluationAI service"""
    print("\n" + "=" * 50)
    print("Testing AI Service...")
    print("=" * 50)
    
    try:
        from evaluation_app.ai_service import EvaluationAI
        
        ai = EvaluationAI(model_name="llama3.2")
        
        if not ai.is_available():
            print("✗ AI service reports as unavailable")
            return False
        
        print("✓ AI service initialized")
        
        # Test chatbot response
        print("\nTesting chatbot response...")
        question = "What is this evaluation system for?"
        print(f"Question: {question}")
        
        response = ai.chatbot_response(question)
        print(f"\nResponse: {response[:200]}..." if len(response) > 200 else f"\nResponse: {response}")
        
        if "error" in response.lower() and "AI Error" in response:
            print("✗ AI returned an error")
            return False
        
        print("✓ Chatbot is working!")
        return True
        
    except Exception as e:
        print(f"✗ Error testing AI service: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("\n🤖 AI Chatbot Test Suite\n")
    
    if not test_ollama_connection():
        print("\n❌ Ollama connection failed. Fix the above issues and try again.")
        return
    
    if not test_ai_service():
        print("\n❌ AI service test failed. Check the errors above.")
        return
    
    print("\n" + "=" * 50)
    print("✅ All tests passed! AI chatbot is ready to use.")
    print("=" * 50)
    print("\nYou can now:")
    print("1. Start your Django server: python manage.py runserver")
    print("2. Open the chatbot widget in your browser")
    print("3. Ask questions and get AI-powered responses!")


if __name__ == "__main__":
    main()
