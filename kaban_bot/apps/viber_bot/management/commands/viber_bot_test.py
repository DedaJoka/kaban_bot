import json

from rest_framework import serializers

from rabbitmq.management.commands.package_creator import CustomCreate
from ...models import ViberUser, Service
from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    help = 'Команда для тестування'

    def handle(self, *args, **options):
        print(f"Запустили команду test")

        service = Service.objects.filter()
        for s in service:
            class ServiceSerializer(serializers.ModelSerializer):
                class Meta:
                    model = Service
                    fields = ['status_code', 'id', 'name', 'parent']

            service_serializer = ServiceSerializer(s)
            service_json_data = service_serializer.data
            json_data = json.dumps(service_json_data, ensure_ascii=False).encode('utf-8')
            decoded_json_data = json_data.decode('utf-8')
            new_package = CustomCreate.create_package(s.id, 'INSERT', 'application/json', 'kvb::service',
                                                      decoded_json_data)
