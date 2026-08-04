from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0002_add_demande_reference"),
    ]

    operations = [
        migrations.AlterField(
            model_name="stock",
            name="article",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="stocks",
                to="app.article",
                verbose_name="Article",
            ),
        ),
        migrations.AddConstraint(
            model_name="stock",
            constraint=models.UniqueConstraint(fields=("article", "emplacement"), name="unique_stock_article_emplacement"),
        ),
    ]
