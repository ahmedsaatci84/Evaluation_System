"""
Views for AI Assistant functionality
Supports multiple languages: English and Arabic
"""
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils.translation import get_language
from .ai_service import EvaluationAI, AIAssistantHelper
from .models import ProfessorTbl, EvaluationTab, ContactMessage
import json


@login_required
@require_http_methods(["POST"])
def ai_chatbot(request):
    """AI Chatbot endpoint"""
    try:
        data = json.loads(request.body)
        question = data.get('question', '')
        
        ai = EvaluationAI()
        
        if not ai.is_available():
            current_lang = get_language()
            if current_lang in ['ar']:
                error_msg = 'مساعد AI غير متاح حالياً. يرجى تثبيت Ollama وتحميل نموذج.'
            else:
                error_msg = 'AI Assistant is currently unavailable. Please install Ollama and download a model.'
            
            return JsonResponse({
                'response': error_msg,
                'available': False
            })
        
        # Prepare context
        context_data = {
            'user': request.user.username,
            'role': request.user.profile.role if hasattr(request.user, 'profile') else 'user',
            'language': ai.current_language
        }
        
        response = ai.chatbot_response(question, context_data)
        
        return JsonResponse({
            'response': response,
            'available': True
        })
        
    except Exception as e:
        current_lang = get_language()
        if current_lang in ['ar']:
            error_msg = f"خطأ: {str(e)}"
        else:
            error_msg = f"Error: {str(e)}"
        return JsonResponse({
            'error': error_msg
        }, status=500)


@login_required
@require_http_methods(["GET"])
def ai_professor_report(request, pk):
    """Generate AI report for a professor"""
    try:
        professor = ProfessorTbl.objects.get(pk=pk)
        
        ai = EvaluationAI()
        
        if not ai.is_available():
            current_lang = get_language()
            if current_lang in ['ar']:
                error_msg = 'مساعد الذكاء الاصطناعي غير متاح'
            else:
                error_msg = 'AI Assistant is not available'
            return JsonResponse({
                'error': error_msg
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
        current_lang = get_language()
        if current_lang in ['ar']:
            error_msg = 'الأستاذ غير موجود'
        else:
            error_msg = 'Professor not found'
        return JsonResponse({
            'error': error_msg
        }, status=404)
    except Exception as e:
        current_lang = get_language()
        if current_lang in ['ar']:
            error_msg = f"خطأ: {str(e)}"
        else:
            error_msg = f"Error: {str(e)}"
        return JsonResponse({
            'error': error_msg
        }, status=500)


@login_required
@require_http_methods(["GET"])
def ai_dashboard_insights(request):
    """Get AI-generated insights for dashboard"""
    try:
        ai = EvaluationAI()
        
        if not ai.is_available():
            current_lang = get_language()
            if current_lang in ['ar']:
                insights_msg = 'رؤى الذكاء الاصطناعي غير متاحة. قم بتثبيت Ollama لتفعيلها.'
            else:
                insights_msg = 'AI insights unavailable. Install Ollama to enable.'
            
            return JsonResponse({
                'insights': insights_msg,
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
        current_lang = get_language()
        if current_lang in ['ar']:
            error_msg = f"خطأ: {str(e)}"
        else:
            error_msg = f"Error: {str(e)}"
        return JsonResponse({
            'error': error_msg
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
            current_lang = get_language()
            if current_lang in ['ar']:
                error_msg = 'مساعد الذكاء الاصطناعي غير متاح'
            else:
                error_msg = 'AI Assistant is not available'
            return JsonResponse({
                'error': error_msg
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
        current_lang = get_language()
        if current_lang in ['ar']:
            error_msg = f"خطأ: {str(e)}"
        else:
            error_msg = f"Error: {str(e)}"
        return JsonResponse({
            'error': error_msg
        }, status=500)


@login_required
@require_http_methods(["POST"])
def ai_categorize_contact(request, pk):
    """Categorize a contact message using AI"""
    try:
        contact = ContactMessage.objects.get(pk=pk)
        
        ai = EvaluationAI()
        
        if not ai.is_available():
            current_lang = get_language()
            if current_lang in ['ar']:
                error_msg = 'مساعد الذكاء الاصطناعي غير متاح'
            else:
                error_msg = 'AI Assistant is not available'
            return JsonResponse({
                'error': error_msg
            }, status=503)
        
        categorization = ai.categorize_contact_message(
            contact.message,
            contact.subject
        )
        
        return JsonResponse({
            'categorization': categorization
        })
        
    except ContactMessage.DoesNotExist:
        current_lang = get_language()
        if current_lang in ['ar']:
            error_msg = 'رسالة الاتصال غير موجودة'
        else:
            error_msg = 'Contact message not found'
        return JsonResponse({
            'error': error_msg
        }, status=404)
    except Exception as e:
        current_lang = get_language()
        if current_lang in ['ar']:
            error_msg = f"خطأ: {str(e)}"
        else:
            error_msg = f"Error: {str(e)}"
        return JsonResponse({
            'error': error_msg
        }, status=500)


@login_required
@require_http_methods(["GET"])
def ai_status(request):
    """Check AI assistant status"""
    ai = EvaluationAI()
    
    return JsonResponse({
        'available': ai.is_available(),
        'model': ai.model_name if ai.is_available() else None,
        'library_installed': ai.available,
        'language': ai.current_language
    })
