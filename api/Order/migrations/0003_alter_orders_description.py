# Generated by Django 5.0 on 2023-12-19 14:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Order', '0002_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orders',
            name='description',
            field=models.TextField(blank=True, null=True, verbose_name='Описание'),
        ),
    ]
