from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q

from ..models import ProfessorTbl
from ..decorators import not_guest_required, can_delete_required


def professor_list(request):
    search_query = request.GET.get('search', '').strip()
    professors = ProfessorTbl.objects.all()
    if search_query:
        for term in (t for t in search_query.split() if t):
            professors = professors.filter(
                Q(profname__icontains=term) | Q(profid__icontains=term) | Q(prophone__icontains=term)
            )
    professors = list(professors.order_by('profname'))
    return render(request, 'evaluation_app/professor/list.html', {
        'professors': professors,
        'search_query': search_query,
        'results_count': len(professors),
    })


@not_guest_required
def professor_create(request):
    if request.method == 'POST':
        profid = request.POST.get('profid', '').strip()
        profname = request.POST.get('profname', '').strip()
        prophone = request.POST.get('prophone', '').strip()

        error_ctx = {'profid': profid, 'profname': profname, 'prophone': prophone}

        if not profid:
            messages.error(request, 'Professor ID is required!')
            return render(request, 'evaluation_app/professor/form.html', error_ctx)
        if not profname:
            messages.error(request, 'Professor name is required!')
            return render(request, 'evaluation_app/professor/form.html', error_ctx)
        try:
            profid = int(profid)
        except ValueError:
            messages.error(request, 'Professor ID must be a valid number!')
            return render(request, 'evaluation_app/professor/form.html', error_ctx)

        prophone_value = int(prophone) if prophone else None

        if ProfessorTbl.objects.filter(profid=profid).exists():
            messages.error(request, f'Professor with ID ({profid}) already exists.')
            return render(request, 'evaluation_app/professor/form.html', error_ctx)

        existing = ProfessorTbl.objects.filter(profname=profname, prophone=prophone_value).first()
        if existing:
            messages.error(
                request,
                f'Professor "{profname}" with the same phone already exists (ID: {existing.profid}).',
            )
            return render(request, 'evaluation_app/professor/form.html', error_ctx)

        ProfessorTbl(profid=profid, profname=profname, prophone=prophone_value).save()
        messages.success(request, f'Professor "{profname}" created successfully!')
        return redirect('professor_list')
    return render(request, 'evaluation_app/professor/form.html')


@not_guest_required
def professor_update(request, pk):
    professor = get_object_or_404(ProfessorTbl, pk=pk)
    if request.method == 'POST':
        profname = request.POST.get('profname', '').strip()
        prophone = request.POST.get('prophone', '').strip() or None

        if not profname:
            messages.error(request, 'Professor name is required!')
            return render(request, 'evaluation_app/professor/form.html', {'professor': professor})

        existing = ProfessorTbl.objects.filter(profname=profname, prophone=prophone).exclude(profid=pk).first()
        if existing:
            messages.error(
                request,
                f'Professor "{profname}" with the same phone already exists (ID: {existing.profid}).',
            )
            return render(request, 'evaluation_app/professor/form.html', {'professor': professor})

        professor.profname = profname
        professor.prophone = prophone
        professor.save()
        messages.success(request, f'Professor "{profname}" updated successfully!')
        return redirect('professor_list')
    return render(request, 'evaluation_app/professor/form.html', {'professor': professor})


@can_delete_required
def professor_delete(request, pk):
    professor = get_object_or_404(ProfessorTbl, pk=pk)
    if request.method == 'POST':
        professor.delete()
        messages.success(request, 'Professor deleted successfully!')
        return redirect('professor_list')
    return render(request, 'evaluation_app/professor/confirm_delete.html', {'professor': professor})


def professor_download_pdf(request, pk):
    from django.http import HttpResponse
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import inch
    from reportlab.pdfgen import canvas
    from reportlab.lib import colors
    from datetime import datetime
    from django.conf import settings as django_settings

    from ..services import get_arabic_fonts, process_arabic_text, PDF_COLORS

    professor = get_object_or_404(ProfessorTbl, pk=pk)
    response = HttpResponse(content_type='application/pdf')
    safe_name = professor.profname.replace(' ', '_') if professor.profname else 'Unknown'
    response['Content-Disposition'] = f'inline; filename="Professor_{professor.profid}_{safe_name}.pdf"'

    p = canvas.Canvas(response, pagesize=A4)
    width, height = A4
    normal_font, bold_font = get_arabic_fonts(str(django_settings.BASE_DIR))
    c = PDF_COLORS
    primary_color = c['primary']
    secondary_color = c['secondary']
    light_gray = c['light_gray']

    p.setFillColor(primary_color)
    p.rect(0, height - 2 * inch, width, 2 * inch, fill=True, stroke=False)
    p.setFillColor(colors.white)
    p.setFont(bold_font, 28)
    p.drawCentredString(width / 2, height - 1 * inch, process_arabic_text("معلومات الأستاذ"))
    p.setFont(normal_font, 12)
    current_date = datetime.now()
    p.drawCentredString(
        width / 2, height - 1.4 * inch,
        process_arabic_text(f"تم الإنشاء بتاريخ: {current_date.strftime('%Y/%m/%d')} الساعة {current_date.strftime('%I:%M %p')}"),
    )

    p.setFillColor(colors.black)
    y = height - 3 * inch

    p.setStrokeColor(secondary_color)
    p.setLineWidth(3)
    p.line(1 * inch, y, width - 1 * inch, y)
    y -= 0.5 * inch

    p.setFont(bold_font, 16)
    p.setFillColor(primary_color)
    p.drawString(1 * inch, y, process_arabic_text("التفاصيل الشخصية"))
    y -= 0.4 * inch

    def draw_field(label, value, y_pos):
        p.setFillColor(light_gray)
        p.rect(1 * inch, y_pos - 0.25 * inch, width - 2 * inch, 0.35 * inch, fill=True, stroke=False)
        p.setFillColor(primary_color)
        p.setFont(bold_font, 12)
        p.drawString(1.2 * inch, y_pos - 0.05 * inch, process_arabic_text(label))
        p.setFillColor(colors.black)
        p.setFont(normal_font, 12)
        p.drawString(3 * inch, y_pos - 0.05 * inch, process_arabic_text(str(value)))
        return y_pos - 0.5 * inch

    y = draw_field("معرف الأستاذ:", professor.profid, y)
    y = draw_field("الاسم الكامل:", professor.profname or "غير متوفر", y)
    y = draw_field("رقم الهاتف:", professor.prophone or "غير متوفر", y)

    p.setFont(normal_font, 9)
    p.setFillColor(colors.grey)
    p.drawCentredString(width / 2, 0.5 * inch, process_arabic_text(
        f"© {current_date.year} نظام التقييم. جميع الحقوق محفوظة."
    ))

    p.showPage()
    p.save()
    return response
