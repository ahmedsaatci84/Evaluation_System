from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Count, Avg
from django.http import HttpResponseRedirect
from django.views.decorators.http import require_http_methods
from django.utils import translation
from django.conf import settings
from datetime import datetime, timedelta

from ..models import (
    EvaluationTab, ProfessorTbl, CourseTbl,
    ParticipantTbl, LocationTbl, ContactMessage, SystemSettings,
)


@require_http_methods(["GET", "POST"])
def set_language(request):
    language = request.GET.get('language') or request.POST.get('language', 'en')
    if language and language in dict(settings.LANGUAGES):
        translation.activate(language)
        request.session['_language'] = language
        response = HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
        response.set_cookie(
            settings.LANGUAGE_COOKIE_NAME,
            language,
            max_age=settings.LANGUAGE_COOKIE_AGE,
            path=settings.LANGUAGE_COOKIE_PATH,
            domain=settings.LANGUAGE_COOKIE_DOMAIN,
        )
        return response
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


def index(request):
    total_evaluations = EvaluationTab.objects.count()
    total_professors = ProfessorTbl.objects.count()
    total_courses = CourseTbl.objects.count()
    total_participants = ParticipantTbl.objects.count()
    total_locations = LocationTbl.objects.count()
    total_contacts = ContactMessage.objects.count()
    unread_contacts = ContactMessage.get_unread_count()

    thirty_days_ago = datetime.now().date() - timedelta(days=30)
    recent_evaluations = (
        EvaluationTab.objects.filter(train__train_date__gte=thirty_days_ago).count()
        if EvaluationTab.objects.filter(train__train_date__isnull=False).exists()
        else 0
    )

    avg_ratings = {}
    for i in range(1, 16):
        field_name = f'ev_q_{i}'
        avg = EvaluationTab.objects.aggregate(avg=Avg(field_name))['avg']
        avg_ratings[field_name] = round(avg, 2) if avg else 0

    overall_avg = round(sum(avg_ratings.values()) / len(avg_ratings), 2) if avg_ratings else 0

    top_courses = CourseTbl.objects.annotate(
        eval_count=Count('training_sessions__evaluations')
    ).order_by('-eval_count')[:5]

    recent_evals = EvaluationTab.objects.select_related(
        'train__course', 'train__professor', 'participant'
    ).order_by('-id')[:5]

    recent_contacts = ContactMessage.get_recent_messages(5)

    return render(request, 'evaluation_app/pages/index.html', {
        'total_evaluations': total_evaluations,
        'total_professors': total_professors,
        'total_courses': total_courses,
        'total_participants': total_participants,
        'total_locations': total_locations,
        'total_contacts': total_contacts,
        'unread_contacts': unread_contacts,
        'recent_evaluations': recent_evaluations,
        'overall_avg': overall_avg,
        'top_courses': top_courses,
        'recent_evals': recent_evals,
        'recent_contacts': recent_contacts,
    })


def about(request):
    return render(request, 'evaluation_app/pages/about.html')
