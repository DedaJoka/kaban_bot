# Generated by Django 4.2 on 2023-08-08 06:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('viber_bot', '0019_viberuser_service_alter_viberuser_executor'),
    ]

    operations = [
        migrations.AlterField(
            model_name='position',
            name='codifier',
            field=models.CharField(blank=True, max_length=100, unique=True, verbose_name='Кодифікатор'),
        ),
    ]
