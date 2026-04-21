from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [

    # ===== HOME & AUTH =====
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),

    # ===== DASHBOARD =====
    path('guru/dashboard/', views.guru_dashboard, name='dashboard_guru'),
    path('murid/dashboard/', views.siswa_dashboard, name='dashboard_siswa'),

    # ===== GURU — MAPEL =====
    path('guru/mapel/tambah/', views.tambah_mapel, name='tambah_mapel'),
    path('guru/mapel/<int:mapel_id>/', views.detail_mapel_guru, name='detail_mapel_guru'),
    path('guru/mapel/<int:mapel_id>/edit/', views.edit_mapel, name='edit_mapel'),
    path('guru/mapel/<int:mapel_id>/hapus/', views.hapus_mapel, name='hapus_mapel'),

    # ===== GURU — BAB =====
    path('guru/mapel/<int:mapel_id>/bab/tambah/', views.tambah_bab, name='tambah_bab'),
    path('guru/bab/<int:bab_id>/', views.detail_bab_guru, name='detail_bab_guru'),
    path('guru/bab/<int:pk>/hapus/', views.hapus_bab, name='hapus_bab'),

    # ===== GURU — TUGAS =====
    path('guru/tugas/tambah/', views.tambah_tugas, name='tambah_tugas'),
    path('guru/tugas/<int:id>/hapus/', views.hapus_tugas, name='hapus_tugas'),

    # ===== GURU — PENILAIAN =====
    path('guru/tugas/<int:tugas_id>/pengumpulan/', views.pengumpulan_tugas_view, name='pengumpulan_tugas'),
    path('guru/pengumpulan/<int:pengumpulan_id>/nilai/', views.nilai_tugas, name='nilai_tugas'),
    path('guru/bab/<int:bab_id>/rekap/', views.rekap_nilai_view, name='rekap_nilai'),

    # ===== GURU — ABSENSI =====
    path('guru/mapel/<int:mapel_id>/absensi/', views.absensi_view, name='absensi_mapel'),
    path('guru/mapel/<int:mapel_id>/absensi/<str:tanggal>/ubah/', views.ubah_absensi_view, name='ubah_absensi_view'),

    # ===== GURU — DAFTAR TUGAS =====
    path('guru/tugas/', views.daftar_tugas_guru, name='daftar_tugas_guru'),

    # ===== SISWA — MAPEL & BAB =====
    path('siswa/mapel/<int:mapel_id>/', views.detail_mapel_siswa, name='detail_mapel_siswa'),
    path('siswa/bab/<int:bab_id>/', views.detail_bab_siswa, name='detail_bab_siswa'),
    path('siswa/tugas/<int:tugas_id>/', views.detail_tugas_siswa, name='detail_tugas_siswa'),

    # ===== SISWA — KUMPUL TUGAS =====
    path('siswa/tugas/<int:tugas_id>/kirim/', views.kirim_tugas, name='kirim_tugas'),
    path('siswa/tugas/<int:tugas_id>/kumpul/', views.kumpul_tugas, name='kumpul_tugas'),
    path('siswa/mapel/<int:mapel_id>/tugas/', views.daftar_tugas_per_mapel, name='daftar_tugas_per_mapel'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)