# Generated by Django 4.2.6 on 2024-03-25 09:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('viber_bot', '0047_alter_price_price'),
    ]

    operations = [
        migrations.AddField(
            model_name='servicerequest',
            name='price',
            field=models.DecimalField(decimal_places=2, default=2, max_digits=10, verbose_name='Вартість'),
            preserve_default=False,
        ),
    ]
