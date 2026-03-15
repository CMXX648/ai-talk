from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("patients/", views.patient_list, name="patient_list"),
    path("patient/<int:patient_id>/", views.patient_detail, name="patient_detail"),
    path("doctors/", views.doctor_list, name="doctor_list"),
]