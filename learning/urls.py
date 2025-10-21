from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('guru/dashboard/', views.guru_dashboard, name='dashboard_guru'),
    path('murid/dashboard/', views.siswa_dashboard, name='dashboard_murid'),
    path('guru/tugas/buat/', views.buat_tugas, name='buat_tugas'),
    path('dashboard/guru/', views.guru_dashboard, name='dashboard_guru'),
    path('tambah-bab/', views.tambah_bab, name='tambah_bab'),
    path('tambah-tugas/', views.buat_tugas, name='tambah_tugas')

]
