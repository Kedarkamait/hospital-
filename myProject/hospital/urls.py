from django.urls import path
from . import views

urlpatterns = [
    # Home
    path('', views.home, name='home'),

    # Registration
    path('register/', views.register_view, name='register'),  # Optional landing page
    path('register/doctor/', views.register_doctor, name='register_doctor'),
    path('register/patient/', views.register_patient, name='register_patient'),

    # Authentication
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),

    # Dashboards
    path('dashboard/doctor/', views.doctor_dashboard, name='doctor_dashboard'),
    path('dashboard/patient/', views.patient_dashboard, name='patient_dashboard'),

    # Static / lists
    path('doctors/', views.doctor_list, name='doctors'),
    path('departments/', views.department_list, name='departments'),
    path('appointment/', views.appointment, name='appointment'),
    path('contact/', views.contact, name='contact'),
    path('register/', views.register, name='register'),
]

