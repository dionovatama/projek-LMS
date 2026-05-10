from django import forms
from .models import Mapel, Tugas, PengumpulanTugas


# -----------------------------
# FORM MAPEL
# -----------------------------
class MapelForm(forms.ModelForm):
    class Meta:
        model = Mapel
        fields = ['nama', 'deskripsi', 'gambar']
        widgets = {
            'nama': forms.TextInput(attrs={'class': 'form-control'}),
            'deskripsi': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'gambar': forms.FileInput(attrs={'class': 'form-control'}),
        }


# -----------------------------
# FORM TUGAS
# -----------------------------
class TugasForm(forms.ModelForm):
    class Meta:
        model = Tugas
        fields = ['judul', 'deskripsi', 'file_tugas', 'deadline']
        widgets = {
            'judul': forms.TextInput(attrs={'class': 'form-control'}),
            'deskripsi': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'file_tugas': forms.FileInput(attrs={'class': 'form-control'}),
            'deadline': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
        }


# -----------------------------
# FORM PENILAIAN (Guru)
# -----------------------------
class PenilaianForm(forms.ModelForm):
    class Meta:
        model = PengumpulanTugas
        fields = ['nilai', 'komentar_guru']
        widgets = {
            'nilai': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                # FIX: tambah atribut min/max agar browser juga memvalidasi
                'min': '0',
                'max': '100',
                'placeholder': 'Masukkan nilai (0 – 100)',
            }),
            'komentar_guru': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Berikan komentar',
            }),
        }

    # FIX: validasi eksplisit di sisi server — tidak cukup mengandalkan
    # atribut min/max HTML karena dapat di-bypass lewat DevTools atau curl.
    def clean_nilai(self):
        nilai = self.cleaned_data.get('nilai')
        if nilai is None:
            return nilai
        if nilai < 0 or nilai > 100:
            raise forms.ValidationError(
                'Nilai harus berada di antara 0 dan 100.'
            )
        return nilai


# -----------------------------
# FORM PENGUMPULAN TUGAS (Siswa)
# -----------------------------
class PengumpulanTugasForm(forms.ModelForm):
    class Meta:
        model = PengumpulanTugas
        fields = ['jawaban_teks', 'jawaban_file']
        widgets = {
            'jawaban_teks': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Tulis jawaban di sini',
            }),
            'jawaban_file': forms.ClearableFileInput(attrs={
                'class': 'form-control',
            }),
        }