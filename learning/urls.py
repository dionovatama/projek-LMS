from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('guru/dashboard/', views.guru_dashboard, name='dashboard_guru'),
    path('murid/dashboard/', views.siswa_dashboard, name='dashboard_siswa'),
    path('guru/tugas/buat/', views.buat_tugas, name='tambah_tugas'),
    path('dashboard/guru/', views.guru_dashboard, name='dashboard_guru'),
    path('tambah-bab/', views.tambah_bab, name='tambah_bab'),
    path('tambah-tugas/', views.buat_tugas, name='tambah_tugas'),
    path('guru/tugas/', views.daftar_tugas_guru, name='daftar_tugas_guru'),
    path('murid/tugas/', views.daftar_tugas_murid, name='daftar_tugas_murid'),
    path('murid/tugas/<int:tugas_id>/', views.detail_tugas_murid, name='detail_tugas_murid'),
    path('kirim_tugas/<int:tugas_id>/', views.kirim_tugas, name='kirim_tugas'),
    path('mapel/<int:mapel_id>/tugas/', views.daftar_tugas_per_mapel, name='daftar_tugas_per_mapel'),
    path('tambah-bab/', views.tambah_bab, name='tambah_bab'),
    path('pengumpulan/mapel/<int:mapel_id>/', views.pengumpulan_per_mapel, name='pengumpulan_per_mapel'),
    path('pengumpulan/bab/<int:bab_id>/', views.pengumpulan_per_bab, name='pengumpulan_per_bab'),
    path('pengumpulan-tugas/', views.daftar_pengumpulan_tugas, name='daftar_pengumpulan_tugas'),

]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

