from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.utils import timezone

from ..models import (
    TrainTbl, TrainParticipantTbl, CourseTbl, ProfessorTbl,
    LocationTbl, ParticipantTbl, EvaluationTab,
)
from ..decorators import user_or_admin_required, can_delete_required
from ..services import (
    get_arabic_fonts, process_arabic_text, get_evaluation_question_values,
    EVALUATION_QUESTIONS, PDF_COLORS,
)


@user_or_admin_required
def train_list(request):
    search_query = request.GET.get('search', '').strip()
    qs = TrainTbl.objects.select_related('course', 'professor', 'location').all()
    if search_query:
        for term in (t for t in search_query.split() if t):
            qs = qs.filter(
                Q(course__coursename__icontains=term) | Q(professor__profname__icontains=term)
                | Q(location__locationname__icontains=term) | Q(trainid__icontains=term)
            )
    sessions = list(qs.order_by('-train_date', '-trainid'))
    return render(request, 'evaluation_app/training/list.html', {
        'training_sessions': sessions,
        'search_query': search_query,
        'total_count': len(sessions),
    })


@user_or_admin_required
def train_create(request):
    if request.method == 'POST':
        TrainTbl(
            course_id=request.POST.get('course') or None,
            professor_id=request.POST.get('professor') or None,
            location_id=request.POST.get('location') or None,
            train_date=request.POST.get('train_date') or None,
            is_active=request.POST.get('is_active') == 'on',
        ).save()
        messages.success(request, 'Training session created successfully!')
        return redirect('train_list')
    return render(request, 'evaluation_app/training/form.html', {
        'courses': list(CourseTbl.objects.all()),
        'professors': list(ProfessorTbl.objects.all()),
        'locations': list(LocationTbl.objects.all()),
        'train': list(TrainTbl.objects.select_related('course', 'professor', 'location').all()),
    })


@user_or_admin_required
def train_update(request, pk):
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
    return render(request, 'evaluation_app/training/form.html', {
        'train': train,
        'courses': list(CourseTbl.objects.all()),
        'professors': list(ProfessorTbl.objects.all()),
        'locations': list(LocationTbl.objects.all()),
    })


@can_delete_required
def train_delete(request, pk):
    train = get_object_or_404(TrainTbl, pk=pk)
    if request.method == 'POST':
        train.delete()
        messages.success(request, 'Training session deleted successfully!')
        return redirect('train_list')
    return render(request, 'evaluation_app/training/confirm_delete.html', {'train': train})


@login_required
def train_download_evaluations_pdf(request, pk):
    from django.http import HttpResponse
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import inch
    from reportlab.pdfgen import canvas
    from reportlab.lib import colors
    from datetime import datetime
    from django.conf import settings as django_settings

    train = get_object_or_404(TrainTbl, pk=pk)
    evaluations = EvaluationTab.objects.filter(train=train).select_related('participant')

    if not evaluations.exists():
        messages.warning(request, 'No evaluations found for this training session.')
        return redirect('train_list')

    response = HttpResponse(content_type='application/pdf')
    train_name = (train.course.coursename or "Unknown") if train.course else "Unknown"
    response['Content-Disposition'] = (
        f'inline; filename="Training_{train.trainid}_{train_name.replace(" ", "_")}_Evaluations.pdf"'
    )

    p = canvas.Canvas(response, pagesize=A4)
    width, height = A4
    normal_font, bold_font = get_arabic_fonts(str(django_settings.BASE_DIR))
    c = PDF_COLORS
    primary_color = c['primary']
    secondary_color = c['secondary']
    accent_color = c['accent']
    separator_color = c['separator']

    # Cover header
    p.setFillColor(primary_color)
    p.rect(0, height - 2.5 * inch, width, 2.5 * inch, fill=True, stroke=False)
    p.setFillColor(colors.white)
    p.setFont(bold_font, 22)
    p.drawCentredString(width / 2, height - 0.9 * inch, process_arabic_text("تقرير تقييمات البرنامج التدريبي"))
    p.setFont(bold_font, 14)
    p.drawCentredString(width / 2, height - 1.3 * inch, process_arabic_text(f"البرنامج: {train_name}"))
    p.setFont(normal_font, 11)
    professor_name = train.professor.profname if train.professor else "غير متوفر"
    location_name = train.location.locationname if train.location else "غير متوفر"
    train_date = train.train_date.strftime('%Y/%m/%d') if train.train_date else "غير متوفر"
    p.drawCentredString(
        width / 2, height - 1.65 * inch,
        process_arabic_text(f"المدرب: {professor_name} | المكان: {location_name} | التاريخ: {train_date}"),
    )
    p.setFont(bold_font, 11)
    p.drawCentredString(width / 2, height - 2 * inch, process_arabic_text(f"عدد التقييمات: {evaluations.count()}"))
    p.setFont(normal_font, 9)
    p.drawCentredString(
        width / 2, height - 2.3 * inch,
        process_arabic_text(f"تاريخ الطباعة: {datetime.now().strftime('%Y/%m/%d')}"),
    )

    p.setFillColor(colors.black)
    y = height - 2.9 * inch
    eval_count = evaluations.count()

    for idx, evaluation in enumerate(evaluations, 1):
        if y < 8 * inch:
            p.showPage()
            p.setFont(normal_font, 10)
            y = height - 1 * inch

        p.setFillColor(secondary_color)
        p.rect(0.8 * inch, y - 0.25 * inch, width - 1.6 * inch, 0.4 * inch, fill=True, stroke=False)
        p.setFillColor(colors.white)
        p.setFont(bold_font, 12)
        pname = evaluation.participant.participant_name if evaluation.participant else "غير متوفر"
        p.drawCentredString(width / 2, y - 0.05 * inch, process_arabic_text(f"تقييم رقم {idx} - المتدرب: {pname}"))
        y -= 0.6 * inch

        q_values = get_evaluation_question_values(evaluation)
        q_counter = group_sum = total_sum = total_count = 0

        for i, (question, value) in enumerate(zip(EVALUATION_QUESTIONS, q_values), 1):
            if y < 1.5 * inch:
                p.showPage()
                p.setFont(normal_font, 10)
                y = height - 1 * inch

            p.setFillColor(colors.black)
            p.setFont(bold_font, 8)
            q_text = process_arabic_text(f"{i}. {question}")
            if len(q_text) > 90:
                words = q_text.split()
                mid = len(words) // 2
                p.drawRightString(width - 1 * inch, y, ' '.join(words[:mid]))
                y -= 0.12 * inch
                p.drawRightString(width - 1 * inch, y, ' '.join(words[mid:]))
            else:
                p.drawRightString(width - 1 * inch, y, q_text)

            p.setFont(bold_font, 10)
            if value is not None:
                p.setFillColor(colors.green if value >= 8 else (colors.orange if value >= 5 else colors.red))
                p.drawString(1 * inch, y, str(value))
                group_sum += value
                total_sum += value
                total_count += 1
            else:
                p.setFillColor(colors.gray)
                p.drawString(1 * inch, y, "N/A")

            y -= 0.25 * inch
            q_counter += 1

            if q_counter == 5 and group_sum > 0:
                if y < 1 * inch:
                    p.showPage()
                    y = height - 1 * inch
                p.setFillColor(accent_color)
                p.rect(0.9 * inch, y - 0.12 * inch, width - 1.8 * inch, 0.25 * inch, fill=True, stroke=False)
                p.setFillColor(colors.white)
                p.setFont(bold_font, 9)
                p.drawCentredString(
                    width / 2, y,
                    process_arabic_text(f"مجموع الأسئلة {i-4} - {i}: {group_sum} (متوسط: {group_sum/5:.2f})"),
                )
                y -= 0.4 * inch
                q_counter = group_sum = 0

        if q_counter > 0 and group_sum > 0:
            if y < 1 * inch:
                p.showPage()
                y = height - 1 * inch
            p.setFillColor(accent_color)
            p.rect(0.9 * inch, y - 0.12 * inch, width - 1.8 * inch, 0.25 * inch, fill=True, stroke=False)
            p.setFillColor(colors.white)
            p.setFont(bold_font, 9)
            start_q = 15 - q_counter + 1
            p.drawCentredString(
                width / 2, y,
                process_arabic_text(f"مجموع الأسئلة {start_q} - 15: {group_sum} (متوسط: {group_sum/q_counter:.2f})"),
            )
            y -= 0.4 * inch

        if total_count > 0:
            if y < 1 * inch:
                p.showPage()
                y = height - 1 * inch
            p.setFillColor(primary_color)
            p.rect(0.9 * inch, y - 0.15 * inch, width - 1.8 * inch, 0.3 * inch, fill=True, stroke=False)
            p.setFillColor(colors.white)
            p.setFont(bold_font, 10)
            p.drawCentredString(
                width / 2, y,
                process_arabic_text(f"المجموع الكلي: {total_sum}/{total_count * 10} | المتوسط: {total_sum/total_count:.2f}/10"),
            )
            y -= 0.5 * inch

        if evaluation.ev_q_notes and evaluation.ev_q_notes.strip():
            if y < 1.5 * inch:
                p.showPage()
                y = height - 1 * inch
            p.setFillColor(primary_color)
            p.setFont(bold_font, 9)
            p.drawRightString(width - 1 * inch, y, process_arabic_text("ملاحظات:"))
            y -= 0.25 * inch
            p.setFillColor(colors.black)
            p.setFont(normal_font, 8)
            notes_text = process_arabic_text(evaluation.ev_q_notes)
            max_w = width - 2 * inch
            lines, current = [], ""
            for word in notes_text.split():
                test = (current + " " + word).strip()
                if p.stringWidth(test, normal_font, 8) < max_w:
                    current = test
                else:
                    lines.append(current)
                    current = word
            if current:
                lines.append(current)
            for line in lines[:3]:
                p.drawRightString(width - 1 * inch, y, line)
                y -= 0.18 * inch
            y -= 0.2 * inch

        if idx < eval_count:
            if y < 1 * inch:
                p.showPage()
                y = height - 1 * inch
            p.setStrokeColor(separator_color)
            p.setLineWidth(1)
            p.setDash(6, 3)
            p.line(1 * inch, y, width - 1 * inch, y)
            p.setDash()
            y -= 0.4 * inch

    p.setFont(normal_font, 8)
    p.setFillColor(colors.gray)
    p.drawCentredString(
        width / 2, 0.5 * inch,
        process_arabic_text(f"تم إنشاء هذا التقرير تلقائياً - تدريب رقم: {train.trainid}"),
    )
    p.showPage()
    p.save()
    return response


# ---- Training Participant views ----

@user_or_admin_required
def train_participant_list(request):
    search_query = request.GET.get('search', '').strip()
    qs = TrainParticipantTbl.objects.select_related('train__course', 'train__professor', 'participant').all()
    if search_query:
        for term in (t for t in search_query.split() if t):
            qs = qs.filter(
                Q(participant__participant_name__icontains=term)
                | Q(train__course__coursename__icontains=term)
                | Q(train__trainid__icontains=term)
            )
    tp_list = list(qs.order_by('-evaluation_date', '-train_participant_id'))
    return render(request, 'evaluation_app/training/participant_list.html', {
        'train_participants': tp_list,
        'search_query': search_query,
        'total_count': len(tp_list),
    })


@user_or_admin_required
def train_participant_create(request):
    preselected_train_id = request.GET.get('train_id', None)
    if request.method == 'POST':
        TrainParticipantTbl(
            train_id=request.POST.get('train') or None,
            participant_id=request.POST.get('participant') or None,
            evaluation_date=request.POST.get('evaluation_date') or None,
            is_active=request.POST.get('is_active') == 'on',
        ).save()
        messages.success(request, 'Training participant created successfully!')
        return redirect('train_participant_list')
    return render(request, 'evaluation_app/training/participant_form.html', {
        'training_sessions': list(
            TrainTbl.objects.select_related('course', 'professor', 'location').filter(is_active=True)
        ),
        'participants': list(ParticipantTbl.objects.all()),
        'preselected_train_id': preselected_train_id,
    })


@user_or_admin_required
def train_participant_update(request, pk):
    tp = get_object_or_404(TrainParticipantTbl, pk=pk)
    if request.method == 'POST':
        tp.train_id = request.POST.get('train') or None
        tp.participant_id = request.POST.get('participant') or None
        tp.evaluation_date = request.POST.get('evaluation_date') or None
        tp.is_active = request.POST.get('is_active') == 'on'
        tp.save()
        messages.success(request, 'Training participant updated successfully!')
        return redirect('train_participant_list')
    return render(request, 'evaluation_app/training/participant_form.html', {
        'train_participant': tp,
        'training_sessions': list(
            TrainTbl.objects.select_related('course', 'professor', 'location').filter(is_active=True)
        ),
        'participants': list(ParticipantTbl.objects.all()),
    })


@can_delete_required
def train_participant_delete(request, pk):
    tp = get_object_or_404(TrainParticipantTbl, pk=pk)
    if request.method == 'POST':
        tp.delete()
        messages.success(request, 'Training participant deleted successfully!')
        return redirect('train_participant_list')
    return render(request, 'evaluation_app/training/participant_confirm_delete.html', {'train_participant': tp})
