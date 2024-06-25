from django.db import models
from django.utils.text import slugify

class Timeslot(models.Model):
    start_time = models.TimeField()
    end_time = models.TimeField()
    slot_text = models.CharField(max_length=100)

    def __str__(self):
        return self.slot_text

class Waiver(models.Model):
    content = models.TextField()
    signed_by = models.CharField(max_length=100)
    signed_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Waiver signed by {self.signed_by} on {self.signed_on}"

class Appointment(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    date = models.DateField()
    timeslot = models.ForeignKey(Timeslot, on_delete=models.CASCADE)
    booked_on = models.DateTimeField(auto_now_add=True)
    waiver = models.OneToOneField(Waiver, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"{self.name} - {self.date} - {self.timeslot.slot_text}"



class Service(models.Model):
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
        super(Service, self).save(*args, **kwargs)

    class Meta:
        ordering = ['-created_at']