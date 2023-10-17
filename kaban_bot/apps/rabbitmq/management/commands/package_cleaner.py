
from ...models import RabbitPackage
from viber_bot.models import Position
from django.core.management.base import BaseCommand, CommandError
from datetime import timedelta
from django.utils import timezone
from django.db.models import Q


class Command(BaseCommand):
    help = 'Обробник пакетів'

    def handle(self, *args, **options):

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
        if deleted_packages < 500:
            self.stdout.write(self.style.SUCCESS(f'Видалено {deleted_packages}. Усі пакети видалені. Exiting...'))