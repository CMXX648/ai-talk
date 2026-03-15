from django.shortcuts import render, get_object_or_404
from .models import Patient, Doctor, FollowUpRecord

def index(request):
    """首页"""
    patient_count = Patient.objects.count()
    doctor_count = Doctor.objects.count()
    record_count = FollowUpRecord.objects.count()
    context = {
        "patient_count": patient_count,
        "doctor_count": doctor_count,
        "record_count": record_count
    }
    return render(request, "core/index.html", context)

def patient_list(request):
    """患者列表"""
    patients = Patient.objects.all()
    return render(request, "core/patient_list.html", {"patients": patients})

def patient_detail(request, patient_id):
    """患者详情"""
    patient = get_object_or_404(Patient, pk=patient_id)
    records = FollowUpRecord.objects.filter(patient=patient).order_by("-record_date")
    return render(request, "core/patient_detail.html", {"patient": patient, "records": records})

def doctor_list(request):
    """医生列表"""
    doctors = Doctor.objects.all()
    return render(request, "core/doctor_list.html", {"doctors": doctors})