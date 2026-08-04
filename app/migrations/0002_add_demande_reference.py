from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='demande',
            name='reference',
            field=models.CharField(blank=True, max_length=20, null=True, unique=True, verbose_name='Référence'),
        ),
    ]
