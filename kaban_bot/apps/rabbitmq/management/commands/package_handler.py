from ...models import RabbitPackage
from viber_bot.models import Position, Service
from django.core.management.base import BaseCommand, CommandError
import json
import time
import datetime


class Command(BaseCommand):
    help = 'Обробник пакетів'

    def handle(self, *args, **options):
        start_time = time.time()
        current_datetime = datetime.datetime.now()

        packages = RabbitPackage.objects.filter(direction='0', status_code='1').order_by('-priority', 'createdon')

        packages_handled = 0
        for package in packages:
            if packages_handled < 5000:
                handler(package)
                packages_handled += 1
            else:
                break

        end_time = time.time()
        execution_time = end_time - start_time
        records_per_minute = (packages_handled / execution_time) * 60
        self.stdout.write(self.style.SUCCESS(f'{current_datetime} - {packages_handled} handled in {execution_time:.5f} seconds. Approximately {records_per_minute:.2f} per minute.'))


def handler(package):
    if package.type == 'crm_position':
        crm_position(package)
    elif package.type == 'crm_product':
        crm_product(package)


def crm_position(package):
    data = json.loads(package.body)

    has_codifier = 'codifier' in data and data['codifier']
    has_name = 'name' in data and data['name']
    has_category_code = 'category_code' in data and data['category_code']
    has_parent_codifier = 'parent_codifier' in data and data['parent_codifier']

    if has_codifier and has_name and has_category_code:
        try:
            # Оновлення існуючого
            position = Position.objects.get(codifier=data['codifier'])
            if position.name != data['name']:
                position.name = data['name']
                position.save()
            if position.type_code != data['category_code']:
                position.type_code = data['category_code']
                position.save()
            if has_parent_codifier and data['parent_codifier'] != 'UA':
                # parent_codifier є і він має дані
                try:
                    parent_position = Position.objects.get(codifier=data['parent_codifier'])
                    position.parent = parent_position
                    position.save()

                    package.last_error = None
                    package.status_code = 2
                    package.save()
                except:
                    package.last_error = f'Не знайдено батьківське розташування з кодифікатором: {data["parent_codifier"]}'
                    package.status_code = 5
                    package.save()
            elif data['parent_codifier'] == 'UA':
                # parent_codifier = Україна
                position.parent = None
                position.save()

                package.last_error = None
                package.status_code = 2
                package.save()
            elif 'parent_codifier' in data:
                # parent_codifier є але він пустий
                package.last_error = 'parent_codifier не містить даних!'
                package.status_code = 5
                package.save()
            else:
                # parent_codifier нема
                position.parent = None
                position.save()

                package.last_error = None
                package.status_code = 2
                package.save()
        except:
            # Створення нового запису
            if has_parent_codifier and data['parent_codifier'] != 'UA':
                # parent_codifier є і він має дані
                try:
                    parent_position = Position.objects.get(codifier=data['parent_codifier'])
                    position = Position(
                        codifier=data['codifier'],
                        name=data['name'],
                        type_code=data['category_code'],
                        parent=parent_position
                    ).save()

                    package.last_error = None
                    package.status_code = 2
                    package.save()
                except:
                    package.last_error = f'Не знайдено батьківське розташування з кодифікатором: {data["parent_codifier"]}'
                    package.status_code = 5
                    package.save()
            elif data['parent_codifier'] == 'UA':
                # parent_codifier = Україна
                position = Position(
                    codifier=data['codifier'],
                    name=data['name'],
                    type_code=data['category_code']
                ).save()

                package.last_error = None
                package.status_code = 2
                package.save()
            elif 'parent_codifier' in data:
                # parent_codifier є але він пустий
                package.last_error = 'parent_codifier не містить даних!'
                package.status_code = 5
                package.save()
            else:
                # parent_codifier нема
                position = Position(
                    codifier=data['codifier'],
                    name=data['name'],
                    type_code=data['category_code']
                ).save()

                package.last_error = None
                package.status_code = 2
                package.save()
    else:
        package.last_error = 'Відсутні обовязкові аргументи!'
        package.status_code = 5
        package.save()


def crm_product(package):
    data = json.loads(package.body)

    try:
        service = Service.objects.get(productnumber=data['productnumber'])

        result_successful(package)
    except:
        has_parent = 'parent' in data and data['parent']
        if has_parent:
            try:
                parent = Service.objects.get(productnumber=data['parent'])

                service = Service(
                    productnumber=data['productnumber'],
                    name=data['name'],
                    parent=parent
                ).save()

                result_successful(package)
            except:
                result_fail(package, 'Не знайдень батьківської послуги!')
        else:
            try:
                service = Service(
                    productnumber=data['productnumber'],
                    name=data['name'],
                ).save()
                result_successful(package)
            except:
                result_fail(package, 'Не вдалося створити!')


def result_successful(package):
    package.last_error = None
    package.status_code = 2
    package.save()


def result_fail(package, text):
    package.last_error = text
    package.status_code = 5
    package.save()
