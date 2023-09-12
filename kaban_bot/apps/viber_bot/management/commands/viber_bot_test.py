from ...models import ViberUser, Service
from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    help = 'Команда для тестування'

    def handle(self, *args, **options):
        print(f"Запустили команду test")

        service = Service.objects.filter(name='Монтаж')
        for s in service:
            print(s.id)
        executors = ViberUser.objects.filter(position__codifier='UA53080370010073240', service__id='11' )

        for executor in executors:
            print(executor)
