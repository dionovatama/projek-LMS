from django.shortcuts import render

def home(request):
    return render(request, 'learning/home.html')
def login_view(request):
    return render(request, 'learning/login.html')

