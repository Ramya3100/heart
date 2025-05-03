from django import forms
from django.contrib.auth.models import User
from .models import Doctor

class DoctorRegistrationForm(forms.ModelForm):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = Doctor
        fields = ['name']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")

class PatientCreationForm(forms.Form):
    patient_id = forms.CharField(max_length=20)
    patient_name = forms.CharField(max_length=100)

class PatientLoginForm(forms.Form):
    patient_id = forms.CharField(max_length=20)
    password = forms.CharField(widget=forms.PasswordInput)

class ChangePasswordForm(forms.Form):
    username = forms.CharField(label="Patient ID (Username)")
    new_password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')

        if new_password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")

