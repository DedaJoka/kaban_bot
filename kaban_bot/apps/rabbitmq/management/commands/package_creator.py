import time, datetime, hashlib, json, re, base64, requests


from ...models import RabbitPackage
from viber_bot.models import UploadedFile
from django.core.management.base import BaseCommand, CommandError
from rest_framework import routers, serializers, viewsets



# Версия пакета
epoch_start = datetime.datetime(year=1, month=1, day=1, hour=0, minute=0)
timestamp = int(time.time())
timestamp_value = int((datetime.datetime.fromtimestamp(timestamp) - epoch_start).total_seconds() * 10000000)


class Command(BaseCommand):
    help = 'Творець пакетів'

    def handle(self, *args, **options):
        print(f"Запустили команду package_creator")



class CustomCreate:
    def create_package(identifier, operation, contentType, type, body):
        new_package = RabbitPackage(direction=1,
                                    priority=1,
                                    status_code=3,
                                    version=timestamp_value,
                                    identifier=identifier,
                                    operation=operation,
                                    contentType=contentType,
                                    type=type,
                                    body=body)
        new_package.save()

    def encode_file_to_base64(file):
        file_content = file.read()
        file_base64 = base64.b64encode(file_content).decode('utf-8')
        return file_base64