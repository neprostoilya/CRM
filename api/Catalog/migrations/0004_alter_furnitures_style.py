# Generated by Django 5.0 on 2024-02-06 15:34

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Catalog', '0003_styles_category'),
    ]

    operations = [
        migrations.AlterField(
            model_name='furnitures',
            name='style',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='style', to='Catalog.styles', verbose_name='Стиль'),
        ),
    ]
