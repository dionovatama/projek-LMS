from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Count
from django.utils import timezone

from .models import (
    CustomUser, GuruProfile, SiswaProfile,
    Kelas, Mapel, Bab, Tugas, PengumpulanTugas,
    Absensi
)


# =========================
# UTIL / GUARD
# =========================
def is_guru(user):
    return hasattr(user, 'role') and user.role == 'guru'


def is_siswa(user):
    return hasattr(user, 'role') and user.role == 'siswa'


# =========================
# HOME & AUTH
# =========================
def home(request):
    return render(request, 'learning/home.html')


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('dashboard_guru' if is_guru(user) else 'dashboard_siswa')

        messages.error(request, 'Username atau password salah.')

    return render(request, 'learning/login.html')


# =========================
# PROFILE (SISWA)
# =========================
@login_required
def profile(request):
    if not is_siswa(request.user):
        return render(request, 'accounts/profile.html')

    siswa = get_object_or_404(SiswaProfile, user=request.user)

    stats = {
        'hadir': Absensi.objects.filter(siswa=siswa, status='hadir').count(),
        'izin': Absensi.objects.filter(siswa=siswa, status='izin').count(),
        'sakit': Absensi.objects.filter(siswa=siswa, status='sakit').count(),
        'alpa': Absensi.objects.filter(siswa=siswa, status='alpa').count(),
    }

    return render(request, 'accounts/profile_siswa.html', {
        'siswa': siswa,
        **stats
    })


# =========================
# DASHBOARD
# =========================
@login_required
def guru_dashboard(request):
    if not is_guru(request.user):
        return redirect('dashboard_siswa')

    guru = get_object_or_404(GuruProfile, user=request.user)
    mapel_list = Mapel.objects.filter(guru=guru)

    return render(request, 'learning/guru_dashboard.html', {
        'mapel_list': mapel_list
    })


@login_required
def siswa_dashboard(request):
    if not is_siswa(request.user):
        return redirect('dashboard_guru')

    siswa = get_object_or_404(SiswaProfile, user=request.user)
    mapel_list = Mapel.objects.filter(kelas=siswa.kelas)

    return render(request, 'learning/siswa_dashboard.html', {
        'siswa': siswa,
        'mapel_list': mapel_list
    })


# =========================
# GURU - MAPEL & BAB
# =========================
@login_required
def daftar_tugas_guru(request):
    guru = get_object_or_404(GuruProfile, user=request.user)
    mapel_list = Mapel.objects.filter(guru=guru)

    return render(request, 'learning/daftar_tugas_guru.html', {
        'mapel_list': mapel_list
    })


@login_required
def detail_mapel_guru(request, mapel_id):
    mapel = get_object_or_404(Mapel, id=mapel_id, guru__user=request.user)
    bab_list = mapel.bab_list.all()

    return render(request, 'learning/detail_mapel_guru.html', {
        'mapel': mapel,
        'bab_list': bab_list
    })


@login_required
def detail_bab_guru(request, bab_id):
    bab = get_object_or_404(Bab, id=bab_id)
    tugas_list = bab.tugas.all()

    return render(request, 'learning/detail_bab_guru.html', {
        'bab': bab,
        'tugas_list': tugas_list
    })


# =========================
# TAMBAH / EDIT / HAPUS
# =========================
@login_required
def tambah_mapel(request):
    guru = get_object_or_404(GuruProfile, user=request.user)
    kelas_list = Kelas.objects.all()

    if request.method == 'POST':
        Mapel.objects.create(
            nama=request.POST.get('nama'),
            deskripsi=request.POST.get('deskripsi'),
            kelas=get_object_or_404(Kelas, id=request.POST.get('kelas')),
            guru=guru,
            gambar=request.FILES.get('gambar')
        )
        return redirect('dashboard_guru')

    return render(request, 'learning/tambah_mapel.html', {'kelas_list': kelas_list})


@login_required
def edit_mapel(request, mapel_id):
    mapel = get_object_or_404(Mapel, id=mapel_id)

    if request.method == 'POST':
        mapel.nama = request.POST.get('nama')
        mapel.deskripsi = request.POST.get('deskripsi')
        if request.FILES.get('gambar'):
            mapel.gambar = request.FILES.get('gambar')
        mapel.save()
        return redirect('dashboard_guru')

    return render(request, 'learning/edit_mapel.html', {'mapel': mapel})


@login_required
def hapus_mapel(request, id):
    mapel = get_object_or_404(Mapel, id=id)
    mapel.delete()
    return redirect('dashboard_guru')


@login_required
def tambah_bab(request, mapel_id):
    mapel = get_object_or_404(Mapel, id=mapel_id)

    if request.method == 'POST':
        Bab.objects.create(
            mapel=mapel,
            judul=request.POST.get('judul'),
            deskripsi=request.POST.get('deskripsi')
        )
        return redirect('detail_mapel_guru', mapel_id=mapel.id)

    return render(request, 'learning/tambah_bab.html', {'mapel': mapel})


@login_required
def hapus_bab(request, pk):
    bab = get_object_or_404(Bab, id=pk)
    mapel_id = bab.mapel.id
    bab.delete()
    return redirect('detail_mapel_guru', mapel_id=mapel_id)


@login_required
def tambah_tugas(request):
    if request.method == 'POST':
        bab = get_object_or_404(Bab, id=request.POST.get('bab'))

        Tugas.objects.create(
            bab=bab,
            judul=request.POST.get('judul'),
            deskripsi=request.POST.get('deskripsi'),
            file_tugas=request.FILES.get('file'),
            deadline=request.POST.get('deadline')
        )

        return redirect('detail_bab_guru', bab_id=bab.id)

    bab_list = Bab.objects.all()
    return render(request, 'learning/tambah_tugas.html', {'bab_list': bab_list})


@login_required
def hapus_tugas(request, id):
    tugas = get_object_or_404(Tugas, id=id)
    bab_id = tugas.bab.id
    tugas.delete()
    return redirect('detail_bab_guru', bab_id=bab_id)


# =========================
# PENILAIAN
# =========================
@login_required
def pengumpulan_tugas_view(request, tugas_id):
    tugas = get_object_or_404(Tugas, id=tugas_id)
    pengumpulan = tugas.pengumpulan_tugas.all()

    return render(request, 'learning/pengumpulan_per_tugas.html', {
        'tugas': tugas,
        'pengumpulan_list': pengumpulan
    })


@login_required
def nilai_tugas(request, pengumpulan_id):
    pengumpulan = get_object_or_404(PengumpulanTugas, id=pengumpulan_id)

    if request.method == 'POST':
        pengumpulan.nilai = request.POST.get('nilai')
        pengumpulan.komentar_guru = request.POST.get('komentar')
        pengumpulan.save()
        return redirect(request.META.get('HTTP_REFERER', 'dashboard_guru'))

    return render(request, 'learning/nilai_tugas.html', {
        'pengumpulan': pengumpulan
    })


@login_required
def rekap_nilai_view(request, bab_id):
    bab = get_object_or_404(Bab, id=bab_id)

    rekap = (
        PengumpulanTugas.objects.filter(tugas__bab=bab)
        .values('siswa__username')
        .annotate(
            rata_rata=Avg('nilai'),
            jumlah=Count('id')
        )
    )

    return render(request, 'learning/rekap_nilai.html', {
        'bab': bab,
        'rekap': rekap
    })


# =========================
# ABSENSI
# =========================
@login_required
def absensi_view(request, mapel_id):
    guru = get_object_or_404(GuruProfile, user=request.user)
    mapel = get_object_or_404(Mapel, id=mapel_id, guru=guru)

    siswa_list = SiswaProfile.objects.filter(kelas=mapel.kelas)
    tanggal = timezone.now().date()

    if request.method == 'POST':
        for siswa in siswa_list:
            status = request.POST.get(f'status_{siswa.id}')
            if status:
                Absensi.objects.update_or_create(
                    siswa=siswa,
                    mapel=mapel,
                    tanggal=tanggal,
                    defaults={'status': status, 'guru': guru}
                )

        return redirect(request.path)

    return render(request, 'learning/absensi_mapel.html', {
        'mapel': mapel,
        'siswa_list': siswa_list,
        'tanggal': tanggal
    })


@login_required
def ubah_absensi_view(request, mapel_id, tanggal):
    mapel = get_object_or_404(Mapel, id=mapel_id)
    siswa_list = SiswaProfile.objects.filter(kelas=mapel.kelas)

    return render(request, 'learning/ubah_absensi.html', {
        'mapel': mapel,
        'siswa_list': siswa_list,
        'tanggal': tanggal
    })


# =========================
# SISWA
# =========================
@login_required
def detail_mapel_siswa(request, mapel_id):
    siswa = get_object_or_404(SiswaProfile, user=request.user)
    mapel = get_object_or_404(Mapel, id=mapel_id, kelas=siswa.kelas)

    return render(request, 'learning/detail_mapel_siswa.html', {
        'mapel': mapel,
        'bab_list': mapel.bab_list.all()
    })


@login_required
def detail_bab_siswa(request, bab_id):
    bab = get_object_or_404(Bab, id=bab_id)

    return render(request, 'learning/detail_bab_siswa.html', {
        'bab': bab,
        'tugas_list': bab.tugas.all()
    })


@login_required
def detail_tugas_siswa(request, tugas_id):
    tugas = get_object_or_404(Tugas, id=tugas_id)

    return render(request, 'learning/detail_tugas_siswa.html', {
        'tugas': tugas
    })


@login_required
def kirim_tugas(request, tugas_id):
    tugas = get_object_or_404(Tugas, id=tugas_id)

    if request.method == 'POST':
        PengumpulanTugas.objects.create(
            tugas=tugas,
            siswa=request.user,
            jawaban_teks=request.POST.get('jawaban'),
            jawaban_file=request.FILES.get('file')
        )
        return redirect('dashboard_siswa')

    return render(request, 'learning/kirim_tugas.html', {'tugas': tugas})


@login_required
def kumpul_tugas(request, tugas_id):
    return kirim_tugas(request, tugas_id)


@login_required
def daftar_tugas_per_mapel(request, mapel_id):
    siswa = get_object_or_404(SiswaProfile, user=request.user)
    mapel = get_object_or_404(Mapel, id=mapel_id, kelas=siswa.kelas)

    tugas_list = Tugas.objects.filter(bab__mapel=mapel)

    return render(request, 'learning/daftar_tugas_siswa.html', {
        'mapel': mapel,
        'tugas_list': tugas_list
    })