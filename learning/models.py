from django.db import models
from django.contrib.auth.models import AbstractUser

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
# 5. Nilai (Otomatis untuk Siswa per Tugas)
# ==========================
class Nilai(models.Model):
    tugas = models.ForeignKey(Tugas, on_delete=models.CASCADE, related_name='nilai_tugas')
    siswa = models.ForeignKey(CustomUser, on_delete=models.CASCADE, limit_choices_to={'role': 'siswa'})
    nilai = models.FloatField(default=0)

    def __str__(self):
        return f"{self.siswa.username} - {self.tugas.judul}: {self.nilai}"
