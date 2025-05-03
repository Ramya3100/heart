from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User, Group
from .models import Doctor, Patient, DiseaseDetection, DiagnosisRecord
from .forms import DoctorRegistrationForm, PatientCreationForm, PatientLoginForm, ChangePasswordForm
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMultiAlternatives
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
from django.urls import reverse
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.hashers import check_password


def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        return redirect('doctor_login')  # or 'doctor_login'
    else:
        return HttpResponse('Activation link is invalid!')
    
from django.contrib.auth.models import Group

from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.http import HttpResponse

from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.shortcuts import render, redirect

def doctor_login_view(request):
    error_message = ""
    active_tab = "doctor"

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        try:
            user = User.objects.get(username=username)

            if not check_password(password, user.password):
                error_message = "Incorrect password."
            elif not user.is_active:
                error_message = "Your account is not activated."
            elif not user.groups.filter(name='Doctor').exists():
                error_message = "You are not registered as a doctor."
            else:
                login(request, user)
                return redirect("doctor_dashboard")
        except User.DoesNotExist:
            error_message = "No account found with this email address."

    return render(request, "home.html", {"error_message_doctor": error_message, "active_tab": active_tab})
    
# Home View
def home_view(request):
    return render(request, 'home.html')

# Doctor Registration View
def doctor_register_view(request):
    error_message = ''  # Initialize the error message to be empty

    if request.method == 'POST':
        form = DoctorRegistrationForm(request.POST)
        
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            name = form.cleaned_data['name']
            
            try:
                user = User.objects.get(email=email)
                if not user.is_active:
                    # Resend activation email
                    send_activation_email(request, user)
                    error_message = 'Account already exists but not activated. Activation link has been resent.'
                else:
                    error_message = 'An active account already exists with this email.'
            except User.DoesNotExist:
                # Create a new user and doctor record
                user = User.objects.create_user(username=email, email=email, password=password, is_active=False)
                Doctor.objects.create(user=user, name=name)
                user.groups.add(Group.objects.get(name='Doctor'))
                
                # Send activation email
                send_activation_email(request, user)
                error_message = 'Please confirm your email address to complete registration.'

        else:
            # If form is not valid, show errors
            error_message = 'There was an error with your submission. Please try again.'

    else:
        form = DoctorRegistrationForm()

    return render(request, 'doctor_register.html', {'form': form, 'error_message': error_message})

def send_activation_email(request, user):
    current_site = get_current_site(request)
    mail_subject = 'Activate your doctor account'
    message = render_to_string('emails/activate_account.html', {
        'user': user,
        'domain': current_site.domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': default_token_generator.make_token(user),
    })
    email = EmailMessage(mail_subject, message, to=[user.email])
    email.content_subtype = 'html'
    email.send()

# Doctor Dashboard View
@login_required
def doctor_dashboard(request):
    doctor = Doctor.objects.get(user=request.user)
    patients = doctor.patients.all()
    view=False

    if request.method == 'POST':
        form = PatientCreationForm(request.POST)
        if form.is_valid():
            patient_id = form.cleaned_data['patient_id']
            patient_name = form.cleaned_data['patient_name']

            patient_user = User.objects.create_user(username=patient_id, password='patient@123', first_name=patient_name)
            patient = Patient.objects.create(doctor=doctor, user=patient_user, patient_id=patient_id)
            view=True
            patient_group = Group.objects.get(name='Patient')
            patient_user.groups.add(patient_group)

            return redirect('doctor_dashboard')
    else:
        form = PatientCreationForm()

    return render(request, 'doctor_dashboard.html', {'patients': patients, 'form': form,'doctor': doctor,'is_patient_view': view  },)

DEFAULT_PASSWORD = 'patient@123'

def patient_login_view(request):
    error_message = ""
    patient_id = ""
    default_password = 'patient@123'

    if request.method == 'POST':
        form = PatientLoginForm(request.POST)
        if form.is_valid():
            patient_id = form.cleaned_data['patient_id']
            password = form.cleaned_data.get('password', '')

            try:
                user = User.objects.get(username=patient_id)
                patient = Patient.objects.get(user=user)

                user = authenticate(username=patient_id, password=password)
                if user is not None:
                    login(request, user)
                    return redirect('patient_dashboard')
                else:
                    error_message = "Invalid credentials."
            except (User.DoesNotExist, Patient.DoesNotExist):
                error_message = "Patient not found."

            # 💡 Clear patient_id on ANY error
            patient_id = ""

    else:
        form = PatientLoginForm()

    return render(request, 'home.html', {
        'form': form,
        'error_message_patient': error_message,
        'patient_id': patient_id,
        'default_password': default_password
    })


# Patient Change Password View
def patient_change_password_view(request):
    error_message = None
    success_message = None

    if request.method == 'POST':
        form = ChangePasswordForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            new_password = form.cleaned_data['new_password']

            try:
                user = User.objects.get(username=username)
                print(user)
                user.set_password(new_password)
                user.save()

                # If you have a Patient model and want to mark a flag
                if hasattr(user, 'patient'):
                    user.patient.has_changed_password = True
                    user.patient.save()

                logout(request)
                success_message = "Password changed successfully! Please login again."

            except User.DoesNotExist:
                error_message = "No patient found with that username."
        else:
            error_message = "Please fix the errors below."
    else:
        form = ChangePasswordForm()

    return render(request, 'patient_change_password.html', {
        'form': form,
        'error_message': error_message,
        'success_message': success_message
    })

@login_required
def patient_dashboard(request, patient_id=None):
    if patient_id:
        # If a doctor is accessing a patient's dashboard
        if not request.user.groups.filter(name='Doctor').exists():
            return HttpResponse("Unauthorized", status=403)

        doctor = Doctor.objects.get(user=request.user)
        patient = get_object_or_404(Patient, doctor=doctor, patient_id=patient_id)
        viewing_as_doctor = True
    else:
        # If the patient is accessing their own dashboard
        patient = get_object_or_404(Patient, user=request.user)
        viewing_as_doctor = False
    if request.method == 'POST':
            received_folder = r"./sounds"  # folder containing received audio 
            lsh = build_lsh_index(threshold=0.8)
            # Step 2: Query the received audio files
            similarity_results = query_received_audio(received_folder, lsh)
            # Step 3: Initialize diagnosis list
            diagnosis = []
            # Step 4: For each received file, check if there's a match in the database
            for received_file, matches in similarity_results.items():
                if matches:
                    # Query the database to get disease name and remarks using the matched IDs
                    for match_id in matches:
                        try:
                            disease = DiseaseDetection.objects.get(id=match_id)
                            DiagnosisRecord.objects.create(
                                patient=patient.user,  # or just `patient` if ForeignKey is to Patient
                                disease_name=disease.disease_name,
                                remarks=disease.remarks
                                )
                            diagnosis.append({
                                'file': received_file,
                                'disease_name': disease.disease_name,
                                'remarks': disease.remarks
                                  })
                        except DiseaseDetection.DoesNotExist:
                            diagnosis.append({
                                'file': received_file,
                                'disease_name': 'No match',
                                'remarks': 'No remarks available'
                                })
                else:
                    diagnosis.append({
                        'file': received_file,
                        'disease_name': 'No match',
                        'remarks': 'No remarks available'
                        })
                # Render results in a template
            return render(request, 'patient_dashboard.html', {'diagnosis': diagnosis,'viewing_as_doctor': viewing_as_doctor,
        'is_patient_view': True },)


    return render(request, 'patient_dashboard.html', {
        'patient': patient,
        'viewing_as_doctor': viewing_as_doctor,
        'is_patient_view': True 
    })

def logout_view(request):
    logout(request)
    return redirect('home')




#######################

import os
import librosa
import numpy as np
from datasketch import MinHash, MinHashLSH

def extract_features(audio_path, n_mfcc=13):
    """Extract MFCCs and convert to MinHash signature."""
    y, sr = librosa.load(audio_path, sr=None)
    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=n_mfcc)
    mean_mfcc = np.mean(mfcc.T, axis=0)
    
    mh = MinHash(num_perm=128)
    for val in mean_mfcc:
        mh.update(str(val).encode('utf-8'))
    return mh

def build_lsh_index(threshold=0.7):
    """Create an LSH index for the database."""
    lsh = MinHashLSH(threshold=threshold, num_perm=128)

    # Fetch audio files from the database (DiseaseDetection model)
    for disease in DiseaseDetection.objects.all():
        file_path = disease.audio.path  # Get the file path of the audio in the database
        mh = extract_features(file_path)
        lsh.insert(str(disease.id), mh)  # Insert disease ID (key) and MinHash (value)

    return lsh

def query_received_audio(received_folder, lsh):
    """Check received files against the LSH index."""
    results = {}
    for file in os.listdir(received_folder):
        if file.endswith(('.wav', '.mp3', '.ogg', '.flac')):
            file_path = os.path.join(received_folder, file)
            mh = extract_features(file_path)
            matches = lsh.query(mh)  # Returns list of matching disease IDs
            results[file] = matches
    return results

