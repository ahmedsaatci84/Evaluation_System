"""
Views for AI Assistant functionality
"""
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .ai_service import EvaluationAI, AIAssistantHelper
from .models import ProfessorTbl, EvaluationTab, ContactMessage
import json


@login_required
@require_http_methods(["POST"])
def ai_chatbot(request):
    """AI Chatbot endpoint"""
    try:
        # Parse request body
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({
                'error': 'Invalid JSON data',
                'response': 'Sorry, I couldn\'t understand your request. Please try again.'
            }, status=400)
        
        question = data.get('question', '').strip()
        
        if not question:
            return JsonResponse({
                'error': 'No question provided',
                'response': 'Please type a question and try again.'
            }, status=400)
        
        ai = EvaluationAI()
        
        if not ai.is_available():
            # Provide helpful fallback response
            fallback_help = get_fallback_response(question)
            return JsonResponse({
                'response': fallback_help,
                'available': False,
                'fallback': True
            })
        
        # Prepare context
        context_data = {
            'user': request.user.username,
            'role': request.user.profile.role if hasattr(request.user, 'profile') else 'user'
        }
        
        response = ai.chatbot_response(question, context_data)
        
        return JsonResponse({
            'response': response,
            'available': True
        })
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"AI Chatbot Error: {error_details}")
        
        return JsonResponse({
            'error': str(e),
            'response': f'Sorry, I encountered an error: {str(e)}\n\nPlease try:\n• Refreshing the page\n• Asking a simpler question\n• Checking if Ollama is running (for AI features)'
        }, status=500)


def get_fallback_response(question):
    """Provide helpful responses when AI is unavailable"""
    question_lower = question.lower()
    
    # Common questions and answers
    if 'professor' in question_lower and ('add' in question_lower or 'create' in question_lower):
        return "To add a professor: Click 'Professors' in the sidebar → 'Add Professor' button → Fill in the form (ID and Name are required) → Click 'Save'."
    
    elif 'course' in question_lower and ('add' in question_lower or 'create' in question_lower):
        return "To add a course: Click 'Courses' in the sidebar → 'Add Course' button → Enter Course ID and Name → Optionally select a Professor → Click 'Save'."
    
    elif 'evaluation' in question_lower and ('add' in question_lower or 'create' in question_lower):
        return "To create an evaluation: Click 'Evaluations' in the sidebar → 'Add Evaluation' → Fill in all required fields including the 15 rating questions → Click 'Save'."
    
    elif 'participant' in question_lower and ('add' in question_lower or 'create' in question_lower):
        return "To add a participant: Click 'Participants' in the sidebar → 'Add Participant' → Enter their details → Click 'Save'."
    
    elif 'location' in question_lower and ('add' in question_lower or 'create' in question_lower):
        return "To add a location: Click 'Locations' in the sidebar → 'Add Location' → Fill in the location details → Click 'Save'."
    
    elif 'language' in question_lower or 'translation' in question_lower:
        return "To change the language: Click the language dropdown in the top-right header → Select your preferred language (English, العربية, Türkçe, or کوردی)."
    
    elif 'search' in question_lower:
        return "To search: Use the search box at the top of any list page. You can search by name, ID, phone, email, or other relevant fields."
    
    elif 'delete' in question_lower:
        return "To delete an item: Find the item in the list → Click the 'Delete' button → Confirm the deletion. Note: You need proper permissions to delete items."
    
    elif 'edit' in question_lower or 'update' in question_lower:
        return "To edit an item: Find the item in the list → Click the 'Edit' button → Make your changes → Click 'Save'."
    
    elif 'help' in question_lower or 'how' in question_lower:
        return "This is an Evaluation Management System. You can:\n• Manage Professors and Courses\n• Add Locations and Participants\n• Create and view Evaluations\n• Search and filter all data\n\nNavigate using the sidebar menu. Need help with a specific feature? Ask me!"
    
    else:
        return """⚠️ AI model is currently downloading (llama3.2, ~2GB). This may take 5-10 minutes.

Meanwhile, I can help you with:
• Adding professors, courses, participants, or locations
• Creating evaluations
• Changing language
• Searching and filtering data

Try asking: "How do I add a professor?" or "How to change language?"

To enable full AI features, please wait for the model download to complete, then refresh this page."""


@login_required
@require_http_methods(["GET"])
def ai_professor_report(request, pk):
    """Generate AI report for a professor"""
    try:
        professor = ProfessorTbl.objects.get(pk=pk)
        
        ai = EvaluationAI()
        
        if not ai.is_available():
            return JsonResponse({
                'error': 'AI Assistant is not available'
            }, status=503)
        
        # Get professor data
        professor_data = AIAssistantHelper.get_professor_ai_data(professor)
        
        # Generate report
        report = ai.generate_professor_report(professor_data)
        
        return JsonResponse({
            'report': report,
            'data': professor_data
        })
        
    except ProfessorTbl.DoesNotExist:
        return JsonResponse({
            'error': 'Professor not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'error': str(e)
        }, status=500)


@login_required
@require_http_methods(["GET"])
def ai_dashboard_insights(request):
    """Get AI-generated insights for dashboard"""
    try:
        ai = EvaluationAI()
        
        if not ai.is_available():
            return JsonResponse({
                'insights': 'AI insights unavailable. Install Ollama to enable.',
                'available': False
            })
        
        stats = AIAssistantHelper.get_dashboard_stats()
        insights = ai.generate_insights_dashboard(stats)
        
        return JsonResponse({
            'insights': insights,
            'stats': stats,
            'available': True
        })
        
    except Exception as e:
        return JsonResponse({
            'error': str(e)
        }, status=500)


@login_required
@require_http_methods(["POST"])
def ai_analyze_notes(request):
    """Analyze evaluation notes"""
    try:
        data = json.loads(request.body)
        evaluation_ids = data.get('evaluation_ids', [])
        
        ai = EvaluationAI()
        
        if not ai.is_available():
            return JsonResponse({
                'error': 'AI Assistant is not available'
            }, status=503)
        
        # Get notes
        notes = EvaluationTab.objects.filter(
            id__in=evaluation_ids
        ).exclude(
            ev_q_notes__isnull=True
        ).exclude(
            ev_q_notes=''
        ).values_list('ev_q_notes', flat=True)
        
        notes_list = list(notes)
        
        # Analyze
        analysis = ai.analyze_evaluation_notes(notes_list)
        
        return JsonResponse({
            'analysis': analysis,
            'notes_count': len(notes_list)
        })
        
    except Exception as e:
        return JsonResponse({
            'error': str(e)
        }, status=500)


@login_required
@require_http_methods(["POST"])
def ai_categorize_contact(request, pk):
    """Categorize a contact message using AI"""
    try:
        contact = ContactMessage.objects.get(pk=pk)
        
        ai = EvaluationAI()
        
        if not ai.is_available():
            return JsonResponse({
                'error': 'AI Assistant is not available'
            }, status=503)
        
        categorization = ai.categorize_contact_message(
            contact.message,
            contact.subject
        )
        
        return JsonResponse({
            'categorization': categorization
        })
        
    except ContactMessage.DoesNotExist:
        return JsonResponse({
            'error': 'Contact message not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'error': str(e)
        }, status=500)


@require_http_methods(["GET"])
def ai_status(request):
    """Check AI assistant status - available without login"""
    try:
        ai = EvaluationAI()
        is_available = ai.is_available()
        
        status_info = {
            'available': is_available,
            'model': ai.model_name if is_available else None,
            'library_installed': ai.available
        }
        
        # Add helpful message if not available
        if not ai.available:
            status_info['message'] = 'Ollama library not installed. Install with: pip install ollama'
        elif not is_available:
            status_info['message'] = 'Ollama service not running or model not downloaded. Run: ollama serve'
        else:
            status_info['message'] = 'AI Assistant is ready'
        
        return JsonResponse(status_info)
    except Exception as e:
        return JsonResponse({
            'available': False,
            'library_installed': False,
            'error': str(e),
            'message': 'Error checking AI status'
        })
