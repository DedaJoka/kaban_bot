# Generated by Django 4.2 on 2023-08-07 08:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('viber_bot', '0018_viberuser_executor'),
    ]

    operations = [
        migrations.AddField(
            model_name='viberuser',
            name='service',
            field=models.ManyToManyField(related_name='viber_user_service', to='viber_bot.service', verbose_name='Послуги'),
        ),
        migrations.AlterField(
            model_name='viberuser',
            name='executor',
            field=models.BooleanField(default=False, verbose_name='Виконавець'),
        ),
    ]
