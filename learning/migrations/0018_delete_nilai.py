from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("learning", "0017_alter_mapel_gambar_and_more"),
    ]

    operations = [
        migrations.DeleteModel(
            name="Nilai",
        ),
    ]
