from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import JsonResponse

from ..models import EvaluationTab, ParticipantTbl, TrainTbl, TrainParticipantTbl
from ..decorators import guest_can_create_evaluation, not_guest_required, can_delete_required


def evaluation_list(request):
    evaluations = list(
        EvaluationTab.objects.select_related(
            'participant', 'train', 'train__course', 'train__professor', 'train__location'
        ).all()
    )
    return render(request, 'evaluation_app/evaluation/list.html', {
        'evaluations': evaluations,
        'total_count': len(evaluations),
    })


@guest_can_create_evaluation
def evaluation_create(request):
    if request.method == 'POST':
        participant_id = request.POST.get('participant') or None
        train_id = request.POST.get('train') or None

        if participant_id and train_id:
            if EvaluationTab.objects.filter(participant_id=participant_id, train_id=train_id).exists():
                messages.error(
                    request,
                    'An evaluation from this participant for this training session already exists. '
                    'Each participant can only submit one evaluation per training session.',
                )
                training_sessions = list(
                    TrainTbl.objects.select_related('course', 'professor', 'location').filter(is_active=True)
                )
                return render(request, 'evaluation_app/evaluation/form.html', {
                    'training_sessions': training_sessions,
                })

        evaluation = EvaluationTab(
            **{f'ev_q_{i}': request.POST.get(f'ev_q_{i}') or None for i in range(1, 16)},
            ev_q_notes=request.POST.get('ev_q_notes'),
            participant_id=participant_id,
            train_id=train_id,
        )
        evaluation.save()
        messages.success(request, 'Evaluation created successfully!')
        return redirect('evaluation_list')

    training_sessions = list(
        TrainTbl.objects.select_related('course', 'professor', 'location').filter(is_active=True)
    )
    return render(request, 'evaluation_app/evaluation/form.html', {
        'training_sessions': training_sessions,
    })


@not_guest_required
def evaluation_update(request, pk):
    evaluation = get_object_or_404(EvaluationTab, pk=pk)
    if request.method == 'POST':
        for i in range(1, 16):
            setattr(evaluation, f'ev_q_{i}', request.POST.get(f'ev_q_{i}') or None)
        evaluation.ev_q_notes = request.POST.get('ev_q_notes')
        new_participant_id = request.POST.get('participant') or None
        new_train_id = request.POST.get('train') or None

        if new_participant_id and new_train_id:
            if EvaluationTab.objects.filter(
                participant_id=new_participant_id, train_id=new_train_id
            ).exclude(id=evaluation.id).exists():
                messages.error(
                    request,
                    'An evaluation from this participant for this training session already exists.',
                )
                return render(request, 'evaluation_app/evaluation/form.html', {
                    'evaluation': evaluation,
                    'participants': list(ParticipantTbl.objects.all()),
                    'training_sessions': list(
                        TrainTbl.objects.select_related('course', 'professor', 'location').filter(is_active=True)
                    ),
                })

        evaluation.participant_id = new_participant_id
        evaluation.train_id = new_train_id
        evaluation.save()
        messages.success(request, 'Evaluation updated successfully!')
        return redirect('evaluation_list')

    return render(request, 'evaluation_app/evaluation/form.html', {
        'evaluation': evaluation,
        'participants': list(ParticipantTbl.objects.all()),
        'training_sessions': list(
            TrainTbl.objects.select_related('course', 'professor', 'location').filter(is_active=True)
        ),
    })


@can_delete_required
def evaluation_delete(request, pk):
    evaluation = get_object_or_404(EvaluationTab, pk=pk)
    if request.method == 'POST':
        evaluation.delete()
        messages.success(request, 'Evaluation deleted successfully!')
        return redirect('evaluation_list')
    return render(request, 'evaluation_app/evaluation/confirm_delete.html', {'evaluation': evaluation})


@login_required
def evaluation_download_pdf(request, pk):
    from django.http import HttpResponse
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import inch
    from reportlab.pdfgen import canvas
    from reportlab.lib import colors
    from datetime import datetime

    from ..services import (
        get_arabic_fonts, process_arabic_text, get_evaluation_question_values,
        EVALUATION_QUESTIONS, PDF_COLORS,
    )
    from django.conf import settings as django_settings

    evaluation = get_object_or_404(EvaluationTab, pk=pk)

    response = HttpResponse(content_type='application/pdf')
    participant_name = evaluation.participant.participant_name if evaluation.participant else "Unknown"
    train_id = evaluation.train.trainid if evaluation.train else "N/A"
    response['Content-Disposition'] = (
        f'inline; filename="Evaluation_{evaluation.id}_{participant_name.replace(" ", "_")}_Train{train_id}.pdf"'
    )

    p = canvas.Canvas(response, pagesize=A4)
    width, height = A4
    normal_font, bold_font = get_arabic_fonts(str(django_settings.BASE_DIR))
    c = PDF_COLORS
    primary_color = c['primary']
    secondary_color = c['secondary']
    accent_color = c['accent']
    light_gray = c['light_gray']

    # Header
    p.setFillColor(primary_color)
    p.rect(0, height - 2.2 * inch, width, 2.2 * inch, fill=True, stroke=False)
    p.setFillColor(colors.white)
    p.setFont(bold_font, 24)
    p.drawCentredString(width / 2, height - 1 * inch, process_arabic_text("تقرير تقييم البرنامج التدريبي"))
    p.setFont(normal_font, 11)
    p.drawCentredString(
        width / 2, height - 1.5 * inch,
        process_arabic_text(f"تاريخ الطباعة: {datetime.now().strftime('%Y/%m/%d')}"),
    )

    p.setFillColor(colors.black)
    y = height - 2.7 * inch

    # Info section helper
    def draw_info_field(label, value, y_pos):
        p.setFillColor(light_gray)
        p.rect(1 * inch, y_pos - 0.2 * inch, width - 2 * inch, 0.3 * inch, fill=True, stroke=False)
        p.setFillColor(primary_color)
        p.setFont(bold_font, 10)
        p.drawRightString(width - 1.2 * inch, y_pos, process_arabic_text(label))
        p.setFillColor(colors.black)
        p.setFont(normal_font, 10)
        p.drawString(1.2 * inch, y_pos, process_arabic_text(str(value)))
        return y_pos - 0.4 * inch

    p.setFont(bold_font, 14)
    p.setFillColor(primary_color)
    p.drawString(1 * inch, y, process_arabic_text("معلومات التقييم"))
    y -= 0.35 * inch
    y = draw_info_field("اسم المتدرب:", participant_name, y)
    y = draw_info_field(
        "اسم البرنامج التدريبي:",
        evaluation.train.course.coursename if evaluation.train and evaluation.train.course else "غير متوفر",
        y,
    )
    y = draw_info_field(
        "اسم المدرب:",
        evaluation.train.professor.profname if evaluation.train and evaluation.train.professor else "غير متوفر",
        y,
    )
    y = draw_info_field(
        "المكان:",
        evaluation.train.location.locationname if evaluation.train and evaluation.train.location else "غير متوفر",
        y,
    )
    y = draw_info_field(
        "تاريخ التدريب:",
        evaluation.train.train_date.strftime('%Y/%m/%d') if evaluation.train and evaluation.train.train_date else "غير متوفر",
        y,
    )
    y -= 0.3 * inch

    # Questions
    p.setFont(bold_font, 14)
    p.setFillColor(primary_color)
    p.drawString(1 * inch, y, process_arabic_text("التقييمات (من 1 إلى 10)"))
    y -= 0.35 * inch

    question_values = get_evaluation_question_values(evaluation)
    q_counter = group_sum = total_sum = total_count = 0

    for i, (question, value) in enumerate(zip(EVALUATION_QUESTIONS, question_values), 1):
        if y < 2 * inch:
            p.showPage()
            p.setFont(normal_font, 10)
            y = height - 1 * inch

        p.setFillColor(colors.black)
        p.setFont(bold_font, 9)
        q_text = process_arabic_text(f"{i}. {question}")
        if len(q_text) > 80:
            words = q_text.split()
            mid = len(words) // 2
            p.drawRightString(width - 1.2 * inch, y, ' '.join(words[:mid]))
            y -= 0.15 * inch
            p.drawRightString(width - 1.2 * inch, y, ' '.join(words[mid:]))
        else:
            p.drawRightString(width - 1.2 * inch, y, q_text)

        p.setFont(bold_font, 11)
        if value is not None:
            p.setFillColor(colors.green if value >= 8 else (colors.orange if value >= 5 else colors.red))
            p.drawString(1.2 * inch, y, str(value))
            group_sum += value
            total_sum += value
            total_count += 1
        else:
            p.setFillColor(colors.gray)
            p.drawString(1.2 * inch, y, "N/A")

        y -= 0.3 * inch
        q_counter += 1

        if q_counter == 5 and group_sum > 0:
            p.setFillColor(accent_color)
            p.rect(1 * inch, y - 0.15 * inch, width - 2 * inch, 0.28 * inch, fill=True, stroke=False)
            p.setFillColor(colors.white)
            p.setFont(bold_font, 10)
            p.drawCentredString(
                width / 2, y,
                process_arabic_text(f"مجموع الأسئلة {i-4} - {i}: {group_sum} (متوسط: {group_sum/5:.2f})"),
            )
            y -= 0.5 * inch
            q_counter = group_sum = 0

    if q_counter > 0 and group_sum > 0:
        p.setFillColor(accent_color)
        p.rect(1 * inch, y - 0.15 * inch, width - 2 * inch, 0.28 * inch, fill=True, stroke=False)
        p.setFillColor(colors.white)
        p.setFont(bold_font, 10)
        start_q = 15 - q_counter + 1
        p.drawCentredString(
            width / 2, y,
            process_arabic_text(f"مجموع الأسئلة {start_q} - 15: {group_sum} (متوسط: {group_sum/q_counter:.2f})"),
        )
        y -= 0.5 * inch

    if total_count > 0:
        if y < 1.5 * inch:
            p.showPage()
            y = height - 1 * inch
        p.setFillColor(primary_color)
        p.rect(1 * inch, y - 0.2 * inch, width - 2 * inch, 0.35 * inch, fill=True, stroke=False)
        p.setFillColor(colors.white)
        p.setFont(bold_font, 12)
        p.drawCentredString(
            width / 2, y,
            process_arabic_text(
                f"المجموع الكلي: {total_sum} / {total_count * 10} | المتوسط العام: {total_sum/total_count:.2f} / 10"
            ),
        )
        y -= 0.6 * inch

    if evaluation.ev_q_notes and evaluation.ev_q_notes.strip():
        if y < 2 * inch:
            p.showPage()
            y = height - 1 * inch
        p.setFillColor(primary_color)
        p.setFont(bold_font, 11)
        p.drawRightString(width - 1.2 * inch, y, process_arabic_text("ملاحظات:"))
        y -= 0.3 * inch
        p.setFillColor(colors.black)
        p.setFont(normal_font, 9)
        notes_text = process_arabic_text(evaluation.ev_q_notes)
        max_w = width - 2.4 * inch
        lines, current = [], ""
        for word in notes_text.split():
            test = (current + " " + word).strip()
            if p.stringWidth(test, normal_font, 9) < max_w:
                current = test
            else:
                lines.append(current)
                current = word
        if current:
            lines.append(current)
        for line in lines:
            p.drawRightString(width - 1.2 * inch, y, line)
            y -= 0.2 * inch

    p.setFont(normal_font, 8)
    p.setFillColor(colors.gray)
    p.drawCentredString(
        width / 2, 0.5 * inch,
        process_arabic_text(f"تم إنشاء هذا التقرير تلقائياً بواسطة نظام التقييم - ID: {evaluation.id}"),
    )
    p.showPage()
    p.save()
    return response


def get_training_participants(request, train_id):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)
    try:
        evaluation_id = request.GET.get('evaluation_id', None)
        train_participants = TrainParticipantTbl.objects.filter(
            train_id=train_id,
            participant__isnull=False,
        ).filter(
            Q(is_active=True) | Q(is_active__isnull=True)
        ).select_related('participant')

        existing_qs = EvaluationTab.objects.filter(train_id=train_id)
        if evaluation_id:
            existing_qs = existing_qs.exclude(id=evaluation_id)
        already_submitted = set(existing_qs.values_list('participant_id', flat=True))

        participants_data = [
            {'id': tp.participant.participant_id, 'name': tp.participant.participant_name}
            for tp in train_participants
            if tp.participant.participant_id not in already_submitted
        ]
        return JsonResponse({'participants': participants_data})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
def get_available_participants(request, train_id):
    try:
        train_participant_id = request.GET.get('train_participant_id', None)
        existing = TrainParticipantTbl.objects.filter(train_id=train_id)
        if train_participant_id:
            existing = existing.exclude(train_participant_id=train_participant_id)
        available = ParticipantTbl.objects.exclude(
            participant_id__in=existing.values_list('participant_id', flat=True)
        )
        return JsonResponse({
            'participants': [
                {'id': p.participant_id, 'name': p.participant_name}
                for p in available
            ]
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
