# Generated by Django 4.2.6 on 2023-10-24 06:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('viber_bot', '0044_viberuser_once'),
    ]

    operations = [
        migrations.AlterField(
            model_name='position',
            name='codifier',
            field=models.CharField(blank=True, max_length=100, null=True, unique=True, verbose_name='Кодифікатор'),
        ),
    ]