# Generated by Django 4.2.6 on 2024-03-25 09:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('viber_bot', '0048_servicerequest_price'),
    ]

    operations = [
        migrations.AlterField(
            model_name='servicerequest',
            name='price',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='Вартість'),
        ),
    ]
