from viberbot.api.messages import TextMessage

from ...models import ViberUser, Service, ServiceRequest
from ... import config, keyboards
from viberbot import BotConfiguration, Api
from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    help = 'Команда для тестування'

    def handle(self, *args, **options):
        print(f"Запустили команду test")

        bot_configuration = BotConfiguration(
            name=config.NAME,
            avatar=config.AVATAR,
            auth_token=config.TOKEN
        )
        viber = Api(bot_configuration)

        servicerequests = ServiceRequest.objects.filter(status_code=4)

        for servicerequest in servicerequests:

            executors = ViberUser.objects.filter(executor=True, position=servicerequest.position, service=servicerequest.service)

            for executor in executors:
                servicerequest.executors.add(executor)
                keyboard = keyboards.start_menu(executor)
                response_message = TextMessage(
                    text=f'Вам доступна нова заявка для обробки.',
                    keyboard=keyboard,
                    min_api_version=6)
                viber.send_messages(executor.viber_id, [response_message])
