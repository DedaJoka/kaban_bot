# Generated by Django 4.2 on 2023-07-26 10:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('viber_bot', '0002_alter_viberuser_options_viberuser_full_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='viberuser',
            name='menu',
            field=models.CharField(blank=True, max_length=100, verbose_name='Меню'),
        ),
        migrations.AlterField(
            model_name='viberuser',
            name='viber_id',
            field=models.CharField(max_length=100, verbose_name='Вайбер ідентифікатор'),
        ),
    ]
