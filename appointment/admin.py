from django.contrib import admin
from django.shortcuts import render
from .models import Appointment, Service, PatientRecord, PatientNote, Services, Waiver
from django.utils.safestring import mark_safe

class AppointmentAdmin(admin.ModelAdmin):
    change_list_template = 'admin/appointments/appointment/change_list.html'
    list_display = ('name', 'phone', 'email', 'date', 'start_time', 'end_time', 'service', 'consultation_notes_preview')
    list_filter = ('date', 'service')
    search_fields = ('name', 'email', 'phone', 'consultation_notes')

    def consultation_notes_preview(self, obj):
        return obj.consultation_notes[:50] + '...' if obj.consultation_notes else ''
    consultation_notes_preview.short_description = 'Consultation Notes'

    def changelist_view(self, request, extra_context=None):
        response = super().changelist_view(request, extra_context=extra_context)
        if request.method == 'GET':
            appointments = list(response.context_data['cl'].queryset.order_by('-date', 'start_time'))
            appointments_by_date = {}
            for appointment in appointments:
                date = appointment.date
                if date not in appointments_by_date:
                    appointments_by_date[date] = []
                appointments_by_date[date].append(appointment)
            context = {
                'appointments_by_date': sorted(appointments_by_date.items(), reverse=True),
                **response.context_data,
            }
            return render(request, self.change_list_template, context)
        return response

    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path('<int:appointment_id>/change/',
                 self.admin_site.admin_view(self.appointment_change_view),
                 name='appointment_change'),
        ]
        return custom_urls + urls

    def appointment_change_view(self, request, appointment_id, form_url='', extra_context=None):
        return self.changeform_view(request, str(appointment_id), form_url, extra_context)
    
    fields = ('name', 'phone', 'email', 'date', 'start_time', 'end_time', 'service', 'consultation_notes')


class PatientNoteInline(admin.TabularInline):
    model = PatientNote
    extra = 1

@admin.register(PatientRecord)
class PatientRecordAdmin(admin.ModelAdmin):
    list_display = ('patient_name', 'date_of_birth', 'contact_number', 'email', 'updated_at')
    search_fields = ('patient_name', 'email', 'contact_number')
    list_filter = ('gender', 'created_at', 'updated_at')
    inlines = [PatientNoteInline]

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)

@admin.register(PatientNote)
class PatientNoteAdmin(admin.ModelAdmin):
    list_display = ('patient', 'date', 'note_preview', 'updated_at')
    search_fields = ('patient__patient_name', 'note')
    list_filter = ('date', 'created_at', 'updated_at')

    def note_preview(self, obj):
        return obj.note[:50] + '...' if len(obj.note) > 50 else obj.note
    note_preview.short_description = 'Note Preview'

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)

class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'duration')

admin.site.register(Appointment, AppointmentAdmin)
admin.site.register(Service, ServiceAdmin)
admin.site.register(Services)
admin.site.register(Waiver)