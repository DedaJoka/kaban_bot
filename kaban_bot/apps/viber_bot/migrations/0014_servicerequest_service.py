# Generated by Django 4.2 on 2023-07-28 09:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('viber_bot', '0013_servicerequest_address_servicerequest_settlement'),
    ]

    operations = [
        migrations.AddField(
            model_name='servicerequest',
            name='service',
            field=models.ForeignKey(default=3, on_delete=django.db.models.deletion.CASCADE, related_name='service_requests_service', to='viber_bot.service', verbose_name='Послуга'),
            preserve_default=False,
        ),
    ]
