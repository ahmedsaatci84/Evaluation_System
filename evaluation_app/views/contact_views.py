from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q

from ..models import ContactMessage
from ..decorators import user_or_admin_required, can_delete_required


def contact(request):
    if request.method == 'POST':
        ContactMessage(
            name=request.POST.get('name'),
            email=request.POST.get('email'),
            phone=request.POST.get('phone', ''),
            subject=request.POST.get('subject'),
            message=request.POST.get('message'),
        ).save()
        messages.success(request, f"Thank you {request.POST.get('name')}! Your message has been received.")
        return redirect('contact')
    return render(request, 'evaluation_app/contact/contact.html')


@user_or_admin_required
def contact_list(request):
    search_query = request.GET.get('search', '').strip()
    contacts = ContactMessage.objects.all()
    if search_query:
        for term in (t for t in search_query.split() if t):
            contacts = contacts.filter(
                Q(name__icontains=term) | Q(email__icontains=term)
                | Q(subject__icontains=term) | Q(message__icontains=term)
                | Q(phone__icontains=term)
            )
    contacts = list(contacts.order_by('-created_at'))
    return render(request, 'evaluation_app/contact/list.html', {
        'contacts': contacts,
        'search_query': search_query,
        'results_count': len(contacts),
    })


@user_or_admin_required
def contact_update(request, pk):
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
    return render(request, 'evaluation_app/contact/form.html', {'contact': contact_msg})


@can_delete_required
def contact_delete(request, pk):
    contact_msg = get_object_or_404(ContactMessage, pk=pk)
    if request.method == 'POST':
        contact_msg.delete()
        messages.success(request, 'Contact message deleted successfully!')
        return redirect('contact_list')
    return render(request, 'evaluation_app/contact/confirm_delete.html', {'contact': contact_msg})
