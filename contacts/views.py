from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from .models import Contact


def contact(request):
    if request.method == 'POST':
        listing_id = request.POST['listing_id']
        listing = request.POST['listing']
        name = request.POST['name']
        email = request.POST['email']
        phone = request.POST.get('phone', '')
        message = request.POST.get('message', '')
        realtor_email = request.POST['realtor_email']

        # Prevent duplicate enquiries from authenticated users
        if request.user.is_authenticated:
            already_contacted = Contact.objects.filter(
                listing_id=listing_id,
                user=request.user
            ).exists()
            if already_contacted:
                messages.error(request, 'You have already made an inquiry for this listing.')
                return redirect(f'/listings/{listing_id}')

        contact = Contact(
            listing=listing,
            listing_id=listing_id,
            name=name,
            email=email,
            phone=phone,
            message=message,
            user=request.user if request.user.is_authenticated else None,
        )
        contact.save()

        # Send notification email to realtor
        try:
            send_mail(
                subject=f'Property Inquiry: {listing}',
                message=(
                    f'New inquiry received for "{listing}".\n\n'
                    f'From: {name}\n'
                    f'Email: {email}\n'
                    f'Phone: {phone}\n\n'
                    f'Message:\n{message}\n\n'
                    f'Log in to the admin panel to view full details.'
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[realtor_email],
                fail_silently=True,
            )
        except Exception:
            pass  # Never let a mail failure block the user

        messages.success(request, 'Your enquiry has been submitted. A realtor will be in touch soon.')
        return redirect(f'/listings/{listing_id}')

    return redirect('listings')
