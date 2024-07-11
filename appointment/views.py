from django.shortcuts import render
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.contrib import messages
from django.conf import settings
from .models import Appointment, Waiver, Services, Service
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.utils import timezone
from datetime import datetime, time, timedelta
from django.urls import reverse
from django.shortcuts import render, get_object_or_404

def home(request):
    services = Services.objects.all()
    return render(request, 'appointment/index.html', {'services': services})


def about(request):
    services = Services.objects.all()
    return render(request, 'appointment/about.html', {'services': services})


def contact(request):
    services = Services.objects.all()
    if request.method == 'POST':
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        
        # Basic validation
        if not all([name, phone, email, subject, message]):
            messages.error(request, 'Please fill out all fields.')
            return redirect('contact')

        # Send email
        send_mail(
            subject=f"Contact Form Submission: {subject}",
            message=f"Name: {name}\nEmail: {email}\nPhone: {phone}\n\nMessage:\n{message}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=['missamaniaesthetics@outlook.com'],  # Replace with your actual email
            fail_silently=False,
        )
        
        messages.success(request, 'Your message has been sent successfully!')
        return redirect('contact')
    return render(request, 'appointment/contact.html')


def generate_timeslots(service, date):
    duration = service.duration
    start_time = time(9, 0)  # 9:00 AM
    end_time = time(19, 0)  # 7:00 PM
    
    timeslots = []
    current_time = start_time
    
    while current_time < end_time:
        slot_end = (datetime.combine(date, current_time) + timedelta(minutes=duration)).time()
        if slot_end <= end_time:
            timeslots.append((current_time, slot_end))
        current_time = slot_end
    
    return timeslots

def get_available_timeslots(request):
    service_id = request.GET.get('service_id')
    date_str = request.GET.get('date')
    
    service = Service.objects.get(id=service_id)
    date = datetime.strptime(date_str, '%Y-%m-%d').date()
    
    all_timeslots = generate_timeslots(service, date)
    booked_appointments = Appointment.objects.filter(date=date)
    
    available_timeslots = []
    for start, end in all_timeslots:
        is_available = True
        for appointment in booked_appointments:
            if (start < appointment.end_time and end > appointment.start_time):
                is_available = False
                break
        if is_available:
            available_timeslots.append({
                'start': start.strftime('%I:%M %p'),
                'end': end.strftime('%I:%M %p'),
                'value': f"{start.strftime('%H:%M')}-{end.strftime('%H:%M')}"
            })
    
    return JsonResponse({'timeslots': available_timeslots})

def book_appointment(request):
    services = Service.objects.all()

    if request.method == 'POST':
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        date_str = request.POST.get('date')
        service_id = request.POST.get('service')
        consultation_notes = request.POST.get('consultation_notes')
        timeslot = request.POST.get('timeslot')
        waiver_signature = request.POST.get('waiver_signature')

        service = Service.objects.get(id=service_id)
        date = datetime.strptime(date_str, '%Y-%m-%d').date()
        start_time, end_time = timeslot.split('-')
        start_time = datetime.strptime(start_time, '%H:%M').time()
        end_time = datetime.strptime(end_time, '%H:%M').time()

        # Check if the selected day is Saturday or Sunday
        if date.weekday() in [5, 6]:
            error_message = 'Sorry, we are closed on weekends. Please select a weekday.'
            return render(request, 'appointment/appointment.html', {
                'error': error_message,
                'services': services,
            })

        # Check if the timeslot is still available
        existing_appointment = Appointment.objects.filter(
            date=date,
            start_time__lt=end_time,
            end_time__gt=start_time
        ).exists()
        
        if existing_appointment:
            error_message = 'The selected timeslot is no longer available. Please choose another timeslot.'
            return render(request, 'appointment/appointment.html', {
                'error': error_message,
                'services': services,
            })


        

        appointment = Appointment.objects.create(
            name=name,
            phone=phone,
            email=email,
            date=date,
            start_time=start_time,
            end_time=end_time,
            service=service,
            consultation_notes=consultation_notes
        )

        send_confirmation_email(appointment)

        return render(request, 'appointment/appointment_success.html', {'appointment': appointment})

    return render(request, 'appointment/appointment.html', {
        'services': services,
    })

def send_confirmation_email(appointment):
    subject = 'Appointment Confirmation'
    message = f"""Dear {appointment.name},

Thank you for booking an appointment with us. Here are the details:

Name: {appointment.name}
Phone: {appointment.phone}
Email: {appointment.email}
Date: {appointment.date}
Service: {appointment.service.name}
Time: {appointment.start_time.strftime('%I:%M %p')} - {appointment.end_time.strftime('%I:%M %p')}
Consultation Notes: {appointment.consultation_notes}

We look forward to seeing you.

Best regards,
Miss Amani Aesthetics"""
    
    sender = settings.DEFAULT_FROM_EMAIL
    recipient_list = [appointment.email, 'missamaniaesthetics@outlook.com']
    send_mail(subject, message, sender, recipient_list)



def doctor_detail(request):
    services = Services.objects.all()
    return render(request, 'appointment/doctor_detail.html', {'services': services})




def service_detail(request, slug):
    service = get_object_or_404(Services, slug=slug)
    services = Services.objects.all()
    context = {
        'service': service,
        'services': services,
    }
    return render(request, 'appointment/service_detail.html', context)
