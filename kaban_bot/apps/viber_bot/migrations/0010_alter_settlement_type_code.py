# Generated by Django 4.2 on 2023-07-27 10:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('viber_bot', '0009_settlement_type_code'),
    ]

    operations = [
        migrations.AlterField(
            model_name='settlement',
            name='type_code',
            field=models.CharField(blank=True, choices=[('O', 'Область або АРК'), ('K', 'Місто, що має спеціальний статус'), ('P', 'Район в області або в АРК'), ('H', 'Територіальна громада'), ('M', 'Місто'), ('T', 'Селище міського типу'), ('C', 'Село'), ('X', 'Селище'), ('B', 'Район в місті')], max_length=1, null=True, verbose_name='Тип'),
        ),
    ]
