import time
import datetime
from ...models import RabbitPackage
from viber_bot.models import Position
from django.core.management.base import BaseCommand, CommandError
from datetime import timedelta
from django.utils import timezone
from django.db.models import Q


class Command(BaseCommand):
    help = 'Чистка пакетів'

    def handle(self, *args, **options):
        start_time = time.time()
        current_datetime = datetime.datetime.now()

        three_days_ago = timezone.now() - timedelta(days=3)

        status_filter = Q(status_code='2')
        createdon_filter = Q(createdon__lte=three_days_ago)

        packages = RabbitPackage.objects.filter(status_filter & createdon_filter).order_by('-priority', 'createdon')

        deleted_packages = 0
        for package in packages:
            if deleted_packages < 500:
                package.delete()
                deleted_packages += 1
                self.stdout.write(self.style.SUCCESS(f'{package.type} - Видалено'))
            else:
                self.stdout.write(self.style.SUCCESS(f'Видалено {deleted_packages}. Exiting...'))
                break

        end_time = time.time()
        execution_time = end_time - start_time
        records_per_minute = (deleted_packages / execution_time) * 60
        self.stdout.write(self.style.SUCCESS(f'{current_datetime} - {deleted_packages} deleted in {execution_time} seconds. Approximately {records_per_minute:.2f} per minute.'))
