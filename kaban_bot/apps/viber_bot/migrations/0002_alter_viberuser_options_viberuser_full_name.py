# Generated by Django 4.2 on 2023-07-26 10:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('viber_bot', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='viberuser',
            options={'verbose_name': 'Користувач Viber', 'verbose_name_plural': 'Користувачі Viber'},
        ),
        migrations.AddField(
            model_name='viberuser',
            name='full_name',
            field=models.CharField(blank=True, max_length=100, verbose_name='ПІБ'),
        ),
    ]
