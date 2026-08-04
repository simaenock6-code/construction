from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0003_stock_relax_article_unique"),
    ]

    operations = [
        migrations.AddField(
            model_name="personnel",
            name="chantier",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="personnels",
                to="app.emplacement",
                verbose_name="Chantier",
            ),
        ),
    ]
