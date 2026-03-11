from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from django.utils import translation
from django.http import HttpResponseRedirect, JsonResponse, FileResponse
from django.views.decorators.http import require_http_methods, require_POST
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt
from django.middleware.csrf import get_token
from django.utils.decorators import method_decorator
from django.conf import settings
from django.db.models import Q
from django.db import models, connection, IntegrityError
from .models import (
    EvaluationTab, ProfessorTbl, CourseTbl, ParticipantTbl, LocationTbl, 
    ContactMessage, UserProfile, SystemSettings, TrainTbl, TrainParticipantTbl
)
from .decorators import (
    guest_can_create_evaluation,
    not_guest_required,
    user_or_admin_required,
    can_delete_required,
    admin_required
)

# Language Switcher
@require_http_methods(["GET", "POST"])
def set_language(request):
    language = request.GET.get('language') or request.POST.get('language', 'en')
    
    # Validate language code
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

# Home View
def index(request):
    from django.db.models import Count, Avg
    from datetime import datetime, timedelta
    
    # Get counts
    total_evaluations = EvaluationTab.objects.count()
    total_professors = ProfessorTbl.objects.count()
    total_courses = CourseTbl.objects.count()
    total_participants = ParticipantTbl.objects.count()
    total_locations = LocationTbl.objects.count()
    
    # Contact messages stats
    total_contacts = ContactMessage.objects.count()
    unread_contacts = ContactMessage.get_unread_count()
    
    # Get recent evaluations (last 30 days) - using train__train_date
    thirty_days_ago = datetime.now().date() - timedelta(days=30)
    recent_evaluations = EvaluationTab.objects.filter(
        train__train_date__gte=thirty_days_ago
    ).count() if EvaluationTab.objects.filter(train__train_date__isnull=False).exists() else 0
    
    # Calculate average ratings
    avg_ratings = {}
    for i in range(1, 16):
        field_name = f'ev_q_{i}'
        avg = EvaluationTab.objects.aggregate(
            avg=Avg(field_name)
        )['avg']
        avg_ratings[field_name] = round(avg, 2) if avg else 0
    
    # Get overall average
    overall_avg = round(sum(avg_ratings.values()) / len(avg_ratings), 2) if avg_ratings else 0
    
    # Get top courses by evaluation count - through train relationship
    top_courses = CourseTbl.objects.annotate(
        eval_count=Count('training_sessions__evaluations')
    ).order_by('-eval_count')[:5]
    
    # Get recent evaluations - updated to use train relationship
    recent_evals = EvaluationTab.objects.select_related(
        'train__course', 'train__professor', 'participant'
    ).order_by('-id')[:5]
    
    # Get recent contact messages
    recent_contacts = ContactMessage.get_recent_messages(5)
    
    context = {
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
    }
    
    return render(request, 'evaluation_app/index.html', context)

# ====================
# EVALUATION VIEWS
# ====================
def evaluation_list(request):
    # Load all evaluations with training session relationships
    evaluations = EvaluationTab.objects.select_related(
        'participant', 
        'train',
        'train__course',
        'train__professor',
        'train__location'
    ).all()
    
    evaluations_list = list(evaluations)
    return render(request, 'evaluation_app/evaluation_list.html', {
        'evaluations': evaluations_list,
        'total_count': len(evaluations_list)
    })

@guest_can_create_evaluation
def evaluation_create(request):
    # Check if user is guest
    is_guest = request.user.is_authenticated and hasattr(request.user, 'profile') and request.user.profile.is_guest()
    
    # Check if guests are allowed to create evaluations
    if is_guest:
        settings = SystemSettings.get_settings()
        if not settings.allow_guest_evaluations:
            messages.error(request, 'Guest users are currently not allowed to create evaluations. Please contact an administrator.')
            return redirect('home')
    
    if request.method == 'POST':
        # Get participant from form (no auto-create for guests)
        participant_id = request.POST.get('participant') or None
        train_id = request.POST.get('train') or None
        
        # Check for duplicate evaluation (same participant + same training session)
        if participant_id and train_id:
            existing_evaluation = EvaluationTab.objects.filter(
                participant_id=participant_id,
                train_id=train_id
            ).first()
            
            if existing_evaluation:
                messages.error(
                    request, 
                    'An evaluation from this participant for this training session already exists. '
                    'Each participant can only submit one evaluation per training session.'
                )
                # Re-display form with error
                participants = list(ParticipantTbl.objects.all())
                training_sessions = list(TrainTbl.objects.select_related('course', 'professor', 'location').filter(is_active=True))
                
                return render(request, 'evaluation_app/evaluation_form.html', {
                    'participants': participants,
                    'training_sessions': training_sessions
                })
        
        evaluation = EvaluationTab(
            ev_q_1=request.POST.get('ev_q_1') or None,
            ev_q_2=request.POST.get('ev_q_2') or None,
            ev_q_3=request.POST.get('ev_q_3') or None,
            ev_q_4=request.POST.get('ev_q_4') or None,
            ev_q_5=request.POST.get('ev_q_5') or None,
            ev_q_6=request.POST.get('ev_q_6') or None,
            ev_q_7=request.POST.get('ev_q_7') or None,
            ev_q_8=request.POST.get('ev_q_8') or None,
            ev_q_9=request.POST.get('ev_q_9') or None,
            ev_q_10=request.POST.get('ev_q_10') or None,
            ev_q_11=request.POST.get('ev_q_11') or None,
            ev_q_12=request.POST.get('ev_q_12') or None,
            ev_q_13=request.POST.get('ev_q_13') or None,
            ev_q_14=request.POST.get('ev_q_14') or None,
            ev_q_15=request.POST.get('ev_q_15') or None,
            ev_q_notes=request.POST.get('ev_q_notes'),
            participant_id=participant_id,
            train_id=request.POST.get('train') or None,
        )
        evaluation.save()
        messages.success(request, 'Evaluation created successfully!')
        return redirect('evaluation_list')
    
    # Prepare context
    participants = list(ParticipantTbl.objects.all())
    training_sessions = list(TrainTbl.objects.select_related('course', 'professor', 'location').filter(is_active=True))
    
    return render(request, 'evaluation_app/evaluation_form.html', {
        'participants': participants,
        'training_sessions': training_sessions
    })

@not_guest_required
def evaluation_update(request, pk):
    evaluation = get_object_or_404(EvaluationTab, pk=pk)
    if request.method == 'POST':
        evaluation.ev_q_1 = request.POST.get('ev_q_1') or None
        evaluation.ev_q_2 = request.POST.get('ev_q_2') or None
        evaluation.ev_q_3 = request.POST.get('ev_q_3') or None
        evaluation.ev_q_4 = request.POST.get('ev_q_4') or None
        evaluation.ev_q_5 = request.POST.get('ev_q_5') or None
        evaluation.ev_q_6 = request.POST.get('ev_q_6') or None
        evaluation.ev_q_7 = request.POST.get('ev_q_7') or None
        evaluation.ev_q_8 = request.POST.get('ev_q_8') or None
        evaluation.ev_q_9 = request.POST.get('ev_q_9') or None
        evaluation.ev_q_10 = request.POST.get('ev_q_10') or None
        evaluation.ev_q_11 = request.POST.get('ev_q_11') or None
        evaluation.ev_q_12 = request.POST.get('ev_q_12') or None
        evaluation.ev_q_13 = request.POST.get('ev_q_13') or None
        evaluation.ev_q_14 = request.POST.get('ev_q_14') or None
        evaluation.ev_q_15 = request.POST.get('ev_q_15') or None
        evaluation.ev_q_notes = request.POST.get('ev_q_notes')
        
        new_participant_id = request.POST.get('participant') or None
        new_train_id = request.POST.get('train') or None
        
        # Check for duplicate evaluation (same participant + same training session)
        # Exclude current evaluation from the check
        if new_participant_id and new_train_id:
            existing_evaluation = EvaluationTab.objects.filter(
                participant_id=new_participant_id,
                train_id=new_train_id
            ).exclude(id=evaluation.id).first()
            
            if existing_evaluation:
                messages.error(
                    request,
                    'An evaluation from this participant for this training session already exists. '
                    'Each participant can only submit one evaluation per training session.'
                )
                # Re-display form with error
                participants = list(ParticipantTbl.objects.all())
                training_sessions = list(TrainTbl.objects.select_related('course', 'professor', 'location').filter(is_active=True))
                return render(request, 'evaluation_app/evaluation_form.html', {
                    'evaluation': evaluation,
                    'participants': participants,
                    'training_sessions': training_sessions
                })
        
        evaluation.participant_id = new_participant_id
        evaluation.train_id = new_train_id
        evaluation.save()
        messages.success(request, 'Evaluation updated successfully!')
        return redirect('evaluation_list')
    
    participants = list(ParticipantTbl.objects.all())
    training_sessions = list(TrainTbl.objects.select_related('course', 'professor', 'location').filter(is_active=True))
    return render(request, 'evaluation_app/evaluation_form.html', {
        'evaluation': evaluation, 
        'participants': participants,
        'training_sessions': training_sessions
    })

@can_delete_required
def evaluation_delete(request, pk):
    evaluation = get_object_or_404(EvaluationTab, pk=pk)
    if request.method == 'POST':
        evaluation.delete()
        messages.success(request, 'Evaluation deleted successfully!')
        return redirect('evaluation_list')
    return render(request, 'evaluation_app/evaluation_confirm_delete.html', {'evaluation': evaluation})

@login_required
def evaluation_download_pdf(request, pk):
    """Generate PDF report for a specific evaluation with Arabic support"""
    from django.http import HttpResponse
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import inch
    from reportlab.pdfgen import canvas
    from reportlab.lib import colors
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from datetime import datetime
    import os
    import arabic_reshaper
    from bidi.algorithm import get_display
    
    evaluation = get_object_or_404(EvaluationTab, pk=pk)
    
    # Create the HttpResponse object with PDF headers
    response = HttpResponse(content_type='application/pdf')
    participant_name = evaluation.participant.participant_name if evaluation.participant else "Unknown"
    train_id = evaluation.train.trainid if evaluation.train else "N/A"
    filename = f'Evaluation_{evaluation.id}_{participant_name.replace(" ", "_")}_Train{train_id}.pdf'
    response['Content-Disposition'] = f'inline; filename="{filename}"'
    
    # Create the PDF object
    p = canvas.Canvas(response, pagesize=A4)
    width, height = A4
    
    # Register Arabic-supporting font
    try:
        font_registered = False
        
        # Try Windows system fonts (Arial, Tahoma support Arabic)
        windows_fonts = [
            ('C:\\Windows\\Fonts\\arial.ttf', 'C:\\Windows\\Fonts\\arialbd.ttf', 'Arial'),
            ('C:\\Windows\\Fonts\\tahoma.ttf', 'C:\\Windows\\Fonts\\tahomabd.ttf', 'Tahoma'),
        ]
        
        for normal_path, bold_path, font_name in windows_fonts:
            if os.path.exists(normal_path):
                try:
                    pdfmetrics.registerFont(TTFont(font_name, normal_path))
                    if os.path.exists(bold_path):
                        pdfmetrics.registerFont(TTFont(f'{font_name}-Bold', bold_path))
                    else:
                        pdfmetrics.registerFont(TTFont(f'{font_name}-Bold', normal_path))
                    
                    normal_font = font_name
                    bold_font = f'{font_name}-Bold'
                    font_registered = True
                    break
                except:
                    continue
        
        if not font_registered:
            normal_font = 'Helvetica'
            bold_font = 'Helvetica-Bold'
            
    except Exception as e:
        normal_font = 'Helvetica'
        bold_font = 'Helvetica-Bold'
    
    # Helper function to process Arabic text
    def process_arabic_text(text):
        """Process Arabic text for proper RTL display in PDF"""
        if not text:
            return ""
        
        text = str(text)
        has_arabic = any('\u0600' <= char <= '\u06FF' for char in text)
        
        if has_arabic:
            reshaped_text = arabic_reshaper.reshape(text)
            bidi_text = get_display(reshaped_text)
            return bidi_text
        
        return text
    
    # Arabic questions
    questions = [
        "كان المدرب على دراية ومعرفة والمام كافي بمواضيع البرنامج",
        "نجح المدرب في ايصال المعلومة الى المتدربين بسهولة",
        "كان المدرب ذو مقدرة على احداث التفاعل والمشاركة البناءة وادارة النقاشات كما كان متمكنا في ادارة المدخلات والاستفسارات",
        "استطاع المدرب ربط المادة التدريبية بالواقع العملي للمتدربين",
        "استخدام المدرب وسائل وانشطة تدريبية مختلفة في تزويد المشاركين بالمهارات",
        "كانت المادة التدريبية المستخدمة ملائمة ومنسجمة مع اهداف البرنامج",
        "كانت المواضيع العلمية للبرنامج منظمة ومرتبطة بشكل منطقي مما سهل عملية التعلم المطلوبة",
        "سلامة وسلاسة اللغة التي كتبت بها المادة التدريبية",
        "المادة التي تم طرحها وتناولها غطت مفردات البرنامج",
        "التكنولوجيا الحديثة التي تم طرحها في البرنامج",
        "الاشعار بوقت تنفيذ البرنامج التدريبي ومكان انعقاد كان مناسب",
        "القاعات التدريبية وفرت بيئة تعليمية مريحة",
        "مكان ووقت وانعقاد البرنامج ساهم في زيادة فاعلية البرنامج",
        "تنظيم برنامج كان مناسبا من حيث (فترات الاستراحة ,مستلزمات التدريب ,الخ)",
        "مدة البرنامج كانت كافية لتغطية كافة اهداف الدورة التدريبية"
    ]
    
    # Set up colors
    primary_color = colors.HexColor('#2c3e50')
    secondary_color = colors.HexColor('#3498db')
    accent_color = colors.HexColor('#27ae60')
    light_gray = colors.HexColor('#ecf0f1')
    
    # Draw header background
    p.setFillColor(primary_color)
    p.rect(0, height - 2.2*inch, width, 2.2*inch, fill=True, stroke=False)
    
    # Title
    p.setFillColor(colors.white)
    p.setFont(bold_font, 24)
    title_text = process_arabic_text("تقرير تقييم البرنامج التدريبي")
    p.drawCentredString(width/2, height - 1*inch, title_text)
    
    # Subtitle
    p.setFont(normal_font, 11)
    current_date = datetime.now()
    date_str = current_date.strftime('%Y/%m/%d')
    subtitle_text = process_arabic_text(f"تاريخ الطباعة: {date_str}")
    p.drawCentredString(width/2, height - 1.5*inch, subtitle_text)
    
    # Reset to black for content
    p.setFillColor(colors.black)
    
    # Starting position for content
    y_position = height - 2.7*inch
    
    # Information Section
    p.setFont(bold_font, 14)
    p.setFillColor(primary_color)
    info_title = process_arabic_text("معلومات التقييم")
    p.drawString(1*inch, y_position, info_title)
    
    y_position -= 0.35*inch
    
    # Information fields
    def draw_info_field(label, value, y_pos):
        p.setFillColor(light_gray)
        p.rect(1*inch, y_pos - 0.2*inch, width - 2*inch, 0.3*inch, fill=True, stroke=False)
        
        p.setFillColor(primary_color)
        p.setFont(bold_font, 10)
        processed_label = process_arabic_text(label)
        p.drawRightString(width - 1.2*inch, y_pos, processed_label)
        
        p.setFillColor(colors.black)
        p.setFont(normal_font, 10)
        processed_value = process_arabic_text(str(value))
        p.drawString(1.2*inch, y_pos, processed_value)
        
        return y_pos - 0.4*inch
    
    # Draw information
    y_position = draw_info_field("اسم المتدرب:", participant_name, y_position)
    
    course_name = evaluation.train.course.coursename if evaluation.train and evaluation.train.course else "غير متوفر"
    y_position = draw_info_field("اسم البرنامج التدريبي:", course_name, y_position)
    
    professor_name = evaluation.train.professor.profname if evaluation.train and evaluation.train.professor else "غير متوفر"
    y_position = draw_info_field("اسم المدرب:", professor_name, y_position)
    
    location_name = evaluation.train.location.locationname if evaluation.train and evaluation.train.location else "غير متوفر"
    y_position = draw_info_field("المكان:", location_name, y_position)
    
    train_date = evaluation.train.train_date.strftime('%Y/%m/%d') if evaluation.train and evaluation.train.train_date else "غير متوفر"
    y_position = draw_info_field("تاريخ التدريب:", train_date, y_position)
    
    y_position -= 0.3*inch
    
    # Questions Section
    p.setFont(bold_font, 14)
    p.setFillColor(primary_color)
    questions_title = process_arabic_text("التقييمات (من 1 إلى 10)")
    p.drawString(1*inch, y_position, questions_title)
    
    y_position -= 0.35*inch
    
    # Get all question values
    question_values = [
        evaluation.ev_q_1, evaluation.ev_q_2, evaluation.ev_q_3, evaluation.ev_q_4, evaluation.ev_q_5,
        evaluation.ev_q_6, evaluation.ev_q_7, evaluation.ev_q_8, evaluation.ev_q_9, evaluation.ev_q_10,
        evaluation.ev_q_11, evaluation.ev_q_12, evaluation.ev_q_13, evaluation.ev_q_14, evaluation.ev_q_15
    ]
    
    # Draw questions with summations
    question_counter = 0
    group_sum = 0
    total_sum = 0
    total_count = 0
    
    for i, (question, value) in enumerate(zip(questions, question_values), 1):
        # Check if we need a new page
        if y_position < 2*inch:
            p.showPage()
            p.setFont(normal_font, 10)
            y_position = height - 1*inch
        
        # Draw question
        p.setFillColor(colors.black)
        p.setFont(bold_font, 9)
        q_text = process_arabic_text(f"{i}. {question}")
        
        # Handle long questions with wrapping
        if len(q_text) > 80:
            # Split into two lines
            words = q_text.split()
            line1 = ' '.join(words[:len(words)//2])
            line2 = ' '.join(words[len(words)//2:])
            p.drawRightString(width - 1.2*inch, y_position, line1)
            y_position -= 0.15*inch
            p.drawRightString(width - 1.2*inch, y_position, line2)
        else:
            p.drawRightString(width - 1.2*inch, y_position, q_text)
        
        # Draw value with color coding
        p.setFont(bold_font, 11)
        if value is not None:
            if value >= 8:
                p.setFillColor(colors.green)
            elif value >= 5:
                p.setFillColor(colors.orange)
            else:
                p.setFillColor(colors.red)
            
            p.drawString(1.2*inch, y_position, str(value))
            group_sum += value
            total_sum += value
            total_count += 1
        else:
            p.setFillColor(colors.gray)
            p.drawString(1.2*inch, y_position, "N/A")
        
        y_position -= 0.3*inch
        question_counter += 1
        
        # Add group summation after every 5 questions
        if question_counter == 5 and group_sum > 0:
            p.setFillColor(accent_color)
            p.rect(1*inch, y_position - 0.15*inch, width - 2*inch, 0.28*inch, fill=True, stroke=False)
            
            p.setFillColor(colors.white)
            p.setFont(bold_font, 10)
            group_avg = group_sum / 5
            sum_text = process_arabic_text(f"مجموع الأسئلة {i-4} - {i}: {group_sum} (متوسط: {group_avg:.2f})")
            p.drawCentredString(width/2, y_position, sum_text)
            
            y_position -= 0.5*inch
            question_counter = 0
            group_sum = 0
    
    # Check if there's a remaining group
    if question_counter > 0 and group_sum > 0:
        p.setFillColor(accent_color)
        p.rect(1*inch, y_position - 0.15*inch, width - 2*inch, 0.28*inch, fill=True, stroke=False)
        
        p.setFillColor(colors.white)
        p.setFont(bold_font, 10)
        group_avg = group_sum / question_counter
        start_q = 15 - question_counter + 1
        sum_text = process_arabic_text(f"مجموع الأسئلة {start_q} - 15: {group_sum} (متوسط: {group_avg:.2f})")
        p.drawCentredString(width/2, y_position, sum_text)
        
        y_position -= 0.5*inch
    
    # Total summation
    if total_count > 0:
        if y_position < 1.5*inch:
            p.showPage()
            y_position = height - 1*inch
        
        p.setFillColor(primary_color)
        p.rect(1*inch, y_position - 0.2*inch, width - 2*inch, 0.35*inch, fill=True, stroke=False)
        
        p.setFillColor(colors.white)
        p.setFont(bold_font, 12)
        total_avg = total_sum / total_count
        total_text = process_arabic_text(f"المجموع الكلي: {total_sum} / {total_count * 10} | المتوسط العام: {total_avg:.2f} / 10")
        p.drawCentredString(width/2, y_position, total_text)
        
        y_position -= 0.6*inch
    
    # Notes section if available
    if evaluation.ev_q_notes and evaluation.ev_q_notes.strip():
        if y_position < 2*inch:
            p.showPage()
            y_position = height - 1*inch
        
        p.setFillColor(primary_color)
        p.setFont(bold_font, 11)
        notes_title = process_arabic_text("ملاحظات:")
        p.drawRightString(width - 1.2*inch, y_position, notes_title)
        
        y_position -= 0.3*inch
        
        p.setFillColor(colors.black)
        p.setFont(normal_font, 9)
        notes_text = process_arabic_text(evaluation.ev_q_notes)
        
        # Wrap notes text
        max_width = width - 2.4*inch
        lines = []
        current_line = ""
        for word in notes_text.split():
            test_line = current_line + " " + word if current_line else word
            if p.stringWidth(test_line, normal_font, 9) < max_width:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word
        if current_line:
            lines.append(current_line)
        
        for line in lines:
            p.drawRightString(width - 1.2*inch, y_position, line)
            y_position -= 0.2*inch
    
    # Footer
    p.setFont(normal_font, 8)
    p.setFillColor(colors.gray)
    footer_text = process_arabic_text(f"تم إنشاء هذا التقرير تلقائياً بواسطة نظام التقييم - ID: {evaluation.id}")
    p.drawCentredString(width/2, 0.5*inch, footer_text)
    
    # Save PDF
    p.showPage()
    p.save()
    
    return response

@login_required
def get_training_participants(request, train_id):
    """AJAX endpoint to get active participants for a specific training session"""
    try:
        # Get the evaluation ID if we're editing (to allow the current participant)
        evaluation_id = request.GET.get('evaluation_id', None)
        
        # Get active participants linked to this training session
        train_participants = TrainParticipantTbl.objects.filter(
            train_id=train_id,
            is_active=True,
            participant__isnull=False
        ).select_related('participant')
        
        # Get participant IDs who have already submitted evaluations for this training
        existing_evaluations = EvaluationTab.objects.filter(
            train_id=train_id
        ).values_list('participant_id', flat=True)
        
        # If editing, exclude the current evaluation from the check
        if evaluation_id:
            existing_evaluations = EvaluationTab.objects.filter(
                train_id=train_id
            ).exclude(id=evaluation_id).values_list('participant_id', flat=True)
        
        participants_data = []
        for tp in train_participants:
            # Only include participants who haven't submitted an evaluation yet
            if tp.participant.participant_id not in existing_evaluations:
                participants_data.append({
                    'id': tp.participant.participant_id,
                    'name': tp.participant.participant_name
                })
        
        return JsonResponse({'participants': participants_data})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@login_required
def get_available_participants(request, train_id):
    """AJAX endpoint to get participants NOT yet added to a specific training session"""
    try:
        # Get the train_participant ID if we're editing (to allow the current participant)
        train_participant_id = request.GET.get('train_participant_id', None)
        
        # Get all participants
        all_participants = ParticipantTbl.objects.all()
        
        # Get participant IDs already added to this training session
        if train_participant_id:
            # If editing, exclude the current train_participant from the check
            existing_participants = TrainParticipantTbl.objects.filter(
                train_id=train_id
            ).exclude(train_participant_id=train_participant_id).values_list('participant_id', flat=True)
        else:
            # For new entries, just get all participants in this training
            existing_participants = TrainParticipantTbl.objects.filter(
                train_id=train_id
            ).values_list('participant_id', flat=True)
        
        # Filter out participants already in the training
        available_participants = all_participants.exclude(
            participant_id__in=existing_participants
        )
        
        participants_data = [
            {
                'id': p.participant_id,
                'name': p.participant_name
            }
            for p in available_participants
        ]
        
        return JsonResponse({'participants': participants_data})
    except Exception as e:
        import traceback
        print(f"Error in get_available_participants: {str(e)}")
        print(traceback.format_exc())
        return JsonResponse({'error': str(e)}, status=400)

# ====================
# PROFESSOR VIEWS
# ====================
def professor_list(request):
    search_query = request.GET.get('search', '').strip()
    professors = ProfessorTbl.objects.all()
    
    if search_query:
        # ALL words must match for more accurate results
        search_terms = [term for term in search_query.split() if term]
        
        for term in search_terms:
            professors = professors.filter(
                Q(profname__icontains=term) |
                Q(profid__icontains=term) |
                Q(prophone__icontains=term)
            )
        
        professors = professors.order_by('profname')
    else:
        professors = professors.order_by('profname')
    
    professors_list = list(professors)
    return render(request, 'evaluation_app/professor_list.html', {
        'professors': professors_list,
        'search_query': search_query,
        'results_count': len(professors_list)
    })

@not_guest_required
def professor_create(request):
    if request.method == 'POST':
        profid = request.POST.get('profid', '').strip()
        profname = request.POST.get('profname', '').strip()
        prophone = request.POST.get('prophone', '').strip()
        
        # Validate required fields
        if not profid:
            messages.error(request, 'معرف الأستاذ مطلوب! الرجاء إدخال رقم المعرف. | Professor ID is required! Please enter the ID number.')
            return render(request, 'evaluation_app/professor_form.html', {
                'profid': profid,
                'profname': profname,
                'prophone': prophone
            })
        
        if not profname:
            messages.error(request, 'اسم الأستاذ مطلوب! الرجاء إدخال الاسم الكامل. | Professor name is required! Please enter the full name.')
            return render(request, 'evaluation_app/professor_form.html', {
                'profid': profid,
                'profname': profname,
                'prophone': prophone
            })
        
        # Convert to proper types
        try:
            profid = int(profid)
        except ValueError:
            messages.error(request, 'معرف الأستاذ يجب أن يكون رقماً صحيحاً! الرجاء إدخال أرقام فقط. | Professor ID must be a valid number! Please enter digits only.')
            return render(request, 'evaluation_app/professor_form.html', {
                'profid': request.POST.get('profid'),
                'profname': profname,
                'prophone': prophone
            })
        
        prophone_value = int(prophone) if prophone else None
        
        # Check for duplicate profid
        if ProfessorTbl.objects.filter(profid=profid).exists():
            messages.error(request, f'تكرار في المعرف! الأستاذ ذو المعرف ({profid}) موجود مسبقاً. الرجاء استخدام معرف آخر. | Duplicate ID! A professor with ID ({profid}) already exists. Please use a different ID.')
            return render(request, 'evaluation_app/professor_form.html', {
                'profid': request.POST.get('profid'),
                'profname': profname,
                'prophone': prophone
            })
        
        # Check for duplicate based on name and phone
        existing_prof = ProfessorTbl.objects.filter(
            profname=profname,
            prophone=prophone_value
        ).first()
        
        if existing_prof:
            messages.error(request, f'تكرار في البيانات! الأستاذ "{profname}" بنفس رقم الهاتف موجود مسبقاً (المعرف: {existing_prof.profid}). | Duplicate data! Professor "{profname}" with the same phone number already exists (ID: {existing_prof.profid}).')
            return render(request, 'evaluation_app/professor_form.html', {
                'profid': request.POST.get('profid'),
                'profname': profname,
                'prophone': prophone
            })
        
        professor = ProfessorTbl(
            profid=profid,
            profname=profname,
            prophone=prophone_value,
        )
        professor.save()
        messages.success(request, f'تم إنشاء الأستاذ "{profname}" بنجاح! | Professor "{profname}" created successfully!')
        return redirect('professor_list')
    return render(request, 'evaluation_app/professor_form.html')

@not_guest_required
def professor_update(request, pk):
    professor = get_object_or_404(ProfessorTbl, pk=pk)
    if request.method == 'POST':
        profname = request.POST.get('profname', '').strip()
        prophone = request.POST.get('prophone', '').strip() or None
        
        # Validate required fields
        if not profname:
            messages.error(request, 'اسم الأستاذ مطلوب! الرجاء إدخال الاسم الكامل. | Professor name is required! Please enter the full name.')
            return render(request, 'evaluation_app/professor_form.html', {'professor': professor})
        
        # Check for duplicate based on name and phone (excluding current professor)
        existing_prof = ProfessorTbl.objects.filter(
            profname=profname,
            prophone=prophone
        ).exclude(profid=pk).first()
        
        if existing_prof:
            messages.error(request, f'تكرار في البيانات! الأستاذ "{profname}" بنفس رقم الهاتف موجود مسبقاً (المعرف: {existing_prof.profid}). | Duplicate data! Professor "{profname}" with the same phone number already exists (ID: {existing_prof.profid}).')
            return render(request, 'evaluation_app/professor_form.html', {'professor': professor})
        
        professor.profname = profname
        professor.prophone = prophone
        professor.save()
        messages.success(request, f'تم تحديث بيانات الأستاذ "{profname}" بنجاح! | Professor "{profname}" updated successfully!')
        return redirect('professor_list')
    return render(request, 'evaluation_app/professor_form.html', {'professor': professor})

@can_delete_required
def professor_delete(request, pk):
    professor = get_object_or_404(ProfessorTbl, pk=pk)
    if request.method == 'POST':
        try:
            professor.delete()
            messages.success(request, 'Professor deleted successfully!')
        except IntegrityError:
            messages.error(request, 'Cannot delete this professor because they have associated courses or training sessions. Please delete or reassign those records first.')
        return redirect('professor_list')
    return render(request, 'evaluation_app/professor_confirm_delete.html', {'professor': professor})

def professor_download_pdf(request, pk):
    from django.http import HttpResponse
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.units import inch
    from reportlab.pdfgen import canvas
    from reportlab.lib import colors
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from datetime import datetime
    import os
    import arabic_reshaper
    from bidi.algorithm import get_display
    
    professor = get_object_or_404(ProfessorTbl, pk=pk)
    
    # Create the HttpResponse object with PDF headers
    response = HttpResponse(content_type='application/pdf')
    filename = f'Professor_{professor.profid}_{professor.profname.replace(" ", "_") if professor.profname else "Unknown"}.pdf'
    response['Content-Disposition'] = f'inline; filename="{filename}"'
    
    # Create the PDF object
    p = canvas.Canvas(response, pagesize=A4)
    width, height = A4
    
    # Register Arabic-supporting font
    try:
        from reportlab.pdfbase.ttfonts import TTFont
        from reportlab.lib.fonts import addMapping
        import reportlab
        from django.conf import settings
        
        font_registered = False
        
        # Try Windows system fonts first (Arial, Tahoma support Arabic)
        windows_fonts = [
            ('C:\\Windows\\Fonts\\arial.ttf', 'C:\\Windows\\Fonts\\arialbd.ttf', 'Arial'),
            ('C:\\Windows\\Fonts\\tahoma.ttf', 'C:\\Windows\\Fonts\\tahomabd.ttf', 'Tahoma'),
            ('C:\\Windows\\Fonts\\times.ttf', 'C:\\Windows\\Fonts\\timesbd.ttf', 'Times'),
        ]
        
        for normal_path, bold_path, font_name in windows_fonts:
            if os.path.exists(normal_path):
                try:
                    pdfmetrics.registerFont(TTFont(font_name, normal_path))
                    if os.path.exists(bold_path):
                        pdfmetrics.registerFont(TTFont(f'{font_name}-Bold', bold_path))
                    else:
                        pdfmetrics.registerFont(TTFont(f'{font_name}-Bold', normal_path))
                    
                    normal_font = font_name
                    bold_font = f'{font_name}-Bold'
                    font_registered = True
                    break
                except:
                    continue
        
        # If no system font found, try bundled font
        if not font_registered:
            static_fonts_dir = os.path.join(settings.BASE_DIR, 'evaluation_app', 'static', 'evaluation_app', 'fonts')
            
            # Try Amiri font (if downloaded)
            amiri_path = os.path.join(static_fonts_dir, 'Amiri-Regular.ttf')
            amiri_bold_path = os.path.join(static_fonts_dir, 'Amiri-Bold.ttf')
            
            if os.path.exists(amiri_path):
                pdfmetrics.registerFont(TTFont('Amiri', amiri_path))
                if os.path.exists(amiri_bold_path):
                    pdfmetrics.registerFont(TTFont('Amiri-Bold', amiri_bold_path))
                else:
                    pdfmetrics.registerFont(TTFont('Amiri-Bold', amiri_path))
                
                normal_font = 'Amiri'
                bold_font = 'Amiri-Bold'
                font_registered = True
        
        # Final fallback to Helvetica (won't display Arabic properly)
        if not font_registered:
            normal_font = 'Helvetica'
            bold_font = 'Helvetica-Bold'
            
    except Exception as e:
        # Fallback to Helvetica
        normal_font = 'Helvetica'
        bold_font = 'Helvetica-Bold'
    
    # Helper function to process Arabic text
    def process_arabic_text(text):
        """Process Arabic text for proper RTL display in PDF"""
        if not text:
            return ""
        
        text = str(text)
        
        # Check if text contains Arabic characters
        has_arabic = any('\u0600' <= char <= '\u06FF' for char in text)
        
        if has_arabic:
            # Reshape Arabic text and apply bidirectional algorithm
            reshaped_text = arabic_reshaper.reshape(text)
            bidi_text = get_display(reshaped_text)
            return bidi_text
        
        return text
    
    # Set up colors
    primary_color = colors.HexColor('#2c3e50')
    secondary_color = colors.HexColor('#3498db')
    light_gray = colors.HexColor('#ecf0f1')
    
    # Draw header background
    p.setFillColor(primary_color)
    p.rect(0, height - 2*inch, width, 2*inch, fill=True, stroke=False)
    
    # Title
    p.setFillColor(colors.white)
    p.setFont(bold_font, 28)
    title_text = process_arabic_text("معلومات الأستاذ")
    p.drawCentredString(width/2, height - 1*inch, title_text)
    
    # Subtitle
    p.setFont(normal_font, 12)
    # Format date in Arabic-friendly way
    current_date = datetime.now()
    date_str = current_date.strftime('%Y/%m/%d')
    time_str = current_date.strftime('%I:%M %p')
    subtitle_text = process_arabic_text(f"تم الإنشاء بتاريخ: {date_str} الساعة {time_str}")
    p.drawCentredString(width/2, height - 1.4*inch, subtitle_text)
    
    # Reset to black for content
    p.setFillColor(colors.black)
    
    # Starting position for content
    y_position = height - 3*inch
    
    # Draw a decorative line
    p.setStrokeColor(secondary_color)
    p.setLineWidth(3)
    p.line(1*inch, y_position, width - 1*inch, y_position)
    
    y_position -= 0.5*inch
    
    # Professor Details Section
    p.setFont(bold_font, 16)
    p.setFillColor(primary_color)
    section_title = process_arabic_text("التفاصيل الشخصية")
    p.drawString(1*inch, y_position, section_title)
    
    y_position -= 0.4*inch
    
    # Draw background boxes for each field
    def draw_field(label, value, y_pos):
        # Background box
        p.setFillColor(light_gray)
        p.rect(1*inch, y_pos - 0.25*inch, width - 2*inch, 0.35*inch, fill=True, stroke=False)
        
        # Label
        p.setFillColor(primary_color)
        p.setFont(bold_font, 12)
        processed_label = process_arabic_text(label)
        p.drawString(1.2*inch, y_pos - 0.05*inch, processed_label)
        
        # Value
        p.setFillColor(colors.black)
        p.setFont(normal_font, 12)
        processed_value = process_arabic_text(str(value))
        p.drawString(3*inch, y_pos - 0.05*inch, processed_value)
        
        return y_pos - 0.5*inch
    
    # Draw fields in Arabic only
    y_position = draw_field("معرف الأستاذ:", professor.profid, y_position)
    y_position = draw_field("الاسم الكامل:", professor.profname or "غير متوفر", y_position)
    y_position = draw_field("رقم الهاتف:", professor.prophone or "غير متوفر", y_position)
    
    y_position -= 0.5*inch
    
    # Additional information section
    p.setStrokeColor(secondary_color)
    p.setLineWidth(2)
    p.line(1*inch, y_position, width - 1*inch, y_position)
    
    y_position -= 0.5*inch
    
    p.setFont(bold_font, 14)
    p.setFillColor(primary_color)
    doc_info_title = process_arabic_text("معلومات الوثيقة")
    p.drawString(1*inch, y_position, doc_info_title)
    
    y_position -= 0.4*inch
    
    y_position = draw_field("نوع الوثيقة:", "ملف الأستاذ", y_position)
    y_position = draw_field("أنشئت بواسطة:", "نظام التقييم", y_position)
    y_position = draw_field("الحالة:", "نشط", y_position)
    
    # Footer
    p.setFont(normal_font, 9)
    p.setFillColor(colors.grey)
    footer_text1 = process_arabic_text("تم إنشاء هذه الوثيقة تلقائياً بواسطة نظام التقييم")
    p.drawCentredString(width/2, 0.75*inch, footer_text1)
    footer_text2 = process_arabic_text(f"© {datetime.now().year} نظام التقييم. جميع الحقوق محفوظة.")
    p.drawCentredString(width/2, 0.5*inch, footer_text2)
    
    # Draw page border
    p.setStrokeColor(primary_color)
    p.setLineWidth(2)
    p.rect(0.5*inch, 0.5*inch, width - 1*inch, height - 1*inch, fill=False, stroke=True)
    
    # Close the PDF object cleanly, and we're done.
    p.showPage()
    p.save()
    
    return response

# ====================
# COURSE VIEWS
# ====================
def course_list(request):
    search_query = request.GET.get('search', '').strip()
    courses = CourseTbl.objects.select_related('prof').all()
    
    if search_query:
        # ALL words must match for more accurate results
        search_terms = [term for term in search_query.split() if term]
        
        for term in search_terms:
            courses = courses.filter(
                Q(coursename__icontains=term) |
                Q(courseid__icontains=term) |
                Q(prof__profname__icontains=term) |
                Q(cid__icontains=term)
            )
        
        courses = courses.order_by('coursename')
    else:
        courses = courses.order_by('coursename')
    
    courses_list = list(courses)
    return render(request, 'evaluation_app/course_list.html', {
        'courses': courses_list,
        'search_query': search_query,
        'results_count': len(courses_list)
    })

@not_guest_required
def course_create(request):
    if request.method == 'POST':
        courseid = request.POST.get('courseid')
        coursename = request.POST.get('coursename')
        prof = request.POST.get('prof') or None
        
        # Check for duplicate courseid
        if courseid and CourseTbl.objects.filter(courseid=courseid).exists():
            messages.error(request, 'A course with this Course ID already exists. Please use a different ID.')
            professors = list(ProfessorTbl.objects.all())
            return render(request, 'evaluation_app/course_form.html', {
                'professors': professors,
                'courseid': courseid,
                'coursename': coursename,
                'prof': prof
            })
        
        course = CourseTbl(
            courseid=courseid,
            coursename=coursename,
            prof_id=prof,
        )
        course.save()
        messages.success(request, 'Course created successfully!')
        return redirect('course_list')
    professors = list(ProfessorTbl.objects.all())
    return render(request, 'evaluation_app/course_form.html', {'professors': professors})

@not_guest_required
def course_update(request, pk):
    course = get_object_or_404(CourseTbl, pk=pk)
    if request.method == 'POST':
        courseid = request.POST.get('courseid')
        coursename = request.POST.get('coursename')
        prof = request.POST.get('prof') or None
        
        # Check for duplicate courseid (excluding current course)
        if courseid and CourseTbl.objects.filter(courseid=courseid).exclude(pk=pk).exists():
            messages.error(request, 'A course with this Course ID already exists. Please use a different ID.')
            professors = list(ProfessorTbl.objects.all())
            # Preserve entered data
            course.courseid = courseid
            course.coursename = coursename
            course.prof_id = prof
            return render(request, 'evaluation_app/course_form.html', {'course': course, 'professors': professors})
        
        course.courseid = courseid
        course.coursename = coursename
        course.prof_id = prof
        course.save()
        messages.success(request, 'Course updated successfully!')
        return redirect('course_list')
    professors = list(ProfessorTbl.objects.all())
    return render(request, 'evaluation_app/course_form.html', {'course': course, 'professors': professors})

@can_delete_required
def course_delete(request, pk):
    course = get_object_or_404(CourseTbl, pk=pk)
    if request.method == 'POST':
        try:
            course.delete()
            messages.success(request, 'Course deleted successfully!')
        except IntegrityError:
            messages.error(request, 'Cannot delete this course because it has associated training sessions. Please delete those records first.')
        return redirect('course_list')
    return render(request, 'evaluation_app/course_confirm_delete.html', {'course': course})

# ====================
# PARTICIPANT VIEWS
# ====================
def participant_list(request):
    search_query = request.GET.get('search', '').strip()
    participants = ParticipantTbl.objects.all()
    
    if search_query:
        # ALL words must match for more accurate results
        search_terms = [term for term in search_query.split() if term]
        
        for term in search_terms:
            participants = participants.filter(
                Q(participant_name__icontains=term) |
                Q(participant_id__icontains=term) |
                Q(participant_phone__icontains=term) |
                Q(participant_email__icontains=term)
            )
        
        participants = participants.order_by('participant_name')
    else:
        participants = participants.order_by('participant_name')
    
    participants_list = list(participants)
    return render(request, 'evaluation_app/participant_list.html', {
        'participants': participants_list,
        'search_query': search_query,
        'results_count': len(participants_list)
    })

@not_guest_required
def participant_create(request):
    if request.method == 'POST':
        participant = ParticipantTbl(
            participant_id=request.POST.get('participant_id'),
            participant_name=request.POST.get('participant_name'),
            participant_phone=request.POST.get('participant_phone') or None,
            participant_email=request.POST.get('participant_email'),
        )
        participant.save()
        messages.success(request, 'Participant created successfully!')
        return redirect('participant_list')
    return render(request, 'evaluation_app/participant_form.html')

@not_guest_required
def participant_update(request, pk):
    participant = get_object_or_404(ParticipantTbl, pk=pk)
    if request.method == 'POST':
        participant.participant_name = request.POST.get('participant_name')
        participant.participant_phone = request.POST.get('participant_phone') or None
        participant.participant_email = request.POST.get('participant_email')
        participant.save()
        messages.success(request, 'Participant updated successfully!')
        return redirect('participant_list')
    return render(request, 'evaluation_app/participant_form.html', {'participant': participant})

@can_delete_required
def participant_delete(request, pk):
    participant = get_object_or_404(ParticipantTbl, pk=pk)
    if request.method == 'POST':
        try:
            participant.delete()
            messages.success(request, 'Participant deleted successfully!')
        except IntegrityError:
            messages.error(request, 'Cannot delete this participant because they have associated training sessions or evaluations. Please delete those records first.')
        return redirect('participant_list')
    return render(request, 'evaluation_app/participant_confirm_delete.html', {'participant': participant})

# ====================
# LOCATION VIEWS
# ====================
def location_list(request):
    search_query = request.GET.get('search', '').strip()
    locations = LocationTbl.objects.all()
    
    if search_query:
        # ALL words must match for more accurate results
        search_terms = [term for term in search_query.split() if term]
        
        for term in search_terms:
            locations = locations.filter(
                Q(locationname__icontains=term) |
                Q(id__icontains=term)
            )
        
        locations = locations.order_by('locationname')
    else:
        locations = locations.order_by('locationname')
    
    locations_list = list(locations)
    return render(request, 'evaluation_app/location_list.html', {
        'locations': locations_list,
        'search_query': search_query,
        'results_count': len(locations_list)
    })

@not_guest_required
def location_create(request):
    if request.method == 'POST':
        location = LocationTbl(
            locationname=request.POST.get('locationname'),
        )
        location.save()
        messages.success(request, 'Location created successfully!')
        return redirect('location_list')
    return render(request, 'evaluation_app/location_form.html')

@not_guest_required
def location_update(request, pk):
    location = get_object_or_404(LocationTbl, pk=pk)
    if request.method == 'POST':
        location.locationname = request.POST.get('locationname')
        location.save()
        messages.success(request, 'Location updated successfully!')
        return redirect('location_list')
    return render(request, 'evaluation_app/location_form.html', {'location': location})

@can_delete_required
def location_delete(request, pk):
    location = get_object_or_404(LocationTbl, pk=pk)
    if request.method == 'POST':
        try:
            location.delete()
            messages.success(request, 'Location deleted successfully!')
        except IntegrityError:
            messages.error(request, 'Cannot delete this location because it has associated training sessions. Please delete those records first.')
        return redirect('location_list')
    return render(request, 'evaluation_app/location_confirm_delete.html', {'location': location})

# ====================
# ABOUT & CONTACT VIEWS
# ====================
def about(request):
    """About page view"""
    return render(request, 'evaluation_app/about.html')

def contact(request):
    """Contact page view with form handling"""
    if request.method == 'POST':
        # Get form data
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone', '')
        subject = request.POST.get('subject')
        message_text = request.POST.get('message')
        
        # Save to database
        contact_message = ContactMessage(
            name=name,
            email=email,
            phone=phone,
            subject=subject,
            message=message_text
        )
        contact_message.save()
        
        messages.success(request, f'Thank you {name}! Your message has been received. We will get back to you soon.')
        return redirect('contact')
    
    return render(request, 'evaluation_app/contact.html')

# ====================
# CONTACT MESSAGE VIEWS
# ====================
@user_or_admin_required
def contact_list(request):
    """List all contact messages"""
    search_query = request.GET.get('search', '').strip()
    contacts = ContactMessage.objects.all()
    
    if search_query:
        # ALL words must match for more accurate results
        search_terms = [term for term in search_query.split() if term]
        
        for term in search_terms:
            contacts = contacts.filter(
                Q(name__icontains=term) |
                Q(email__icontains=term) |
                Q(subject__icontains=term) |
                Q(message__icontains=term) |
                Q(phone__icontains=term)
            )
        
        contacts = contacts.order_by('-created_at')
    else:
        contacts = contacts.order_by('-created_at')
    
    contacts_list = list(contacts)
    return render(request, 'evaluation_app/contact_list.html', {
        'contacts': contacts_list,
        'search_query': search_query,
        'results_count': len(contacts_list)
    })

@user_or_admin_required
def contact_update(request, pk):
    """Update a contact message (mark as read, add notes, etc.)"""
    contact_msg = get_object_or_404(ContactMessage, pk=pk)
    
    if request.method == 'POST':
        contact_msg.name = request.POST.get('name')
        contact_msg.email = request.POST.get('email')
        contact_msg.phone = request.POST.get('phone', '')
        contact_msg.subject = request.POST.get('subject')
        contact_msg.message = request.POST.get('message')
        contact_msg.is_read = request.POST.get('is_read') == 'on'
        contact_msg.save()
        
        messages.success(request, 'Contact message updated successfully!')
        return redirect('contact_list')
    
    return render(request, 'evaluation_app/contact_form.html', {'contact': contact_msg})

@can_delete_required
def contact_delete(request, pk):
    """Delete a contact message"""
    contact_msg = get_object_or_404(ContactMessage, pk=pk)
    
    if request.method == 'POST':
        contact_msg.delete()
        messages.success(request, 'Contact message deleted successfully!')
        return redirect('contact_list')
    
    return render(request, 'evaluation_app/contact_confirm_delete.html', {'contact': contact_msg})


# ============================================
# AUTHENTICATION VIEWS
# ============================================

def user_login(request):
    """Handle user login"""
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            
            # Redirect to next parameter or home
            next_url = request.GET.get('next', 'home')
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'evaluation_app/login.html')


def user_register(request):
    """Handle user registration"""
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        phone = request.POST.get('phone', '')
        role = request.POST.get('role', 'guest')
        
        # Validation
        if not username or not email or not password:
            messages.error(request, 'Please fill in all required fields.')
            return render(request, 'evaluation_app/register.html')
        
        if password != password_confirm:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'evaluation_app/register.html')
        
        if len(password) < 6:
            messages.error(request, 'Password must be at least 6 characters long.')
            return render(request, 'evaluation_app/register.html')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return render(request, 'evaluation_app/register.html')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered.')
            return render(request, 'evaluation_app/register.html')
        
        # Validate role
        if role not in ['admin', 'user', 'guest']:
            role = 'guest'
        
        # Create user
        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name
            )
            
            # Update profile with role and phone
            user.profile.role = role
            user.profile.phone = phone
            user.profile.save()
            
            messages.success(request, f'Account created successfully! You can now log in as {role}.')
            return redirect('login')
            
        except Exception as e:
            messages.error(request, f'Error creating account: {str(e)}')
            return render(request, 'evaluation_app/register.html')
    
    return render(request, 'evaluation_app/register.html')


@login_required
def user_logout(request):
    """Handle user logout with verification"""
    if request.method == 'POST':
        logout(request)
        messages.success(request, 'You have been logged out successfully.')
        return redirect('home')
    return render(request, 'evaluation_app/logout_confirm.html')


@login_required
def user_dashboard(request):
    """User dashboard showing profile and stats"""
    # Ensure user has a profile (create if doesn't exist)
    try:
        user_profile = request.user.profile
    except UserProfile.DoesNotExist:
        user_profile = UserProfile.objects.create(user=request.user, role='guest')
    
    context = {
        'user_profile': user_profile,
    }
    
    # Add role-specific data
    if user_profile.is_admin():
        context['total_users'] = User.objects.count()
        context['total_evaluations'] = EvaluationTab.objects.count()
        context['unread_contacts'] = ContactMessage.get_unread_count()
        # Add system settings for admin
        context['system_settings'] = SystemSettings.get_settings()
    
    return render(request, 'evaluation_app/dashboard.html', context)


# System Management Views
def system_closed(request):
    """Display system closed/maintenance page"""
    settings = SystemSettings.get_settings()
    context = {
        'settings': settings,
        'closure_message': settings.closure_message or 'The system is currently closed for maintenance. Please check back later.',
        'closure_end_date': settings.closure_end_date,
    }
    return render(request, 'evaluation_app/system_closed.html', context)


@login_required
def toggle_system_status(request):
    """Toggle system open/closed status (admin only)"""
    # Check if user is admin
    if not hasattr(request.user, 'profile') or not request.user.profile.is_admin():
        messages.error(request, 'You do not have permission to manage system status.')
        return redirect('home')
    
    settings = SystemSettings.get_settings()
    settings.is_system_open = not settings.is_system_open
    settings.updated_by = request.user
    
    if not settings.is_system_open:
        from django.utils import timezone
        settings.closure_start_date = timezone.now()
    
    settings.save()
    
    status = "opened" if settings.is_system_open else "closed"
    messages.success(request, f'System has been {status} successfully.')
    
    return redirect(request.META.get('HTTP_REFERER', 'home'))


@login_required
def manage_system_settings(request):
    """Manage system settings (admin only)"""
    # Check if user is admin
    if not hasattr(request.user, 'profile') or not request.user.profile.is_admin():
        messages.error(request, 'You do not have permission to manage system settings.')
        return redirect('home')
    
    settings = SystemSettings.get_settings()
    
    if request.method == 'POST':
        settings.is_system_open = request.POST.get('is_system_open') == 'on'
        settings.closure_message = request.POST.get('closure_message', '')
        settings.allow_admin_access = request.POST.get('allow_admin_access') == 'on'
        settings.allow_guest_evaluations = request.POST.get('allow_guest_evaluations') == 'on'
        
        # Handle closure end date
        closure_end_date = request.POST.get('closure_end_date')
        if closure_end_date:
            from django.utils import timezone
            from datetime import datetime
            try:
                settings.closure_end_date = timezone.make_aware(
                    datetime.strptime(closure_end_date, '%Y-%m-%dT%H:%M')
                )
            except ValueError:
                pass
        
        if not settings.is_system_open:
            from django.utils import timezone
            if not settings.closure_start_date:
                settings.closure_start_date = timezone.now()
        else:
            settings.closure_start_date = None
        
        settings.updated_by = request.user
        settings.save()
        
        messages.success(request, 'System settings updated successfully.')
        return redirect('manage_system_settings')
    
    context = {
        'settings': settings,
    }
    return render(request, 'evaluation_app/system_settings.html', context)


# ====================
# TRAINING SESSION VIEWS
# ====================
@user_or_admin_required
def train_list(request):
    """List all training sessions"""
    search_query = request.GET.get('search', '').strip()
    training_sessions = TrainTbl.objects.select_related('course', 'professor', 'location').all()
    
    if search_query:
        search_terms = [term for term in search_query.split() if term]
        for term in search_terms:
            training_sessions = training_sessions.filter(
                Q(course__coursename__icontains=term) |
                Q(professor__profname__icontains=term) |
                Q(location__locationname__icontains=term) |
                Q(trainid__icontains=term)
            )
    
    training_sessions_list = list(training_sessions.order_by('-train_date', '-trainid'))
    
    return render(request, 'evaluation_app/train_list.html', {
        'training_sessions': training_sessions_list,
        'search_query': search_query,
        'total_count': len(training_sessions_list)
    })


@user_or_admin_required
def train_create(request):
    """Create a new training session"""
    if request.method == 'POST':
        train = TrainTbl(
            course_id=request.POST.get('course') or None,
            professor_id=request.POST.get('professor') or None,
            location_id=request.POST.get('location') or None,
            train_date=request.POST.get('train_date') or None,
            is_active=request.POST.get('is_active') == 'on',
        )
        train.save()
        messages.success(request, 'Training session created successfully!')
        return redirect('train_list')
    
    courses = list(CourseTbl.objects.all())
    professors = list(ProfessorTbl.objects.all())
    locations = list(LocationTbl.objects.all())
    train = list(TrainTbl.objects.select_related('course', 'professor', 'location').all())
    
    return render(request, 'evaluation_app/train_form.html', {
        'courses': courses,
        'professors': professors,
        'locations': locations,
        'train': train
    })


@user_or_admin_required
def train_update(request, pk):
    """Update an existing training session"""
    train = get_object_or_404(TrainTbl, pk=pk)
    
    if request.method == 'POST':
        train.course_id = request.POST.get('course') or None
        train.professor_id = request.POST.get('professor') or None
        train.location_id = request.POST.get('location') or None
        train.train_date = request.POST.get('train_date') or None
        train.is_active = request.POST.get('is_active') == 'on'
        train.save()
        messages.success(request, 'Training session updated successfully!')
        return redirect('train_list')
    
    courses = list(CourseTbl.objects.all())
    professors = list(ProfessorTbl.objects.all())
    locations = list(LocationTbl.objects.all())
    
    return render(request, 'evaluation_app/train_form.html', {
        'train': train,
        'courses': courses,
        'professors': professors,
        'locations': locations
    })


@can_delete_required
def train_delete(request, pk):
    """Delete a training session"""
    train = get_object_or_404(TrainTbl, pk=pk)
    
    if request.method == 'POST':
        train.delete()
        messages.success(request, 'Training session deleted successfully!')
        return redirect('train_list')
    
    return render(request, 'evaluation_app/train_confirm_delete.html', {'train': train})


@login_required
def train_download_evaluations_pdf(request, pk):
    """Generate PDF report for all evaluations of a specific training session"""
    from django.http import HttpResponse
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import inch
    from reportlab.pdfgen import canvas
    from reportlab.lib import colors
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from datetime import datetime
    import os
    import arabic_reshaper
    from bidi.algorithm import get_display
    
    train = get_object_or_404(TrainTbl, pk=pk)
    
    # Get all evaluations for this training session
    evaluations = EvaluationTab.objects.filter(train=train).select_related('participant')
    
    if not evaluations.exists():
        messages.warning(request, 'No evaluations found for this training session.')
        return redirect('train_list')
    
    # Create the HttpResponse object with PDF headers
    response = HttpResponse(content_type='application/pdf')
    train_name = train.course.coursename if train.course else "Unknown"
    filename = f'Training_{train.trainid}_{train_name.replace(" ", "_")}_Evaluations.pdf'
    response['Content-Disposition'] = f'inline; filename="{filename}"'
    
    # Create the PDF object
    p = canvas.Canvas(response, pagesize=A4)
    width, height = A4
    
    # Register Arabic-supporting font
    try:
        font_registered = False
        
        # Try Windows system fonts (Arial, Tahoma support Arabic)
        windows_fonts = [
            ('C:\\Windows\\Fonts\\arial.ttf', 'C:\\Windows\\Fonts\\arialbd.ttf', 'Arial'),
            ('C:\\Windows\\Fonts\\tahoma.ttf', 'C:\\Windows\\Fonts\\tahomabd.ttf', 'Tahoma'),
        ]
        
        for normal_path, bold_path, font_name in windows_fonts:
            if os.path.exists(normal_path):
                try:
                    pdfmetrics.registerFont(TTFont(font_name, normal_path))
                    if os.path.exists(bold_path):
                        pdfmetrics.registerFont(TTFont(f'{font_name}-Bold', bold_path))
                    else:
                        pdfmetrics.registerFont(TTFont(f'{font_name}-Bold', normal_path))
                    
                    normal_font = font_name
                    bold_font = f'{font_name}-Bold'
                    font_registered = True
                    break
                except:
                    continue
        
        if not font_registered:
            normal_font = 'Helvetica'
            bold_font = 'Helvetica-Bold'
            
    except Exception as e:
        normal_font = 'Helvetica'
        bold_font = 'Helvetica-Bold'
    
    # Helper function to process Arabic text
    def process_arabic_text(text):
        """Process Arabic text for proper RTL display in PDF"""
        if not text:
            return ""
        
        text = str(text)
        has_arabic = any('\u0600' <= char <= '\u06FF' for char in text)
        
        if has_arabic:
            reshaped_text = arabic_reshaper.reshape(text)
            bidi_text = get_display(reshaped_text)
            return bidi_text
        
        return text
    
    # Arabic questions
    questions = [
        "كان المدرب على دراية ومعرفة والمام كافي بمواضيع البرنامج",
        "نجح المدرب في ايصال المعلومة الى المتدربين بسهولة",
        "كان المدرب ذو مقدرة على احداث التفاعل والمشاركة البناءة وادارة النقاشات كما كان متمكنا في ادارة المدخلات والاستفسارات",
        "استطاع المدرب ربط المادة التدريبية بالواقع العملي للمتدربين",
        "استخدام المدرب وسائل وانشطة تدريبية مختلفة في تزويد المشاركين بالمهارات",
        "كانت المادة التدريبية المستخدمة ملائمة ومنسجمة مع اهداف البرنامج",
        "كانت المواضيع العلمية للبرنامج منظمة ومرتبطة بشكل منطقي مما سهل عملية التعلم المطلوبة",
        "سلامة وسلاسة اللغة التي كتبت بها المادة التدريبية",
        "المادة التي تم طرحها وتناولها غطت مفردات البرنامج",
        "التكنولوجيا الحديثة التي تم طرحها في البرنامج",
        "الاشعار بوقت تنفيذ البرنامج التدريبي ومكان انعقاد كان مناسب",
        "القاعات التدريبية وفرت بيئة تعليمية مريحة",
        "مكان ووقت وانعقاد البرنامج ساهم في زيادة فاعلية البرنامج",
        "تنظيم برنامج كان مناسبا من حيث (فترات الاستراحة ,مستلزمات التدريب ,الخ)",
        "مدة البرنامج كانت كافية لتغطية كافة اهداف الدورة التدريبية"
    ]
    
    # Set up colors
    primary_color = colors.HexColor('#2c3e50')
    secondary_color = colors.HexColor('#3498db')
    accent_color = colors.HexColor('#27ae60')
    light_gray = colors.HexColor('#ecf0f1')
    separator_color = colors.HexColor('#95a5a6')
    
    # Draw header background
    p.setFillColor(primary_color)
    p.rect(0, height - 2.5*inch, width, 2.5*inch, fill=True, stroke=False)
    
    # Title
    p.setFillColor(colors.white)
    p.setFont(bold_font, 22)
    title_text = process_arabic_text("تقرير تقييمات البرنامج التدريبي")
    p.drawCentredString(width/2, height - 0.9*inch, title_text)
    
    # Training info
    p.setFont(bold_font, 14)
    course_name = train.course.coursename if train.course else "غير متوفر"
    course_text = process_arabic_text(f"البرنامج: {course_name}")
    p.drawCentredString(width/2, height - 1.3*inch, course_text)
    
    p.setFont(normal_font, 11)
    professor_name = train.professor.profname if train.professor else "غير متوفر"
    location_name = train.location.locationname if train.location else "غير متوفر"
    train_date = train.train_date.strftime('%Y/%m/%d') if train.train_date else "غير متوفر"
    
    info_line = process_arabic_text(f"المدرب: {professor_name} | المكان: {location_name} | التاريخ: {train_date}")
    p.drawCentredString(width/2, height - 1.65*inch, info_line)
    
    # Count info
    p.setFont(bold_font, 11)
    count_text = process_arabic_text(f"عدد التقييمات: {evaluations.count()}")
    p.drawCentredString(width/2, height - 2*inch, count_text)
    
    # Date
    p.setFont(normal_font, 9)
    current_date = datetime.now()
    date_str = current_date.strftime('%Y/%m/%d')
    date_text = process_arabic_text(f"تاريخ الطباعة: {date_str}")
    p.drawCentredString(width/2, height - 2.3*inch, date_text)
    
    # Reset to black for content
    p.setFillColor(colors.black)
    
    # Starting position for content
    y_position = height - 2.9*inch
    
    # Process each evaluation
    evaluation_count = 0
    
    for evaluation in evaluations:
        evaluation_count += 1
        
        # Check if we need a new page
        if y_position < 8*inch:
            p.showPage()
            p.setFont(normal_font, 10)
            y_position = height - 1*inch
        
        # Evaluation header
        p.setFillColor(secondary_color)
        p.rect(0.8*inch, y_position - 0.25*inch, width - 1.6*inch, 0.4*inch, fill=True, stroke=False)
        
        p.setFillColor(colors.white)
        p.setFont(bold_font, 12)
        participant_name = evaluation.participant.participant_name if evaluation.participant else "غير متوفر"
        eval_header = process_arabic_text(f"تقييم رقم {evaluation_count} - المتدرب: {participant_name}")
        p.drawCentredString(width/2, y_position - 0.05*inch, eval_header)
        
        y_position -= 0.6*inch
        
        # Get all question values
        question_values = [
            evaluation.ev_q_1, evaluation.ev_q_2, evaluation.ev_q_3, evaluation.ev_q_4, evaluation.ev_q_5,
            evaluation.ev_q_6, evaluation.ev_q_7, evaluation.ev_q_8, evaluation.ev_q_9, evaluation.ev_q_10,
            evaluation.ev_q_11, evaluation.ev_q_12, evaluation.ev_q_13, evaluation.ev_q_14, evaluation.ev_q_15
        ]
        
        # Draw questions with summations
        question_counter = 0
        group_sum = 0
        total_sum = 0
        total_count = 0
        
        for i, (question, value) in enumerate(zip(questions, question_values), 1):
            # Check if we need a new page
            if y_position < 1.5*inch:
                p.showPage()
                p.setFont(normal_font, 10)
                y_position = height - 1*inch
            
            # Draw question
            p.setFillColor(colors.black)
            p.setFont(bold_font, 8)
            q_text = process_arabic_text(f"{i}. {question}")
            
            # Handle long questions with wrapping
            if len(q_text) > 90:
                words = q_text.split()
                line1 = ' '.join(words[:len(words)//2])
                line2 = ' '.join(words[len(words)//2:])
                p.drawRightString(width - 1*inch, y_position, line1)
                y_position -= 0.12*inch
                p.drawRightString(width - 1*inch, y_position, line2)
            else:
                p.drawRightString(width - 1*inch, y_position, q_text)
            
            # Draw value with color coding
            p.setFont(bold_font, 10)
            if value is not None:
                if value >= 8:
                    p.setFillColor(colors.green)
                elif value >= 5:
                    p.setFillColor(colors.orange)
                else:
                    p.setFillColor(colors.red)
                
                p.drawString(1*inch, y_position, str(value))
                group_sum += value
                total_sum += value
                total_count += 1
            else:
                p.setFillColor(colors.gray)
                p.drawString(1*inch, y_position, "N/A")
            
            y_position -= 0.25*inch
            question_counter += 1
            
            # Add group summation after every 5 questions
            if question_counter == 5 and group_sum > 0:
                if y_position < 1*inch:
                    p.showPage()
                    y_position = height - 1*inch
                
                p.setFillColor(accent_color)
                p.rect(0.9*inch, y_position - 0.12*inch, width - 1.8*inch, 0.25*inch, fill=True, stroke=False)
                
                p.setFillColor(colors.white)
                p.setFont(bold_font, 9)
                group_avg = group_sum / 5
                sum_text = process_arabic_text(f"مجموع الأسئلة {i-4} - {i}: {group_sum} (متوسط: {group_avg:.2f})")
                p.drawCentredString(width/2, y_position, sum_text)
                
                y_position -= 0.4*inch
                question_counter = 0
                group_sum = 0
        
        # Check if there's a remaining group
        if question_counter > 0 and group_sum > 0:
            if y_position < 1*inch:
                p.showPage()
                y_position = height - 1*inch
            
            p.setFillColor(accent_color)
            p.rect(0.9*inch, y_position - 0.12*inch, width - 1.8*inch, 0.25*inch, fill=True, stroke=False)
            
            p.setFillColor(colors.white)
            p.setFont(bold_font, 9)
            group_avg = group_sum / question_counter
            start_q = 15 - question_counter + 1
            sum_text = process_arabic_text(f"مجموع الأسئلة {start_q} - 15: {group_sum} (متوسط: {group_avg:.2f})")
            p.drawCentredString(width/2, y_position, sum_text)
            
            y_position -= 0.4*inch
        
        # Total summation for this evaluation
        if total_count > 0:
            if y_position < 1*inch:
                p.showPage()
                y_position = height - 1*inch
            
            p.setFillColor(primary_color)
            p.rect(0.9*inch, y_position - 0.15*inch, width - 1.8*inch, 0.3*inch, fill=True, stroke=False)
            
            p.setFillColor(colors.white)
            p.setFont(bold_font, 10)
            total_avg = total_sum / total_count
            total_text = process_arabic_text(f"المجموع الكلي: {total_sum}/{total_count * 10} | المتوسط: {total_avg:.2f}/10")
            p.drawCentredString(width/2, y_position, total_text)
            
            y_position -= 0.5*inch
        
        # Notes section if available
        if evaluation.ev_q_notes and evaluation.ev_q_notes.strip():
            if y_position < 1.5*inch:
                p.showPage()
                y_position = height - 1*inch
            
            p.setFillColor(primary_color)
            p.setFont(bold_font, 9)
            notes_title = process_arabic_text("ملاحظات:")
            p.drawRightString(width - 1*inch, y_position, notes_title)
            
            y_position -= 0.25*inch
            
            p.setFillColor(colors.black)
            p.setFont(normal_font, 8)
            notes_text = process_arabic_text(evaluation.ev_q_notes)
            
            # Wrap notes text
            max_width = width - 2*inch
            lines = []
            current_line = ""
            for word in notes_text.split():
                test_line = current_line + " " + word if current_line else word
                if p.stringWidth(test_line, normal_font, 8) < max_width:
                    current_line = test_line
                else:
                    lines.append(current_line)
                    current_line = word
            if current_line:
                lines.append(current_line)
            
            for line in lines[:3]:  # Limit to 3 lines for space
                p.drawRightString(width - 1*inch, y_position, line)
                y_position -= 0.18*inch
            
            y_position -= 0.2*inch
        
        # Separator line between evaluations (dashed line)
        if evaluation_count < evaluations.count():
            if y_position < 1*inch:
                p.showPage()
                y_position = height - 1*inch
            
            p.setStrokeColor(separator_color)
            p.setLineWidth(1)
            p.setDash(6, 3)  # Dashed line pattern
            p.line(1*inch, y_position, width - 1*inch, y_position)
            p.setDash()  # Reset to solid line
            
            y_position -= 0.4*inch
    
    # Footer on last page
    p.setFont(normal_font, 8)
    p.setFillColor(colors.gray)
    footer_text = process_arabic_text(f"تم إنشاء هذا التقرير تلقائياً - تدريب رقم: {train.trainid}")
    p.drawCentredString(width/2, 0.5*inch, footer_text)
    
    # Save PDF
    p.showPage()
    p.save()
    
    return response


@login_required
def train_report_pdf(request, pk):
    """Generate summary report PDF: training info + all participants + sum/avg per evaluation part in table format"""
    from django.http import HttpResponse
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.lib.enums import TA_CENTER, TA_RIGHT
    from datetime import datetime
    import os
    import arabic_reshaper
    from bidi.algorithm import get_display

    train = get_object_or_404(TrainTbl, pk=pk)

    evaluations = EvaluationTab.objects.filter(train=train).select_related('participant').order_by(
        'participant__participant_name'
    )

    if not evaluations.exists():
        messages.warning(request, 'No evaluations found for this training session.')
        return redirect('train_list')

    # ── Font setup ──────────────────────────────────────────────────────────
    try:
        font_registered = False
        windows_fonts = [
            ('C:\\Windows\\Fonts\\arial.ttf',  'C:\\Windows\\Fonts\\arialbd.ttf',  'Arial'),
            ('C:\\Windows\\Fonts\\tahoma.ttf', 'C:\\Windows\\Fonts\\tahomabd.ttf', 'Tahoma'),
        ]
        for normal_path, bold_path, font_name in windows_fonts:
            if os.path.exists(normal_path):
                try:
                    pdfmetrics.registerFont(TTFont(font_name, normal_path))
                    pdfmetrics.registerFont(TTFont(f'{font_name}-Bold',
                                                   bold_path if os.path.exists(bold_path) else normal_path))
                    normal_font = font_name
                    bold_font   = f'{font_name}-Bold'
                    font_registered = True
                    break
                except Exception:
                    continue
        if not font_registered:
            normal_font = 'Helvetica'
            bold_font   = 'Helvetica-Bold'
    except Exception:
        normal_font = 'Helvetica'
        bold_font   = 'Helvetica-Bold'

    def ar(text):
        """Reshape + bidi-reorder Arabic text for ReportLab."""
        if not text:
            return ""
        text = str(text)
        if any('\u0600' <= c <= '\u06FF' for c in text):
            return get_display(arabic_reshaper.reshape(text))
        return text

    # ── Collect evaluation data ──────────────────────────────────────────────
    rows_data   = []
    part1_sums  = []
    part2_sums  = []
    part3_sums  = []
    total_sums  = []

    for idx, ev in enumerate(evaluations, 1):
        q = [ev.ev_q_1,  ev.ev_q_2,  ev.ev_q_3,  ev.ev_q_4,  ev.ev_q_5,
             ev.ev_q_6,  ev.ev_q_7,  ev.ev_q_8,  ev.ev_q_9,  ev.ev_q_10,
             ev.ev_q_11, ev.ev_q_12, ev.ev_q_13, ev.ev_q_14, ev.ev_q_15]

        p1 = [v for v in q[0:5]  if v is not None]
        p2 = [v for v in q[5:10] if v is not None]
        p3 = [v for v in q[10:15] if v is not None]

        p1_sum  = sum(p1) if p1 else 0
        p2_sum  = sum(p2) if p2 else 0
        p3_sum  = sum(p3) if p3 else 0
        tot_sum = p1_sum + p2_sum + p3_sum

        all_valid = [v for v in q if v is not None]
        p1_avg   = p1_sum  / len(p1)  if p1  else 0.0
        p2_avg   = p2_sum  / len(p2)  if p2  else 0.0
        p3_avg   = p3_sum  / len(p3)  if p3  else 0.0
        tot_avg  = tot_sum / len(all_valid) if all_valid else 0.0

        part1_sums.append(p1_sum)
        part2_sums.append(p2_sum)
        part3_sums.append(p3_sum)
        total_sums.append(tot_sum)

        name = ev.participant.participant_name if ev.participant else "N/A"
        rows_data.append([
            str(idx),
            ar(name),
            str(p1_sum),
            f"{p1_avg:.2f}",
            str(p2_sum),
            f"{p2_avg:.2f}",
            str(p3_sum),
            f"{p3_avg:.2f}",
            str(tot_sum),
            f"{tot_avg:.2f}",
        ])

    n = len(rows_data)
    ov_p1  = sum(part1_sums)
    ov_p2  = sum(part2_sums)
    ov_p3  = sum(part3_sums)
    ov_tot = sum(total_sums)

   

    # ── PDF setup ───────────────────────────────────────────────────────────
    response = HttpResponse(content_type='application/pdf')
    train_name = train.course.coursename if train.course else "Training"
    filename   = f'Report_Training_{train.trainid}_{train_name.replace(" ", "_")}.pdf'
    response['Content-Disposition'] = f'inline; filename="{filename}"'

    doc = SimpleDocTemplate(
        response, pagesize=landscape(A4),
        leftMargin=0.4*inch, rightMargin=0.4*inch,
        topMargin=0.4*inch, bottomMargin=0.4*inch,
    )

    primary_col   = colors.HexColor("#c7a67a")
    secondary_col = colors.HexColor('#3498db')
    accent_col    = colors.HexColor('#27ae60')
    light_gray    = colors.HexColor('#ecf0f1')
    summary_col   = colors.HexColor("#F3DDDD")

    def ps(name_id, font=None, size=10, color=colors.black, align=TA_CENTER, bold=False):
        return ParagraphStyle(name_id,
                              fontName=bold_font if bold else (font or normal_font),
                              fontSize=size, textColor=color, alignment=align,
                              leading=size + 3)

    story = []

    # ── Header block ────────────────────────────────────────────────────────
    course_name    = ar(train.course.coursename     if train.course    else "N/A")
    professor_name = ar(train.professor.profname    if train.professor else "N/A")
    location_name  = ar(train.location.locationname if train.location  else "N/A")
    train_date_str = train.train_date.strftime('%Y/%m/%d') if train.train_date else "N/A"

    
    label_col     = colors.HexColor('#a8d8ea')   # soft light-blue for labels
    value_col     = colors.white
    card_bg       = colors.HexColor('#34495e')   # slightly lighter than primary

    # Row 1 – big centred title + print date in small text below
    title_NOC = Paragraph(
        ar("شركة نفط الشمال"),
        ps('T', size=15, color=colors.white, bold=True),
    )
    
    title_dept = Paragraph(
        ar("إدارة قسم التدريب والتطوير"),
        ps('T', size=15, color=colors.white, bold=True),
    )
    title_p = Paragraph(
        ar("تقرير البرنامج التدريبي"),
        ps('T', size=15, color=colors.white, bold=True),
    )

    # Row 2 – five info cards: label on top, value below
    def info_cell(label, value):
        lbl = Paragraph(ar(label), ps(f'lbl{label}', size=7, color=label_col, bold=True))
        val = Paragraph(str(value),  ps(f'val{label}', size=10, color=value_col, bold=True))
        return [lbl, val]   # two-row inner table per card

    card_w = doc.width / 5

    def make_card(label, value):
        inner = Table([[Paragraph(ar(label), ps(f'cl{label}', size=7,  color=label_col, bold=True))],
                       [Paragraph(str(value), ps(f'cv{label}', size=10, color=value_col, bold=True))]],
                      colWidths=[card_w - 8])
        inner.setStyle(TableStyle([
            ('ALIGN',         (0, 0), (-1, -1), 'CENTER'),
            ('TOPPADDING',    (0, 0), (-1, -1), 2),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ]))
        return inner

    info_cards = [
        make_card("البرنامج",       course_name),
        make_card("المدرب",          professor_name),
        make_card("المكان",          location_name),
        make_card("التاريخ",         train_date_str),
        make_card("عدد المشاركين",   str(n)),
    ]

    info_row_tbl = Table([info_cards], colWidths=[card_w] * 5)
    info_row_tbl.setStyle(TableStyle([
        ('BACKGROUND',    (0, 0), (-1, -1), card_bg),
        ('ALIGN',         (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN',        (0, 0), (-1, -1), 'MIDDLE'),
        ('LINEAFTER',     (0, 0), (3, 0),   0.5, colors.HexColor('#4a6278')),
        ('TOPPADDING',    (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))

    # Assemble the two-row header table
    header_tbl = Table(
        [[title_NOC], [title_dept], [title_p],[info_row_tbl]],
        colWidths=[doc.width],
    )
    header_tbl.setStyle(TableStyle([
        # Row 0 – title
        ('BACKGROUND',    (0, 0), (0, 1), primary_col),
        ('ALIGN',         (0, 0), (0, 1), 'CENTER'),
        ('TOPPADDING',    (0, 0), (0, 0), 12),
        ('BOTTOMPADDING', (0, 0), (0, 0), 4),
        ('TOPPADDING',    (0, 1), (0, 1), 2),
        ('BOTTOMPADDING', (0, 1), (0, 1), 10),
        # Row 2 – info cards (no extra padding, card handles it)
        ('TOPPADDING',    (0, 2), (0, 2), 0),
        ('BOTTOMPADDING', (0, 2), (0, 2), 0),
        ('LEFTPADDING',   (0, 0), (-1, -1), 0),
        ('RIGHTPADDING',  (0, 0), (-1, -1), 0),
        # Accent bottom border on title rows
      
    ]))
    story.append(header_tbl)
    story.append(Spacer(1, 0.18*inch))

    # ── Main data table ─────────────────────────────────────────────────────
    # Row 0 – group span headers; Row 1 – sub-column headers; Row 2+ – data; last – summary
    hdr_style_w = ps('HW', size=9, color=colors.white, bold=True)
    hdr_style_b = ps('HB', size=9, color=colors.white, bold=True)

    row0 = [
        Paragraph(ar("م"),             hdr_style_w),
        Paragraph(ar("اسم المشارك"),   hdr_style_w),
        Paragraph(ar("القسم الأول (Q1-Q5)"),   hdr_style_b), "",
        Paragraph(ar("القسم الثاني (Q6-Q10)"),  hdr_style_b), "",
        Paragraph(ar("القسم الثالث (Q11-Q15)"), hdr_style_b), "",
        Paragraph(ar("المجموع الكلي"),           hdr_style_b), "",
    ]
    row1 = [
        "", "",
        Paragraph(ar("المجموع"), hdr_style_w), Paragraph(ar("المتوسط"), hdr_style_w),
        Paragraph(ar("المجموع"), hdr_style_w), Paragraph(ar("المتوسط"), hdr_style_w),
        Paragraph(ar("المجموع"), hdr_style_w), Paragraph(ar("المتوسط"), hdr_style_w),
        Paragraph(ar("المجموع"), hdr_style_w), Paragraph(ar("المتوسط"), hdr_style_w),
    ]
    sum_style = ps('SUM', size=9, color=colors.red, bold=True)
    

    table_data = [row0, row1] + rows_data

    # Landscape A4 usable width ≈ 10.69 in
    col_w = [0.35*inch, 2.4*inch,
             0.75*inch, 0.75*inch,
             0.75*inch, 0.75*inch,
             0.75*inch, 0.75*inch,
             0.82*inch, 0.82*inch]

    main_tbl = Table(table_data, colWidths=col_w, repeatRows=2)
    main_tbl.setStyle(TableStyle([
        # ── Span group headers
        ('SPAN', (0, 0), (0, 1)),   # # column
        ('SPAN', (1, 0), (1, 1)),   # name column
        ('SPAN', (2, 0), (3, 0)),   # Part 1
        ('SPAN', (4, 0), (5, 0)),   # Part 2
        ('SPAN', (6, 0), (7, 0)),   # Part 3
        ('SPAN', (8, 0), (9, 0)),   # Total
        # ── Header background
        ('BACKGROUND', (0, 0), (-1, 1), secondary_col),
        # ── Summary row
        ('BACKGROUND', (0, -1), (-1, -1), summary_col),
        ('TEXTCOLOR',  (0, -1), (-1, -1), colors.black),
        ('FONTNAME',   (0, -1), (-1, -1), normal_font),
        # ── Alternating data rows
        ('ROWBACKGROUNDS', (0, 2), (-1, -2), [colors.white, light_gray]),
        # ── Fonts
        ('FONTNAME',  (0, 0),  (-1, 1),  bold_font),
        ('FONTSIZE',  (0, 0),  (-1, 1),  9),
        ('TEXTCOLOR', (0, 0),  (-1, 1),  colors.white),
        ('FONTNAME',  (0, 2),  (-1, -2), normal_font),
        ('FONTSIZE',  (0, 2),  (-1, -2), 9),
        # ── Alignment
        ('ALIGN',   (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN',  (0, 0), (-1, -1), 'MIDDLE'),
        # ── Grid
        ('GRID',    (0, 0), (-1, -1), 0.4, colors.HexColor('#bdc3c7')),
        ('BOX',     (0, 0), (-1, -1), 1.5, primary_col),
        # ── Padding
        ('TOPPADDING',    (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        # ── Accent columns (part totals) slightly tinted
        ('BACKGROUND', (2, 2), (3, -2), colors.HexColor('#eaf4fb')),
        ('BACKGROUND', (4, 2), (5, -2), colors.HexColor('#eafaf1')),
        ('BACKGROUND', (6, 2), (7, -2), colors.HexColor('#fef9e7')),
        ('BACKGROUND', (8, 2), (9, -2), colors.HexColor('#fdedec')),
    ]))
    story.append(main_tbl)

    # ── Footer ───────────────────────────────────────────────────────────────
    story.append(Spacer(1, 0.12*inch))
    footer_p = Paragraph(
        f"{ar('تم إنشاء هذا التقرير تلقائياً بتاريخ')}: {datetime.now().strftime('%Y/%m/%d %H:%M')}  |  "
        f"{ar('تدريب رقم')}: {train.trainid}",
        ps('F', size=12, color=colors.gray),
    )
    story.append(footer_p)

    doc.build(story)
    return response


# ====================
# TRAINING PARTICIPANT VIEWS
# ====================
@user_or_admin_required
def train_participant_list(request):
    """List all training participants"""
    search_query = request.GET.get('search', '').strip()
    train_participants = TrainParticipantTbl.objects.select_related(
        'train__course', 'train__professor', 'participant'
    ).all()
    
    if search_query:
        search_terms = [term for term in search_query.split() if term]
        for term in search_terms:
            train_participants = train_participants.filter(
                Q(participant__participant_name__icontains=term) |
                Q(train__course__coursename__icontains=term) |
                Q(train__trainid__icontains=term)
            )
    
    train_participants_list = list(train_participants.order_by('-evaluation_date', '-train_participant_id'))
    
    return render(request, 'evaluation_app/train_participant_list.html', {
        'train_participants': train_participants_list,
        'search_query': search_query,
        'total_count': len(train_participants_list)
    })


@user_or_admin_required
def train_participant_create(request):
    """Create a new training participant"""
    # Get pre-selected train_id from query parameter
    preselected_train_id = request.GET.get('train_id', None)
    
    if request.method == 'POST':
        train_participant = TrainParticipantTbl(
            train_id=request.POST.get('train') or None,
            participant_id=request.POST.get('participant') or None,
            evaluation_date=request.POST.get('evaluation_date') or None,
            is_active=request.POST.get('is_active') == 'on',
        )
        train_participant.save()
        messages.success(request, 'Training participant created successfully!')
        return redirect('train_participant_list')
    
    training_sessions = list(TrainTbl.objects.select_related('course', 'professor', 'location').filter(is_active=True))
    participants = list(ParticipantTbl.objects.all())
    
    return render(request, 'evaluation_app/train_participant_form.html', {
        'training_sessions': training_sessions,
        'participants': participants,
        'preselected_train_id': preselected_train_id
    })


@user_or_admin_required
def train_participant_update(request, pk):
    """Update an existing training participant"""
    train_participant = get_object_or_404(TrainParticipantTbl, pk=pk)
    
    if request.method == 'POST':
        train_participant.train_id = request.POST.get('train') or None
        train_participant.participant_id = request.POST.get('participant') or None
        train_participant.evaluation_date = request.POST.get('evaluation_date') or None
        train_participant.is_active = request.POST.get('is_active') == 'on'
        train_participant.save()
        messages.success(request, 'Training participant updated successfully!')
        return redirect('train_participant_list')
    
    training_sessions = list(TrainTbl.objects.select_related('course', 'professor', 'location').filter(is_active=True))
    participants = list(ParticipantTbl.objects.all())
    
    return render(request, 'evaluation_app/train_participant_form.html', {
        'train_participant': train_participant,
        'training_sessions': training_sessions,
        'participants': participants
    })


@can_delete_required
def train_participant_delete(request, pk):
    """Delete a training participant"""
    train_participant = get_object_or_404(TrainParticipantTbl, pk=pk)
    
    if request.method == 'POST':
        train_participant.delete()
        messages.success(request, 'Training participant deleted successfully!')
        return redirect('train_participant_list')
    
    return render(request, 'evaluation_app/train_participant_confirm_delete.html', {
        'train_participant': train_participant
    })


# ==================== Database Backup Management ====================
import os
import shutil
import logging
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

def get_backup_dir():
    """Get backup directory and ensure it exists"""
    backup_dir = settings.BASE_DIR / 'backups'
    backup_dir.mkdir(exist_ok=True)
    return backup_dir

def get_db_engine():
    """Detect database engine"""
    engine = settings.DATABASES['default']['ENGINE'].lower()
    if 'mssql' in engine or 'sql_server' in engine:
        return 'mssql'
    elif 'sqlite' in engine:
        return 'sqlite'
    elif 'postgresql' in engine or 'postgres' in engine:
        return 'postgresql'
    elif 'mysql' in engine:
        return 'mysql'
    return 'unknown'

def format_file_size(size_bytes):
    """Format bytes to human-readable size"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} PB"

@admin_required
@ensure_csrf_cookie
def database_backup(request):
    """Database backup management page - Admin only"""
    try:
        # Get backup directory
        backup_dir = get_backup_dir()
        
        # Get list of existing backups
        backups = []
        if backup_dir.exists():
            # Only support .bak (native database) backups
            backup_files = list(backup_dir.glob('*.bak'))
            for backup_file in sorted(backup_files, key=lambda x: x.stat().st_mtime, reverse=True):
                try:
                    file_stat = backup_file.stat()
                    backups.append({
                        'name': backup_file.name,
                        'size': file_stat.st_size,
                        'size_formatted': format_file_size(file_stat.st_size),
                        'created': datetime.fromtimestamp(file_stat.st_mtime),
                        'path': str(backup_file),
                        'type': 'Native DB'
                    })
                except Exception as e:
                    logger.error(f"Error reading backup file {backup_file}: {str(e)}")
                    continue
        
        # Get database info
        db_config = settings.DATABASES['default']
        db_engine = get_db_engine()
        
        db_info = {
            'name': db_config.get('NAME', 'Unknown'),
            'host': db_config.get('HOST', 'localhost'),
            'engine': db_engine.upper(),
            'engine_type': db_engine,
        }
        
        # Calculate total backup size
        total_size = sum(b['size'] for b in backups)
        
        context = {
            'backups': backups[:20],  # Show last 20 backups
            'total_backups': len(backups),
            'total_size': format_file_size(total_size),
            'db_info': db_info,
            'backup_dir': str(backup_dir),
        }
        
        return render(request, 'evaluation_app/database_backup.html', context)
        
    except Exception as e:
        logger.error(f"Database backup page error: {str(e)}")
        messages.error(request, f'Error loading backup page: {str(e)}')
        return redirect('dashboard')


@csrf_exempt
@require_POST
@admin_required
def database_backup_create(request):
    """Create a database backup - Admin only"""
    try:
        # Get backup directory
        backup_dir = get_backup_dir()
        
        # Generate backup filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        db_config = settings.DATABASES['default']
        db_name = db_config.get('NAME', 'database')
        db_engine = get_db_engine()
        
        # Remove any path components from db_name to avoid directory traversal
        db_name_clean = os.path.basename(str(db_name))
        backup_filename = f'{db_name_clean}_backup_{timestamp}.bak'
        backup_path = backup_dir / backup_filename
        
        logger.info(f"Starting backup: {backup_filename} (Engine: {db_engine})")
        
        # Execute database-specific backup
        if db_engine == 'mssql':
            # MSSQL backup
            # Convert Windows path to SQL Server format
            backup_path_str = str(backup_path.absolute()).replace('/', '\\')
            
            logger.info(f"Backup path: {backup_path_str}")
            
            # Use sqlcmd directly to avoid Django transaction issues
            # BACKUP DATABASE cannot run inside a transaction
            import subprocess
            
            # Build sqlcmd command
            sqlcmd_args = [
                'sqlcmd',
                '-S', db_config.get('HOST', 'localhost'),
                '-U', db_config.get('USER'),
                '-P', db_config.get('PASSWORD'),
                '-d', db_name,
                '-Q', f"BACKUP DATABASE [{db_name}] TO DISK = N'{backup_path_str}' WITH FORMAT, INIT, NAME = N'{db_name}-Full Database Backup', SKIP, NOREWIND, NOUNLOAD, STATS = 10"
            ]
            
            logger.info(f"Executing backup via sqlcmd...")
            result = subprocess.run(sqlcmd_args, capture_output=True, text=True, timeout=300)
            
            if result.returncode != 0:
                error_output = result.stderr or result.stdout
                logger.error(f"Backup failed: {error_output}")
                
                if 'permission' in error_output.lower() or 'Operating system error 2' in error_output:
                    raise PermissionError(
                        f"SQL Server cannot write to the backup directory. "
                        f"Please ensure the SQL Server service account has write permissions to: {backup_dir}"
                    )
                raise Exception(f"Backup failed: {error_output}")
            
            logger.info(f"sqlcmd completed successfully")
            
            # Wait for file system to sync
            import time
            time.sleep(2)
                
        elif db_engine == 'sqlite':
            # SQLite backup - simple file copy
            db_path = Path(db_name)
            if db_path.exists():
                shutil.copy2(db_path, backup_path)
            else:
                raise FileNotFoundError(f"SQLite database file not found: {db_name}")
                
        elif db_engine == 'postgresql':
            # PostgreSQL backup using pg_dump
            import subprocess
            pg_dump_cmd = [
                'pg_dump',
                '-h', db_config.get('HOST', 'localhost'),
                '-U', db_config.get('USER', 'postgres'),
                '-F', 'c',  # Custom format
                '-f', str(backup_path),
                db_name
            ]
            result = subprocess.run(pg_dump_cmd, capture_output=True, text=True)
            if result.returncode != 0:
                raise Exception(f"pg_dump failed: {result.stderr}")
                
        elif db_engine == 'mysql':
            # MySQL backup using mysqldump
            import subprocess
            mysqldump_cmd = [
                'mysqldump',
                '-h', db_config.get('HOST', 'localhost'),
                '-u', db_config.get('USER', 'root'),
                f'-p{db_config.get("PASSWORD", "")}',
                '--result-file', str(backup_path),
                db_name
            ]
            result = subprocess.run(mysqldump_cmd, capture_output=True, text=True)
            if result.returncode != 0:
                raise Exception(f"mysqldump failed: {result.stderr}")
        else:
            raise NotImplementedError(f"Backup not implemented for {db_engine}")
        
        # Verify backup file was created
        logger.info(f"Checking if backup file exists: {backup_path}")
        if not backup_path.exists():
            # List files in backup directory for debugging
            existing_files = list(backup_dir.glob('*'))
            logger.error(f"Backup file not found. Files in backup directory: {[f.name for f in existing_files]}")
            raise FileNotFoundError(
                f"Backup file was not created at expected location: {backup_path}. "
                f"SQL Server may have created it elsewhere or lacks write permissions to this directory."
            )
        
        file_size = backup_path.stat().st_size
        logger.info(f"Backup completed: {backup_filename} ({format_file_size(file_size)})")
        
        success_msg = f'Database backup created successfully! File: {backup_filename}'
        
        messages.success(request, success_msg)
        
        return JsonResponse({
            'success': True,
            'message': success_msg,
            'filename': backup_filename,
            'size': file_size,
            'size_formatted': format_file_size(file_size)
        })
        
    except PermissionError as e:
        logger.error(f"Backup permission error: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': f'Permission denied: {str(e)}'
        }, status=403)
        
    except Exception as e:
        logger.error(f"Backup creation failed: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_POST
@admin_required
def database_backup_restore(request, filename):
    """Restore a database backup - Admin only"""
    try:
        backup_dir = get_backup_dir()
        backup_path = backup_dir / filename
        
        # Security check - ensure file is within backup directory
        if not str(backup_path.resolve()).startswith(str(backup_dir.resolve())):
            raise PermissionError('Invalid backup file path!')
        
        if not backup_path.exists():
            raise FileNotFoundError('Backup file not found!')
        
        # Check if this is a JSON backup (Django dumpdata format)
        if backup_path.suffix == '.json':
            logger.info(f"Restoring JSON backup: {filename}")
            
            import subprocess
            import sys
            
            # Use Django's loaddata command with UTF-8 encoding support
            result = subprocess.run(
                [sys.executable, 'manage.py', 'loaddata', str(backup_path)],
                capture_output=True,
                text=False,  # Get bytes to handle encoding properly
                cwd=settings.BASE_DIR,
                env={**os.environ, 'PYTHONIOENCODING': 'utf-8'}
            )
            
            if result.returncode != 0:
                error_msg = result.stderr.decode('utf-8', errors='replace')
                raise Exception(f"Django loaddata failed: {error_msg}")
            
            logger.info(f"JSON restore completed: {filename}")
            messages.success(request, f'Database restored successfully from: {filename}')
            
            return JsonResponse({
                'success': True,
                'message': f'Database restored from JSON backup: {filename}'
            })
        
        # Get database configuration for native backups
        db_config = settings.DATABASES['default']
        db_name = db_config.get('NAME', 'database')
        db_engine = get_db_engine()
        
        logger.info(f"Starting restore: {filename} (Engine: {db_engine})")
        
        # Execute database-specific restore
        if db_engine == 'mssql':
            # MSSQL restore - must connect to master, not the target database
            backup_path_str = str(backup_path.absolute()).replace('/', '\\')
            
            import pyodbc
            
            # Build connection string to master database
            driver = db_config.get('OPTIONS', {}).get('driver', 'ODBC Driver 17 for SQL Server')
            host = db_config.get('HOST', 'localhost')
            port = db_config.get('PORT', '1433')
            user = db_config.get('USER', '')
            password = db_config.get('PASSWORD', '')
            extra_params = db_config.get('OPTIONS', {}).get('extra_params', '')
            
            conn_str = (
                f"DRIVER={{{driver}}};"
                f"SERVER={host},{port};"
                f"DATABASE=master;"
                f"UID={user};"
                f"PWD={password};"
            )
            if extra_params:
                conn_str += f"{extra_params};"
            
            # Close Django's connection to free the database
            connection.close()
            
            # Open a separate connection to master for the restore
            master_conn = pyodbc.connect(conn_str, autocommit=True)
            master_cursor = master_conn.cursor()
            
            try:
                # Check permissions
                master_cursor.execute("""
                    SELECT IS_SRVROLEMEMBER('dbcreator'), IS_SRVROLEMEMBER('sysadmin')
                """)
                row = master_cursor.fetchone()
                has_perm = any(row[i] == 1 for i in range(2))
                
                if not has_perm:
                    raise PermissionError(
                        "User does not have RESTORE DATABASE permission. "
                        "The SQL user needs dbcreator server role or sysadmin. "
                        "Run the grant_backup_permissions.sql script as a SQL admin."
                    )
                
                # Set database to single user to kick all connections
                master_cursor.execute(f"""
                    ALTER DATABASE [{db_name}] SET SINGLE_USER WITH ROLLBACK IMMEDIATE
                """)
                
                # Execute restore from master context
                restore_sql = f"""
                    RESTORE DATABASE [{db_name}]
                    FROM DISK = N'{backup_path_str}'
                    WITH REPLACE, RECOVERY
                """
                master_cursor.execute(restore_sql)
                
                # Consume all result sets from RESTORE (progress messages)
                while master_cursor.nextset():
                    pass
                
                # Return to multi-user mode
                master_cursor.execute(f"""
                    ALTER DATABASE [{db_name}] SET MULTI_USER
                """)
                
            except Exception:
                # Ensure database is brought back online on failure
                try:
                    # Consume any pending result sets first
                    try:
                        while master_cursor.nextset():
                            pass
                    except Exception:
                        pass
                    
                    # If DB is stuck in Restoring state, bring it online
                    master_cursor.execute(f"""
                        IF EXISTS (SELECT 1 FROM sys.databases WHERE name = '{db_name}' AND state_desc = 'RESTORING')
                            RESTORE DATABASE [{db_name}] WITH RECOVERY
                    """)
                    while master_cursor.nextset():
                        pass
                except Exception:
                    pass
                try:
                    master_cursor.execute(f"""
                        ALTER DATABASE [{db_name}] SET MULTI_USER
                    """)
                except Exception:
                    pass
                raise
            finally:
                master_cursor.close()
                master_conn.close()
                
        elif db_engine == 'sqlite':
            # SQLite restore - simple file copy
            db_path = Path(db_name)
            # Create backup of current database
            if db_path.exists():
                current_backup = db_path.with_suffix('.bak.current')
                shutil.copy2(db_path, current_backup)
            
            # Restore from backup
            shutil.copy2(backup_path, db_path)
            
        elif db_engine == 'postgresql':
            # PostgreSQL restore using pg_restore
            import subprocess
            pg_restore_cmd = [
                'pg_restore',
                '-h', db_config.get('HOST', 'localhost'),
                '-U', db_config.get('USER', 'postgres'),
                '-d', db_name,
                '--clean',
                str(backup_path)
            ]
            result = subprocess.run(pg_restore_cmd, capture_output=True, text=True)
            if result.returncode != 0:
                raise Exception(f"pg_restore failed: {result.stderr}")
                
        elif db_engine == 'mysql':
            # MySQL restore using mysql
            import subprocess
            mysql_cmd = [
                'mysql',
                '-h', db_config.get('HOST', 'localhost'),
                '-u', db_config.get('USER', 'root'),
                f'-p{db_config.get("PASSWORD", "")}',
                db_name
            ]
            with open(backup_path, 'r') as f:
                result = subprocess.run(mysql_cmd, stdin=f, capture_output=True, text=True)
            if result.returncode != 0:
                raise Exception(f"mysql restore failed: {result.stderr}")
        else:
            raise NotImplementedError(f"Restore not implemented for {db_engine}")
        
        logger.info(f"Restore completed: {filename}")
        messages.success(request, f'Database restored successfully from: {filename}')
        
        return JsonResponse({
            'success': True,
            'message': f'Database restored from: {filename}'
        })
        
    except PermissionError as e:
        logger.error(f"Restore permission error: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': f'Permission denied: {str(e)}'
        }, status=403)
        
    except Exception as e:
        logger.error(f"Restore failed: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@admin_required
def database_backup_download(request, filename):
    """Download a database backup file - Admin only"""
    try:
        backup_dir = get_backup_dir()
        backup_path = backup_dir / filename
        
        # Security check - ensure file is within backup directory
        if not str(backup_path.resolve()).startswith(str(backup_dir.resolve())):
            messages.error(request, 'Invalid backup file path!')
            return redirect('database_backup')
        
        if not backup_path.exists():
            messages.error(request, 'Backup file not found!')
            return redirect('database_backup')
        
        # Serve the file
        response = FileResponse(
            open(backup_path, 'rb'),
            as_attachment=True,
            filename=filename
        )
        return response
        
    except Exception as e:
        logger.error(f"Download failed: {str(e)}")
        messages.error(request, f'Download failed: {str(e)}')
        return redirect('database_backup')


@admin_required
def database_backup_delete(request, filename):
    """Delete a database backup file - Admin only"""
    if request.method != 'POST':
        return redirect('database_backup')
    
    try:
        backup_dir = get_backup_dir()
        backup_path = backup_dir / filename
        
        # Security check
        if not str(backup_path.resolve()).startswith(str(backup_dir.resolve())):
            messages.error(request, 'Invalid backup file path!')
            return redirect('database_backup')
        
        if backup_path.exists():
            backup_path.unlink()
            logger.info(f"Backup deleted: {filename}")
            messages.success(request, f'Backup deleted: {filename}')
        else:
            messages.warning(request, 'Backup file not found!')
        
    except Exception as e:
        logger.error(f"Delete failed: {str(e)}")
        messages.error(request, f'Delete failed: {str(e)}')
    
    return redirect('database_backup')
