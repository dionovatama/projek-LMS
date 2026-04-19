from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from learning.models import SiswaProfile, GuruProfile, Absensi, Mapel

@login_required
def profile(request):
    user = request.user

    if user.role == 'siswa':
        siswa = get_object_or_404(SiswaProfile, user=user)
        context = {
            'siswa': siswa,
            'hadir': Absensi.objects.filter(siswa=siswa, status='hadir').count(),
            'izin':  Absensi.objects.filter(siswa=siswa, status='izin').count(),
            'sakit': Absensi.objects.filter(siswa=siswa, status='sakit').count(),
            'alpa':  Absensi.objects.filter(siswa=siswa, status='alpa').count(),
        }
        return render(request, 'accounts/profile_siswa.html', context)

    else:  # guru
        guru = get_object_or_404(GuruProfile, user=user)
        mapel_list = Mapel.objects.filter(guru=guru)
        context = {
            'guru': guru,
            'mapel_list': mapel_list,
        }
        return render(request, 'accounts/profile_guru.html', context)
    
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from learning.models import SiswaProfile, Absensi

@login_required
def profile_siswa(request):
    siswa = SiswaProfile.objects.get(user=request.user)

    # Hitung absensi
    hadir = Absensi.objects.filter(siswa=siswa, status='hadir').count()
    sakit = Absensi.objects.filter(siswa=siswa, status='sakit').count()
    izin = Absensi.objects.filter(siswa=siswa, status='izin').count()
    alpa = Absensi.objects.filter(siswa=siswa, status='alpa').count()

    context = {
        'siswa': siswa,
        'hadir': hadir,
        'sakit': sakit,
        'izin': izin,
        'alpa': alpa,
    }
    return render(request, 'accounts/profile_siswa.html', context)

# Create your views here.
