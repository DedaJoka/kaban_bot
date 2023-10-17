import base64
import datetime
import time
import pika

from django.conf import settings
from django.core.management.base import BaseCommand

from ...models import RabbitPackage


# Версия пакета

epoch_start = datetime.datetime(year=1, month=1, day=1, hour=0, minute=0)
timestamp = int(time.time())
timestamp_value = int((datetime.datetime.fromtimestamp(timestamp) - epoch_start).total_seconds() * 10000000)


class Command(BaseCommand):
    help = 'Творець пакетів'

    def handle(self, *args, **options):
        start_time = time.time()
        current_datetime = datetime.datetime.now()

        connection = pika.BlockingConnection(pika.URLParameters(settings.RABBIT_CONNECTION_STR))
        channel = connection.channel()
        channel.queue_declare(queue='q_broadcast_bot', durable=True)

        messages_consumed = 0

        try:
            while messages_consumed < 4000:
                method_frame, header_frame, body = channel.basic_get(queue='q_broadcast_bot', auto_ack=True)
                if body:
                    messages_consumed += 1

                    header = header_frame.headers
                    decode_body = body.decode('utf-8')

                    if header['sender'] == 'crm':
                        new_package = RabbitPackage(direction=0,
                                                    priority=1,
                                                    status_code=1,
                                                    version=header['version'],
                                                    identifier=header['id'],
                                                    operation=header['operation'].upper(),
                                                    contentType=header_frame.content_type,
                                                    type=header['type'],
                                                    body=decode_body)
                        new_package.save()
                    # self.stdout.write(self.style.SUCCESS(f'Received message: {header["type"]}'))

                else:
                    # self.stdout.write(self.style.SUCCESS(f'Received {messages_consumed}. Queue is empty. Exiting...'))
                    break
        except KeyboardInterrupt:
            self.stdout.write(self.style.SUCCESS(f'Received {messages_consumed}. User interrupted. Exiting...'))
        finally:
            connection.close()
            end_time = time.time()
            execution_time = end_time - start_time
            records_per_minute = (messages_consumed / execution_time) * 60
            self.stdout.write(self.style.SUCCESS(f'{current_datetime} - {messages_consumed} received in {execution_time:.5f} seconds. Approximately {records_per_minute:.2f} per minute.'))

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