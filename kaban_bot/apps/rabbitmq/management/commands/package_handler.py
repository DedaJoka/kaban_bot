from ...models import RabbitPackage
from viber_bot.models import Position
from django.core.management.base import BaseCommand, CommandError
import json


class Command(BaseCommand):
    help = 'Обробник пакетів'

    def handle(self, *args, **options):
        print(f"Запустили команду package_handler")

        packages = RabbitPackage.objects.filter(direction='0', status_code='1').order_by('-priority', 'createdon')
        for package in packages:
            handler(package)




def handler(package):
    if package.type == 'crm_position':
        crm_position(package)


def crm_position(package):
    data = json.loads(package.body)

    has_codifier = 'codifier' in data and data['codifier']
    has_name = 'name' in data and data['name']
    has_category_code = 'category_code' in data and data['category_code']
    has_parent_codifier = 'parent_codifier' in data and data['parent_codifier']

    if package.operation == 'INSERT' and has_codifier and has_name and has_category_code:
        try:
            # Оновлення існуючого
            position = Position.objects.get(codifier=data['codifier'])
            if position.name != data['name']:
                position.name = data['name']
                position.save()
            if position.type_code != data['category_code']:
                position.type_code = data['category_code']
                position.save()
            if has_parent_codifier:
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
            if has_parent_codifier:
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