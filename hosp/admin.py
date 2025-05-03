from django.contrib import admin

# Register your models here.
from .models import DiseaseDetection,DiagnosisRecord

admin.site.register(DiseaseDetection)
admin.site.register(DiagnosisRecord)