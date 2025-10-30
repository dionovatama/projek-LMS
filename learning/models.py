from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.contrib.auth.models import User
from django.utils import timezone

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
# 2. Kelas
# ==========================
class Kelas(models.Model):
    nama = models.CharField(max_length=100)

    def __str__(self):
        return self.nama


# ==========================
# 3. Profil Guru & Siswa
# ==========================
# models.py

class GuruProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    kelas = models.ManyToManyField('Kelas', related_name='guru_kelas', blank=True)
    mapel = models.ManyToManyField('Mapel', related_name='pengajar_mapel', blank=True)  # ubah related_name-nya

    def __str__(self):
        return self.user.username


class SiswaProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    kelas = models.ForeignKey(Kelas, on_delete=models.CASCADE, related_name='siswa_kelas')
    
    def __str__(self):
        return self.user.username


# ==========================
# 4. Mapel (Mata Pelajaran)
# ==========================
class Mapel(models.Model):
    nama = models.CharField(max_length=100)
    guru = models.ForeignKey('GuruProfile', on_delete=models.SET_NULL, null=True, blank=True, related_name='mapel_diajarkan')
    kelas = models.ForeignKey(Kelas, on_delete=models.CASCADE, related_name='mapel_kelas')
    gambar = models.ImageField(upload_to='mapel/', blank=True, null=True)
    deskripsi = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.nama} - {self.kelas.nama}"


# ==========================
# 5. Bab (Sub-materi dari Mapel)
# ==========================
class Bab(models.Model):
    mapel = models.ForeignKey(Mapel, on_delete=models.CASCADE, related_name='bab_list')
    judul = models.CharField(max_length=200)
    deskripsi = models.TextField(default='', blank=True)

    def __str__(self):
        return f"{self.judul} - {self.mapel.nama}"


# ==========================
# 6. Tugas (Tiap Bab punya banyak Tugas)
# ==========================
class Tugas(models.Model):
    bab = models.ForeignKey(Bab, on_delete=models.CASCADE, related_name='tugas')
    judul = models.CharField(max_length=200)
    file_tugas = models.FileField(upload_to='tugas_files/', blank=True, null=True)  # ⬅️ ini bagian penting
    deskripsi = models.TextField(default='', blank=True)
    deadline = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.judul} ({self.bab.judul})"


# ==========================
# 7. Pengumpulan Tugas
# ==========================
class PengumpulanTugas(models.Model):
    tugas = models.ForeignKey(Tugas, on_delete=models.CASCADE, related_name='pengumpulan_tugas')
    siswa = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    jawaban_teks = models.TextField(blank=True, null=True)
    jawaban_file = models.FileField(upload_to='tugas/', blank=True, null=True)
    waktu_dikumpulkan = models.DateTimeField(auto_now_add=True)
    nilai = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    komentar_guru = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.siswa.username} - {self.tugas.judul}"



# ==========================
# 8. Nilai
# ==========================
class Nilai(models.Model):
    tugas = models.ForeignKey(Tugas, on_delete=models.CASCADE, related_name='nilai_tugas')
    siswa = models.ForeignKey(SiswaProfile, on_delete=models.CASCADE)
    nilai = models.FloatField(default=0)

    def __str__(self):
        return f"{self.siswa.user.username} - {self.tugas.judul}: {self.nilai}"
    




#absesinsi

class Absensi(models.Model):
    guru = models.ForeignKey(GuruProfile, on_delete=models.CASCADE)
    mapel = models.ForeignKey(Mapel, on_delete=models.CASCADE)
    siswa = models.ForeignKey(SiswaProfile, on_delete=models.CASCADE)
    tanggal = models.DateField(default=timezone.now)
    status = models.CharField(
        max_length=10,
        choices=[
            ('hadir', 'Hadir'),
            ('izin', 'Izin'),
            ('sakit', 'Sakit'),
            ('alpa', 'Alpa')
        ]
    )

    class Meta:
        unique_together = ('siswa', 'mapel', 'tanggal')

    def __str__(self):
        return f"{self.siswa.user.username} - {self.mapel.nama} ({self.tanggal})"
