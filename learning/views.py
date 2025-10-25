from .models import CustomUser
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.decorators import login_required



def home(request):
    return render(request, 'learning/home.html')

def guru_dashboard(request):
    return render(request, 'learning/guru_dashboard.html')

from .models import Mapel, Bab

def siswa_dashboard(request):
    mapel_list = Mapel.objects.all()  # ambil semua mapel
    context = {'mapel_list': mapel_list}
    return render(request, 'learning/siswa_dashboard.html', context)

from .models import Mapel, Bab

def tambah_bab(request):
    mapel_list = Mapel.objects.all()

    if request.method == "POST":
        mapel_id = request.POST.get("mapel")
        judul = request.POST.get("judul")
        deskripsi = request.POST.get("deskripsi")

        # Ambil mapel sesuai id yang dipilih
        mapel = Mapel.objects.get(id=mapel_id)

        # Simpan bab baru
        Bab.objects.create(mapel=mapel, judul=judul, deskripsi=deskripsi)

        return redirect('dashboard_guru')  # balik ke dashboard setelah berhasil

    return render(request, 'learning/tambah_bab.html', {'mapel_list': mapel_list})


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
                elif user.role == 'siswa':
                    return redirect('dashboard_siswa')

            return redirect('home')
        else:
            messages.error(request, 'Username atau password salah.')

    return render(request, 'learning/login.html')


from .models import Bab, Tugas, Mapel, PengumpulanTugas
from django.contrib import messages
from django.shortcuts import render, get_object_or_404

def pengumpulan_per_mapel(request, mapel_id):
    mapel = get_object_or_404(Mapel, id=mapel_id)
    tugas_list = Tugas.objects.filter(bab__mapel=mapel)
    pengumpulan_list = PengumpulanTugas.objects.filter(tugas__in=tugas_list)

    context = {
        'mapel': mapel,
        'pengumpulan_list': pengumpulan_list
    }
    return render(request, 'learning/pengumpulan_per_mapel.html', context)


# Pengumpulan per Bab
def pengumpulan_per_bab(request, bab_id):
    bab = get_object_or_404(Bab, id=bab_id)
    tugas_list = Tugas.objects.filter(bab=bab)
    pengumpulan_list = PengumpulanTugas.objects.filter(tugas__in=tugas_list)

    context = {
        'bab': bab,
        'pengumpulan_list': pengumpulan_list
    }
    return render(request, 'learning/pengumpulan_per_bab.html', context)


def buat_tugas(request):
    if request.user.role != 'guru':
        messages.error(request, 'Hanya guru yang bisa menambah tugas.')
        return redirect('dashboard_siswa')

    if request.method == 'POST':
        bab_id = request.POST.get('bab')
        judul = request.POST.get('nama_tugas')
        deskripsi = request.POST.get('deskripsi')
        deadline = request.POST.get('deadline')

        bab = Bab.objects.get(id=bab_id)
        Tugas.objects.create(
            bab=bab,
            judul=judul,
            deskripsi=deskripsi,
            deadline=deadline
        )
        messages.success(request, 'Tugas berhasil ditambahkan!')
        return redirect('dashboard_guru')

    bab_list = Bab.objects.filter(mapel__guru=request.user)
    return render(request, 'learning/tambah_tugas.html', {'bab_list': bab_list})

@login_required
def daftar_pengumpulan_tugas(request):
    if request.user.role != 'guru':
        messages.error(request, "Hanya guru yang bisa melihat pengumpulan tugas.")
        return redirect('dashboard_siswa')
    
    # Ambil semua pengumpulan tugas dari mapel yang diajar guru
    pengumpulan_list = PengumpulanTugas.objects.filter(
        tugas__bab__mapel__guru=request.user
    ).select_related('tugas', 'siswa', 'tugas__bab__mapel')

    return render(request, 'learning/daftar_pengumpulan_tugas.html', {
        'pengumpulan_list': pengumpulan_list
    })


from django.contrib.auth.decorators import login_required


from .models import Tugas

@login_required
def daftar_tugas_guru(request):
    if request.user.role != 'guru':
        return redirect('dashboard_siswa')
    
    tugas_list = Tugas.objects.filter(bab__mapel__guru=request.user)
    return render(request, 'learning/daftar_tugas_guru.html', {'tugas_list': tugas_list})

@login_required
def daftar_tugas_murid(request):
    tugas_list = Tugas.objects.all()  # nanti bisa difilter per mapel
    return render(request, 'learning/daftar_tugas_murid.html', {'tugas_list': tugas_list})

from django.shortcuts import render, get_object_or_404
from .models import Tugas

def detail_tugas_murid(request, tugas_id):
    tugas = get_object_or_404(Tugas, id=tugas_id)
    return render(request, 'learning/detail_tugas_murid.html', {'tugas': tugas})


from .models import PengumpulanTugas

@login_required
def kirim_tugas(request, tugas_id):
    tugas = Tugas.objects.get(id=tugas_id)

    if request.method == 'POST':
        file = request.FILES.get('file_jawaban')
        catatan = request.POST.get('catatan')

        PengumpulanTugas.objects.create(
            tugas=tugas,
            siswa=request.user,
            file_jawaban=file,
            catatan=catatan
        )
        messages.success(request, 'Tugas berhasil dikumpulkan!')
        return redirect('detail_tugas_murid', tugas_id=tugas.id)

    return render(request, 'learning/kirim_tugas.html', {'tugas': tugas})

def daftar_tugas_per_mapel(request, mapel_id):
    mapel = Mapel.objects.get(id=mapel_id)
    tugas_list = Tugas.objects.filter(bab__mapel=mapel)
    context = {
        'mapel': mapel,
        'tugas_list': tugas_list
    }
    return render(request, 'learning/daftar_tugas_per_mapel.html', context)
