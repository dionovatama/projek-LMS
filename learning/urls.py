from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('guru/dashboard/', views.guru_dashboard, name='dashboard_guru'),
    path('murid/dashboard/', views.siswa_dashboard, name='dashboard_murid'),
]
