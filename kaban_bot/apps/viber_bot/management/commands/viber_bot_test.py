import json

from rest_framework import serializers

from rabbitmq.management.commands.package_creator import CustomCreate
from ...models import ViberUser, Service
from rabbitmq.models import RabbitPackage
from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    help = 'Команда для тестування'

    def handle(self, *args, **options):
        print(f"Запустили команду test")
        new_package = RabbitPackage(direction=1,
                                    priority=1,
                                    status_code=3,
                                    version=456,
                                    identifier='test',
                                    operation='test',
                                    contentType='test',
                                    type='test',
                                    body='test')
        new_package.save()