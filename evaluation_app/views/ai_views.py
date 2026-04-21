"""
AI Assistant views — thin HTTP handlers delegating to EvaluationAI service.
"""
import json

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.utils.translation import get_language
from django.views.decorators.http import require_http_methods

from ..ai_service import EvaluationAI, AIAssistantHelper
from ..models import ProfessorTbl, EvaluationTab, ContactMessage


def _ai_unavailable_msg():
    lang = get_language()
    if lang == 'ar':
        return 'مساعد AI غير متاح حالياً. يرجى تثبيت Ollama وتحميل نموذج.'
    return 'AI Assistant is currently unavailable. Please install Ollama and download a model.'


def _error_msg(e):
    lang = get_language()
    return f"خطأ: {e}" if lang == 'ar' else f"Error: {e}"


@login_required
@require_http_methods(["POST"])
def ai_chatbot(request):
    try:
        data = json.loads(request.body)
        question = data.get('question', '')
        ai = EvaluationAI()
        if not ai.is_available():
            return JsonResponse({'response': _ai_unavailable_msg(), 'available': False})
        context_data = {
            'user': request.user.username,
            'role': request.user.profile.role if hasattr(request.user, 'profile') else 'user',
            'language': ai.current_language,
        }
        return JsonResponse({'response': ai.chatbot_response(question, context_data), 'available': True})
    except Exception as e:
        return JsonResponse({'error': _error_msg(e)}, status=500)


@login_required
@require_http_methods(["GET"])
def ai_professor_report(request, pk):
    try:
        professor = ProfessorTbl.objects.get(pk=pk)
        ai = EvaluationAI()
        if not ai.is_available():
            return JsonResponse({'error': _ai_unavailable_msg()}, status=503)
        professor_data = AIAssistantHelper.get_professor_ai_data(professor)
        return JsonResponse({'report': ai.generate_professor_report(professor_data), 'data': professor_data})
    except ProfessorTbl.DoesNotExist:
        return JsonResponse({'error': 'Professor not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': _error_msg(e)}, status=500)


@login_required
@require_http_methods(["GET"])
def ai_dashboard_insights(request):
    try:
        ai = EvaluationAI()
        if not ai.is_available():
            return JsonResponse({'insights': _ai_unavailable_msg(), 'available': False})
        stats = AIAssistantHelper.get_dashboard_stats()
        return JsonResponse({'insights': ai.generate_insights_dashboard(stats), 'stats': stats, 'available': True})
    except Exception as e:
        return JsonResponse({'error': _error_msg(e)}, status=500)


@login_required
@require_http_methods(["POST"])
def ai_analyze_notes(request):
    try:
        data = json.loads(request.body)
        evaluation_ids = data.get('evaluation_ids', [])
        ai = EvaluationAI()
        if not ai.is_available():
            return JsonResponse({'error': _ai_unavailable_msg()}, status=503)
        notes_list = list(
            EvaluationTab.objects.filter(id__in=evaluation_ids)
            .exclude(ev_q_notes__isnull=True).exclude(ev_q_notes='')
            .values_list('ev_q_notes', flat=True)
        )
        return JsonResponse({'analysis': ai.analyze_evaluation_notes(notes_list), 'notes_count': len(notes_list)})
    except Exception as e:
        return JsonResponse({'error': _error_msg(e)}, status=500)


@login_required
@require_http_methods(["POST"])
def ai_categorize_contact(request, pk):
    try:
        contact = ContactMessage.objects.get(pk=pk)
        ai = EvaluationAI()
        if not ai.is_available():
            return JsonResponse({'error': _ai_unavailable_msg()}, status=503)
        return JsonResponse({'categorization': ai.categorize_contact_message(contact.message, contact.subject)})
    except ContactMessage.DoesNotExist:
        return JsonResponse({'error': 'Contact message not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': _error_msg(e)}, status=500)


@login_required
@require_http_methods(["GET"])
def ai_status(request):
    ai = EvaluationAI()
    return JsonResponse({
        'available': ai.is_available(),
        'model': ai.model_name if ai.is_available() else None,
        'library_installed': ai.available,
        'language': ai.current_language,
    })
