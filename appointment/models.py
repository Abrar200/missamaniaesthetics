from django.db import models
from django.utils.text import slugify
from django.utils import timezone
import datetime
from django.contrib.auth.models import User
import json



class Service(models.Model):
    name = models.CharField(max_length=100, null=True)
    duration = models.IntegerField(help_text="Duration in minutes", null=True)

    def __str__(self):
        return self.name


class Waiver(models.Model):
    content = models.TextField()
    signed_by = models.CharField(max_length=100)
    signed_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Waiver signed by {self.signed_by} on {self.signed_on}"
    
    def get_formatted_content(self):
        try:
            content_dict = json.loads(self.content.replace("'", '"'))
            formatted_content = ""
            for key, value in content_dict.items():
                formatted_key = key.replace('_', ' ').capitalize()
                formatted_content += f"{formatted_key}: {value}\n"
            return formatted_content
        except json.JSONDecodeError:
            return self.content

class Appointment(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    date = models.DateField()
    start_time = models.TimeField(null=True)
    end_time = models.TimeField(null=True)
    consultation_notes = models.TextField(blank=True, null=True, verbose_name="Consultation Notes")
    service = models.ForeignKey(Service, null=True, on_delete=models.CASCADE)
    booked_on = models.DateTimeField(auto_now_add=True)
    waiver = models.OneToOneField(Waiver, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.name} - {self.date} - {self.start_time} to {self.end_time} ({self.service.name})"

    class Meta:
        unique_together = ('date', 'start_time', 'end_time')



class Services(models.Model):
    title = models.CharField(max_length=200)
    banner_image = models.ImageField(upload_to='service_banners/')
    description = models.TextField()
    slug = models.SlugField(unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super(Services, self).save(*args, **kwargs)

    class Meta:
        ordering = ['-created_at']




class PatientRecord(models.Model):
    patient_name = models.CharField(max_length=100)
    date_of_birth = models.DateField(null=True, blank=True)
    contact_number = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)

    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_records')
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='updated_records')

    def __str__(self):
        return f"{self.patient_name} - {self.date_of_birth}"

    class Meta:
        ordering = ['-updated_at']

class PatientNote(models.Model):
    patient = models.ForeignKey(PatientRecord, on_delete=models.CASCADE, related_name='notes')
    date = models.DateField()
    note = models.TextField()
    image = models.ImageField(upload_to='patient_notes/', null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_notes')
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='updated_notes')

    def __str__(self):
        return f"{self.patient.patient_name} - {self.date}"

    class Meta:
        ordering = ['-date']