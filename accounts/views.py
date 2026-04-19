from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def profile(request):
    if request.user.role == 'siswa':
        return render(request, 'accounts/profile_siswa.html')
    else:
        return render(request, 'accounts/profile_guru.html')
    
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
