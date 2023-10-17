import json
import re
import geocoder
import os
import base64

from django.db.models import Q
from django.db import transaction
from django.http import HttpResponseBadRequest, HttpResponse
from rest_framework import serializers
from viberbot.api.messages import TextMessage, PictureMessage
from datetime import date, datetime, timedelta
from . import config, keyboards
from .models import ViberUser, Service, Position, ServiceRequest, UploadedFile
from rabbitmq.models import RabbitPackage
from rabbitmq.management.commands.package_creator import CustomCreate
from viberbot import BotConfiguration, Api
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

# Create your views here.
bot_configuration = BotConfiguration(
    name=config.NAME,
    avatar=config.AVATAR,
    auth_token=config.TOKEN
)
# viber = Api(bot_configuration)
from kaban_bot.apps.custom_api import CustomApi
viber = CustomApi(bot_configuration)


@csrf_exempt
def incoming(request):
    # Отримуємо тіло запиту
    request_body = request.body
    if not request_body:
        # Якщо тіло порожнє - повертаємо помилку
        return HttpResponseBadRequest('Пусте тіло запиту')

    # Декодуємо тіло запиту з JSON в python dict
    request_dict = json.loads(request.body.decode('utf-8'))
    event = request_dict['event']

    # Обробка івентів
    if (event == 'webhook' or event == 'unsubscribed' or event == 'delivered' or event == 'seen'):
        return HttpResponse(status=200)
    elif event == 'subscribed':
        conversation_started(request_dict)
        return HttpResponse(status=200)
    elif event == 'conversation_started':
        conversation_started(request_dict)
        return HttpResponse(status=200)
    elif event == 'message':
        message(request_dict)
        return HttpResponse(status=200)
    else:
        print(f'Undeclared event: {event}')
        return HttpResponseBadRequest(f'Undeclared event: {event}')


# Функція обробки event == 'message'
def message(request_dict):
    # Отримуємо інформацію
    message_type = request_dict['message']['type']
    message_text = request_dict['message']['text']
    viber_id = request_dict['sender']['id']
    viber_user = ViberUser.objects.get(viber_id=viber_id)

    if viber_user.menu == 'phone_number':
        message_text = 'phone_number::' + message_text

    print(f'\n\nmessage_type = {message_type}\nmessage_text = {message_text}\n\n')

    if message_type == 'text':
        if viber_user.menu == 'registration':
            save_menu(viber_user, message_text)
            registration(message_text, viber_user)
        # Проверка номера телефона и требование его
        elif not viber_user.phone_number and not re.match(r'^phone_number::', message_text):
            save_menu(viber_user, "phone_number")
            keyboard = keyboards.phone_number()
            response_message = TextMessage(
                text="Для продовження необхідно пройти авторизацію. Для цього поділіться номером телефону, котрий прив'язаний до вайберу, або введіть Ваш контактний номер телефону\nФормат: +380ХХХХХХХХХ або 0ХХХХХХХХХ",
                keyboard=keyboard,
                min_api_version=6)
            viber.send_messages(viber_user.viber_id, [response_message])
        elif re.match(r'^phone_number::\+380\d{9}$', message_text):
            phone_number = message_text.split('::')[1]
            viber_user_phone_number(viber_user, phone_number)
        elif re.match(r'^phone_number::0\d{9}$', message_text):
            phone_number = "+38" + message_text.split('::')[1]
            viber_user_phone_number(viber_user, phone_number)
        elif re.match(r'^phone_number::\d{9}$', message_text):
            phone_number = "+380" + message_text.split('::')[1]
            viber_user_phone_number(viber_user, phone_number)
        elif re.match(r'^phone_number::\+380\d{9}::(?:yes|no)$', message_text):
            split_message_text = message_text.split('::')
            if split_message_text[2] == 'yes':
                viber_user.phone_number = split_message_text[1]
                viber_user.save()
                save_menu(viber_user, 'start')
                keyboard = keyboards.start_menu(viber_user)
                response_message = TextMessage(
                    text=f'Дякуємо, Ваш номер збережено. Ви можете його змінити в будь-який момент в налаштуваннях.\nДля продовження скористайтесь контекстним меню.',
                    keyboard=keyboard,
                    min_api_version=6)
                viber.send_messages(viber_user.viber_id, [response_message])

                # Відправляємо користувача до ЦРМ
                ViberUserToRabbitMQ(viber_user, 'INSERT')

            elif split_message_text[2] == 'no':
                save_menu(viber_user, "phone_number")
                keyboard = keyboards.phone_number()
                response_message = TextMessage(
                    text="Для продовження необхідно пройти авторизацію. Для цього поділіться номером телефону, котрий прив'язаний до вайберу, або введіть Ваш контактний номер телефону\nФормат: +380ХХХХХХХХХ або 0ХХХХХХХХХ",
                    keyboard=keyboard,
                    min_api_version=6)
                viber.send_messages(viber_user.viber_id, [response_message])
        elif re.match(r'^phone_number::', message_text):
            save_menu(viber_user, "phone_number")
            keyboard = keyboards.phone_number()
            response_message = TextMessage(
                text="Невірний формат!\nФормат: +380ХХХХХХХХХ або 0ХХХХХХХХХ",
                keyboard=keyboard,
                min_api_version=6)
            viber.send_messages(viber_user.viber_id, [response_message])
        elif message_text == 'change_phone_number':
            keyboard = keyboards.yes_no('change_phone_number')
            response_message = TextMessage(
                text=f'Ваш поточний номер телефону: {viber_user.phone_number}\nВи впевнені що хочете його змінити?',
                keyboard=keyboard,
                min_api_version=6)
            viber.send_messages(viber_user.viber_id, [response_message])
        elif re.match(r'^change_phone_number::(?:yes|no)$', message_text):
            split_message_text = message_text.split('::')
            if split_message_text[1] == 'yes':
                save_menu(viber_user, "phone_number")
                keyboard = keyboards.phone_number()
                response_message = TextMessage(
                    text="Надайте новий номер телефону. Для цього поділіться номером телефону, котрий прив'язаний до вайберу, або введіть Ваш контактний номер телефону\nФормат: +380ХХХХХХХХХ або 0ХХХХХХХХХ",
                    keyboard=keyboard,
                    min_api_version=6)
                viber.send_messages(viber_user.viber_id, [response_message])
            elif split_message_text[1] == 'no':
                setting(viber_user)
        elif message_text == 'start':
            save_menu(viber_user, message_text)
            keyboard = keyboards.start_menu(viber_user)
            response_message = TextMessage(
                text=f'Для продовження скористайтесь контекстним меню.',
                keyboard=keyboard,
                min_api_version=6)

            import time
            start = time.time()

            viber.send_messages(viber_user.viber_id, [response_message])

            print('!ELAPSED TIME!!! START', time.time() - start)

        elif message_text == 'setting':
            save_menu(viber_user, message_text)
            setting(viber_user)
        elif message_text == 'service':
            save_menu(viber_user, message_text)
            service_0(viber_user)
        elif re.match(r'^service::\d{1,2}$', message_text):
            save_menu(viber_user, message_text)
            service_1(viber_user, message_text.split('::')[1])
        elif re.match(r'^service::\d{1,2}::location::\d{1,8}::(?:yes|no)$', message_text):
            save_menu(viber_user, message_text)
            verification_service_request(viber_user)
        elif message_text == 'my_requests':
            save_menu(viber_user, message_text)
            my_requests(viber_user)
        elif re.match(r'^my_request::VSR-\d{1,4}-\d{1,2}-\d{1,2}-\d{1,6}$', message_text):
            service_number = message_text.split('::')[1]
            service_request = ServiceRequest.objects.get(number=service_number)
            my_request_handler(viber_user, service_request)
        elif re.match(r'^my_request::VSR-\d{1,4}-\d{1,2}-\d{1,2}-\d{1,6}::cancel$', message_text):
            service_number = message_text.split('::')[1]
            service_request = ServiceRequest.objects.get(number=service_number)
            my_request_cancel(viber_user, service_request)
        elif re.match(r'^my_request::VSR-\d{1,4}-\d{1,2}-\d{1,2}-\d{1,6}::cancel::(?:yes|no)$', message_text):
            split_message_text = message_text.split('::')
            service_number = split_message_text[1]
            service_request = ServiceRequest.objects.get(number=service_number)
            my_request_cancel_handler(viber_user, service_request, split_message_text[3])
        elif re.match(r'^my_request::VSR-\d{1,4}-\d{1,2}-\d{1,2}-\d{1,6}::reject$', message_text):
            service_number = message_text.split('::')[1]
            service_request = ServiceRequest.objects.get(number=service_number)
            my_request_reject(viber_user, service_request)
        elif re.match(r'^my_request::VSR-\d{1,4}-\d{1,2}-\d{1,2}-\d{1,6}::confirm$', message_text):
            service_number = message_text.split('::')[1]
            service_request = ServiceRequest.objects.get(number=service_number)
            my_request_confirm(viber_user, service_request)
        elif re.match(r'^my_request::VSR-\d{1,4}-\d{1,2}-\d{1,2}-\d{1,6}::problem$', message_text):
            service_number = message_text.split('::')[1]
            service_request = ServiceRequest.objects.get(number=service_number)
            my_request_problem(viber_user, service_request)
        elif re.match(r'^my_request::VSR-\d{1,4}-\d{1,2}-\d{1,2}-\d{1,6}::assessment$', message_text):
            service_number = message_text.split('::')[1]
            service_request = ServiceRequest.objects.get(number=service_number)
            my_request_assessment(viber_user, service_request)
        elif re.match(r'^my_request::VSR-\d{1,4}-\d{1,2}-\d{1,2}-\d{1,6}::assessment::\d{1}$', message_text):
            split_message_text = message_text.split('::')
            service_request = ServiceRequest.objects.get(number=split_message_text[1])
            my_request_assessment_handler(viber_user, service_request, split_message_text[3])
        elif re.match(r'^service::\d{1,3}::location$', message_text):
            service = Service.objects.get(id=message_text.split('::')[1])
            keyboard = keyboards.service_1(service.parent.id)
            response_message = TextMessage(
                text=f'Нажаль надання локації доступне лише з телефону. Подайте заявку з телефону.',
                keyboard=keyboard[1],
                min_api_version=6)
            viber.send_messages(viber_user.viber_id, [response_message])
        # Майстр
        elif message_text == 'master_registration':
            save_menu(viber_user, message_text)
            keyboard = keyboards.master_registration(viber_id)
            response_message = TextMessage(
                text=f'Для того щоб стати майстром Вам необхідно буде надати більш детальну інформацію про себе та свої навички. Чи походжуєтесь на обробку інформації?',
                keyboard=keyboard,
                min_api_version=6)
            viber.send_messages(viber_user.viber_id, [response_message])
        elif message_text == 'master_requests':
            save_menu(viber_user, message_text)
            master_requests(viber_user)
        elif message_text == 'master_service_requests_available':
            save_menu(viber_user, message_text)
            master_service_requests_available(viber_user)
        elif re.match(r'^master_service_request_available::VSR-\d{1,4}-\d{1,2}-\d{1,2}-\d{1,6}$', message_text):
            service_number = message_text.split('::')[1]
            service_request = ServiceRequest.objects.get(number=service_number)
            master_service_request_available(viber_user, service_request)
        elif re.match(r'^master_service_request::VSR-\d{1,4}-\d{1,2}-\d{1,2}-\d{1,6}::respond$', message_text):
            service_number = message_text.split('::')[1]
            service_request = ServiceRequest.objects.get(number=service_number)
            master_service_request_respond(viber_user, service_request)
        elif message_text == 'master_service_requests_confirmed':
            save_menu(viber_user, message_text)
            master_service_requests_confirmed(viber_user)
        elif re.match(r'^master_service_request_confirmed::VSR-\d{1,4}-\d{1,2}-\d{1,2}-\d{1,6}$', message_text):
            service_number = message_text.split('::')[1]
            service_request = ServiceRequest.objects.get(number=service_number)
            master_service_request_confirmed(viber_user, service_request)
        elif re.match(r'^master_service_request::VSR-\d{1,4}-\d{1,2}-\d{1,2}-\d{1,6}::done$', message_text):
            service_number = message_text.split('::')[1]
            service_request = ServiceRequest.objects.get(number=service_number)
            master_service_request_done(viber_user, service_request)
        elif re.match(r'^master_service_request::VSR-\d{1,4}-\d{1,2}-\d{1,2}-\d{1,6}::done::(?:yes|no)$', message_text):
            split_message_text = message_text.split('::')
            service_request = ServiceRequest.objects.get(number=split_message_text[1])
            master_service_request_done_handler(viber_user, service_request, split_message_text[3])
        elif re.match(r'^master_service_request::VSR-\d{1,4}-\d{1,2}-\d{1,2}-\d{1,6}::problem$', message_text):
            service_number = message_text.split('::')[1]
            service_request = ServiceRequest.objects.get(number=service_number)
            master_service_request_problem(viber_user, service_request)


        # Адмін
        elif message_text == 'test':
            service_request = ServiceRequest.objects.get(number='VSR-2023-09-21-1')
            ServiceRequestToRabbitMQ(service_request, 'INSERT')
    elif message_type == 'location':
        if re.match(r'^service::\d{1,2}::location$', message_text):
            lat = request_dict['message']['location']['lat']
            lon = request_dict['message']['location']['lon']
            address = request_dict['message']['location']['address']
            create_service_request(viber_user, message_text, lat, lon, address)
    elif message_type == "contact":
        phone_number = "+" + request_dict['message']['contact']['phone_number']
        viber_user_phone_number(viber_user, phone_number)


# Функція обробки event == 'conversation_started' and 'subscribed'
def conversation_started(request_dict):
    viber_id = request_dict['user']['id']

    # Перевірка наявності користувача у базі
    viber_user = ViberUser.objects.filter(viber_id=viber_id).exists()
    if not viber_user:
        viber_user = ViberUser(viber_id=viber_id, menu='registration')
        viber_user.save()
        response_message = TextMessage(
            text='Вітаємо Вас!\nДаний бот допоможе принести у Вашу оселю ще більше тепла та затишку. Всі майстри кваліфіковані, мають необхідні сертифікації та індивідуальний підхід до кожного клієнта. Ви зможете замовити будь-яку існуючу послугу без зайвих турбот та всього у пару кліків. Вперед до змін!',
            min_api_version=4)
        viber.send_messages(viber_id, [response_message])
        response_message = TextMessage(
            text='Для проходження реєстрації введіть Ваше прізвище, ім’я, по батькові у називному відмінку.',
            min_api_version=4)
        viber.send_messages(viber_id, [response_message])
    else:
        viber_user = ViberUser.objects.get(viber_id=viber_id)
        keyboard = keyboards.start_menu(viber_user)
        response_message = TextMessage(
            text=f'З поверненням {viber_user.full_name}!\nДаний бот допоможе принести у Вашу оселю ще більше тепла та затишку. Всі майстри кваліфіковані, мають необхідні сертифікації та індивідуальний підхід до кожного клієнта. Ви зможете замовити будь-яку існуючу послугу без зайвих турбот та всього у пару кліків. Вперед до змін!',
            keyboard=keyboard,
            min_api_version=6)
        viber.send_messages(viber_id, [response_message])

        # Відправляємо користувача до ЦРМ
        ViberUserToRabbitMQ(viber_user, 'UPDATE')


def registration(message_text, viber_user):
    viber_user.full_name = message_text
    viber_user.save()
    save_menu(viber_user, "phone_number")
    keyboard = keyboards.phone_number()
    response_message = TextMessage(
        text="Для продовження необхідно пройти авторизацію. Для цього поділіться номером телефону, котрий прив'язаний до вайберу, або введіть Ваш контактний номер телефону\nФормат: +380ХХХХХХХХХ або 0ХХХХХХХХХ",
        keyboard=keyboard,
        min_api_version=6)
    viber.send_messages(viber_user.viber_id, [response_message])


# ╔╗╔══╗─╔══╗╔╗╔╗╔═══╗╔╗╔╗╔════╗
# ║║║╔═╝─║╔╗║║║║║║╔══╝║║║║╚═╗╔═╝
# ║╚╝║───║║║║║║║║║╚══╗║╚╝║──║║──
# ║╔╗║───║║║║║║╔║║╔══╝║╔╗║──║║──
# ║║║╚═╗╔╝║║║║╚╝║║╚══╗║║║║──║║──
# ╚╝╚══╝╚═╝╚╝╚══╝╚═══╝╚╝╚╝──╚╝──


# Мої заявки
def my_requests(viber_user):
    fourteen_days_ago = datetime.now() - timedelta(days=14)
    excluded_status_codes = [3, 7, 8, 9]
    service_requests = ServiceRequest.objects.filter(
        Q(customer=viber_user) &
        ~Q(status_code__in=excluded_status_codes) &
        Q(modifiedon__gte=fourteen_days_ago)
    )
    text = ""
    if not service_requests:
        text = "Від Вас заявок не знайдено"
        keyboard = keyboards.service_0()
    else:
        keyboard = keyboards.my_requests(viber_user)
    for request in service_requests:
        status_text = request.get_status_code_display()
        request_text = f'Номер заявки: {request.number}\nПослуга: {request.service}\nАдреса: {request.address}\nСтатус заявки: {status_text}\n\n'
        text = text + request_text

    response_message = TextMessage(
        text=text,
        keyboard=keyboard,
        min_api_version=6)
    viber.send_messages(viber_user.viber_id, [response_message])


def my_request_handler(viber_user, service_request):
    if service_request.status_code == '4':
        keyboard = keyboards.my_request_cancel(service_request)
        response_message = TextMessage(
            text=f'На цю заявку ще не відгукнувся жодний майстер',
            keyboard=keyboard,
            min_api_version=6)
        viber.send_messages(viber_user.viber_id, [response_message])
    elif service_request.status_code == '5':
        executor = service_request.executors.first()
        keyboard = keyboards.my_request_confirmation(service_request)
        response_message = TextMessage(
            text=f'На Вашу заявку відгукнувся майстр {executor.full_name}\nРейтинг майстра: {executor.executor_rating}',
            keyboard=keyboard,
            min_api_version=6)
        viber.send_messages(viber_user.viber_id, [response_message])
    elif service_request.status_code == '6':
        keyboard = keyboards.my_request_cancel(service_request)
        response_message = TextMessage(
            text=f'Ваша заявка в роботі. Очікуйте дзвінка від майстра.',
            keyboard=keyboard,
            min_api_version=6)
        viber.send_messages(viber_user.viber_id, [response_message])
    elif service_request.status_code == '2':
        keyboard = keyboards.my_request_done(service_request)
        response_message = TextMessage(
            text=f'Майстр позначив Вашу заявку як виконану. Ви можете оцінити майстра або повідомити про проблему.',
            keyboard=keyboard,
            min_api_version=6)
        viber.send_messages(viber_user.viber_id, [response_message])


def my_request_cancel(viber_user, service_request):
    keyboard = keyboards.yes_no(f'my_request::{service_request.number}::cancel')
    response_message = TextMessage(
        text=f'Ви впевнені що хочете скасувати заявку {service_request.number}?',
        keyboard=keyboard,
        min_api_version=6)
    viber.send_messages(viber_user.viber_id, [response_message])


def my_request_cancel_handler(viber_user, service_request, response):
    executors_count = service_request.executors.count()

    if response == "yes":
        # Переводимо заявку у статус "Скасованої"
        service_request.status_code = 3
        service_request.save()

        # Відправляемо повідомлення Замовнику
        keyboard = keyboards.my_requests(viber_user)
        response_message = TextMessage(
            text=f'Ваша заявка {service_request.number} - скасована',
            keyboard=keyboard,
            min_api_version=6)
        viber.send_messages(viber_user.viber_id, [response_message])

        if service_request.status_code in ("5", "6"):
            # Відправляемо повідомлення Виконавцю
            executor = service_request.executors.first()
            keyboard = keyboards.start_menu(executor)
            response_message = TextMessage(
                text=f'Замовник {service_request.customer} відмінив заявку {service_request.number}',
                keyboard=keyboard,
                min_api_version=6)
            viber.send_messages(executor.viber_id, [response_message])

    elif response == "no":
        my_requests(viber_user)


def my_request_reject(viber_user, service_request):
    # Відправляемо повідомлення Виконавцю
    executor = service_request.executors.first()
    keyboard = keyboards.start_menu(executor)
    response_message = TextMessage(
        text=f'Замовник {service_request.customer} відхилив заявку {service_request.number}',
        keyboard=keyboard,
        min_api_version=6)
    viber.send_messages(executor.viber_id, [response_message])

    with transaction.atomic():
        # Додаємо відхилених виконавців
        rejected_executors = service_request.executors.all()
        for executor in rejected_executors:
            service_request.rejected_executors.add(executor)

        # Список всіх виконавців, котрі підходять під заявку
        executors = ViberUser.objects.filter(
            executor=True,
            position=service_request.position,
            service=service_request.service,
            status_code=0
        ).exclude(
            pk__in=service_request.rejected_executors.values_list('pk', flat=True)
        )

        # Очистка всіх виконавців
        service_request.executors.clear()
        # Додаємо підходящих виконавців
        service_request.executors.set(executors)
        # Статус "Очікування майстра"
        service_request.status_code = 4
        # Зберігаємо дані
        service_request.save()

    # Відправляємо повідомлення Майстрам
    for executor in executors:
        keyboard = keyboards.start_menu(executor)
        response_message = TextMessage(
            text=f'Вам доступна нова заявка для обробки.',
            keyboard=keyboard,
            min_api_version=6)
        viber.send_messages(executor.viber_id, [response_message])

    # Відправляємо повідомлення клієнту
    keyboard = keyboards.service_0()
    response_message = TextMessage(
        text=f'Майстер відхилений. Заявка розіслана іншим майстрам. Очікуємо відповіть від них. Після того, як відповіть буде отримана, Ви отримаєте повідомлення.',
        keyboard=keyboard,
        min_api_version=6)
    viber.send_messages(viber_user.viber_id, [response_message])


def my_request_confirm(viber_user, service_request):
    # Переводимо заявку у статус "Очікування майстра"
    service_request.status_code = 6
    service_request.save()

    # Відправляемо повідомлення Виконавцю
    executor = service_request.executors.first()
    keyboard = keyboards.start_menu(executor)
    response_message = TextMessage(
        text=f'Замовник підтвердив заявку, на яку Ви відгукнулись\nНомер заявки: {service_request.number}',
        keyboard=keyboard,
        min_api_version=6)
    viber.send_messages(executor.viber_id, [response_message])

    # Відправляємо повідомлення клієнту
    keyboard = keyboards.service_0()
    response_message = TextMessage(
        text=f"Заявка успішно підтверджена. Майстер зв'яжеться з вами найближчим часом",
        keyboard=keyboard,
        min_api_version=6)
    viber.send_messages(viber_user.viber_id, [response_message])


def my_request_problem(viber_user, service_request):
    with transaction.atomic():
        service_request.status_code = 8
        service_request.save()

    keyboard = keyboards.my_requests(viber_user)
    response_message = TextMessage(
        text=f'Дякую. Заявка {service_request.number} передана до відділу підтримки, незабаром з вами звяжуться для уточнення деталей',
        keyboard=keyboard,
        min_api_version=6)
    viber.send_messages(viber_user.viber_id, [response_message])


def my_request_assessment(viber_user, service_request):
    keyboard = keyboards.zero_to_five(f'my_request::{service_request.number}::assessment')
    response_message = TextMessage(
        text=f'Оберіть оцінку від 1 до 5, де 1 - це найнижча оцінка, а 5 - найвища',
        keyboard=keyboard,
        min_api_version=6)
    viber.send_messages(viber_user.viber_id, [response_message])


def my_request_assessment_handler(viber_user, service_request, response):
    with transaction.atomic():
        service_request.status_code = 9
        service_request.save()

    keyboard = keyboards.start_menu(viber_user)
    response_message = TextMessage(
        text=f'Дякуємо за Вашу оцінку.\nДля продовження скористайтесь контекстним меню.',
        keyboard=keyboard,
        min_api_version=6)
    viber.send_messages(viber_user.viber_id, [response_message])

    executor = service_request.executors.first()
    body = {
        'viber_id': executor.viber_id,
        'type_assessment': "executor",
        'assessment': response,
    }
    new_package = CustomCreate.create_package(service_request.id, "INSERT", 'application/json', 'kvb::assessment', json.dumps(body))


# Послуги
def service_0(viber_user):
    keyboard = keyboards.service_0()
    response_message = TextMessage(
        text=f'Оберіть послугу',
        keyboard=keyboard,
        min_api_version=6)
    viber.send_messages(viber_user.viber_id, [response_message])


def service_1(viber_user, service_id):
    keyboard = keyboards.service_1(service_id)
    response_message = TextMessage(
        text=keyboard[0],
        keyboard=keyboard[1],
        min_api_version=6)
    viber.send_messages(viber_user.viber_id, [response_message])


def create_service_request(viber_user, message_text, lat, lon, address):
    print(message_text)
    location = geocoder.osm([lat, lon], method='reverse')

    # location_info = location.raw
    # print(location_info)

    city = location.city
    town = location.town
    code_ua = location.raw['address']['ISO3166-2-lvl4'].replace("-", "")

    # display_name = location.raw['display_name']

    split_address = address.split(", ")
    display_address = ''
    if len(split_address) >= 5:
        display_address = split_address[-4] + ', '
    display_address = display_address + location.raw['display_name']
    # print(display_address)

    if city:
        position = Position.objects.filter(name=city, codifier__startswith=code_ua)
    elif town:
        position = Position.objects.filter(name=city, codifier__startswith=code_ua)

    if position:
        viber_user.address = display_address
        viber_user.save()
        service = Service.objects.get(id=message_text.split('::')[1])
        keyboard = keyboards.yes_no(message_text + '::' + str(position[0].id))
        response_message = TextMessage(
            text=f'Ви підтверджуєте заявку?\nПослуга: {service.name}\nМісце проведення: {display_address}',
            keyboard=keyboard,
            min_api_version=6)
        viber.send_messages(viber_user.viber_id, [response_message])
    else:
        print("НЕ НАШЛИ РАСПОЛОЖЕНИЕ")


# "Підтвердження" на створення заявку
def verification_service_request(viber_user):
    service_id = viber_user.menu.split('::')[1]
    position_id = viber_user.menu.split('::')[3]
    verification = viber_user.menu.split('::')[4]
    if verification == "no":
        service_1(viber_user, service_id)
    elif verification == "yes":
        today = date.today()
        start_date = datetime.combine(today, datetime.min.time())
        end_date = datetime.combine(today, datetime.max.time())

        service_request_created_today = ServiceRequest.objects.filter(createdon__range=(start_date, end_date))
        count_service_request_created_today = service_request_created_today.count()
        formatted_today = today.strftime("%Y-%m-%d-")

        number = 'VSR-' + formatted_today + str(count_service_request_created_today + 1)

        position = Position.objects.get(id=position_id)
        service = Service.objects.get(id=service_id)
        service_request = ServiceRequest(number=number, customer=viber_user, address=viber_user.address,
                                         position=position, service=service, status_code=4)
        service_request.save()
        # ServiceRequestToRabbitMQ(service_request, 'INSERT')

        keyboard = keyboards.start()
        response_message = TextMessage(text=f'Ваша заявка створена!\nНомер заявки: {number}',
                                       keyboard=keyboard,
                                       min_api_version=6)
        viber.send_messages(viber_user.viber_id, [response_message])
        service_request_handler(service_request)


# Функція яка додає виконавців і оповіщує їх про створення нової заяки
def service_request_handler(service_request):
    executors = ViberUser.objects.filter(executor=True, position=service_request.position,
                                         service=service_request.service)

    for executor in executors:
        service_request.executors.add(executor)
        keyboard = keyboards.start_menu(executor)
        response_message = TextMessage(
            text=f'Вам доступна нова заявка для обробки.',
            keyboard=keyboard,
            min_api_version=6)
        viber.send_messages(executor.viber_id, [response_message])


# ╔╗──╔╗╔══╗╔══╗╔════╗╔═══╗╔═══╗
# ║║──║║║╔╗║║╔═╝╚═╗╔═╝║╔══╝║╔═╗║
# ║╚╗╔╝║║╚╝║║║────║║──║╚══╗║╚═╝║
# ║╔╗╔╗║║╔╗║║║────║║──║╔══╝║╔══╝
# ║║╚╝║║║║║║║╚═╗──║║──║╚══╗║║───
# ╚╝──╚╝╚╝╚╝╚══╝──╚╝──╚═══╝╚╝───


# Кнопка "Заявки" у майстрів
def master_requests(viber_user):
    text = "Ваші заявки"
    keyboard = keyboards.master_requests(viber_user)
    response_message = TextMessage(
        text=text,
        keyboard=keyboard,
        min_api_version=6)
    viber.send_messages(viber_user.viber_id, [response_message])


# Заявки для майстрів
def master_service_requests_available(viber_user):
    service_requests = ServiceRequest.objects.filter(executors=viber_user, status_code=4)
    text = ""
    for request in service_requests:
        status_text = request.get_status_code_display()
        request_text = f'Номер заявки: {request.number}\nПослуга: {request.service}\nНаселений пункт: {request.position}\n\n'
        text = text + request_text

    if service_requests.exists():
        keyboard = keyboards.master_service_requests("available", service_requests)
        response_message = TextMessage(
            text=text,
            keyboard=keyboard,
            min_api_version=6)
        viber.send_messages(viber_user.viber_id, [response_message])
    else:
        keyboard = keyboards.master_requests(viber_user)
        response_message = TextMessage(
            text="Заявки відсутні",
            keyboard=keyboard,
            min_api_version=6)
        viber.send_messages(viber_user.viber_id, [response_message])


def master_service_request_available(viber_user, service_request):
    keyboard = keyboards.master_service_request('available', service_request)
    text = f'Номер заявки: {service_request.number}\nПослуга: {service_request.service}\nНаселений пункт: {service_request.position}\nЗаявник: {service_request.customer.full_name}\nРейтинг замовника: {service_request.customer.customer_rating}\n'
    response_message = TextMessage(
        text=text,
        keyboard=keyboard,
        min_api_version=6)
    viber.send_messages(viber_user.viber_id, [response_message])


def master_service_request_respond(viber_user, service_request):
    with transaction.atomic():
        # Відвязуємо всіх виконавців
        service_request.executors.clear()

        # Привязуємо того, хто відгукнувся
        service_request.executors.add(viber_user)

        # Статус "Очікування підтвердження"
        service_request.status_code = 5
        service_request.save()

    # Відправляємо повідомлення майстру
    keyboard = keyboards.start_menu(viber_user)
    text = f'Ви відгунулися на заявку. Коли замовник підтвердить заявку, вам прийде повідомлення. Для подальшої роботи скористайтесь контекстним меню'
    response_message = TextMessage(
        text=text,
        keyboard=keyboard,
        min_api_version=6)
    viber.send_messages(viber_user.viber_id, [response_message])

    # Відправляємо повідомлення замовнику і просимо його перейти в мої заявки та підтвердити
    keyboard = keyboards.start_menu(service_request.customer)
    text = f'На вашу заявку відгукнувся майстер. Перейдіть до послуг, оберіть мої заявки та підтвердіть майстра!'
    response_message = TextMessage(
        text=text,
        keyboard=keyboard,
        min_api_version=6)
    viber.send_messages(service_request.customer.viber_id, [response_message])


def master_service_requests_confirmed(viber_user):
    service_requests = ServiceRequest.objects.filter(executors=viber_user, status_code=6)
    text = ""
    for request in service_requests:
        status_text = request.get_status_code_display()
        request_text = f'Номер заявки: {request.number}\nПослуга: {request.service}\nНаселений пункт: {request.position}\n\n'
        text = text + request_text

    if service_requests.exists():
        keyboard = keyboards.master_service_requests('confirmed', service_requests)
        response_message = TextMessage(
            text=text,
            keyboard=keyboard,
            min_api_version=6)
        viber.send_messages(viber_user.viber_id, [response_message])
    else:
        keyboard = keyboards.master_requests(viber_user)
        response_message = TextMessage(
            text="Заявки відсутні",
            keyboard=keyboard,
            min_api_version=6)
        viber.send_messages(viber_user.viber_id, [response_message])


def master_service_request_confirmed(viber_user, service_request):
    keyboard = keyboards.master_service_request('confirmed', service_request)
    text = f'Номер заявки: {service_request.number}\nПослуга: {service_request.service}\nНаселений пункт: {service_request.position}\nАдреса: {service_request.address}\nЗаявник: {service_request.customer.full_name}\nНомер телефона: {service_request.customer.phone_number}\nРейтинг замовника: {service_request.customer.customer_rating}\n'
    response_message = TextMessage(
        text=text,
        keyboard=keyboard,
        min_api_version=6)
    viber.send_messages(viber_user.viber_id, [response_message])


def master_service_request_done(viber_user, service_request):
    keyboard = keyboards.yes_no(f'master_service_request::{service_request.number}::done')
    response_message = TextMessage(
        text=f'Ви хочете позначити що заявка {service_request.number} виконана?',
        keyboard=keyboard,
        min_api_version=6)
    viber.send_messages(viber_user.viber_id, [response_message])


def master_service_request_done_handler(viber_user, service_request, response):
    if response == 'yes':
        with transaction.atomic():
            # Статус "Виконана"
            service_request.modifiedon = datetime.now()
            service_request.status_code = 2
            service_request.save()

        # Відправляємо повідомлення майстру
        keyboard = keyboards.start_menu(viber_user)
        response_message = TextMessage(
            text=f'Ви підтвердили виконання заявки {service_request.number}',
            keyboard=keyboard,
            min_api_version=6)
        viber.send_messages(viber_user.viber_id, [response_message])

        # Відправляємо повідомлення замовнику і просимо його перейти в мої заявки та підтвердити
        keyboard = keyboards.start_menu(service_request.customer)
        response_message = TextMessage(
            text=f'Майстер підтвердив виконання Вашої заявки {service_request.number}',
            keyboard=keyboard,
            min_api_version=6)
        viber.send_messages(service_request.customer.viber_id, [response_message])
    elif response == 'no':
        # Відправляємо повідомлення майстру
        keyboard = keyboards.master_service_request('confirmed', service_request)
        response_message = TextMessage(
            text=f'Обрана заявка {service_request.number}',
            keyboard=keyboard,
            min_api_version=6)
        viber.send_messages(viber_user.viber_id, [response_message])


def master_service_request_problem(viber_user, service_request):
    with transaction.atomic():
        # Статус "Виконана"
        service_request.status_code = 7
        service_request.save()

    keyboard = keyboards.master_requests(viber_user)
    response_message = TextMessage(
        text=f'Дякую. Заявка {service_request.number} передана до відділу підтримки, незабаром з вами звяжуться для уточнення деталей',
        keyboard=keyboard,
        min_api_version=6)
    viber.send_messages(viber_user.viber_id, [response_message])


# "Погодження" на реєстрацію майстра
def master_registration_page_view(request, viber_id):
    services = Service.objects.filter()
    viber_user = ViberUser.objects.get(viber_id=viber_id)
    # services = json.dumps(nodeToJSON(Service, None), ensure_ascii=False)
    # position = json.dumps(nodeToJSON(Position, None), ensure_ascii=False)
    # return render(request, 'master_registration_page.html', {'user': viber_user, 'services': services, 'position': position})
    return render(request, 'master_registration_page.html',
                  {'viber_user': viber_user, 'services': services})


# Функція обробки submit реєстрації майстра
def master_registration_page_submit(request):
    if request.method == 'POST':
        form_data = request.POST
        form_file = request.FILES
        viber_user = ViberUser.objects.get(viber_id=form_data["viber_id"])

        body = {
            'viber_id': form_data["viber_id"],
            'services': [],
            'certificates': []
        }

        # Перевірка і апдейт full_name
        if viber_user.full_name != form_data["full_name"]:
            viber_user.full_name = form_data["full_name"]
            viber_user.save()

        # Очиcтка послуг
        viber_user.service.clear()

        # DATA
        for key, value in form_data.items():
            # Послуги
            if key.startswith("service::"):
                service_id = key.split("::")[1]
                service = Service.objects.get(id=service_id)
                if service not in viber_user.service.all():
                    viber_user.service.add(service)

                service = {
                    'service_id': service_id
                }
                body['services'].append(service)
            # щось інше
            else:
                print(f'{key} - {value}')

        # FILES
        for key, value in form_file.items():
            manufacturer = key.split("::")[1]
            file_name = f'{form_data["viber_id"]}_{manufacturer}_{value.name}'
            file_content_type = value.content_type
            file_base64 = CustomCreate.encode_file_to_base64(value)
            certificate = {
                'manufacturer': manufacturer,
                # 'filename': file_name,
                # 'file_content_type': file_content_type,
                'content_base64': f'{file_name}:{file_content_type};base64,{file_base64}'
            }
            body['certificates'].append(certificate)

        json_body = json.dumps(body)

        new_package = CustomCreate.create_package(form_data["viber_id"], 'INSERT', "application/json", 'kvb_master',
                                                  json_body)

        # Перенаправлення на сторінку "дякуємо за реєстрацію"
        return redirect('https://www.google.com.ua/')


# Функція древовидний запис у Json
def nodeToJSON(model_name, id):
    if id:
        objects = model_name.objects.filter(id=id)
    else:
        objects = model_name.objects.filter(parent__isnull=True)
    data = []
    for object in objects:
        node = {}
        node['id'] = object.id
        node['text'] = object.name

        childrens = object.get_children()
        if childrens:
            node['childrens'] = []
            for children in childrens:
                node['childrens'].append(nodeToJSON(model_name, children.id))
        data.append(node)
    return data


def ViberUserToRabbitMQ(viber_user, operation):
    class ViberUserSerializer(serializers.ModelSerializer):
        class Meta:
            model = ViberUser
            fields = ['status_code', 'viber_id', 'full_name', 'phone_number']

    viber_user_serializer = ViberUserSerializer(viber_user)
    viber_user_json_data = viber_user_serializer.data
    json_data = json.dumps(viber_user_json_data, ensure_ascii=False).encode('utf-8')
    decoded_json_data = json_data.decode('utf-8')
    new_package = CustomCreate.create_package(viber_user.viber_id, operation, 'application/json', 'kvb::viber_user',
                                              decoded_json_data)


def ServiceRequestToRabbitMQ(service_request, operation):
    body = {
        'status_code': service_request.status_code,
        'number': service_request.number,
        'customer': service_request.customer.viber_id,
        'address': service_request.address,
        'position': service_request.position.codifier,
        'service': service_request.service.id
    }
    new_package = CustomCreate.create_package(service_request.id, operation, 'application/json', 'kvb::service_request',
                                              json.dumps(body))


def viber_user_phone_number(viber_user, phone_number):
    save_menu(viber_user, f'phone_number::{phone_number}')
    keyboard = keyboards.yes_no(f'phone_number::{phone_number}')
    response_message = TextMessage(
        text=f'Ви підтверджуєте, що номер телефону введено коректно?\n{phone_number}',
        keyboard=keyboard,
        min_api_version=6)
    viber.send_messages(viber_user.viber_id, [response_message])


# Налаштування
def setting(viber_user):
    keyboard = keyboards.setting()
    response_message = TextMessage(
        text=f'Для продовження скористайтесь контекстним меню.',
        keyboard=keyboard,
        min_api_version=6)

    import time
    start = time.time()
    viber.send_messages(viber_user.viber_id, [response_message])
    print('!ELAPSED TIME!!! SETTING', time.time() - start)

# Функція записує меню у вайбер-користувача
def save_menu(viber_user, menu):
    viber_user.menu = menu
    viber_user.save()
