import hashlib
import pika
import datetime
import time

from django.conf import settings
from django.core.management.base import BaseCommand
from ...models import RabbitPackage

class Command(BaseCommand):
    help = 'Відправник пакетів'

    def handle(self, *args, **options):
        start_time = time.time()
        current_datetime = datetime.datetime.now()

        packages = RabbitPackage.objects.filter(direction='1', status_code='3').order_by('-priority', 'createdon')

        sent_messages = 0

        for package in packages:
            send_to_broadcast(package)
            if package.status_code == 4:
                sent_messages += 1
                # self.stdout.write(self.style.SUCCESS(f'{package.type} - відправлено'))
        self.stdout.write(self.style.SUCCESS(f'{current_datetime} Sending {sent_messages}'))
        end_time = time.time()
        execution_time = end_time - start_time
        records_per_minute = (sent_messages / execution_time) * 60
        self.stdout.write(self.style.SUCCESS(f'{current_datetime} - {sent_messages} sent in {execution_time:.5f} seconds. Approximately {records_per_minute:.2f} per minute.'))



def send_to_broadcast(package):
    try:
        hash_object = hashlib.md5(package.body.encode())
        hash_sum = 'md5:' + hash_object.hexdigest().upper()

        headers = {
            "version": package.version,
            "hash": hash_sum,
            "id": package.identifier,
            "operation": package.operation,
            "sender": "kvb",
            "type": package.type
        }

        properties = pika.BasicProperties(headers=headers,
                                          content_type=package.contentType,
                                          priority=package.priority,
                                          delivery_mode=2)
        connection = pika.BlockingConnection(pika.URLParameters(settings.RABBIT_CONNECTION_STR))
        channel = connection.channel()
        channel.basic_publish(exchange='ex_global', routing_key='to_broadcast', properties=properties,
                              body=package.body)
        connection.close()

        package.status_code = 4
        package.save()

    except pika.exceptions.AMQPConnectionError as e:
        error_message = f"Виникла помилка під час спроби підключення до RabbitMQ: {str(e)}"
        print(error_message)
    except Exception as e:
        error_message = f"Сталася невідома помилка: {str(e)}"
        print(error_message)