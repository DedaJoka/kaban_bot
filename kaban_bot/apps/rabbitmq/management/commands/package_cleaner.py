from ...models import RabbitPackage
from viber_bot.models import Position
from django.core.management.base import BaseCommand, CommandError
import json


class Command(BaseCommand):
    help = 'Обробник пакетів'

    def handle(self, *args, **options):
        print(f"Запустили команду package_cleaner")

        packages = RabbitPackage.objects.filter(status_code='2').order_by('-priority', 'createdon')

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