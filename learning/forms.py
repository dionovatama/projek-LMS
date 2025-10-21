from django import forms
from .models import Tugas

class TugasForm(forms.ModelForm):
    class Meta:
        model = Tugas
        fields = ['bab', 'judul', 'deskripsi', 'deadline']
