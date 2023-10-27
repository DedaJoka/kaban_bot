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
from django.db.models.functions import Left
from pyuca import Collator

# Create your views here.
bot_configuration = BotConfiguration(
    name=config.NAME,
    avatar=config.AVATAR,
    auth_token=config.TOKEN
)
# viber = Api(bot_configuration)
from kaban_bot.apps.custom_api import CustomApi

viber = CustomApi(bot_configuration)
collator = Collator()


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

    global global_text_message, global_keyboard_message, global_viber_id
    global_text_message = None
    global_keyboard_message = None
    global_viber_id = None

    # Обробка івентів
    if (event == 'webhook' or event == 'unsubscribed' or event == 'delivered' or event == 'seen'):
        return HttpResponse(status=200)
    elif event == 'subscribed' or event == 'conversation_started':
        # начало общения с ботом
        started(request_dict)
        send(request_dict['user']['id'])
        return HttpResponse(status=200)
    elif event == 'message':
        message(request_dict)
        return HttpResponse(status=200)
    else:
        print(f'Undeclared event: {event}')
        return HttpResponseBadRequest(f'Undeclared event: {event}')


def send(viber_user_id):
    if global_text_message:
        response_message = TextMessage(
            text=global_text_message,
            keyboard=global_keyboard_message,
            min_api_version=6)
        viber.send_messages(viber_user_id, [response_message])
        print('отправили сообщение')
    else:
        print(
            f'НЕЗАШЛИ в условие send\n\t\tglobal_text_message - {global_text_message}\n\t\tglobal_viber_id - {global_viber_id}')


# Функція обробки початку спілкування з ботом'
def started(request_dict):
    global global_text_message, global_keyboard_message, global_viber_id

    viber_id = request_dict['user']['id']
    global_viber_id = viber_id

    # Перевірка наявності користувача у базі
    viber_user = ViberUser.objects.filter(viber_id=viber_id).exists()
    if not viber_user:
        viber_user = ViberUser(viber_id=viber_id, menu='registration')
        viber_user.save()
        global_text_message = 'Вітаємо Вас!\nДаний бот допоможе принести у Вашу оселю ще більше тепла та затишку. Всі майстри кваліфіковані, мають необхідні сертифікації та індивідуальний підхід до кожного клієнта. Ви зможете замовити будь-яку існуючу послугу без зайвих турбот та всього у пару кліків. Вперед до змін!\n\nДля проходження реєстрації введіть Ваше прізвище, ім’я, по батькові у називному відмінку.'
    else:
        viber_user = ViberUser.objects.get(viber_id=viber_id)
        viber_user.once = 0
        viber_user.save()
        global_text_message = f'З поверненням {viber_user.full_name}!\nДаний бот допоможе принести у Вашу оселю ще більше тепла та затишку. Всі майстри кваліфіковані, мають необхідні сертифікації та індивідуальний підхід до кожного клієнта. Ви зможете замовити будь-яку існуючу послугу без зайвих турбот та всього у пару кліків. Вперед до змін!'
        global_keyboard_message = keyboards.start_menu(viber_user)

        # Відправляємо користувача до ЦРМ
        ViberUserToRabbitMQ(viber_user, 'UPDATE')


# Функція обробки event == 'message'
def message(request_dict):
    global global_text_message, global_keyboard_message, global_viber_id
    # Отримуємо інформацію
    message_type = request_dict['message']['type']
    message_text = request_dict['message']['text']
    global_viber_id = request_dict['sender']['id']
    viber_user = ViberUser.objects.get(viber_id=global_viber_id)

    print(request_dict['sender']['id'])
    print(f'\n\nmessage_type = {message_type}\nmessage_text = {message_text}\n\n')

    need_handled = False
    if not re.match(r"^\d+&&", message_text):
        if re.match(r'^service::\d{1,3}::location_manual::(\w)::\d{1,6}::(\w)::\d{1,3}::\d{1,6}$', viber_user.menu) and not re.match(r"https://", message_text):
            modified_street = message_text.replace(" ", "_")
            message = viber_user.menu + '::' + modified_street
            need_handled = True
        elif re.match(r'^service::\d{1,3}::location_manual::(\w)::\d{1,6}::(\w)::\d{1,3}::\d{1,6}::street$', viber_user.menu) and not re.match(r"https://", message_text):
            modified_number = message_text.replace(" ", "_")
            message = viber_user.menu + '::' + modified_number
            need_handled = True
        elif re.match(r'^service::\d{1,3}::location_manual::(\w)::\d{1,6}::(\w)::\d{1,3}::\d{1,6}::street::number$', viber_user.menu) and not re.match(r"https://", message_text):
            message = viber_user.menu + '::' + message_text
            need_handled = True
        elif viber_user.menu == 'phone_number' and message_text != 'setting':
            message = 'phone_number::' + message_text
            need_handled = True
        else:
            message = message_text
            need_handled = True
    elif not re.match(r"https://", message_text):
        once = message_text.split('&&')[0]
        message = message_text.split('&&')[1]
        print(f'???? {once} = {viber_user.once} ????')
        global_viber_id = viber_user.viber_id

        if int(once) == viber_user.once and global_viber_id:
            need_handled = True
            viber_user.once += 1
            viber_user.save()

    print(f'то что пытаемя обработать\nmessage = {message}\n\n')

    if need_handled:
        print("handled")

        if message_type == 'text':
            if viber_user.menu == 'registration':
                viber_user.full_name = message
                viber_user.menu = "phone_number"
                viber_user.save()

                global_text_message = "Для продовження необхідно пройти авторизацію. Для цього поділіться номером телефону, котрий прив'язаний до вайберу, або введіть Ваш контактний номер телефону\nФормат: +380ХХХХХХХХХ або 0ХХХХХХХХХ"
                global_keyboard_message = keyboards.phone_number(viber_user)
            elif not viber_user.phone_number and not re.match(r'^phone_number::', message):
                save_menu(viber_user, "phone_number")
                global_text_message = "Для продовження необхідно пройти авторизацію. Для цього поділіться номером телефону, котрий прив'язаний до вайберу, або введіть Ваш контактний номер телефону\nФормат: +380ХХХХХХХХХ або 0ХХХХХХХХХ"
                global_keyboard_message = keyboards.phone_number(viber_user)
            elif re.match(r'^phone_number::\+380\d{9}$', message):
                phone_number = message.split('::')[1]
                global_text_message = f'Ви підтверджуєте, що номер телефону введено коректно?\n{phone_number}'
                global_keyboard_message = keyboards.yes_no(viber_user, f'phone_number::{phone_number}')
            elif re.match(r'^phone_number::380\d{9}$', message):
                phone_number = '+' + message.split('::')[1]
                global_text_message = f'Ви підтверджуєте, що номер телефону введено коректно?\n{phone_number}'
                global_keyboard_message = keyboards.yes_no(viber_user, f'phone_number::{phone_number}')
            elif re.match(r'^phone_number::0\d{9}$', message):
                phone_number = "+38" + message.split('::')[1]
                global_text_message = f'Ви підтверджуєте, що номер телефону введено коректно?\n{phone_number}'
                global_keyboard_message = keyboards.yes_no(viber_user, f'phone_number::{phone_number}')
            elif re.match(r'^phone_number::\d{9}$', message):
                phone_number = "+380" + message.split('::')[1]
                global_text_message = f'Ви підтверджуєте, що номер телефону введено коректно?\n{phone_number}'
                global_keyboard_message = keyboards.yes_no(viber_user, f'phone_number::{phone_number}')
            elif re.match(r'^phone_number::\+380\d{9}::(?:yes|no)$', message):
                message_split = message.split('::')

                if message_split[2] == 'yes':
                    viber_user.phone_number = message_split[1]
                    viber_user.menu = 'start'
                    viber_user.save()

                    global_text_message = f'Дякуємо, Ваш номер збережено. Ви можете його змінити в будь-який момент в налаштуваннях.\nДля продовження скористайтесь контекстним меню.'
                    global_keyboard_message = keyboards.start_menu(viber_user)

                    # Відправляємо користувача до ЦРМ
                    ViberUserToRabbitMQ(viber_user, 'INSERT')

                elif message_split[2] == 'no':
                    global_text_message = "Для продовження необхідно пройти авторизацію. Для цього поділіться номером телефону, котрий прив'язаний до вайберу, або введіть Ваш контактний номер телефону\nФормат: +380ХХХХХХХХХ або 0ХХХХХХХХХ"
                    global_keyboard_message = keyboards.phone_number(viber_user)
            elif re.match(r'^phone_number::', message):
                global_text_message = "Невірний формат!\nФормат: +380ХХХХХХХХХ або 0ХХХХХХХХХ"
                global_keyboard_message = keyboards.phone_number(viber_user)
            elif re.match(r'^service::\d{1,2}$', message):
                keyboard = keyboards.service_1(viber_user, message.split('::')[1])
                global_text_message = keyboard[0]
                global_keyboard_message = keyboard[1]
            elif re.match(r'^service::\d{1,3}::location$', message):
                keyboard = keyboards.service_1(viber_user, message.split('::')[1])
                global_text_message = f'Нажаль дана функція доступна лише з телефону. Подайте заявку через телефон, або вкажіть вдресу власноруч.'
                global_keyboard_message = keyboard[1]
            elif re.match(r'^service::\d{1,2}::location::\d{1,8}::(?:yes|no)$', message):
                handling = verification_service_request(viber_user, message)
                global_text_message = handling[0]
                global_keyboard_message = handling[1]
            elif re.match(r'^service::\d{1,3}::location_manual$', message):
                global_text_message = f'Оберіть букву, з якої починається Ваша область.'
                global_keyboard_message = keyboards.location_region_startswith(viber_user, message)
            elif re.match(r'^service::\d{1,3}::location_manual::(\w)$', message):
                global_text_message = f'Оберіть Вашу область.'
                global_keyboard_message = keyboards.location_region_picker(viber_user, message)
            elif re.match(r'^service::\d{1,3}::location_manual::(\w)::\d{1,3}$', message):
                global_text_message = f'Оберіть букву, з якої починається Ваш населений пункт.'
                global_keyboard_message = keyboards.location_populated_centre_startswith(viber_user, message)
            elif re.match(r'^service::\d{1,3}::location_manual::(\w)::\d{1,6}::(\w)::\d{1,3}$', message):
                global_text_message = f'Оберіть Ваш населений пункт.'
                global_keyboard_message = keyboards.location_populated_centre_picker(viber_user, message)
            elif re.match(r'^service::\d{1,3}::location_manual::(\w)::\d{1,6}::(\w)::\d{1,3}::\d{1,6}$', message):
                save_menu(viber_user, message)
                global_text_message = f'Введіть назву Вашої вулиці\nНаприклад:\n\tвул. Богдана Хмельницького\n\tпровулок Незалежності'
                global_keyboard_message = keyboards.start_input(viber_user)
            elif re.match(r'^service::\d{1,3}::location_manual::(\w)::\d{1,6}::(\w)::\d{1,3}::\d{1,6}::.+$', message) and re.match(r'^service::\d{1,3}::location_manual::(\w)::\d{1,6}::(\w)::\d{1,3}::\d{1,6}$', viber_user.menu):
                handling = location_manual_street_handler(viber_user, message)
                global_text_message = handling[0]
                global_keyboard_message = handling[1]
            elif re.match(r'^service::\d{1,3}::location_manual::(\w)::\d{1,6}::(\w)::\d{1,3}::\d{1,6}::street::[\w\\/а-яА-Яa-zA-Z]+$', message):
                handling = location_manual_number_handler(viber_user, message)
                global_text_message = handling[0]
                global_keyboard_message = handling[1]
            elif re.match(r'^service::\d{1,3}::location_manual::(\w)::\d{1,6}::(\w)::\d{1,3}::\d{1,6}::street::number::\d+$', message):
                handling = location_manual_handler(viber_user, message)
                global_text_message = handling[0]
                global_keyboard_message = handling[1]
            elif re.match(r'^service::\d{1,3}::location_manual::(\w)::\d{1,6}::(\w)::\d{1,3}::\d{1,6}::street::number::skip$', message):
                handling = location_manual_handler(viber_user, message, True)
                global_text_message = handling[0]
                global_keyboard_message = handling[1]
            elif message == 'my_requests':
                handling = my_requests(viber_user)
                global_text_message = handling[0]
                global_keyboard_message = handling[1]
            elif re.match(r'^my_request::VSR-\d{1,4}-\d{1,2}-\d{1,2}-\d{1,6}$', message):
                service_number = message_text.split('::')[1]
                service_request = ServiceRequest.objects.get(number=service_number)
                handling = my_request_handler(viber_user, service_request)
                global_text_message = handling[0]
                global_keyboard_message = handling[1]
            elif re.match(r'^my_request::VSR-\d{1,4}-\d{1,2}-\d{1,2}-\d{1,6}::confirm$', message):
                message_split = message.split('::')
                service_request = ServiceRequest.objects.get(number=message_split[1])

                handling = my_request_confirm(viber_user, service_request)
                global_text_message = handling[0]
                global_keyboard_message = handling[1]
            elif re.match(r'^my_request::VSR-\d{1,4}-\d{1,2}-\d{1,2}-\d{1,6}::problem$', message):
                message_split = message.split('::')
                service_request = ServiceRequest.objects.get(number=message_split[1])

                handling = my_request_problem(viber_user, service_request)
                global_text_message = handling[0]
                global_keyboard_message = handling[1]
            elif re.match(r'^my_request::VSR-\d{1,4}-\d{1,2}-\d{1,2}-\d{1,6}::assessment$', message):
                global_text_message = f'Оберіть оцінку від 1 до 5, де 1 - це найнижча оцінка, а 5 - найвища'
                global_keyboard_message = keyboards.zero_to_five(viber_user, message)
            elif re.match(r'^my_request::VSR-\d{1,4}-\d{1,2}-\d{1,2}-\d{1,6}::assessment::\d$', message):
                message_split = message.split('::')
                service_request = ServiceRequest.objects.get(number=message_split[1])

                handling = my_request_assessment(viber_user, service_request, message_split[3])
                global_text_message = handling[0]
                global_keyboard_message = handling[1]
            elif re.match(r'^my_request::VSR-\d{1,4}-\d{1,2}-\d{1,2}-\d{1,6}::reject$', message):
                message_split = message.split('::')
                service_request = ServiceRequest.objects.get(number=message_split[1])

                handling = my_request_reject(viber_user, service_request)
                global_text_message = handling[0]
                global_keyboard_message = handling[1]
            elif re.match(r'^my_request::VSR-\d{1,4}-\d{1,2}-\d{1,2}-\d{1,6}::cancel$', message):
                message_split = message.split('::')
                global_text_message = f'Ви впевнені що хочете скасувати заявку {message_split[1]}'
                global_keyboard_message = keyboards.yes_no(viber_user, message)
            elif re.match(r'^my_request::VSR-\d{1,4}-\d{1,2}-\d{1,2}-\d{1,6}::cancel::(?:yes|no)$', message):
                message_split = message.split('::')
                service_request = ServiceRequest.objects.get(number=message_split[1])

                handling = my_request_cancel(viber_user, service_request, message_split[3])
                global_text_message = handling[0]
                global_keyboard_message = handling[1]
            elif message == 'master_requests':
                global_text_message = f'Для продовження скористайтесь контекстним меню.'
                global_keyboard_message = keyboards.master_requests(viber_user)
            elif re.match(r'^master_requests::available$', message):
                service_requests = ServiceRequest.objects.filter(executors=viber_user, status_code=4)

                handling = master_requests_handler(viber_user, 'available', service_requests)
                global_text_message = handling[0]
                global_keyboard_message = handling[1]
            elif re.match(r'^master_requests::confirmed$', message):
                service_requests = ServiceRequest.objects.filter(executors=viber_user, status_code=6)

                handling = master_requests_handler(viber_user, 'confirmed', service_requests)
                global_text_message = handling[0]
                global_keyboard_message = handling[1]
            elif re.match(r'^master_request::(?:available|confirmed)::VSR-\d{1,4}-\d{1,2}-\d{1,2}-\d{1,6}$', message):
                message_split = message.split('::')
                service_request = ServiceRequest.objects.get(number=message_split[2])

                if message_split[1] == 'available':
                    global_text_message = f'Номер заявки: {service_request.number}\nПослуга: {service_request.service}\nНаселений пункт: {service_request.position}\nЗаявник: {service_request.customer.full_name}\nРейтинг замовника: {service_request.customer.customer_rating}'
                    global_keyboard_message = keyboards.master_service_request(viber_user, 'available', service_request)

                elif message_split[1] == 'confirmed':
                    global_text_message = f'Номер заявки: {service_request.number}\nПослуга: {service_request.service}\n\nНаселений пункт: {service_request.position}\nАдреса: {service_request.address}\n\nЗаявник: {service_request.customer.full_name}\nНомер телефона: {service_request.customer.phone_number}\nРейтинг замовника: {service_request.customer.customer_rating}\n'
                    global_keyboard_message = keyboards.master_service_request(viber_user, 'confirmed', service_request)
            elif re.match(r'^master_service_request::VSR-\d{1,4}-\d{1,2}-\d{1,2}-\d{1,6}::respond$', message):
                message_split = message.split('::')
                service_request = ServiceRequest.objects.get(number=message_split[1])

                handling = master_request_respond_handler(viber_user, service_request)
                global_text_message = handling[0]
                global_keyboard_message = handling[1]
            elif re.match(r'^master_service_request::VSR-\d{1,4}-\d{1,2}-\d{1,2}-\d{1,6}::problem$', message):
                message_split = message.split('::')
                service_request = ServiceRequest.objects.get(number=message_split[1])

                handling = master_request_problem_handler(viber_user, service_request)
                global_text_message = handling[0]
                global_keyboard_message = handling[1]
            elif re.match(r'^master_service_request::VSR-\d{1,4}-\d{1,2}-\d{1,2}-\d{1,6}::done$', message):
                message_split = message.split('::')
                global_text_message = f'Ви хочете позначити що заявка {message_split[1]} виконана?'
                global_keyboard_message = keyboards.yes_no(viber_user, message)
            elif re.match(r'^master_service_request::VSR-\d{1,4}-\d{1,2}-\d{1,2}-\d{1,6}::done::(?:yes|no)$', message):
                message_split = message.split('::')
                service_request = ServiceRequest.objects.get(number=message_split[1])

                handling = master_request_done_handler(viber_user, service_request, message_split[3])
                global_text_message = handling[0]
                global_keyboard_message = handling[1]
            elif message == 'start':
                save_menu(viber_user, 'start')
                global_text_message = f'Для продовження скористайтесь контекстним меню.'
                global_keyboard_message = keyboards.start_menu(viber_user)
            elif message == 'service':
                global_text_message = f'Оберіть послугу'
                global_keyboard_message = keyboards.service_0(viber_user)
            elif message == 'setting':
                global_text_message = f'Для продовження скористайтесь контекстним меню.'
                global_keyboard_message = keyboards.setting(viber_user)
            elif message == 'change_phone_number':
                global_text_message = f'Ваш поточний номер телефону: {viber_user.phone_number}\nВи впевнені що хочете його змінити?'
                global_keyboard_message = keyboards.yes_no(viber_user, 'change_phone_number')
            elif re.match(r'^change_phone_number::(?:yes|no)$', message):
                handling = change_phone_number(viber_user, message)
                global_text_message = handling[0]
                global_keyboard_message = handling[1]
            elif message == 'master_registration':
                global_text_message = f'Для того щоб стати майстром Вам необхідно буде надати більш детальну інформацію про себе та свої навички. Чи походжуєтесь на обробку інформації?'
                global_keyboard_message = keyboards.master_registration(viber_user)
            elif message == 'test':
                handling = test(viber_user)
                global_text_message = handling[0]
                global_keyboard_message = handling[1]
        elif message_type == 'location':
            if re.match(r'^service::\d{1,2}::location$', message):
                lat = request_dict['message']['location']['lat']
                lon = request_dict['message']['location']['lon']
                address = request_dict['message']['location']['address']
                handling = location_handler(viber_user, message, lat, lon, address)
                global_text_message = handling[0]
                global_keyboard_message = handling[1]
        elif message_type == "contact":
            phone_number = "+" + request_dict['message']['contact']['phone_number']

            global_text_message = f'Ви підтверджуєте, що номер телефону введено коректно?\n{phone_number}'
            global_keyboard_message = keyboards.yes_no(viber_user, f'phone_number::{phone_number}')
    send(request_dict['sender']['id'])


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
        Q(modifiedon__gte=fourteen_days_ago))
    text = ""
    if not service_requests:
        text = "Від Вас заявок не знайдено"
        keyboard = keyboards.service_0(viber_user)
    else:
        keyboard = keyboards.my_requests(viber_user, service_requests)
        for request in service_requests:
            status_text = request.get_status_code_display()
            request_text = f'Номер заявки: {request.number}\nПослуга: {request.service}\nАдреса: {request.address}\nСтатус заявки: {status_text}\n\n'
            text = text + request_text

    return text, keyboard


def my_request_handler(viber_user, service_request):
    if service_request.status_code == '4':
        text = f'На цю заявку ще не відгукнувся жодний майстер'
        keyboard = keyboards.my_request_cancel(viber_user, service_request)
    elif service_request.status_code == '5':
        executor = service_request.executors.first()
        text = f'На Вашу заявку відгукнувся майстр {executor.full_name}\nРейтинг майстра: {executor.executor_rating}'
        keyboard = keyboards.my_request_confirmation(viber_user, service_request)
    elif service_request.status_code == '6':
        text = f'Ваша заявка в роботі. Очікуйте дзвінка від майстра.'
        keyboard = keyboards.my_request_cancel(viber_user, service_request)
    elif service_request.status_code == '2':
        text = f'Майстр позначив Вашу заявку як виконану. Ви можете оцінити майстра або повідомити про проблему.'
        keyboard = keyboards.my_request_done(viber_user, service_request)
    return text, keyboard


def my_request_confirm(viber_user, service_request):
    with transaction.atomic():
        # Переводимо заявку у статус "В роботі (Підтверджений майстер)"
        service_request.status_code = 6
        service_request.save()

    # Відправляемо повідомлення майстру
    executor = service_request.executors.first()
    keyboard = keyboards.start_menu(executor)
    response_message = TextMessage(
        text=f'Замовник підтвердив заявку, на яку Ви відгукнулись\nНомер заявки: {service_request.number}',
        keyboard=keyboard,
        min_api_version=6)
    viber.send_messages(executor.viber_id, [response_message])

    # Відправляємо повідомлення замовнику
    text = f"Заявка успішно підтверджена. Майстер зв'яжеться з вами найближчим часом"
    keyboard = keyboards.service_0(viber_user)
    return text, keyboard


def my_request_problem(viber_user, service_request):
    with transaction.atomic():
        # Переводимо заявку у статус "Уточнення (від клієнта)"
        service_request.status_code = 8
        service_request.save()
    text = f'Дякую. Заявка {service_request.number} передана до відділу підтримки, незабаром з вами звяжуться для уточнення деталей'
    keyboard = keyboards.service_0(viber_user)
    return text, keyboard


def my_request_assessment(viber_user, service_request, response):
    with transaction.atomic():
        # Переводимо заявку у статус "Завершено"
        service_request.status_code = 9
        service_request.save()

    executor = service_request.executors.first()
    body = {
        'viber_id': executor.viber_id,
        'type_assessment': "executor",
        'assessment': response,
    }
    new_package = CustomCreate.create_package("INSERT", 'application/json', 'kvb::assessment', json.dumps(body), service_request.id)

    text = f'Дякуємо за Вашу оцінку.\nДля продовження скористайтесь контекстним меню.'
    keyboard = keyboards.start_menu(viber_user)
    return text, keyboard


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
    text = f'Майстер відхилений. Заявка розіслана іншим майстрам. Очікуємо відповіть від них. Після того, як відповіть буде отримана, Ви отримаєте повідомлення.'
    keyboard = keyboards.service_0(viber_user)
    return text, keyboard


def my_request_cancel(viber_user, service_request, response):
    executors_count = service_request.executors.count()

    if response == "yes":
        with transaction.atomic():
            # Переводимо заявку у статус "Скасованої"
            service_request.status_code = 3
            service_request.save()

        if service_request.status_code in ("5", "6"):
            # Відправляемо повідомлення Виконавцю
            executor = service_request.executors.first()
            keyboard = keyboards.start_menu(executor)
            response_message = TextMessage(
                text=f'Замовник {service_request.customer} відмінив заявку {service_request.number}',
                keyboard=keyboard,
                min_api_version=6)
            viber.send_messages(executor.viber_id, [response_message])

        # Відправляемо повідомлення Замовнику
        text = f'Ваша заявка {service_request.number} - скасована'
        keyboard = keyboards.service_0(viber_user)

        return text, keyboard

    elif response == "no":
        handling = my_requests(viber_user)
        return handling[0], handling[1]


def change_phone_number(viber_user, message):
    message_split = message.split('::')
    if message_split[1] == 'yes':
        save_menu(viber_user, "phone_number")
        text = "Надайте новий номер телефону. Для цього поділіться номером телефону, котрий прив'язаний до вайберу, або введіть Ваш контактний номер телефону\nФормат: +380ХХХХХХХХХ або 0ХХХХХХХХХ"
        keyboard = keyboards.phone_number(viber_user)
    elif message_split[1] == 'no':
        text = f'Для продовження скористайтесь контекстним меню.'
        keyboard = keyboards.setting(viber_user)
    return text, keyboard


def location_handler(viber_user, message, lat, lon, address):
    location = geocoder.osm([lat, lon], method='reverse')

    # print(location.raw)
    # print(address)
    # print(location.raw['display_name'])

    city = location.city
    town = location.town
    code_ua = location.raw['address']['ISO3166-2-lvl4'].replace("-", "")

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

    # print(position)

    if position:
        viber_user.address = display_address
        viber_user.save()
        service = Service.objects.get(id=message.split('::')[1])
        keyboard = keyboards.yes_no(viber_user, message + '::' + str(position[0].id))
        text = f'Ви підтверджуєте заявку?\nПослуга: {service.name}\nМісце проведення: {display_address}'
    else:
        key_def = keyboards.service_1(viber_user, message.split('::')[1])
        text = 'Розташування не було знайдене, вкажіть його вручну.'
        keyboard = key_def[1]

    return text, keyboard


def location_manual_handler(viber_user, message, skip=False):
    message_split = message.split("::")
    position = Position.objects.get(id=message_split[7])
    if skip:
        address = viber_user.address
    else:
        address = viber_user.address + ', кв. ' + message_split[10]
    viber_user.address = address
    viber_user.save()

    full_path = get_parents_names(position)

    display_address = full_path + ', ' + viber_user.address

    print(full_path)
    print(display_address)

    viber_user.address = display_address
    viber_user.save()
    service = Service.objects.get(id=message.split('::')[1])
    text = f'Ви підтверджуєте заявку?\nПослуга: {service.name}\n\nМісце проведення: {display_address}'
    keyboard = keyboards.yes_no(viber_user, 'service::' + str(service.id) + '::location::' + str(position.id))

    body = {
        'address': display_address,
    }
    json_body = json.dumps(body, ensure_ascii=False)
    new_package = CustomCreate.create_package('INSERT', 'application/json', 'kvb::address', json_body)

    return text, keyboard


def location_manual_street_handler(viber_user, message):
    message_split = message.split("::")
    menu = "::".join(message_split[:-1])

    street = message_split[8]
    modified_street = street.replace("_", " ")
    viber_user.address = modified_street
    viber_user.menu = menu + '::street'
    viber_user.save()

    text = f'Введіть номер Вашого будинку\nНаприклад: 64 (64/1)'
    keyboard = keyboards.start_input(viber_user)

    return text, keyboard

def location_manual_number_handler(viber_user, message):
    message_split = message.split("::")
    menu = "::".join(message_split[:-1])

    number = message_split[9]
    modified_number = number.replace("_", " ")
    viber_user.address = viber_user.address + ', буд. ' + modified_number
    viber_user.menu = menu + '::number'
    viber_user.save()

    text = f'Введіть номер Вшої квартири\nНаприклад: 108\n\nЯкщо квартира відсутня, натисніть кнопку "Пропустити"'
    keyboard = keyboards.skip(viber_user, viber_user.menu)
    return text, keyboard


# "Підтвердження" на створення заявку
def verification_service_request(viber_user, message):
    message_split = message.split("::")
    service_id = message_split[1]
    position_id = message_split[3]
    response = message_split[4]
    if response == "no":
        key_def = keyboards.service_1(viber_user, message.split('::')[1])
        text = key_def[0]
        keyboard = key_def[1]
    elif response == "yes":
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

        text = f'Ваша заявка створена!\nНомер заявки: {number}'
        keyboard = keyboards.start(viber_user)

        service_request_handler(service_request)
    return text, keyboard


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


def master_requests_handler(viber_user, prefix, service_requests):
    text = ""
    for request in service_requests:
        request_text = f'Номер заявки: {request.number}\nПослуга: {request.service}\nНаселений пункт: {request.position}\n\n'
        text = text + request_text

    if service_requests.exists():
        keyboard = keyboards.master_service_requests(viber_user, prefix, service_requests)
    else:
        text = "Заявки відсутні"
        keyboard = keyboards.master_requests(viber_user)
    return text, keyboard


def master_request_respond_handler(viber_user, service_request):
    with transaction.atomic():
        # Відвязуємо всіх виконавців
        service_request.executors.clear()

        # Привязуємо того, хто відгукнувся
        service_request.executors.add(viber_user)

        # Статус "Очікування підтвердження"
        service_request.status_code = 5
        service_request.save()

    # Відправляємо повідомлення замовнику і просимо його перейти в мої заявки та підтвердити майстра
    text = f'На вашу заявку відгукнувся майстер. Перейдіть до послуг, оберіть мої заявки та підтвердіть майстра!'
    keyboard = keyboards.start_menu(service_request.customer)
    response_message = TextMessage(
        text=text,
        keyboard=keyboard,
        min_api_version=6)
    viber.send_messages(service_request.customer.viber_id, [response_message])

    # Відправляємо повідомлення майстру
    text = f'Ви відгунулися на заявку. Коли замовник підтвердить заявку, вам прийде повідомлення. Для подальшої роботи скористайтесь контекстним меню'
    keyboard = keyboards.start_menu(viber_user)
    return text, keyboard


def master_request_problem_handler(viber_user, service_request):
    with transaction.atomic():
        # Статус "Уточнення (від майстра)"
        service_request.status_code = 7
        service_request.save()

        text = f'Дякуємо. Заявка {service_request.number} передана до відділу підтримки, незабаром з вами звяжуться для уточнення деталей.'
        keyboard = keyboards.master_requests(viber_user)

        return text, keyboard


def master_request_done_handler(viber_user, service_request, response):
    if response == 'yes':
        with transaction.atomic():
            # Статус "Виконана"
            service_request.modifiedon = datetime.now()
            service_request.status_code = 2
            service_request.save()

        # Відправляємо повідомлення замовнику
        keyboard = keyboards.start_menu(service_request.customer)
        response_message = TextMessage(
            text=f'Майстер підтвердив виконання Вашої заявки {service_request.number}',
            keyboard=keyboard,
            min_api_version=6)
        viber.send_messages(service_request.customer.viber_id, [response_message])

        # Відправляємо повідомлення майстру
        text = f'Ви підтвердили виконання заявки {service_request.number}'
        keyboard = keyboards.start_menu(viber_user)
    elif response == 'no':
        # Відправляємо повідомлення майстру
        text = f'Обрана заявка {service_request.number}'
        keyboard = keyboards.master_service_request(viber_user, 'confirmed', service_request)
    return text, keyboard


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

        new_package = CustomCreate.create_package('INSERT', "application/json", 'kvb_master', json_body, form_data["viber_id"])

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


def get_parents_names(node):
    names = [node.name]
    while node.parent:
        node = node.parent
        names.insert(0, node.name)
    return ", ".join(names)


def ViberUserToRabbitMQ(viber_user, operation):
    class ViberUserSerializer(serializers.ModelSerializer):
        class Meta:
            model = ViberUser
            fields = ['status_code', 'viber_id', 'full_name', 'phone_number']

    viber_user_serializer = ViberUserSerializer(viber_user)
    viber_user_json_data = viber_user_serializer.data
    json_data = json.dumps(viber_user_json_data, ensure_ascii=False).encode('utf-8')
    decoded_json_data = json_data.decode('utf-8')
    new_package = CustomCreate.create_package(operation, 'application/json', 'kvb::viber_user', decoded_json_data, viber_user.viber_id)


def ServiceRequestToRabbitMQ(service_request, operation):
    body = {
        'status_code': service_request.status_code,
        'number': service_request.number,
        'customer': service_request.customer.viber_id,
        'address': service_request.address,
        'position': service_request.position.codifier,
        'service': service_request.service.id
    }
    new_package = CustomCreate.create_package(operation, 'application/json', 'kvb::service_request', json.dumps(body), service_request.id)


# Функція записує меню у вайбер-користувача
def save_menu(viber_user, menu):
    viber_user.menu = menu
    viber_user.save()

import pysnooper

# @pysnooper.snoop()
def test(viber_user):
    print("test")
    text = f'TEST'
    keyboard = keyboards.star1_menu(viber_user)
    return text, keyboard
