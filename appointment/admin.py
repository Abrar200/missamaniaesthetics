from django.contrib import admin
from django.shortcuts import render
from .models import Appointment, Timeslot, Waiver

class AppointmentAdmin(admin.ModelAdmin):
    change_list_template = 'admin/appointments/appointment/change_list.html'

    def changelist_view(self, request, extra_context=None):
        response = super().changelist_view(request, extra_context=extra_context)
        if request.method == 'GET':
            appointments = list(response.context_data['cl'].queryset.order_by('date', 'timeslot__start_time'))
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

admin.site.register(Appointment, AppointmentAdmin)
admin.site.register(Timeslot)
admin.site.register(Waiver)