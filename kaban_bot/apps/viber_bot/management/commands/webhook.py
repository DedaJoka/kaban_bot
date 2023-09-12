import requests
import json

from ... import config
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = 'Команда для встановлення або видалення webhook'

    def add_arguments(self, parser):
        parser.add_argument('--url', type=str, help='Аргумент для передачі посилання webhook')

    def handle(self, *args, **options):
        url = options['url']
        print(f"Запустили команду webhook")

        headers = {'X-Viber-Auth-Token': config.TOKEN}
        hook = 'https://chatapi.viber.com/pa/set_webhook'

        if url:
            print(f'Встановлюємо webhook: {url}')
            post_data = dict(url=url)
        else:
            print(f'Видаляємо webhook')
            post_data = dict(url="")

        r = requests.post(hook, json.dumps(post_data), headers=headers)

        print(json.dumps(post_data))
        print(r.json())
        if r.json()['status'] == 0 and r.json()['status_message'] == 'ok':
            if url:
                return 'Webhook успішно встановлений'
            else:
                return 'Webhook видалено'
        elif r.json()['status'] != 0:
            return "Помилка"
        else:
            return "Щось взагалі не те!"