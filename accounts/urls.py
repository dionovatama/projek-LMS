from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView


app_name = 'accounts'

urlpatterns = [
    path('profile/', views.profile, name='profile'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
]