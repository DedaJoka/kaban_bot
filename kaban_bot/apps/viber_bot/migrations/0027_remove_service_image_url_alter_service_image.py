# Generated by Django 4.2 on 2023-08-24 09:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('viber_bot', '0026_rename_file_service_image'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='service',
            name='image_url',
        ),
        migrations.AlterField(
            model_name='service',
            name='image',
            field=models.FileField(upload_to='viber_bot_buttons/', verbose_name='Зображення'),
        ),
    ]
