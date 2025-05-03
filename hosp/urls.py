from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('register/doctor/', views.doctor_register_view, name='doctor_register'),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
    path('doctor/dashboard/', views.doctor_dashboard, name='doctor_dashboard'),
    path('doctor/patient/<str:patient_id>/dashboard/', views.patient_dashboard, name='doctor_view_patient_dashboard'),
    path('patient/login/', views.patient_login_view, name='patient_login'),
    path('patient/change-password/', views.patient_change_password_view, name='patient_change_password'),
    path('doctor/login/', views.doctor_login_view, name='doctor_login'),
    path('patient/dashboard/', views.patient_dashboard, name='patient_dashboard'),
    path('logout/', views.logout_view, name='logout'),

]
