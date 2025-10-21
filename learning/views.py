from .models import CustomUser
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.decorators import login_required



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


from .models import Bab, Tugas
from django.contrib import messages


def buat_tugas(request):
    if request.user.role != 'guru':
        messages.error(request, 'Hanya guru yang bisa menambah tugas.')
        return redirect('dashboard_murid')

    if request.method == 'POST':
        bab_id = request.POST.get('bab')
        nama_tugas = request.POST.get('nama_tugas')
        deskripsi = request.POST.get('deskripsi')
        deadline = request.POST.get('deadline')

        bab = Bab.objects.get(id=bab_id)
        Tugas.objects.create(
            bab=bab,
            nama_tugas=nama_tugas,
            deskripsi=deskripsi,
            deadline=deadline
        )
        messages.success(request, 'Tugas berhasil ditambahkan!')
        return redirect('dashboard_guru')

    bab_list = Bab.objects.filter(mapel__guru=request.user)
    return render(request, 'learning/tambah_tugas.html', {'bab_list': bab_list})

from .models import Bab
from django.contrib.auth.decorators import login_required


def tambah_bab(request):
    if request.method == 'POST':
        nama_bab = request.POST.get('nama_bab')
        mapel_id = request.POST.get('mapel_id')

        if nama_bab and mapel_id:
            bab = Bab.objects.create(nama_bab=nama_bab, mapel_id=mapel_id)
            bab.save()
            return redirect('dashboard_guru')  # arahkan ke halaman dashboard guru setelah tambah

    return render(request, 'learning/tambah_bab.html')

