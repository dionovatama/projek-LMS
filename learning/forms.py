from django import forms
from .models import PengumpulanTugas
from .models import Mapel, Tugas

class MapelForm(forms.ModelForm):
    class Meta:
        model = Mapel
        fields = ['nama', 'deskripsi', 'gambar']

class TugasForm(forms.ModelForm):
    class Meta:
        model = Tugas
        fields = ['bab', 'judul', 'deskripsi', 'file_tugas', 'deadline']


class PenilaianForm(forms.ModelForm):
    class Meta:
        model = PengumpulanTugas
        fields = ['nilai', 'komentar_guru']
        widgets = {
            'nilai': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'komentar_guru': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class PengumpulanTugasForm(forms.ModelForm):
    class Meta:
        model = PengumpulanTugas
        fields = ['jawaban_teks', 'jawaban_file']  # sesuaikan dengan field file yang ada di model kamu
