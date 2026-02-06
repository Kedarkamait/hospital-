from django.contrib import admin
from .models import (
    Profile, Doctor, Patient,
    Appointment, Specialization, Availability
)

admin.site.register(Profile)
admin.site.register(Doctor)
admin.site.register(Patient)
admin.site.register(Appointment)
admin.site.register(Specialization)
admin.site.register(Availability)
