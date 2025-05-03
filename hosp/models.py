
from django.db import models
from django.contrib.auth.models import User

class Doctor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Patient(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='patients')
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    patient_id = models.CharField(max_length=20, unique=True)
    has_changed_password = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

class DiseaseDetection(models.Model):
    disease_name = models.CharField(max_length=255)
    audio = models.FileField(upload_to='audio/')
    remarks = models.TextField()

    def __str__(self):
        return self.disease_name


class DiagnosisRecord(models.Model):
    patient = models.ForeignKey(User, on_delete=models.CASCADE)
    disease_name = models.CharField(max_length=255)
    remarks = models.TextField()
    diagnosed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.patient.username} - {self.disease_name} ({self.diagnosed_at})"
