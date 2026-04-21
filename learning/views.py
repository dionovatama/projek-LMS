from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Count
from django.utils import timezone
from datetime import date

from .models import (
    GuruProfile, SiswaProfile,
    Kelas, Mapel, Bab, Tugas, PengumpulanTugas,
    Absensi
)
from .forms import PenilaianForm


# =============================================================
# HELPERS
# =============================================================

def is_guru(user):
    return hasattr(user, 'role') and user.role == 'guru'


def is_siswa(user):
    return hasattr(user, 'role') and user.role == 'siswa'


def guru_required(view_func):
    """Decorator: hanya guru yang boleh akses."""
    @login_required
    def wrapper(request, *args, **kwargs):
        if not is_guru(request.user):
            messages.error(request, 'Akses ditolak.')
            return redirect('dashboard_siswa')
        return view_func(request, *args, **kwargs)
    wrapper.__name__ = view_func.__name__
    return wrapper


def siswa_required(view_func):
    """Decorator: hanya siswa yang boleh akses."""
    @login_required
    def wrapper(request, *args, **kwargs):
        if not is_siswa(request.user):
            messages.error(request, 'Akses ditolak.')
            return redirect('dashboard_guru')
        return view_func(request, *args, **kwargs)
    wrapper.__name__ = view_func.__name__
    return wrapper


# =============================================================
# HOME & AUTH
# =============================================================

def home(request):
    return render(request, 'learning/home.html')


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('dashboard_guru' if is_guru(user) else 'dashboard_siswa')

        messages.error(request, 'Username atau password salah.')

    return render(request, 'learning/login.html')


# =============================================================
# PROFILE
# =============================================================

@login_required
def profile(request):
    user = request.user

    if is_siswa(user):
        siswa = get_object_or_404(SiswaProfile, user=user)
        context = {
            'siswa': siswa,
            'hadir': Absensi.objects.filter(siswa=siswa, status='hadir').count(),
            'izin':  Absensi.objects.filter(siswa=siswa, status='izin').count(),
            'sakit': Absensi.objects.filter(siswa=siswa, status='sakit').count(),
            'alpa':  Absensi.objects.filter(siswa=siswa, status='alpa').count(),
        }
        return render(request, 'accounts/profile_siswa.html', context)

    # guru
    guru = get_object_or_404(GuruProfile, user=user)
    return render(request, 'accounts/profile_guru.html', {
        'guru': guru,
        'mapel_list': Mapel.objects.filter(guru=guru),
    })


# =============================================================
# DASHBOARD
# =============================================================

@login_required
def guru_dashboard(request):
    if not is_guru(request.user):
        return redirect('dashboard_siswa')

    guru = get_object_or_404(GuruProfile, user=request.user)
    return render(request, 'learning/guru_dashboard.html', {
        'mapel_list': Mapel.objects.filter(guru=guru)
    })


@login_required
def siswa_dashboard(request):
    if not is_siswa(request.user):
        return redirect('dashboard_guru')

    siswa = get_object_or_404(SiswaProfile, user=request.user)
    return render(request, 'learning/siswa_dashboard.html', {
        'siswa': siswa,
        'mapel_list': Mapel.objects.filter(kelas=siswa.kelas)
    })


# =============================================================
# GURU — MAPEL
# =============================================================

@guru_required
def daftar_tugas_guru(request):
    guru = get_object_or_404(GuruProfile, user=request.user)
    return render(request, 'learning/daftar_tugas_guru.html', {
        'mapel_list': Mapel.objects.filter(guru=guru)
    })


@guru_required
def detail_mapel_guru(request, mapel_id):
    mapel = get_object_or_404(Mapel, id=mapel_id, guru__user=request.user)
    return render(request, 'learning/detail_mapel_guru.html', {
        'mapel': mapel,
        'bab_list': mapel.bab_list.all()
    })


@guru_required
def tambah_mapel(request):
    guru = get_object_or_404(GuruProfile, user=request.user)
    kelas_list = guru.kelas_diajar.all()

    if request.method == 'POST':
        nama = request.POST.get('nama', '').strip()
        kelas_id = request.POST.get('kelas')

        if not nama:
            messages.error(request, 'Nama mapel tidak boleh kosong.')
        elif not kelas_id:
            messages.error(request, 'Pilih kelas terlebih dahulu.')
        else:
            Mapel.objects.create(
                nama=nama,
                deskripsi=request.POST.get('deskripsi', ''),
                kelas=get_object_or_404(Kelas, id=kelas_id),
                guru=guru,
                gambar=request.FILES.get('gambar')
            )
            messages.success(request, 'Mapel berhasil ditambahkan!')
            return redirect('dashboard_guru')

    return render(request, 'learning/tambah_mapel.html', {
        'kelas_list': kelas_list
    })


@guru_required
def edit_mapel(request, mapel_id):
    mapel = get_object_or_404(Mapel, id=mapel_id, guru__user=request.user)
    kelas_list = Kelas.objects.all()

    if request.method == 'POST':
        nama = request.POST.get('nama', '').strip()
        kelas_id = request.POST.get('kelas')

        if not nama:
            messages.error(request, 'Nama mapel tidak boleh kosong.')
        else:
            mapel.nama = nama
            mapel.deskripsi = request.POST.get('deskripsi', '')
            if kelas_id:
                mapel.kelas = get_object_or_404(Kelas, id=kelas_id)
            if request.FILES.get('gambar'):
                mapel.gambar = request.FILES['gambar']
            mapel.save()
            messages.success(request, 'Mapel berhasil diperbarui!')
            return redirect('dashboard_guru')

    return render(request, 'learning/edit_mapel.html', {
        'mapel': mapel,
        'kelas_list': kelas_list
    })


@guru_required
def hapus_mapel(request, id):
    mapel = get_object_or_404(Mapel, id=id, guru__user=request.user)
    mapel.delete()
    messages.success(request, 'Mapel berhasil dihapus.')
    return redirect('dashboard_guru')


# =============================================================
# GURU — BAB
# =============================================================

@guru_required
def tambah_bab(request, mapel_id):
    mapel = get_object_or_404(Mapel, id=mapel_id, guru__user=request.user)

    if request.method == 'POST':
        judul = request.POST.get('judul', '').strip()
        if not judul:
            messages.error(request, 'Judul bab tidak boleh kosong.')
            return render(request, 'learning/tambah_bab.html', {'mapel': mapel})

        Bab.objects.create(
            mapel=mapel,
            judul=judul,
            deskripsi=request.POST.get('deskripsi', '').strip()
        )
        messages.success(request, 'Bab berhasil ditambahkan!')
        return redirect('detail_mapel_guru', mapel_id=mapel.id)

    return render(request, 'learning/tambah_bab.html', {'mapel': mapel})


@guru_required
def hapus_bab(request, pk):
    bab = get_object_or_404(Bab, id=pk)
    # pastikan bab milik guru yang login
    get_object_or_404(Mapel, id=bab.mapel.id, guru__user=request.user)
    mapel_id = bab.mapel.id
    bab.delete()
    messages.success(request, 'Bab berhasil dihapus.')
    return redirect('detail_mapel_guru', mapel_id=mapel_id)


@guru_required
def detail_bab_guru(request, bab_id):
    bab = get_object_or_404(Bab, id=bab_id)
    # pastikan bab milik mapel guru yang login
    get_object_or_404(Mapel, id=bab.mapel.id, guru__user=request.user)

    return render(request, 'learning/detail_bab_guru.html', {
        'bab': bab,
        'tugas_list': bab.tugas.all()
    })


# =============================================================
# GURU — TUGAS
# =============================================================

@guru_required
def tambah_tugas(request):
    guru = get_object_or_404(GuruProfile, user=request.user)
    bab_list = Bab.objects.filter(mapel__guru=guru).select_related('mapel')

    bab_obj = None
    bab_id_param = request.GET.get('bab')
    if bab_id_param:
        bab_obj = bab_list.filter(id=bab_id_param).first()

    if request.method == 'POST':
        bab_id = request.POST.get('bab')
        judul = request.POST.get('judul', '').strip()

        if not bab_id or not judul:
            messages.error(request, 'Bab dan judul tugas wajib diisi.')
        else:
            bab = get_object_or_404(Bab, id=bab_id)
            Tugas.objects.create(
                bab=bab,
                judul=judul,
                deskripsi=request.POST.get('deskripsi', ''),
                file_tugas=request.FILES.get('file_tugas'),
                deadline=request.POST.get('deadline') or None
            )
            messages.success(request, 'Tugas berhasil ditambahkan!')
            return redirect('detail_bab_guru', bab_id=bab.id)

    return render(request, 'learning/tambah_tugas.html', {
        'bab_list': bab_list,
        'bab_obj': bab_obj,
    })


@guru_required
def hapus_tugas(request, id):
    tugas = get_object_or_404(Tugas, id=id)
    # pastikan tugas milik guru yang login
    get_object_or_404(Mapel, id=tugas.bab.mapel.id, guru__user=request.user)
    bab_id = tugas.bab.id
    tugas.delete()
    messages.success(request, 'Tugas berhasil dihapus.')
    return redirect('detail_bab_guru', bab_id=bab_id)


# =============================================================
# GURU — PENILAIAN
# =============================================================

@guru_required
def pengumpulan_tugas_view(request, tugas_id):
    tugas = get_object_or_404(Tugas, id=tugas_id)
    # pastikan tugas milik guru yang login
    get_object_or_404(Mapel, id=tugas.bab.mapel.id, guru__user=request.user)

    pengumpulan_list = tugas.pengumpulan_tugas.all().select_related('siswa')

    return render(request, 'learning/pengumpulan_per_tugas.html', {
        'tugas': tugas,
        'pengumpulan_list': pengumpulan_list
    })


@guru_required
def nilai_tugas(request, pengumpulan_id):
    pengumpulan = get_object_or_404(PengumpulanTugas, id=pengumpulan_id)
    form = PenilaianForm(instance=pengumpulan)

    if request.method == 'POST':
        form = PenilaianForm(request.POST, instance=pengumpulan)
        if form.is_valid():
            form.save()
            messages.success(request, 'Nilai berhasil disimpan!')
            return redirect('pengumpulan_tugas', tugas_id=pengumpulan.tugas.id)
        else:
            messages.error(request, 'Periksa kembali input nilai.')

    return render(request, 'learning/nilai_tugas.html', {
        'pengumpulan': pengumpulan,
        'form': form,
    })


@guru_required
def rekap_nilai_view(request, bab_id):
    bab = get_object_or_404(Bab, id=bab_id)

    rekap = (
        PengumpulanTugas.objects.filter(tugas__bab=bab)
        .values('siswa__username')
        .annotate(
            rata_rata=Avg('nilai'),
            jumlah_tugas=Count('id')
        )
        .order_by('siswa__username')
    )

    return render(request, 'learning/rekap_nilai.html', {
        'bab': bab,
        'rekap': rekap
    })


# =============================================================
# GURU — ABSENSI
# =============================================================

@guru_required
def absensi_view(request, mapel_id):
    guru = get_object_or_404(GuruProfile, user=request.user)
    mapel = get_object_or_404(Mapel, id=mapel_id, guru=guru)
    siswa_list = SiswaProfile.objects.filter(kelas=mapel.kelas).select_related('user')

    # Ambil tanggal dari GET param, default hari ini
    tanggal_str = request.GET.get('tanggal')
    try:
        tanggal = date.fromisoformat(tanggal_str) if tanggal_str else timezone.now().date()
    except ValueError:
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
        messages.success(request, 'Absensi berhasil disimpan!')
        return redirect(f"{request.path}?tanggal={tanggal}")

    # Tambahkan status absen ke tiap siswa
    status_map = {
        a['siswa_id']: a['status']
        for a in Absensi.objects.filter(mapel=mapel, tanggal=tanggal).values('siswa_id', 'status')
    }
    for siswa in siswa_list:
        siswa.status_absen = status_map.get(siswa.id, '')

    return render(request, 'learning/absensi_mapel.html', {
        'mapel': mapel,
        'siswa_list': siswa_list,
        'tanggal': tanggal,
    })


@guru_required
def ubah_absensi_view(request, mapel_id, tanggal):
    mapel = get_object_or_404(Mapel, id=mapel_id, guru__user=request.user)
    siswa_list = SiswaProfile.objects.filter(kelas=mapel.kelas).select_related('user')

    return render(request, 'learning/ubah_absensi.html', {
        'mapel': mapel,
        'siswa_list': siswa_list,
        'tanggal': tanggal
    })


# =============================================================
# SISWA — MAPEL & BAB
# =============================================================

@siswa_required
def detail_mapel_siswa(request, mapel_id):
    siswa = get_object_or_404(SiswaProfile, user=request.user)
    mapel = get_object_or_404(Mapel, id=mapel_id, kelas=siswa.kelas)

    return render(request, 'learning/detail_mapel_siswa.html', {
        'mapel': mapel,
        'bab_list': mapel.bab_list.all()
    })


@siswa_required
def detail_bab_siswa(request, bab_id):
    bab = get_object_or_404(Bab, id=bab_id)

    return render(request, 'learning/detail_bab_siswa.html', {
        'bab': bab,
        'tugas_list': bab.tugas.all()
    })


@siswa_required
def detail_tugas_siswa(request, tugas_id):
    tugas = get_object_or_404(Tugas, id=tugas_id)
    pengumpulan = PengumpulanTugas.objects.filter(
        tugas=tugas, siswa=request.user
    ).first()

    return render(request, 'learning/detail_tugas_siswa.html', {
        'tugas': tugas,
        'pengumpulan': pengumpulan,
    })


@siswa_required
def kirim_tugas(request, tugas_id):
    tugas = get_object_or_404(Tugas, id=tugas_id)

    # Cegah double submit
    if PengumpulanTugas.objects.filter(tugas=tugas, siswa=request.user).exists():
        messages.warning(request, 'Kamu sudah mengumpulkan tugas ini.')
        return redirect('detail_tugas_siswa', tugas_id=tugas_id)

    if request.method == 'POST':
        jawaban_teks = request.POST.get('jawaban', '').strip()
        jawaban_file = request.FILES.get('file')

        if not jawaban_teks and not jawaban_file:
            messages.error(request, 'Isi jawaban teks atau upload file terlebih dahulu.')
            return render(request, 'learning/kirim_tugas.html', {'tugas': tugas})

        PengumpulanTugas.objects.create(
            tugas=tugas,
            siswa=request.user,
            jawaban_teks=jawaban_teks,
            jawaban_file=jawaban_file
        )
        messages.success(request, 'Tugas berhasil dikumpulkan!')
        return redirect('detail_tugas_siswa', tugas_id=tugas_id)

    return render(request, 'learning/kirim_tugas.html', {'tugas': tugas})


@siswa_required
def kumpul_tugas(request, tugas_id):
    return kirim_tugas(request, tugas_id)


@siswa_required
def daftar_tugas_per_mapel(request, mapel_id):
    siswa = get_object_or_404(SiswaProfile, user=request.user)
    mapel = get_object_or_404(Mapel, id=mapel_id, kelas=siswa.kelas)

    return render(request, 'learning/daftar_tugas_per_mapel.html', {
        'mapel': mapel,
        'tugas_list': Tugas.objects.filter(bab__mapel=mapel)
    })