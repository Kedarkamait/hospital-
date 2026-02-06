from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from .forms import RegisterForm

from .models import Profile, Doctor, Patient, Appointment, Department
from .forms import DoctorRegistrationForm, PatientRegistrationForm


# ===================== HOME =====================
def home(request):
    return render(request, 'hospital/home.html')


# ===================== DOCTOR REGISTRATION =====================
def register_doctor(request):
    if request.method == 'POST':
        form = DoctorRegistrationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            if User.objects.filter(username=username).exists():
                messages.error(request, "Username already exists!")
                return redirect('register_doctor')

            user = User.objects.create_user(
                username=username,
                password=password
            )

            Profile.objects.filter(user=user).update(role='doctor')

            doctor = form.save(commit=False)
            doctor.user = user
            doctor.save()

            messages.success(request, "Doctor registered successfully!")
            return redirect('login')
    else:
        form = DoctorRegistrationForm()

    return render(request, 'hospital/register_doctor.html', {'form': form})


# ===================== PATIENT REGISTRATION =====================
def register_patient(request):
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password != confirm_password:
            messages.error(request, "Passwords do not match")
            return redirect('register_patient')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken")
            return redirect('register_patient')

        user = User.objects.create_user(username=username, email=email, password=password)
        user.first_name = full_name
        user.save()

        # Profile and Patient automatically created via signals
        Profile.objects.filter(user=user).update(role='patient')
        Patient.objects.create(user=user, age=0, gender='Not Specified', phone='')

        messages.success(request, "Patient registered successfully!")
        return redirect('login')

    return render(request, 'hospital/register_patient.html')

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! You can now log in.')
            return redirect('login')
    else:
        form = RegisterForm()
    return render(request, 'hospital/register.html', {'form': form})


# ===================== LOGIN =====================
def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        if not username or not password:
            messages.error(request, "Username and password are required.")
            return render(request, 'hospital/login.html')

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)

            profile, _ = Profile.objects.get_or_create(user=user)

            if profile.role == 'doctor':
                return redirect('doctor_dashboard')
            elif profile.role == 'patient':
                return redirect('patient_dashboard')
            else:
                logout(request)
                messages.error(request, "User role not assigned.")
        else:
            messages.error(request, "Invalid username or password.")

    return render(request, 'hospital/login.html')


# ===================== LOGOUT =====================
def user_logout(request):
    logout(request)
    return redirect('login')


# ===================== DOCTOR DASHBOARD =====================
@login_required
def doctor_dashboard(request):
    if request.user.profile.role != 'doctor':
        return redirect('login')

    appointments = Appointment.objects.filter(doctor__user=request.user)
    return render(request, 'hospital/doctor_dashboard.html', {
        'appointments': appointments
    })


# ===================== PATIENT DASHBOARD =====================
@login_required
def patient_dashboard(request):
    if request.user.profile.role != 'patient':
        return redirect('login')

    appointments = Appointment.objects.filter(patient__user=request.user)
    return render(request, 'hospital/patient_dashboard.html', {
        'appointments': appointments
    })


# ===================== STATIC PAGES =====================
def doctor_list(request):
    return render(request, 'hospital/doctor.html')


def department_list(request):
    return render(request, 'hospital/department.html')


def contact(request):
    return render(request, 'hospital/contact.html')


def register_view(request):
    return render(request, 'hospital/register.html')


def login_view(request):
    return render(request, 'hospital/login.html')


# ===================== APPOINTMENT BOOKING =====================
def appointment(request):
    departments = Department.objects.all()
    doctors = Doctor.objects.all()

    if request.method == "POST":
        patient_name = request.POST.get('patient_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        department_id = request.POST.get('department')
        doctor_id = request.POST.get('doctor')
        appointment_date = request.POST.get('appointment_date')

        if not all([patient_name, email, phone, department_id, doctor_id, appointment_date]):
            messages.error(request, "Please fill all required fields!")
            return redirect('appointment')

        try:
            doctor = Doctor.objects.get(id=doctor_id)
        except Doctor.DoesNotExist:
            messages.error(request, "Invalid doctor selection.")
            return redirect('appointment')

        patient_user, _ = User.objects.get_or_create(
            username=email,
            defaults={'first_name': patient_name, 'email': email}
        )

        patient, _ = Patient.objects.get_or_create(
            user=patient_user,
            defaults={'phone': phone, 'age': 0, 'gender': 'Not Specified'}
        )

        Appointment.objects.create(
            doctor=doctor,
            patient=patient,
            date=appointment_date,
            time="09:00"
        )

        messages.success(request, "Appointment booked successfully!")
        return redirect('appointment')

    return render(request, 'hospital/appointment.html', {
        'departments': departments,
        'doctors': doctors
    })
