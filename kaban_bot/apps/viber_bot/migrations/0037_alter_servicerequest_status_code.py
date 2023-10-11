# Generated by Django 4.2 on 2023-09-20 18:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('viber_bot', '0036_viberuser_phone_number'),
    ]

    operations = [
        migrations.AlterField(
            model_name='servicerequest',
            name='status_code',
            field=models.CharField(choices=[('0', 'Створена'), ('1', 'В роботі'), ('2', 'Виконана'), ('3', 'Скасована'), ('4', 'Очікування майстра'), ('5', 'Очікування підтвердження'), ('6', 'В роботі (Підтверджений майстер)'), ('7', 'Уточнення (від майстра)'), ('8', 'Уточнення (від клієнта)')], default=0, max_length=1, verbose_name='Стан'),
        ),
    ]
