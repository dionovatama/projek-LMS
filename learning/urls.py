from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    # ===== HALAMAN UTAMA & LOGIN =====
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),

    # ===== DASHBOARD =====
    path('guru/dashboard/', views.guru_dashboard, name='dashboard_guru'),
    path('murid/dashboard/', views.siswa_dashboard, name='dashboard_siswa'),

    # ===== GURU - MAPEL & BAB =====
    path('guru/tugas/', views.daftar_tugas_guru, name='daftar_tugas_guru'),
    path('guru/mapel/<int:mapel_id>/', views.detail_mapel_guru, name='detail_mapel_guru'),
    path('guru/bab/<int:bab_id>/', views.detail_bab_guru, name='detail_bab_guru'),

    # ===== FORM TAMBAH =====
    path('guru/tambah_mapel/', views.tambah_mapel, name='tambah_mapel'),
    path('guru/mapel/<int:mapel_id>/edit/', views.edit_mapel, name='edit_mapel'),
    path('guru/tambah-bab/', views.tambah_bab, name='tambah_bab'),
    path('tambah-tugas/', views.tambah_tugas, name='tambah_tugas'),

    # ==== FORM HAPUS =====
    path('guru/mapel/hapus/<int:id>/', views.hapus_mapel, name='hapus_mapel'),



    # ===== PENILAIAN =====
    path('guru/tugas/<int:tugas_id>/pengumpulan/', views.pengumpulan_tugas_view, name='pengumpulan_tugas'),
    path('guru/nilai/<int:pengumpulan_id>/', views.nilai_tugas, name='nilai_tugas'),
    path('pengumpulan/<int:pengumpulan_id>/nilai/', views.nilai_tugas, name='nilai_tugas'),
    path('guru/bab/<int:bab_id>/rekap/', views.rekap_nilai_view, name='rekap_nilai'),

    #absensi
    path('guru/mapel/<int:mapel_id>/absensi/', views.absensi_view, name='absensi_mapel'),
    path('mapel/<int:mapel_id>/absensi/ubah/<str:tanggal>/', views.ubah_absensi_view, name='ubah_absensi_view'),





    # ===== SISWA =====
    path('mapel/<int:mapel_id>/', views.detail_mapel_siswa, name='detail_mapel_siswa'),
    path('bab/<int:bab_id>/', views.detail_bab_siswa, name='detail_bab_siswa'),
    path('tugas/<int:tugas_id>/', views.detail_tugas_siswa, name='detail_tugas_siswa'),




    path('murid/tugas/<int:tugas_id>/kirim/', views.kirim_tugas, name='kirim_tugas'),
    path('tugas/<int:tugas_id>/kirim/', views.kirim_tugas, name='kirim_tugas'),
    path('murid/mapel/<int:mapel_id>/', views.daftar_tugas_per_mapel, name='daftar_tugas_per_mapel'),
    path('murid/tugas/<int:tugas_id>/kumpul/', views.kumpul_tugas, name='kumpul_tugas'),


    

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
