import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):
    """
    Tambahkan MinValueValidator(0) dan MaxValueValidator(100)
    pada PengumpulanTugas.nilai.

    Catatan: validator Django disimpan di kode Python, bukan sebagai
    constraint database. Migration ini diperlukan agar Django mengenali
    perubahan state model, meski tidak mengubah skema tabel di PostgreSQL.
    Jika ingin constraint di level database, tambahkan CheckConstraint
    di Meta.constraints (lihat komentar di bawah).
    """

    dependencies = [
        ('learning', '0017_alter_mapel_gambar_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pengumpulantugas',
            name='nilai',
            field=models.DecimalField(
                blank=True,
                decimal_places=2,
                max_digits=5,
                null=True,
                validators=[
                    django.core.validators.MinValueValidator(
                        0,
                        message='Nilai tidak boleh kurang dari 0.',
                    ),
                    django.core.validators.MaxValueValidator(
                        100,
                        message='Nilai tidak boleh lebih dari 100.',
                    ),
                ],
            ),
        ),

        # OPSIONAL tapi direkomendasikan: tambahkan constraint di level
        # database PostgreSQL agar data invalid tidak bisa masuk
        # lewat jalur apapun (termasuk raw SQL atau Django shell).
        #
        # Uncomment baris di bawah jika ingin mengaktifkan:
        #
        # migrations.AddConstraint(
        #     model_name='pengumpulantugas',
        #     constraint=models.CheckConstraint(
        #         check=models.Q(nilai__gte=0) & models.Q(nilai__lte=100),
        #         name='nilai_antara_0_dan_100',
        #     ),
        # ),
    ]
