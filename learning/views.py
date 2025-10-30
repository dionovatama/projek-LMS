from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Count
from .models import Tugas, PengumpulanTugas, Absensi
from .forms import  MapelForm, PengumpulanTugasForm
from django import forms
from django.utils import timezone
from datetime import datetime


from .models import (
    CustomUser, GuruProfile, SiswaProfile,
    Kelas, Mapel, Bab, Tugas, PengumpulanTugas,
    Absensi
)

# ========================
# HALAMAN UTAMA
# ========================
def home(request):
    return render(request, 'learning/home.html')


# ========================
# LOGIN
# ========================
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            if hasattr(user, 'role'):
                if user.role == 'guru':
                    return redirect('dashboard_guru')
                elif user.role == 'siswa':
                    return redirect('dashboard_siswa')
            return redirect('home')
        else:
            messages.error(request, 'Username atau password salah.')

    return render(request, 'learning/login.html')





# ========================
# DASHBOARD GURU
# ========================
from .models import GuruProfile, Mapel

def guru_dashboard(request):
    guru_profile = GuruProfile.objects.get(user=request.user)
    mapel_list = Mapel.objects.filter(guru=guru_profile)

    if request.method == "POST":
        nama = request.POST.get('nama')
        deskripsi = request.POST.get('deskripsi')
        gambar = request.FILES.get('gambar')

        Mapel.objects.create(
            nama=nama,
            deskripsi=deskripsi,
            gambar=gambar,
            guru=guru_profile,
            kelas=guru_profile.kelas.first()  # ambil kelas pertama (kalau banyak)
        )

    return render(request, 'learning/guru_dashboard.html', {'mapel_list': mapel_list})


@login_required
def tambah_mapel(request):
    guru_profile = GuruProfile.objects.get(user=request.user)
    kelas_list = Kelas.objects.all()  # semua kelas tampil

    if request.method == 'POST':
        nama = request.POST.get('nama')
        deskripsi = request.POST.get('deskripsi')
        kelas_id = request.POST.get('kelas')
        gambar = request.FILES.get('gambar')

        kelas = get_object_or_404(Kelas, id=kelas_id)

        Mapel.objects.create(
            nama=nama,
            deskripsi=deskripsi,
            kelas=kelas,
            guru=guru_profile,
            gambar=gambar
        )
        return redirect('dashboard_guru')

    return render(request, 'learning/tambah_mapel.html', {'kelas_list': kelas_list})


@login_required
def edit_mapel(request, mapel_id):
    guru_profile = GuruProfile.objects.get(user=request.user)
    mapel = get_object_or_404(Mapel, id=mapel_id, guru=guru_profile)
    kelas_list = Kelas.objects.all()

    if request.method == 'POST':
        mapel.nama = request.POST.get('nama')
        mapel.deskripsi = request.POST.get('deskripsi')
        kelas_id = request.POST.get('kelas')
        if kelas_id:
            mapel.kelas = get_object_or_404(Kelas, id=kelas_id)

        if 'gambar' in request.FILES:
            mapel.gambar = request.FILES['gambar']

        mapel.save()
        return redirect('dashboard_guru')

    return render(request, 'learning/edit_mapel.html', {
        'mapel': mapel,
        'kelas_list': kelas_list
    })



@login_required
def daftar_tugas_guru(request):
    # ambil guru yang login sekarang
    guru_profile = GuruProfile.objects.get(user=request.user)

    # ambil semua mapel yang diampu guru ini
    mapel_list = Mapel.objects.filter(guru=guru_profile)

    context = {
        'mapel_list': mapel_list,
    }

    return render(request, 'learning/daftar_tugas_guru.html', context)



# ========================
# DETAIL MAPEL → DAFTAR BAB
# ========================
@login_required
def detail_mapel_guru(request, mapel_id):
    """Tampilan daftar Bab dan Tugas dalam 1 Mapel"""
    mapel = get_object_or_404(Mapel, id=mapel_id, guru__user=request.user)
    bab_list = Bab.objects.filter(mapel=mapel).prefetch_related('tugas')

    return render(request, 'learning/detail_mapel_guru.html', {
        'mapel': mapel,
        'bab_list': bab_list
    })


# ========================
# DETAIL BAB → DAFTAR TUGAS + PENGUMPULAN
# ========================
@login_required
def detail_bab_guru(request, bab_id):
    bab = get_object_or_404(Bab, id=bab_id, mapel__guru__user=request.user)
    tugas_list = Tugas.objects.filter(bab=bab).prefetch_related('pengumpulan_tugas')

    # total nilai rata-rata per siswa (optional)
    pengumpulan = PengumpulanTugas.objects.filter(tugas__bab=bab)
    avg_nilai = pengumpulan.aggregate(rata_rata=Avg('nilai'))['rata_rata']

    return render(request, 'learning/detail_bab_guru.html', {
        'bab': bab,
        'tugas_list': tugas_list,
        'avg_nilai': avg_nilai,
    })


# ===============================
# 1️⃣ Halaman Pengumpulan Tugas
# ===============================
from django.shortcuts import render, get_object_or_404
from .models import Tugas, PengumpulanTugas

@login_required
def pengumpulan_tugas_view(request, tugas_id):
    tugas = get_object_or_404(Tugas, id=tugas_id)
    pengumpulan_list = PengumpulanTugas.objects.filter(tugas=tugas).select_related('siswa')

    context = {
        'tugas': tugas,
        'pengumpulan_list': pengumpulan_list,
    }
    return render(request, 'learning/pengumpulan_per_tugas.html', context)


# ===============================
# 2️⃣ Halaman Rekap Nilai per Bab
# ===============================
def rekap_nilai_view(request, bab_id):
    bab = get_object_or_404(Bab, id=bab_id)
    
    rekap = (
        PengumpulanTugas.objects.filter(tugas__bab=bab)
        .values('siswa__username')
        .annotate(
            jumlah_tugas=Count('tugas', distinct=True),
            rata_rata=Avg('nilai')
        )
        .order_by('siswa__username')
    )

    context = {
        'bab': bab,
        'rekap': rekap,
    }
    return render(request, 'learning/rekap_nilai.html', context)




@login_required
def tambah_tugas(request):
    if request.user.role != 'guru':
        messages.error(request, 'Hanya guru yang bisa menambah tugas.')
        return redirect('dashboard_siswa')

    guru_profile = GuruProfile.objects.get(user=request.user)
    bab_list = Bab.objects.filter(mapel__guru=guru_profile)

    bab_id_default = request.GET.get('bab')  # ambil dari query param
    bab_obj = None
    if bab_id_default:
        bab_obj = get_object_or_404(Bab, id=bab_id_default)

    if request.method == 'POST':
        bab_id = request.POST.get('bab') or bab_id_default
        judul = request.POST.get('judul')
        deskripsi = request.POST.get('deskripsi')
        deadline = request.POST.get('deadline')

        bab = get_object_or_404(Bab, id=bab_id)
        Tugas.objects.create(
            bab=bab,
            judul=judul,
            deskripsi=deskripsi,
            deadline=deadline
        )
        messages.success(request, 'Tugas berhasil ditambahkan!')
        return redirect('detail_bab_guru', bab_id=bab.id)

    return render(request, 'learning/tambah_tugas.html', {
        'bab_list': bab_list,
        'bab': bab_obj  # <── ini penting biar template gak error
    })





# ========================
# FORM TAMBAH BAB
# ========================
@login_required
def tambah_bab(request):
    guru_profile = GuruProfile.objects.get(user=request.user)
    mapel_list = Mapel.objects.filter(guru=guru_profile)

    if request.method == "POST":
        mapel_id = request.POST.get("mapel")
        judul = request.POST.get("judul")
        deskripsi = request.POST.get("deskripsi")

        mapel = get_object_or_404(Mapel, id=mapel_id)
        Bab.objects.create(mapel=mapel, judul=judul, deskripsi=deskripsi)
        messages.success(request, 'Bab berhasil ditambahkan!')
        return redirect('dashboard_guru')

    return render(request, 'learning/tambah_bab.html', {'mapel_list': mapel_list})




# ========================
# NILAIKAN TUGAS SISWA
# ========================
# === Form Penilaian ===
class PenilaianForm(forms.ModelForm):
    class Meta:
        model = PengumpulanTugas
        fields = ['nilai', 'komentar_guru']
        widgets = {
            'nilai': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'komentar_guru': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }



login_required
def nilai_tugas(request, pengumpulan_id):
    pengumpulan = get_object_or_404(PengumpulanTugas, id=pengumpulan_id)

    if request.method == 'POST':
        form = PenilaianForm(request.POST, instance=pengumpulan)
        if form.is_valid():
            form.save()
            messages.success(request, 'Nilai dan komentar berhasil disimpan!')
            # Balik lagi ke daftar pengumpulan tugas
            return redirect('pengumpulan_tugas', tugas_id=pengumpulan.tugas.id)
    else:
        form = PenilaianForm(instance=pengumpulan)

    return render(request, 'learning/nilai_tugas.html', {
        'form': form,
        'pengumpulan': pengumpulan
    })
# ========================
# KIRIM TUGAS SISWA
# ========================
@login_required
def kirim_tugas(request, tugas_id):
    tugas = get_object_or_404(Tugas, id=tugas_id)

    if request.method == 'POST':
        form = PengumpulanTugasForm(request.POST, request.FILES)
        if form.is_valid():
            pengumpulan = form.save(commit=False)
            pengumpulan.tugas = tugas
            pengumpulan.siswa = request.user  # pastikan user siswa
            pengumpulan.save()
            return redirect('daftar_tugas')  # arahkan ke halaman daftar tugas
    else:
        form = PengumpulanTugasForm()

    context = {
        'tugas': tugas,
        'form': form,
    }
    return render(request, 'tugas/kirim_tugas.html', context)



@login_required
def daftar_tugas_per_mapel(request, mapel_id):
    if request.user.role != 'siswa':
        return redirect('dashboard_guru')

    siswa_profile = SiswaProfile.objects.get(user=request.user)
    mapel = get_object_or_404(Mapel, id=mapel_id, kelas=siswa_profile.kelas)
    tugas_list = Tugas.objects.filter(bab__mapel=mapel).select_related('bab')

    context = {
        'mapel': mapel,
        'tugas_list': tugas_list
    }
    return render(request, 'learning/daftar_tugas_per_mapel.html', context)

@login_required
def kumpul_tugas(request, tugas_id):
    if request.user.role != 'siswa':
        return redirect('dashboard_guru')

    siswa_profile = SiswaProfile.objects.get(user=request.user)
    tugas = get_object_or_404(Tugas, id=tugas_id)

    if request.method == 'POST':
        file = request.FILES.get('file')
        if not file:
            messages.error(request, 'Silakan pilih file sebelum mengirim.')
            return redirect(request.path)

        PengumpulanTugas.objects.create(
            tugas=tugas,
            siswa=siswa_profile.user,
            file=file
        )
        messages.success(request, 'Tugas berhasil dikumpulkan!')
        return redirect('daftar_tugas_per_mapel', mapel_id=tugas.bab.mapel.id)

    return render(request, 'learning/kumpul_tugas.html', {'tugas': tugas})


# ========================
# ABSENSI
# ========================
@login_required
def absensi_view(request, mapel_id):
    guru_profile = GuruProfile.objects.get(user=request.user)
    mapel = get_object_or_404(Mapel, id=mapel_id, guru=guru_profile)

    tanggal_str = request.GET.get('tanggal')

    # parsing tanggal fleksibel
    if tanggal_str:
        try:
            tanggal = datetime.strptime(tanggal_str, '%Y-%m-%d').date()
        except ValueError:
            try:
                tanggal = datetime.strptime(tanggal_str, '%b. %d, %Y').date()
            except ValueError:
                try:
                    tanggal = datetime.strptime(tanggal_str, '%b %d, %Y').date()
                except ValueError:
                    tanggal = timezone.now().date()
    else:
        tanggal = timezone.now().date()

    siswa_list = SiswaProfile.objects.filter(kelas=mapel.kelas)

    if request.method == 'POST':
        for siswa in siswa_list:
            status = request.POST.get(f'status_{siswa.id}')
            if status:
                Absensi.objects.update_or_create(
                    guru=guru_profile,
                    mapel=mapel,
                    siswa=siswa,
                    tanggal=tanggal,
                    defaults={'status': status}
                )
        messages.success(request, f'Absensi tanggal {tanggal} berhasil disimpan!')
        return redirect(f"{request.path}?tanggal={tanggal}")

    absensi_tercatat = Absensi.objects.filter(mapel=mapel, tanggal=tanggal)
    absensi_dict = {a.siswa.id: a.status for a in absensi_tercatat}
    sudah_ada = absensi_tercatat.exists()

    # 🧩 tambahkan status_absen ke tiap siswa
    for siswa in siswa_list:
        siswa.status_absen = absensi_dict.get(siswa.id, '')

    context = {
        'mapel': mapel,
        'siswa_list': siswa_list,
        'tanggal': tanggal,
        'sudah_ada': sudah_ada
    }
    return render(request, 'learning/absensi_mapel.html', context)



@login_required
def ubah_absensi_view(request, mapel_id, tanggal):
    guru_profile = GuruProfile.objects.get(user=request.user)
    mapel = get_object_or_404(Mapel, id=mapel_id, guru=guru_profile)
    tanggal = datetime.strptime(tanggal, "%Y-%m-%d").date()

    absensi_list = Absensi.objects.filter(mapel=mapel, tanggal=tanggal).select_related('siswa__user')

    if request.method == 'POST':
        for absensi in absensi_list:
            status = request.POST.get(f'status_{absensi.siswa.id}')
            if status:
                absensi.status = status
                absensi.save()
        messages.success(request, f'Absensi tanggal {tanggal} berhasil diubah!')
        return redirect('absensi_view', mapel_id=mapel.id)

    context = {
        'mapel': mapel,
        'tanggal': tanggal,
        'absensi_list': absensi_list
    }




# ========================
# DASHBOARD SISWA
# ========================
@login_required
def siswa_dashboard(request):
    if not hasattr(request.user, 'siswaprofile'):
        return redirect('dashboard_guru')  # antisipasi kalau bukan siswa

    siswa_profile = SiswaProfile.objects.get(user=request.user)
    mapel_list = Mapel.objects.filter(kelas=siswa_profile.kelas)

    context = {
        'siswa': siswa_profile,
        'mapel_list': mapel_list
    }
    return render(request, 'learning/siswa_dashboard.html', context)
    return render(request, 'learning/ubah_absensi.html', context)

# ========================
# DETAIL MAPEL SISWA & BAB & tugas
# ========================
login_required
def detail_mapel_siswa(request, mapel_id):
    mapel = get_object_or_404(Mapel, id=mapel_id)
    bab_list = Bab.objects.filter(mapel=mapel)

    context = {
        'mapel': mapel,
        'bab_list': bab_list,
    }
    return render(request, 'learning/detail_mapel_siswa.html', context)


@login_required
def detail_bab_siswa(request, bab_id):
    bab = get_object_or_404(Bab, id=bab_id)
    tugas_list = Tugas.objects.filter(bab=bab)

    context = {
        'bab': bab,
        'tugas_list': tugas_list,
    }
    return render(request, 'learning/detail_bab_siswa.html', context)

@login_required
def detail_tugas_siswa(request, tugas_id):
    siswa_profile = SiswaProfile.objects.get(user=request.user)
    tugas = get_object_or_404(Tugas, id=tugas_id)

    # Cek apakah siswa sudah mengumpulkan
    pengumpulan = PengumpulanTugas.objects.filter(
        tugas=tugas, siswa=request.user
    ).first()

    if request.method == 'POST':
        jawaban_teks = request.POST.get('jawaban_teks')
        jawaban_file = request.FILES.get('jawaban_file')  # ✅ sesuai dengan model

        if pengumpulan:
            # Update pengumpulan lama
            if jawaban_teks:
                pengumpulan.jawaban_teks = jawaban_teks
            if jawaban_file:
                pengumpulan.jawaban_file = jawaban_file
            pengumpulan.save()
        else:
            # Buat pengumpulan baru
            PengumpulanTugas.objects.create(
                tugas=tugas,
                siswa=request.user,
                jawaban_teks=jawaban_teks,
                jawaban_file=jawaban_file
            )

        messages.success(request, "Jawaban berhasil dikumpulkan!")
        return redirect('detail_tugas_siswa', tugas_id=tugas.id)

    context = {
        'tugas': tugas,
        'pengumpulan': pengumpulan,
    }
    return render(request, 'learning/detail_tugas_siswa.html', context)

