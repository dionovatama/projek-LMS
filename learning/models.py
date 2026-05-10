import os

from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator  # FIX: tambah import
from django.db import models
from django.utils import timezone
from django.utils.crypto import get_random_string


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
class GuruProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    kelas_diajar = models.ManyToManyField(
        'Kelas',
        related_name='guru_yang_mengajar',
        blank=True,
    )
    mapel = models.ManyToManyField(
        'Mapel',
        related_name='pengajar_mapel',
        blank=True,
    )

    def __str__(self):
        return self.user.username


class SiswaProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    kelas = models.ForeignKey(Kelas, on_delete=models.CASCADE, related_name='siswa_kelas')

    def __str__(self):
        return self.user.username


# ==========================
# upload_to helpers
# ==========================
def _random_name(ext: str) -> str:
    """Hasilkan nama file acak 32 karakter + ekstensi yang sudah lowercase."""
    return get_random_string(32) + ext.lower()


def upload_gambar_mapel(instance, filename: str) -> str:
    """Path untuk gambar Mapel → media/mapel/<random>.ext"""
    ext = os.path.splitext(filename)[1]
    return f"mapel/{_random_name(ext)}"


def upload_file_tugas(instance, filename: str) -> str:
    """Path untuk file lampiran Tugas dari guru → media/tugas_files/<random>.ext"""
    ext = os.path.splitext(filename)[1]
    return f"tugas_files/{_random_name(ext)}"


def upload_jawaban_siswa(instance, filename: str) -> str:
    """Path untuk file jawaban PengumpulanTugas → media/jawaban/<random>.ext"""
    ext = os.path.splitext(filename)[1]
    return f"jawaban/{_random_name(ext)}"


# ==========================
# 4. Mapel (Mata Pelajaran)
# ==========================
class Mapel(models.Model):
    nama = models.CharField(max_length=100)
    guru = models.ForeignKey(
        'GuruProfile',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='mapel_diajarkan',
    )
    kelas = models.ForeignKey(Kelas, on_delete=models.CASCADE, related_name='mapel_kelas')
    gambar = models.ImageField(upload_to=upload_gambar_mapel, blank=True, null=True)
    deskripsi = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.nama} - {self.kelas.nama}"


# ==========================
# 5. Bab
# ==========================
class Bab(models.Model):
    mapel = models.ForeignKey(Mapel, on_delete=models.CASCADE, related_name='bab_list')
    judul = models.CharField(max_length=200)
    deskripsi = models.TextField(default='', blank=True)

    def __str__(self):
        return f"{self.judul} - {self.mapel.nama}"


# ==========================
# 6. Tugas
# ==========================
class Tugas(models.Model):
    bab = models.ForeignKey(Bab, on_delete=models.CASCADE, related_name='tugas')
    judul = models.CharField(max_length=200)
    file_tugas = models.FileField(upload_to=upload_file_tugas, blank=True, null=True)
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
    jawaban_file = models.FileField(upload_to=upload_jawaban_siswa, blank=True, null=True)
    waktu_dikumpulkan = models.DateTimeField(auto_now_add=True)

    # FIX: tambahkan validators untuk membatasi nilai antara 0 dan 100.
    # Validasi terjadi di dua lapis:
    #   1. Model level — Django memanggil full_clean() sebelum save via ModelForm.
    #   2. Form level  — PenilaianForm.clean_nilai() sebagai guard eksplisit.
    # Dua lapis ini memastikan data invalid tidak bisa masuk melalui jalur apapun.
    nilai = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[
            MinValueValidator(0, message='Nilai tidak boleh kurang dari 0.'),
            MaxValueValidator(100, message='Nilai tidak boleh lebih dari 100.'),
        ],
    )
    komentar_guru = models.TextField(null=True, blank=True)

    class Meta:
        unique_together = ('tugas', 'siswa')

    def __str__(self):
        return f"{self.siswa.username} - {self.tugas.judul}"


# ==========================
# 8. Nilai (belum digunakan — kandidat hapus di sprint berikutnya)
# ==========================
class Nilai(models.Model):
    tugas = models.ForeignKey(Tugas, on_delete=models.CASCADE, related_name='nilai_tugas')
    siswa = models.ForeignKey(SiswaProfile, on_delete=models.CASCADE)
    nilai = models.FloatField(default=0)

    def __str__(self):
        return f"{self.siswa.user.username} - {self.tugas.judul}: {self.nilai}"


# ==========================
# 9. Absensi
# ==========================
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
            ('alpa', 'Alpa'),
        ],
    )

    class Meta:
        unique_together = ('siswa', 'mapel', 'tanggal')

    def __str__(self):
        return f"{self.siswa.user.username} - {self.mapel.nama} ({self.tanggal})"