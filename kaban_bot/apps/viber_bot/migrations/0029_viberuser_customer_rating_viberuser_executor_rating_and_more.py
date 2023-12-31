# Generated by Django 4.2 on 2023-09-01 14:22

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('viber_bot', '0028_service_priority'),
    ]

    operations = [
        migrations.AddField(
            model_name='viberuser',
            name='customer_rating',
            field=models.FloatField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0.0), django.core.validators.MaxValueValidator(5.0)], verbose_name='Рейтинг клієнта'),
        ),
        migrations.AddField(
            model_name='viberuser',
            name='executor_rating',
            field=models.FloatField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0.0), django.core.validators.MaxValueValidator(5.0)], verbose_name='Рейтинг майстра'),
        ),
        migrations.AlterField(
            model_name='servicerequest',
            name='status_code',
            field=models.CharField(choices=[('0', 'Створена'), ('1', 'В роботі'), ('2', 'Виконана'), ('3', 'Скасована')], default=0, max_length=1, verbose_name='Стан'),
        ),
    ]
