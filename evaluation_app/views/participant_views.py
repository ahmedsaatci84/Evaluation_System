from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q

from ..models import ParticipantTbl
from ..decorators import not_guest_required, can_delete_required


def participant_list(request):
    search_query = request.GET.get('search', '').strip()
    participants = ParticipantTbl.objects.all()
    if search_query:
        for term in (t for t in search_query.split() if t):
            participants = participants.filter(
                Q(participant_name__icontains=term) | Q(participant_id__icontains=term)
                | Q(participant_phone__icontains=term) | Q(participant_email__icontains=term)
            )
    participants = list(participants.order_by('participant_name'))
    return render(request, 'evaluation_app/participant/list.html', {
        'participants': participants,
        'search_query': search_query,
        'results_count': len(participants),
    })


@not_guest_required
def participant_create(request):
    if request.method == 'POST':
        ParticipantTbl(
            participant_id=request.POST.get('participant_id'),
            participant_name=request.POST.get('participant_name'),
            participant_phone=request.POST.get('participant_phone') or None,
            participant_email=request.POST.get('participant_email'),
        ).save()
        messages.success(request, 'Participant created successfully!')
        return redirect('participant_list')
    return render(request, 'evaluation_app/participant/form.html')


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
    return render(request, 'evaluation_app/participant/form.html', {'participant': participant})


@can_delete_required
def participant_delete(request, pk):
    participant = get_object_or_404(ParticipantTbl, pk=pk)
    if request.method == 'POST':
        participant.delete()
        messages.success(request, 'Participant deleted successfully!')
        return redirect('participant_list')
    return render(request, 'evaluation_app/participant/confirm_delete.html', {'participant': participant})
