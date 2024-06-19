from django.shortcuts import render
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.contrib import messages
from django.conf import settings
from .models import Appointment, Timeslot, Waiver
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.utils import timezone
from datetime import datetime
from django.urls import reverse


def home(request):
    return render(request, 'appointment/index.html')


def about(request):
    return render(request, 'appointment/about.html')


def contact(request):
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


def book_appointment(request):

    waiver_content = """

        Surgery Waiver and Consent Form

Please read this waiver and consent form carefully. By signing this document, you acknowledge that you have read, understood, and agreed to the terms outlined below. If you have any questions or concerns, please consult with our staff before signing.

1. Purpose of the Procedure
I, the undersigned, hereby consent to the performance of surgical procedures by Nurse Lizan and his/her designated medical team. I understand that the purpose of the procedure is to improve physical appearance and/or functionality as discussed in my consultation.

2. Risks and Complications
I acknowledge that all surgical procedures carry inherent risks and potential complications, including but not limited to:
- Infection
- Scarring
- Nerve damage
- Bleeding and hematoma formation
- Anesthesia complications
- Unsatisfactory results requiring additional procedures

I understand that despite all precautions, these and other unforeseen complications may occur, and no guarantee has been made as to the results or the absence of complications.

3. Pre-Operative and Post-Operative Care
I agree to follow all pre-operative and post-operative instructions provided by Nurse Lizan and the medical staff. Failure to adhere to these instructions may increase the risk of complications.

4. Alternative Treatments
I acknowledge that alternative treatments and procedures have been discussed with me, including but not limited to non-surgical options. I have had the opportunity to ask questions about these alternatives and have had those questions answered to my satisfaction.

5. Photography and Medical Records
I consent to the taking of photographs and videos before, during, and after the procedure. These images may be used for medical records, educational purposes, or marketing, with the understanding that my identity will be protected unless I provide explicit consent for disclosure.

6. Financial Responsibility
I understand that I am financially responsible for the costs associated with the surgical procedure, including any potential costs related to complications or additional treatments.

7. Informed Consent
I have had the opportunity to discuss my medical history, including any allergies, medications, and past surgeries, with Nurse Lizan. I have provided accurate and complete information and have not withheld any relevant details.

8. Acknowledgment of Understanding
I acknowledge that I have read and fully understand the contents of this waiver and consent form. I have had the opportunity to ask questions and have received satisfactory answers. By signing below, I voluntarily agree to undergo the surgical procedure and accept the associated risks.

    """

    if request.method == 'POST':
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        date_str = request.POST.get('date')
        timeslot_id = request.POST.get('timeslot')
        timeslot = Timeslot.objects.get(id=timeslot_id)
        waiver_signature = request.POST.get('waiver_signature')

        date = datetime.strptime(date_str, '%Y-%m-%d').date()

        # Check if the selected day is Saturday or Sunday
        if date.weekday() in [5, 6]:  # Saturday is 5, Sunday is 6
            appointment_url = reverse('appointment')
            error_message = f'Sorry, we are closed on weekends. Please <a href="{appointment_url}" style="font-weight: bold; color: blue; text-decoration: underline;">refresh the page</a> and select a weekday.'
            return render(request, 'appointment/appointment.html', {'error': error_message, 'waiver_content': waiver_content})


        # Check if the timeslot is available for the selected date
        existing_appointment = Appointment.objects.filter(date=date, timeslot=timeslot).exists()
        if existing_appointment:
            # Timeslot is already booked, display an error message
            appointment_url = reverse('appointment')
            error_message = f'The selected timeslot is already booked. Please <a href="{appointment_url}" style="font-weight: bold; color: blue; text-decoration: underline;">refresh the page</a> and book another timeslot.'
            return render(request, 'appointment/appointment.html', {'error': error_message, 'waiver_content': waiver_content})


        waiver = Waiver.objects.create(content=waiver_content, signed_by=waiver_signature)

        # Create a new appointment
        appointment = Appointment.objects.create(
            name=name,
            phone=phone,
            email=email,
            date=date,
            timeslot=timeslot,
            waiver=waiver
        )

        # Send confirmation email to the user and the staff
        send_confirmation_email(appointment)

        return render(request, 'appointment/appointment_success.html', {'appointment': appointment})

    # Get the list of available timeslots
    timeslots = Timeslot.objects.all()
    return render(request, 'appointment/appointment.html', {'timeslots': timeslots, 'waiver_content': waiver_content})

def send_confirmation_email(appointment):
    subject = 'Appointment Confirmation'
    message = f"Dear {appointment.name},\n\nThank you for booking an appointment with us. Here are the details:\n\nName: {appointment.name}\nPhone: {appointment.phone}\nEmail: {appointment.email}\nDate: {appointment.date}\nTimeslot: {appointment.timeslot.slot_text}\n\nWe look forward to seeing you.\n\nBest regards,\nMiss Amani Aesthetics"
    sender = settings.DEFAULT_FROM_EMAIL
    recipient_list = [appointment.email, 'missamaniaesthetics@outlook.com']
    send_mail(subject, message, sender, recipient_list)


def doctor_detail(request):
    return render(request, 'appointment/doctor_detail.html')
