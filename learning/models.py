from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings

# ==========================
# 1. Custom User
# ==========================
class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('guru', 'Guru'),
        ('siswa', 'Siswa'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)

    def __str__(self):
        return f"{self.username} ({self.role})"


# ==========================
# 2. Mapel (Mata Pelajaran)
# ==========================
class Mapel(models.Model):
    nama = models.CharField(max_length=100)
    guru = models.ForeignKey(CustomUser, on_delete=models.CASCADE, limit_choices_to={'role': 'guru'})
    gambar = models.ImageField(upload_to='mapel/', blank=True, null=True)
    deskripsi = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nama


# ==========================
# 3. Bab (Sub-materi dari Mapel)
# ==========================
class Bab(models.Model):
    mapel = models.ForeignKey(Mapel, on_delete=models.CASCADE, related_name='bab_list')
    judul = models.CharField(max_length=200)
    deskripsi = models.TextField(default='', blank=True)  # <-- fix ini bro


    def __str__(self):
        return f"{self.judul} - {self.mapel.nama}"


# ==========================
# 4. Tugas (Tiap Bab punya banyak Tugas)
# ==========================
class Tugas(models.Model):
    bab = models.ForeignKey(Bab, on_delete=models.CASCADE, related_name='tugas_list')
    judul = models.CharField(max_length=200)
    deskripsi = models.TextField(default='', blank=True)
    deadline = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.judul} ({self.bab.judul})"
    

# ==========================
# 5.pengumpulan Tugas
# ==========================

class PengumpulanTugas(models.Model):
    tugas = models.ForeignKey(Tugas, on_delete=models.CASCADE)
    siswa = models.ForeignKey('CustomUser', on_delete=models.CASCADE)
    file_jawaban = models.FileField(upload_to='tugas_siswa/')
    catatan = models.TextField(blank=True)
    nilai = models.FloatField(blank=True, null=True)
    tanggal_kumpul = models.DateTimeField(auto_now_add=True)



# ==========================
# 6. Nilai (Otomatis untuk Siswa per Tugas)
# ==========================
class Nilai(models.Model):
    tugas = models.ForeignKey(Tugas, on_delete=models.CASCADE, related_name='nilai_tugas')
    siswa = models.ForeignKey(CustomUser, on_delete=models.CASCADE, limit_choices_to={'role': 'siswa'})
    nilai = models.FloatField(default=0)

    def __str__(self):
        return f"{self.siswa.username} - {self.tugas.judul}: {self.nilai}"
    
    from django.conf import settings

class PengumpulanTugas(models.Model):
    tugas = models.ForeignKey('Tugas', on_delete=models.CASCADE)
    siswa = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    file_jawaban = models.FileField(upload_to='tugas_siswa/', blank=True, null=True)
    catatan = models.TextField(blank=True, null=True)
    tanggal_kumpul = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='Menunggu Penilaian')

    def __str__(self):
        return f"{self.siswa.username} - {self.tugas.judul}"
