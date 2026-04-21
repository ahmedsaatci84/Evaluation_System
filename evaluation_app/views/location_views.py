from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q

from ..models import LocationTbl
from ..decorators import not_guest_required, can_delete_required


def location_list(request):
    search_query = request.GET.get('search', '').strip()
    locations = LocationTbl.objects.all()
    if search_query:
        for term in (t for t in search_query.split() if t):
            locations = locations.filter(
                Q(locationname__icontains=term) | Q(id__icontains=term)
            )
    locations = list(locations.order_by('locationname'))
    return render(request, 'evaluation_app/location/list.html', {
        'locations': locations,
        'search_query': search_query,
        'results_count': len(locations),
    })


@not_guest_required
def location_create(request):
    if request.method == 'POST':
        LocationTbl(locationname=request.POST.get('locationname')).save()
        messages.success(request, 'Location created successfully!')
        return redirect('location_list')
    return render(request, 'evaluation_app/location/form.html')


@not_guest_required
def location_update(request, pk):
    location = get_object_or_404(LocationTbl, pk=pk)
    if request.method == 'POST':
        location.locationname = request.POST.get('locationname')
        location.save()
        messages.success(request, 'Location updated successfully!')
        return redirect('location_list')
    return render(request, 'evaluation_app/location/form.html', {'location': location})


@can_delete_required
def location_delete(request, pk):
    location = get_object_or_404(LocationTbl, pk=pk)
    if request.method == 'POST':
        location.delete()
        messages.success(request, 'Location deleted successfully!')
        return redirect('location_list')
    return render(request, 'evaluation_app/location/confirm_delete.html', {'location': location})
