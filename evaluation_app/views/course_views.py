from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q

from ..models import CourseTbl, ProfessorTbl
from ..decorators import not_guest_required, can_delete_required


def course_list(request):
    search_query = request.GET.get('search', '').strip()
    courses = CourseTbl.objects.select_related('prof').all()
    if search_query:
        for term in (t for t in search_query.split() if t):
            courses = courses.filter(
                Q(coursename__icontains=term) | Q(courseid__icontains=term)
                | Q(prof__profname__icontains=term) | Q(cid__icontains=term)
            )
    courses = list(courses.order_by('coursename'))
    return render(request, 'evaluation_app/course/list.html', {
        'courses': courses,
        'search_query': search_query,
        'results_count': len(courses),
    })


@not_guest_required
def course_create(request):
    if request.method == 'POST':
        CourseTbl(
            courseid=request.POST.get('courseid'),
            coursename=request.POST.get('coursename'),
            prof_id=request.POST.get('prof') or None,
        ).save()
        messages.success(request, 'Course created successfully!')
        return redirect('course_list')
    return render(request, 'evaluation_app/course/form.html', {
        'professors': list(ProfessorTbl.objects.all()),
    })


@not_guest_required
def course_update(request, pk):
    course = get_object_or_404(CourseTbl, pk=pk)
    if request.method == 'POST':
        course.courseid = request.POST.get('courseid')
        course.coursename = request.POST.get('coursename')
        course.prof_id = request.POST.get('prof') or None
        course.save()
        messages.success(request, 'Course updated successfully!')
        return redirect('course_list')
    return render(request, 'evaluation_app/course/form.html', {
        'course': course,
        'professors': list(ProfessorTbl.objects.all()),
    })


@can_delete_required
def course_delete(request, pk):
    course = get_object_or_404(CourseTbl, pk=pk)
    if request.method == 'POST':
        course.delete()
        messages.success(request, 'Course deleted successfully!')
        return redirect('course_list')
    return render(request, 'evaluation_app/course/confirm_delete.html', {'course': course})
