# Generated by Django 4.2 on 2023-07-27 10:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('viber_bot', '0007_alter_service_options_alter_service_parent_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='settlement',
            name='codifier',
            field=models.CharField(blank=True, max_length=100, verbose_name='Кодифікатор'),
        ),
        migrations.AlterField(
            model_name='settlement',
            name='name',
            field=models.CharField(blank=True, max_length=19, verbose_name='Назва'),
        ),
    ]
