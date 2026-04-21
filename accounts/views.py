from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Avg
from learning.models import SiswaProfile, GuruProfile, Absensi, Mapel, Tugas, PengumpulanTugas


@login_required
def profile(request):
    user = request.user

    if user.role == 'siswa':
        siswa = get_object_or_404(SiswaProfile, user=user)

        # Absensi
        hadir = Absensi.objects.filter(siswa=siswa, status='hadir').count()
        izin  = Absensi.objects.filter(siswa=siswa, status='izin').count()
        sakit = Absensi.objects.filter(siswa=siswa, status='sakit').count()
        alpa  = Absensi.objects.filter(siswa=siswa, status='alpa').count()

        # Statistik tugas
        total_tugas   = Tugas.objects.filter(bab__mapel__kelas=siswa.kelas).count()
        tugas_selesai = PengumpulanTugas.objects.filter(siswa=user).count()
        tugas_belum   = max(0, total_tugas - tugas_selesai)

        # Rata-rata nilai
        rata_nilai = PengumpulanTugas.objects.filter(
            siswa=user, nilai__isnull=False
        ).aggregate(rata=Avg('nilai'))['rata']

        context = {
            'siswa': siswa,
            'hadir': hadir,
            'izin': izin,
            'sakit': sakit,
            'alpa': alpa,
            'total_tugas': total_tugas,
            'tugas_selesai': tugas_selesai,
            'tugas_belum': tugas_belum,
            'rata_nilai': rata_nilai,
        }
        return render(request, 'accounts/profile_siswa.html', context)

    else:  # guru
        guru = get_object_or_404(GuruProfile, user=user)
        context = {
            'guru': guru,
            'mapel_list': Mapel.objects.filter(guru=guru),
        }
        return render(request, 'accounts/profile_guru.html', context)