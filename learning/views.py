from functools import wraps

from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Count
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.crypto import get_random_string
from datetime import date
import os

from .forms import PenilaianForm
from .models import (
    Absensi, Bab, GuruProfile, Kelas, Mapel,
    PengumpulanTugas, SiswaProfile, Tugas,
)


# =============================================================
# KONSTANTA
# =============================================================

ALLOWED_IMAGE_EXT = {'.jpg', '.jpeg', '.png', '.webp'}
ALLOWED_TUGAS_EXT = {
    '.pdf', '.doc', '.docx', '.xls', '.xlsx',
    '.ppt', '.pptx', '.zip', '.rar',
    '.jpg', '.jpeg', '.png', '.txt',
}

MAX_IMAGE_SIZE = 2  * 1024 * 1024   # 2 MB
MAX_TUGAS_SIZE = 10 * 1024 * 1024   # 10 MB

VALID_ABSENSI_STATUS = {'hadir', 'izin', 'sakit', 'alpa'}


# =============================================================
# HELPERS — file
# =============================================================

def validate_file(file, allowed_ext, max_size, label='File'):
    """
    Validasi ekstensi dan ukuran file.
    Return (True, '')            jika valid atau file=None.
    Return (False, pesan_error)  jika tidak valid.
    """
    if file is None:
        return True, ''
    ext = os.path.splitext(file.name)[1].lower()
    if ext not in allowed_ext:
        return False, f'{label} harus berformat: {", ".join(sorted(allowed_ext))}'
    if file.size > max_size:
        return False, f'{label} maksimal {max_size // (1024 * 1024)} MB'
    return True, ''


def safe_filename(original_name):
    """Ganti nama file dengan string acak — cegah path traversal."""
    ext = os.path.splitext(original_name)[1].lower()
    return get_random_string(32) + ext


# =============================================================
# HELPERS — role & decorator
# =============================================================

def is_guru(user):
    return hasattr(user, 'role') and user.role == 'guru'


def is_siswa(user):
    return hasattr(user, 'role') and user.role == 'siswa'


# FIX #8 & #9: pakai @wraps agar metadata view (nama, docstring) terjaga.
# Menggantikan wrapper.__name__ = view_func.__name__ yang tidak lengkap.
def guru_required(view_func):
    """Decorator: hanya guru yang boleh akses view."""
    @login_required
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not is_guru(request.user):
            messages.error(request, 'Akses ditolak.')
            return redirect('dashboard_siswa')
        return view_func(request, *args, **kwargs)
    return wrapper


def siswa_required(view_func):
    """Decorator: hanya siswa yang boleh akses view."""
    @login_required
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not is_siswa(request.user):
            messages.error(request, 'Akses ditolak.')
            return redirect('dashboard_guru')
        return view_func(request, *args, **kwargs)
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
# DASHBOARD
# FIX #8: guru_dashboard pakai @guru_required (bukan @login_required + cek manual).
# FIX #9: siswa_dashboard pakai @siswa_required (bukan @login_required + cek manual).
# Pola role-check sekarang seragam di seluruh codebase.
# =============================================================

@guru_required
def guru_dashboard(request):
    guru = get_object_or_404(GuruProfile, user=request.user)
    return render(request, 'learning/guru_dashboard.html', {
        'mapel_list': Mapel.objects.filter(guru=guru)
                           .select_related('kelas')
                           .prefetch_related('bab_list'),
    })


@siswa_required
def siswa_dashboard(request):
    siswa = get_object_or_404(SiswaProfile, user=request.user)
    return render(request, 'learning/siswa_dashboard.html', {
        'siswa': siswa,
        'mapel_list': Mapel.objects.filter(kelas=siswa.kelas)
                           .select_related('kelas')
                           .prefetch_related('bab_list'),
    })


# =============================================================
# NOTE — FIX #5: fungsi profile() dihapus dari learning/views.py.
# Profile yang aktif ada di accounts/views.py dan terhubung ke
# URL 'accounts:profile'. Dua fungsi profile yang identik membingungkan
# dan berisiko dipakai tidak sengaja lewat import atau URL yang salah.
# =============================================================


# =============================================================
# GURU — MAPEL
# =============================================================

@guru_required
def daftar_tugas_guru(request):
    guru = get_object_or_404(GuruProfile, user=request.user)
    return render(request, 'learning/daftar_tugas_guru.html', {
        'mapel_list': Mapel.objects.filter(guru=guru).select_related('kelas'),
    })


@guru_required
def detail_mapel_guru(request, mapel_id):
    mapel = get_object_or_404(Mapel, id=mapel_id, guru__user=request.user)
    return render(request, 'learning/detail_mapel_guru.html', {
        'mapel': mapel,
        'bab_list': mapel.bab_list.all(),
    })


@guru_required
def tambah_mapel(request):
    guru       = get_object_or_404(GuruProfile, user=request.user)
    kelas_list = guru.kelas_diajar.all()

    if request.method == 'POST':
        nama     = request.POST.get('nama', '').strip()
        kelas_id = request.POST.get('kelas')
        gambar   = request.FILES.get('gambar')

        if not nama:
            messages.error(request, 'Nama mapel tidak boleh kosong.')
        elif not kelas_id:
            messages.error(request, 'Pilih kelas terlebih dahulu.')
        else:
            ok, err = validate_file(gambar, ALLOWED_IMAGE_EXT, MAX_IMAGE_SIZE, 'Gambar')
            if not ok:
                messages.error(request, err)
            else:
                # FIX #4: filter dengan guru_yang_mengajar=guru agar guru tidak bisa
                # memilih kelas milik guru lain dengan memanipulasi POST data.
                kelas = get_object_or_404(Kelas, id=kelas_id, guru_yang_mengajar=guru)
                if gambar:
                    gambar.name = safe_filename(gambar.name)
                Mapel.objects.create(
                    nama=nama,
                    deskripsi=request.POST.get('deskripsi', ''),
                    kelas=kelas,
                    guru=guru,
                    gambar=gambar,
                )
                messages.success(request, 'Mapel berhasil ditambahkan!')
                return redirect('dashboard_guru')

    return render(request, 'learning/tambah_mapel.html', {'kelas_list': kelas_list})


@guru_required
def edit_mapel(request, mapel_id):
    mapel      = get_object_or_404(Mapel, id=mapel_id, guru__user=request.user)
    kelas_list = Kelas.objects.all()

    if request.method == 'POST':
        nama     = request.POST.get('nama', '').strip()
        kelas_id = request.POST.get('kelas')
        gambar   = request.FILES.get('gambar')

        if not nama:
            messages.error(request, 'Nama mapel tidak boleh kosong.')
        else:
            ok, err = validate_file(gambar, ALLOWED_IMAGE_EXT, MAX_IMAGE_SIZE, 'Gambar')
            if not ok:
                messages.error(request, err)
                return render(request, 'learning/edit_mapel.html', {
                    'mapel': mapel, 'kelas_list': kelas_list,
                })
            mapel.nama      = nama
            mapel.deskripsi = request.POST.get('deskripsi', '')
            if kelas_id:
                mapel.kelas = get_object_or_404(Kelas, id=kelas_id)
            if gambar:
                gambar.name  = safe_filename(gambar.name)
                mapel.gambar = gambar
            mapel.save()
            messages.success(request, 'Mapel berhasil diperbarui!')
            return redirect('dashboard_guru')

    return render(request, 'learning/edit_mapel.html', {
        'mapel': mapel, 'kelas_list': kelas_list,
    })


@guru_required
def hapus_mapel(request, mapel_id):
    mapel = get_object_or_404(Mapel, id=mapel_id, guru__user=request.user)
    if request.method != 'POST':
        return redirect('detail_mapel_guru', mapel_id=mapel_id)
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
            deskripsi=request.POST.get('deskripsi', '').strip(),
        )
        messages.success(request, 'Bab berhasil ditambahkan!')
        return redirect('detail_mapel_guru', mapel_id=mapel.id)

    return render(request, 'learning/tambah_bab.html', {'mapel': mapel})


@guru_required
def hapus_bab(request, pk):
    # FIX #1: dua query terpisah → satu query dengan lookup lintas relasi.
    # get_object_or_404(Bab) + get_object_or_404(Mapel) digabung menjadi:
    bab = get_object_or_404(Bab, id=pk, mapel__guru__user=request.user)

    if request.method != 'POST':
        return redirect('detail_mapel_guru', mapel_id=bab.mapel_id)

    mapel_id = bab.mapel_id   # FK langsung, tidak perlu query bab.mapel.id
    bab.delete()
    messages.success(request, 'Bab berhasil dihapus.')
    return redirect('detail_mapel_guru', mapel_id=mapel_id)


@guru_required
def detail_bab_guru(request, bab_id):
    # FIX #1: sama seperti hapus_bab — satu query mencakup validasi kepemilikan.
    bab = get_object_or_404(Bab, id=bab_id, mapel__guru__user=request.user)

    return render(request, 'learning/detail_bab_guru.html', {
        'bab': bab,
        'tugas_list': bab.tugas.all(),
    })


# =============================================================
# GURU — TUGAS
# =============================================================

@guru_required
def tambah_tugas(request):
    guru     = get_object_or_404(GuruProfile, user=request.user)
    bab_list = Bab.objects.filter(mapel__guru=guru).select_related('mapel')

    bab_obj = None
    bab_id_param = request.GET.get('bab')
    if bab_id_param:
        bab_obj = bab_list.filter(id=bab_id_param).first()

    if request.method == 'POST':
        bab_id = request.POST.get('bab')
        judul  = request.POST.get('judul', '').strip()

        if not bab_id or not judul:
            messages.error(request, 'Bab dan judul tugas wajib diisi.')
        else:
            bab        = get_object_or_404(Bab, id=bab_id, mapel__guru=guru)
            file_tugas = request.FILES.get('file_tugas')

            ok, err = validate_file(file_tugas, ALLOWED_TUGAS_EXT, MAX_TUGAS_SIZE, 'File tugas')
            if not ok:
                messages.error(request, err)
                return render(request, 'learning/tambah_tugas.html', {
                    'bab_list': bab_list, 'bab_obj': bab_obj,
                })

            if file_tugas:
                file_tugas.name = safe_filename(file_tugas.name)

            Tugas.objects.create(
                bab=bab,
                judul=judul,
                deskripsi=request.POST.get('deskripsi', ''),
                file_tugas=file_tugas,
                deadline=request.POST.get('deadline') or None,
            )
            messages.success(request, 'Tugas berhasil ditambahkan!')
            return redirect('detail_bab_guru', bab_id=bab.id)

    return render(request, 'learning/tambah_tugas.html', {
        'bab_list': bab_list, 'bab_obj': bab_obj,
    })


@guru_required
def hapus_tugas(request, tugas_id):
    # FIX #2: dua query terpisah → satu query dengan lookup lintas relasi.
    # get_object_or_404(Tugas) + get_object_or_404(Mapel) digabung menjadi:
    tugas = get_object_or_404(Tugas, id=tugas_id, bab__mapel__guru__user=request.user)

    if request.method != 'POST':
        return redirect('detail_bab_guru', bab_id=tugas.bab_id)

    bab_id = tugas.bab_id   # FK langsung, tidak perlu query tugas.bab.id
    tugas.delete()
    messages.success(request, 'Tugas berhasil dihapus.')
    return redirect('detail_bab_guru', bab_id=bab_id)


# =============================================================
# GURU — PENILAIAN
# =============================================================

@guru_required
def pengumpulan_tugas_view(request, tugas_id):
    # FIX #2: satu query sekaligus validasi kepemilikan guru.
    tugas = get_object_or_404(Tugas, id=tugas_id, bab__mapel__guru__user=request.user)

    pengumpulan_list = tugas.pengumpulan_tugas.all().select_related('siswa')
    sudah_dinilai    = pengumpulan_list.filter(nilai__isnull=False).count()
    belum_dinilai    = pengumpulan_list.filter(nilai__isnull=True).count()

    return render(request, 'learning/pengumpulan_per_tugas.html', {
        'tugas': tugas,
        'pengumpulan_list': pengumpulan_list,
        'sudah_dinilai': sudah_dinilai,
        'belum_dinilai': belum_dinilai,
    })


@guru_required
def nilai_tugas(request, pengumpulan_id):
    # FIX #3: dua query terpisah → satu query dengan lookup lintas relasi.
    # get_object_or_404(PengumpulanTugas) + get_object_or_404(Mapel) digabung:
    pengumpulan = get_object_or_404(
        PengumpulanTugas,
        id=pengumpulan_id,
        tugas__bab__mapel__guru__user=request.user,
    )

    form = PenilaianForm(instance=pengumpulan)

    if request.method == 'POST':
        form = PenilaianForm(request.POST, instance=pengumpulan)
        if form.is_valid():
            form.save()
            messages.success(request, 'Nilai berhasil disimpan!')
            # Gunakan tugas_id (FK integer) langsung, hindari query .tugas.id
            return redirect('pengumpulan_tugas', tugas_id=pengumpulan.tugas_id)
        messages.error(request, 'Periksa kembali input nilai.')

    return render(request, 'learning/nilai_tugas.html', {
        'pengumpulan': pengumpulan,
        'form': form,
    })


@guru_required
def rekap_nilai_view(request, bab_id):
    # Satu query sekaligus validasi kepemilikan guru.
    bab = get_object_or_404(Bab, id=bab_id, mapel__guru__user=request.user)

    rekap = (
        PengumpulanTugas.objects.filter(tugas__bab=bab)
        .values('siswa__username', 'siswa__first_name', 'siswa__last_name')
        .annotate(rata_rata=Avg('nilai'), jumlah_tugas=Count('id'))
        .order_by('siswa__username')
    )

    rekap_list    = list(rekap)
    sudah_dinilai = sum(1 for r in rekap_list if r['rata_rata'] is not None)
    belum_dinilai = len(rekap_list) - sudah_dinilai

    return render(request, 'learning/rekap_nilai.html', {
        'bab': bab,
        'rekap': rekap_list,
        'sudah_dinilai': sudah_dinilai,
        'belum_dinilai': belum_dinilai,
    })


# =============================================================
# GURU — ABSENSI
# =============================================================

@guru_required
def absensi_view(request, mapel_id):
    guru      = get_object_or_404(GuruProfile, user=request.user)
    mapel     = get_object_or_404(Mapel, id=mapel_id, guru=guru)
    siswa_list = (
        SiswaProfile.objects
        .filter(kelas=mapel.kelas)
        .select_related('user')
        .order_by('user__first_name', 'user__username')
    )

    tanggal_str = request.GET.get('tanggal')
    try:
        tanggal = date.fromisoformat(tanggal_str) if tanggal_str else timezone.now().date()
    except ValueError:
        tanggal = timezone.now().date()

    if request.method == 'POST':
        for siswa in siswa_list:
            status = request.POST.get(f'status_{siswa.id}')
            if status and status in VALID_ABSENSI_STATUS:
                Absensi.objects.update_or_create(
                    siswa=siswa,
                    mapel=mapel,
                    tanggal=tanggal,
                    defaults={'status': status, 'guru': guru},
                )
        messages.success(request, 'Absensi berhasil disimpan!')
        return redirect(f"{request.path}?tanggal={tanggal}")

    status_map = {
        a['siswa_id']: a['status']
        for a in Absensi.objects.filter(mapel=mapel, tanggal=tanggal)
                                .values('siswa_id', 'status')
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
    # FIX #7: view ini sebelumnya hanya me-render 'ubah_absensi.html' yang
    # tidak ada di project (TemplateDoesNotExist crash), dan tidak punya POST
    # handler sama sekali. Sekarang:
    # - validasi format tanggal dari URL parameter
    # - POST handler lengkap dengan whitelist status
    # - render ke absensi_mapel.html yang sudah ada (sambil menunggu
    #   template ubah_absensi.html dibuat oleh tim frontend)
    mapel      = get_object_or_404(Mapel, id=mapel_id, guru__user=request.user)
    guru       = mapel.guru
    siswa_list = (
        SiswaProfile.objects
        .filter(kelas=mapel.kelas)
        .select_related('user')
        .order_by('user__first_name', 'user__username')
    )

    try:
        tanggal_date = date.fromisoformat(tanggal)
    except ValueError:
        messages.error(request, 'Format tanggal tidak valid.')
        return redirect('absensi_mapel', mapel_id=mapel_id)

    if request.method == 'POST':
        for siswa in siswa_list:
            status = request.POST.get(f'status_{siswa.id}')
            if status and status in VALID_ABSENSI_STATUS:
                Absensi.objects.update_or_create(
                    siswa=siswa,
                    mapel=mapel,
                    tanggal=tanggal_date,
                    defaults={'status': status, 'guru': guru},
                )
        messages.success(request, f'Absensi {tanggal_date} berhasil diperbarui!')
        return redirect(f"{request.path}")

    status_map = {
        a['siswa_id']: a['status']
        for a in Absensi.objects.filter(mapel=mapel, tanggal=tanggal_date)
                                .values('siswa_id', 'status')
    }
    for siswa in siswa_list:
        siswa.status_absen = status_map.get(siswa.id, '')

    return render(request, 'learning/absensi_mapel.html', {
        'mapel': mapel,
        'siswa_list': siswa_list,
        'tanggal': tanggal_date,
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
        'bab_list': mapel.bab_list.all(),
    })


@siswa_required
def detail_bab_siswa(request, bab_id):
    siswa = get_object_or_404(SiswaProfile, user=request.user)
    bab   = get_object_or_404(Bab, id=bab_id, mapel__kelas=siswa.kelas)
    return render(request, 'learning/detail_bab_siswa.html', {
        'bab': bab,
        'tugas_list': bab.tugas.all(),
    })


@siswa_required
def detail_tugas_siswa(request, tugas_id):
    siswa = get_object_or_404(SiswaProfile, user=request.user)
    tugas = get_object_or_404(Tugas, id=tugas_id, bab__mapel__kelas=siswa.kelas)
    pengumpulan = PengumpulanTugas.objects.filter(
        tugas=tugas, siswa=request.user
    ).first()
    return render(request, 'learning/detail_tugas_siswa.html', {
        'tugas': tugas,
        'pengumpulan': pengumpulan,
    })


@siswa_required
def kirim_tugas(request, tugas_id):
    siswa = get_object_or_404(SiswaProfile, user=request.user)
    tugas = get_object_or_404(Tugas, id=tugas_id, bab__mapel__kelas=siswa.kelas)

    if PengumpulanTugas.objects.filter(tugas=tugas, siswa=request.user).exists():
        messages.warning(request, 'Kamu sudah mengumpulkan tugas ini.')
        return redirect('detail_tugas_siswa', tugas_id=tugas_id)

    if request.method == 'POST':
        jawaban_teks = request.POST.get('jawaban', '').strip()
        jawaban_file = request.FILES.get('file')

        if not jawaban_teks and not jawaban_file:
            messages.error(request, 'Isi jawaban teks atau upload file terlebih dahulu.')
            return render(request, 'learning/kirim_tugas.html', {'tugas': tugas})

        ok, err = validate_file(jawaban_file, ALLOWED_TUGAS_EXT, MAX_TUGAS_SIZE, 'File jawaban')
        if not ok:
            messages.error(request, err)
            return render(request, 'learning/kirim_tugas.html', {'tugas': tugas})

        if jawaban_file:
            jawaban_file.name = safe_filename(jawaban_file.name)

        PengumpulanTugas.objects.create(
            tugas=tugas,
            siswa=request.user,
            jawaban_teks=jawaban_teks,
            jawaban_file=jawaban_file,
        )
        messages.success(request, 'Tugas berhasil dikumpulkan!')
        return redirect('detail_tugas_siswa', tugas_id=tugas_id)

    return render(request, 'learning/kirim_tugas.html', {'tugas': tugas})


# FIX #6: hapus fungsi wrapper @siswa_required terpisah yang hanya memanggil
# kirim_tugas — diganti dengan alias satu baris yang lebih jelas.
# urls.py mengarahkan kedua URL langsung ke views.kirim_tugas / views.kumpul_tugas.
kumpul_tugas = kirim_tugas


@siswa_required
def daftar_tugas_per_mapel(request, mapel_id):
    siswa = get_object_or_404(SiswaProfile, user=request.user)
    mapel = get_object_or_404(Mapel, id=mapel_id, kelas=siswa.kelas)
    return render(request, 'learning/daftar_tugas_per_mapel.html', {
        'mapel': mapel,
        'tugas_list': Tugas.objects.filter(bab__mapel=mapel).select_related('bab'),
    })