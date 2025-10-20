from .models import CustomUser
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages



def home(request):
    return render(request, 'learning/home.html')

def guru_dashboard(request):
    return render(request, 'learning/guru_dashboard.html')

def siswa_dashboard(request):
    return render(request, 'learning/siswa_dashboard.html')


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            # Cek apakah user itu guru atau murid
            if hasattr(user, 'role'):  # supaya gak error kalau belum ada field role
                if user.role == 'guru':
                    return redirect('dashboard_guru')
                elif user.role == 'murid':
                    return redirect('dashboard_murid')

            return redirect('home')
        else:
            messages.error(request, 'Username atau password salah.')

    return render(request, 'learning/login.html')
