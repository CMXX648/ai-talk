from django.contrib import admin
from .models import Doctor, Patient, FollowUpRecord

@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ["name", "gender", "phone", "department", "title", "created_at"]
    search_fields = ["name", "phone", "department"]
    list_filter = ["department"]

@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ["name", "gender", "age", "phone", "created_at"]
    search_fields = ["name", "phone"]
    list_filter = ["gender"]

@admin.register(FollowUpRecord)
class FollowUpRecordAdmin(admin.ModelAdmin):
    list_display = ["patient", "doctor", "record_date", "next_follow_up"]
    search_fields = ["patient__name", "doctor__name", "content"]
    list_filter = ["record_date", "doctor"]
    raw_id_fields = ["patient", "doctor"]