import pytz
import math

from datetime import date, datetime, timedelta
from . import config
from django.conf import settings
from .models import ViberUser, Service, ServiceRequest, Position
from django.db.models import F, Q
from pyuca import Collator
from django.core.paginator import Paginator
from django.db.models.functions import Left

collator = Collator()


def button_img(columns, rows, text, img, actiontype, actionbody):
    button = {
        "Columns": columns,
        "Rows": rows,
        "Text": f"{text}",
        "TextOpacity": 0,
        "Image": img,
        "ImageScaleType": "fit",
        "BgColor": config.colorBg_button,
        "ActionType": actiontype,
        "ActionBody": actionbody,
    }
    return button


def button(columns, rows, text, img, bgimg, actiontype, actionbody, opacity=100):
    button = {
        "Columns": columns,
        "Rows": rows,
        "Text": text,
        "Image": img,
        "ImageScaleType": "fit",
        "BgMedia": bgimg,
        "BgMediaScaleType": "fit",
        "BgColor": config.colorBg_button,
        "ActionType": actiontype,
        "ActionBody": actionbody,
        "TextOpacity": opacity,
    }
    return button


def silent_button(columns, rows):
    button = {
        "Columns": columns,
        "Rows": rows,
        "Text": "",
        "ActionType": "",
        "ActionBody": "",
        "Silent": "true",
        "TextOpacity": 0,
    }
    return button


# buttons.append(button(6, 1, # Columns & Rows
# f'<font size=22 color="#FFFFFF"><b>СюдаПисатьТекст</b></font>',
# # img - картинка (НЕ ОБЯЗАТЕЛЬНО)
# f'',
# # bgimg - картинка фона (НЕ ОБЯЗАТЕЛЬНО)
# f'{config.domain}{settings.STATIC_URL}viber_bot_buttons/6x1/green.png',
# # actiontype - ТИП ОТВЕТА
# 'reply',
# # actionbody - ОТВЕТ (дописать ", 0" - прозрачный текст)
# f'{viber_user.once}&&СюдаПистьОтвет',
# ))


def button_back(text, img, bgimg, actionbody, opacity=100):
    button = {
        "Columns": 5,
        "Rows": 1,
        "Text": text,
        "Image": img,
        "ImageScaleType": "fit",
        "BgMedia": bgimg,
        "BgMediaScaleType": "fit",
        "BgColor": config.colorBg_button,
        "ActionType": "reply",
        "ActionBody": actionbody,
        "TextOpacity": opacity,
    }
    return button


# buttons.append(button_back(f'<font size=22 color="#404040"><b>Назад</b></font>',
#                            # img - картинка (НЕ ОБЯЗАТЕЛЬНО)
#                            f'',
#                            # bgimg - картинка фона (НЕ ОБЯЗАТЕЛЬНО)
#                            f'{config.domain}{settings.STATIC_URL}viber_bot_buttons/5x1/gray_light.png',
#                            # actionbody - ОТВЕТ (дописать ", 0" - прозрачный текст)
#                            f'{viber_user.once}&&СюдаПистьОтвет',
#                            ))

# {viber_user.once}&&

def button_home(viber_user):
    button = {
        "Columns": 1,
        "Rows": 1,
        "Text": "До головного меню",
        "Image": f'{config.domain}{settings.STATIC_URL}viber_bot_buttons/1x1_home.png',
        "ImageScaleType": "fit",
        "BgMediaScaleType": "fit",
        "BgColor": config.colorBg_button,
        "ActionType": "reply",
        "ActionBody": f'{viber_user.once}&&start',
        "TextOpacity": 0,
    }
    return button


# buttons.append(button_home(viber_user))


def keyboard_def(buttons, іnputfieldstate):
    keyboard = {
        "Type": "keyboard",
        "DefaultHeight": "false",
        "BgColor": config.colorBg_keyboard,
        "Buttons": buttons,
        "InputFieldState": іnputfieldstate
    }
    return keyboard


def keyboard_input():
    keyboard = {
        "Type": "keyboard",
        "DefaultHeight": "false",
        "BgColor": config.colorBg_keyboard,
        "Buttons": "",
        "InputFieldState": "regular"
    }
    return keyboard


# Клавиатурки:
def start_menu(viber_user):
    buttons = []

    if viber_user.executor:
        buttons.append(button(6, 1,  # Columns & Rows
                              f'<font size=22 color="#FFFFFF"><b>Заявки</b></font>',
                              # img - картинка (НЕ ОБЯЗАТЕЛЬНО)
                              f'{config.domain}{settings.STATIC_URL}viber_bot_buttons/master_requests.png',
                              # bgimg - картинка фона (НЕ ОБЯЗАТЕЛЬНО)
                              f'',
                              # actiontype - ТИП ОТВЕТА
                              'reply',
                              # actionbody - ОТВЕТ
                              f'{viber_user.once}&&master_requests', 0
                              ))

    buttons.append(button(6, 1,  # Columns & Rows
                          f'<font size=22 color="#FFFFFF"><b>Послуги</b></font>',
                          # img - картинка (НЕ ОБЯЗАТЕЛЬНО)
                          f'{config.domain}{settings.STATIC_URL}viber_bot_buttons/main_service.png',
                          # bgimg - картинка фона (НЕ ОБЯЗАТЕЛЬНО)
                          f'',
                          # actiontype - ТИП ОТВЕТА
                          'reply',
                          # actionbody - ОТВЕТ
                          f'{viber_user.once}&&service', 0
                          ))
    buttons.append(button(6, 1,  # Columns & Rows
                          f'<font size=22 color="#FFFFFF"><b>Магазин</b></font>',
                          # img - картинка (НЕ ОБЯЗАТЕЛЬНО)
                          f'{config.domain}{settings.STATIC_URL}viber_bot_buttons/main_market.png',
                          # bgimg - картинка фона (НЕ ОБЯЗАТЕЛЬНО)
                          f'',
                          # actiontype - ТИП ОТВЕТА
                          'open-url',
                          # actionbody - ОТВЕТ
                          f'https://ecotherm.com.ua/', 0
                          ))
    buttons.append(button(6, 1,  # Columns & Rows
                          f'<font size=22 color="#FFFFFF"><b>Налаштування</b></font>',
                          # img - картинка (НЕ ОБЯЗАТЕЛЬНО)
                          f'{config.domain}{settings.STATIC_URL}viber_bot_buttons/main_settings.png',
                          # bgimg - картинка фона (НЕ ОБЯЗАТЕЛЬНО)
                          f'',
                          # actiontype - ТИП ОТВЕТА
                          'reply',
                          # actionbody - ОТВЕТ (дописать ", 0" - прозрачный текст)
                          f'{viber_user.once}&&setting', 0
                          ))
    if viber_user.system_administrator:
        buttons.append(button(6, 1,  # Columns & Rows
                              f'<font size=22 color="#404040"><b>test</b></font>',
                              # img - картинка (НЕ ОБЯЗАТЕЛЬНО)
                              f'',
                              # bgimg - картинка фона (НЕ ОБЯЗАТЕЛЬНО)
                              f'',
                              # actiontype - ТИП ОТВЕТА
                              'reply',
                              # actionbody - ОТВЕТ (дописать " 0" - прозрачный текст)
                              f'{viber_user.once}&&test',
                              ))

    keyboard = keyboard_def(buttons, "hidden")
    return keyboard


# МАСТЕРОВ:

# "Заявки" для майстрів
def master_requests(viber_user):
    buttons = []

    available_service_requests = ServiceRequest.objects.filter(executors=viber_user, status_code=4)
    count_service_requests = len(available_service_requests)
    buttons.append(button(6, 1,  # Columns & Rows
                          f'<font size=22 color="#FFFFFF"><b>Доступні заявки ({count_service_requests})</b></font>',
                          # img - картинка (НЕ ОБЯЗАТЕЛЬНО)
                          f'',
                          # bgimg - картинка фона (НЕ ОБЯЗАТЕЛЬНО)
                          f'{config.domain}{settings.STATIC_URL}viber_bot_buttons/6x1/blue.png',
                          # actiontype - ТИП ОТВЕТА
                          'reply',
                          # actionbody - ОТВЕТ (дописать ", 0" - прозрачный текст)
                          f'{viber_user.once}&&master_requests::available',
                          ))

    confirmed_service_requests = ServiceRequest.objects.filter(executors=viber_user, status_code=6)
    count_confirmed_service_requests = len(confirmed_service_requests)
    buttons.append(button(6, 1,  # Columns & Rows
                          f'<font size=22 color="#FFFFFF"><b>Підтверджені заявки ({count_confirmed_service_requests})</b></font>',
                          # img - картинка (НЕ ОБЯЗАТЕЛЬНО)
                          f'',
                          # bgimg - картинка фона (НЕ ОБЯЗАТЕЛЬНО)
                          f'{config.domain}{settings.STATIC_URL}viber_bot_buttons/6x1/blue.png',
                          # actiontype - ТИП ОТВЕТА
                          'reply',
                          # actionbody - ОТВЕТ (дописать ", 0" - прозрачный текст)
                          f'{viber_user.once}&&master_requests::confirmed',
                          ))

    buttons.append(button_back(f'<font size=22 color="#404040"><b>Назад</b></font>',
                               # img - картинка (НЕ ОБЯЗАТЕЛЬНО)
                               f'',
                               # bgimg - картинка фона (НЕ ОБЯЗАТЕЛЬНО)
                               f'{config.domain}{settings.STATIC_URL}viber_bot_buttons/5x1/gray_light.png',
                               # actionbody - ОТВЕТ (дописать ", 0" - прозрачный текст)
                               f'{viber_user.once}&&start',
                               ))
    buttons.append(button_home(viber_user))

    keyboard = keyboard_def(buttons, "hidden")
    return keyboard


# "Доступні заявки" для майстрів
def master_service_requests(viber_user, prefix, service_requests):
    buttons = []
    for request in service_requests:
        buttons.append(button(6, 1,  # Columns & Rows
                              f'<font size=22 color="#FFFFFF"><b>{request.number}</b></font>',
                              # img - картинка (НЕ ОБЯЗАТЕЛЬНО)
                              f'',
                              # bgimg - картинка фона (НЕ ОБЯЗАТЕЛЬНО)
                              f'{config.domain}{settings.STATIC_URL}viber_bot_buttons/6x1/blue.png',
                              # actiontype - ТИП ОТВЕТА
                              'reply',
                              # actionbody - ОТВЕТ (дописать ", 0" - прозрачный текст)
                              f'{viber_user.once}&&master_request::{prefix}::{request.number}',
                              ))
    buttons.append(button_back(f'<font size=22 color="#404040"><b>Назад</b></font>',
                               # img - картинка (НЕ ОБЯЗАТЕЛЬНО)
                               f'',
                               # bgimg - картинка фона (НЕ ОБЯЗАТЕЛЬНО)
                               f'{config.domain}{settings.STATIC_URL}viber_bot_buttons/5x1/gray_light.png',
                               # actionbody - ОТВЕТ (дописать ", 0" - прозрачный текст)
                               f'{viber_user.once}&&master_requests',
                               ))
    buttons.append(button_home(viber_user))

    keyboard = keyboard_def(buttons, "hidden")
    return keyboard


# Конкретна заявка для майстрів
def master_service_request(viber_user, prefix, service_request):
    buttons = []
    if prefix == 'available':
        buttons.append(button(6, 1,  # Columns & Rows
                              f'<font size=22 color="#FFFFFF"><b>Відгукнутися</b></font>',
                              # img - картинка (НЕ ОБЯЗАТЕЛЬНО)
                              f'',
                              # bgimg - картинка фона (НЕ ОБЯЗАТЕЛЬНО)
                              f'{config.domain}{settings.STATIC_URL}viber_bot_buttons/6x1/blue.png',
                              # actiontype - ТИП ОТВЕТА
                              'reply',
                              # actionbody - ОТВЕТ (дописать ", 0" - прозрачный текст)
                              f'{viber_user.once}&&master_service_request::{service_request.number}::respond',
                              ))
    elif prefix == 'confirmed':
        buttons.append(button(6, 1,  # Columns & Rows
                              f'<font size=22 color="#FFFFFF"><b>Позначити як виконану</b></font>',
                              # img - картинка (НЕ ОБЯЗАТЕЛЬНО)
                              f'',
                              # bgimg - картинка фона (НЕ ОБЯЗАТЕЛЬНО)
                              f'{config.domain}{settings.STATIC_URL}viber_bot_buttons/6x1/blue.png',
                              # actiontype - ТИП ОТВЕТА
                              'reply',
                              # actionbody - ОТВЕТ (дописать ", 0" - прозрачный текст)
                              f'{viber_user.once}&&master_service_request::{service_request.number}::done',
                              ))
        buttons.append(button(6, 1,  # Columns & Rows
                              f'<font size=22 color="#FFFFFF"><b>Повідомити про проблему</b></font>',
                              # img - картинка (НЕ ОБЯЗАТЕЛЬНО)
                              f'',
                              # bgimg - картинка фона (НЕ ОБЯЗАТЕЛЬНО)
                              f'{config.domain}{settings.STATIC_URL}viber_bot_buttons/6x1/blue.png',
                              # actiontype - ТИП ОТВЕТА
                              'reply',
                              # actionbody - ОТВЕТ (дописать ", 0" - прозрачный текст)
                              f'{viber_user.once}&&master_service_request::{service_request.number}::problem',
                              ))
    buttons.append(button_back(f'<font size=22 color="#404040"><b>Назад</b></font>',
                               # img - картинка (НЕ ОБЯЗАТЕЛЬНО)
                               f'',
                               # bgimg - картинка фона (НЕ ОБЯЗАТЕЛЬНО)
                               f'{config.domain}{settings.STATIC_URL}viber_bot_buttons/5x1/gray_light.png',
                               # actionbody - ОТВЕТ (дописать ", 0" - прозрачный текст)
                               f'{viber_user.once}&&master_requests::{prefix}',
                               ))
    buttons.append(button_home(viber_user))

    keyboard = keyboard_def(buttons, "hidden")
    return keyboard


def service_0(viber_user):
    buttons = []
    services = Service.objects.filter(parent__isnull=True).order_by('priority')
    for service in services:
        buttons.append(button(service.columns, service.rows,  # Columns & Rows
                              f'<font size=22 color="#FFFFFF"><b>{service.name}</b></font>',
                              # img - картинка (НЕ ОБЯЗАТЕЛЬНО)
                              f'{config.domain}{service.image.url}',
                              # bgimg - картинка фона (НЕ ОБЯЗАТЕЛЬНО)
                              f'',
                              # actiontype - ТИП ОТВЕТА
                              'reply',
                              # actionbody - ОТВЕТ (дописать ", 0" - прозрачный текст)
                              f'{viber_user.once}&&service::{service.id}', 0
                              ))
    buttons.append(button(6, 1,  # Columns & Rows
                          f'<font size=22 color="#FFFFFF"><b>Мої заявки</b></font>',
                          # img - картинка (НЕ ОБЯЗАТЕЛЬНО)
                          f'{config.domain}{settings.STATIC_URL}viber_bot_buttons/6x1_my_requests.png',
                          # bgimg - картинка фона (НЕ ОБЯЗАТЕЛЬНО)
                          f'',
                          # actiontype - ТИП ОТВЕТА
                          'reply',
                          # actionbody - ОТВЕТ (дописать ", 0" - прозрачный текст)
                          f'{viber_user.once}&&my_requests', 0
                          ))
    buttons.append(button_back(f'<font size=22 color="#404040"><b>Назад</b></font>',
                               # img - картинка (НЕ ОБЯЗАТЕЛЬНО)
                               f'',
                               # bgimg - картинка фона (НЕ ОБЯЗАТЕЛЬНО)
                               f'{config.domain}{settings.STATIC_URL}viber_bot_buttons/5x1/gray_light.png',
                               # actionbody - ОТВЕТ (дописать ", 0" - прозрачный текст)
                               f'{viber_user.once}&&start',
                               ))
    buttons.append(button_home(viber_user))

    keyboard = keyboard_def(buttons, "hidden")
    return keyboard


# "Послуги дочірні"
def service_1(viber_user, service_id):
    buttons = []
    services = Service.objects.filter(parent=service_id).order_by('priority')
    if services:
        text = f'Ви обрали "{services[0].parent}". Оберіть послугу.'
        for service in services:
            buttons.append(button(service.columns, service.rows,  # Columns & Rows
                                  f'<font size=22 color="#FFFFFF"><b>{service.name}</b></font>',
                                  # img - картинка (НЕ ОБЯЗАТЕЛЬНО)
                                  f'{config.domain}{service.image.url}',
                                  # bgimg - картинка фона (НЕ ОБЯЗАТЕЛЬНО)
                                  f'',
                                  # actiontype - ТИП ОТВЕТА
                                  'reply',
                                  # actionbody - ОТВЕТ (дописать ", 0" - прозрачный текст)
                                  f'{viber_user.once}&&service::{service.id}', 0
                                  ))

        # Додавання кнопки "назад"
        if services[0].parent.parent:
            buttons.append(button_back(f'<font size=22 color="#404040"><b>Назад</b></font>',
                                       # img - картинка (НЕ ОБЯЗАТЕЛЬНО)
                                       f'',
                                       # bgimg - картинка фона (НЕ ОБЯЗАТЕЛЬНО)
                                       f'{config.domain}{settings.STATIC_URL}viber_bot_buttons/5x1/gray_light.png',
                                       # actionbody - ОТВЕТ (дописать ", 0" - прозрачный текст)
                                       f'{viber_user.once}&&service::{services[0].parent.parent.id}',
                                       ))
        else:
            buttons.append(button_back(f'<font size=22 color="#404040"><b>Назад</b></font>',
                                       # img - картинка (НЕ ОБЯЗАТЕЛЬНО)
                                       f'',
                                       # bgimg - картинка фона (НЕ ОБЯЗАТЕЛЬНО)
                                       f'{config.domain}{settings.STATIC_URL}viber_bot_buttons/5x1/gray_light.png',
                                       # actionbody - ОТВЕТ (дописать ", 0" - прозрачный текст)
                                       f'{viber_user.once}&&service',
                                       ))
        buttons.append(button_home(viber_user))
    else:
        services = Service.objects.get(id=service_id)
        text = f'Ви обрали "{services}".\nНадайте місце, де буде відбуватися послуга. Ви можете поширити свою геолокацію або вказати власноруч адресу по єтапно.'
        buttons.append(button(6, 1,  # Columns & Rows
                              f'<font size=22 color="#FFFFFF"><b>Надати геолокацію</b></font>',
                              # img - картинка (НЕ ОБЯЗАТЕЛЬНО)
                              f'{config.domain}{settings.STATIC_URL}viber_bot_buttons/geolocation.png',
                              # bgimg - картинка фона (НЕ ОБЯЗАТЕЛЬНО)
                              f'',
                              # actiontype - ТИП ОТВЕТА
                              'location-picker',
                              # actionbody - ОТВЕТ (дописать ", 0" - прозрачный текст)
                              f'{viber_user.once}&&service::{service_id}::location', 0
                              ))
        buttons.append(button(6, 1,  # Columns & Rows
                              f'<font size=22 color="#FFFFFF"><b>Вказати власноруч</b></font>',
                              # img - картинка (НЕ ОБЯЗАТЕЛЬНО)
                              f'{config.domain}{settings.STATIC_URL}viber_bot_buttons/geolocation_manual.png',
                              # bgimg - картинка фона (НЕ ОБЯЗАТЕЛЬНО)
                              f'',
                              # actiontype - ТИП ОТВЕТА
                              'reply',
                              # actionbody - ОТВЕТ (дописать ", 0" - прозрачный текст)
                              f'{viber_user.once}&&service::{service_id}::location_manual', 0
                              ))
        if services.parent:
            buttons.append(button_back(f'<font size=22 color="#404040"><b>Назад</b></font>',
                                       # img - картинка (НЕ ОБЯЗАТЕЛЬНО)
                                       f'',
                                       # bgimg - картинка фона (НЕ ОБЯЗАТЕЛЬНО)
                                       f'{config.domain}{settings.STATIC_URL}viber_bot_buttons/5x1/gray_light.png',
                                       # actionbody - ОТВЕТ (дописать ", 0" - прозрачный текст)
                                       f'{viber_user.once}&&service::{services.parent.id}',
                                       ))
        else:
            buttons.append(button_back(f'<font size=22 color="#404040"><b>Назад</b></font>',
                                       # img - картинка (НЕ ОБЯЗАТЕЛЬНО)
                                       f'',
                                       # bgimg - картинка фона (НЕ ОБЯЗАТЕЛЬНО)
                                       f'{config.domain}{settings.STATIC_URL}viber_bot_buttons/5x1/gray_light.png',
                                       # actionbody - ОТВЕТ (дописать ", 0" - прозрачный текст)
                                       f'{viber_user.once}&&service',
                                       ))
        buttons.append(button_home(viber_user))

    keyboard = keyboard_def(buttons, "hidden")
    return text, keyboard


# "Мої заявки"
def my_requests(viber_user, service_requests):
    buttons = []

    for request in service_requests:
        buttons.append(button(6, 1,  # Columns & Rows
                              f'<font size=22 color="#FFFFFF"><b>{request.number}</b></font>',
                              # img - картинка (НЕ ОБЯЗАТЕЛЬНО)
                              f'',
                              # bgimg - картинка фона (НЕ ОБЯЗАТЕЛЬНО)
                              f'{config.domain}{settings.STATIC_URL}viber_bot_buttons/6x1/green.png',
                              # actiontype - ТИП ОТВЕТА
                              'reply',
                              # actionbody - ОТВЕТ (дописать ", 0" - прозрачный текст)
                              f'{viber_user.once}&&my_request::{request.number}',
                              ))
    buttons.append(button_back(f'<font size=22 color="#404040"><b>Назад</b></font>',
                               # img - картинка (НЕ ОБЯЗАТЕЛЬНО)
                               f'',
                               # bgimg - картинка фона (НЕ ОБЯЗАТЕЛЬНО)
                               f'{config.domain}{settings.STATIC_URL}viber_bot_buttons/5x1/gray_light.png',
                               # actionbody - ОТВЕТ (дописать ", 0" - прозрачный текст)
                               f'{viber_user.once}&&service',
                               ))
    buttons.append(button_home(viber_user))

    keyboard = keyboard_def(buttons, "hidden")
    return keyboard


def my_request_cancel(viber_user, service_request):
    buttons = []
    buttons.append(button(6, 1,  # Columns & Rows
                          f'<font size=22 color="#FFFFFF"><b>Відмінити заявку</b></font>',
                          # img - картинка (НЕ ОБЯЗАТЕЛЬНО)
                          f'',
                          # bgimg - картинка фона (НЕ ОБЯЗАТЕЛЬНО)
                          f'{config.domain}{settings.STATIC_URL}viber_bot_buttons/6x1/green.png',
                          # actiontype - ТИП ОТВЕТА
                          'reply',
                          # actionbody - ОТВЕТ (дописать ", 0" - прозрачный текст)
                          f'{viber_user.once}&&my_request::{service_request.number}::cancel',
                          ))
    buttons.append(button_back(f'<font size=22 color="#404040"><b>Назад</b></font>',
                               # img - картинка (НЕ ОБЯЗАТЕЛЬНО)
                               f'',
                               # bgimg - картинка фона (НЕ ОБЯЗАТЕЛЬНО)
                               f'{config.domain}{settings.STATIC_URL}viber_bot_buttons/5x1/gray_light.png',
                               # actionbody - ОТВЕТ (дописать ", 0" - прозрачный текст)
                               f'{viber_user.once}&&my_requests',
                               ))
    buttons.append(button_home(viber_user))
    keyboard = keyboard_def(buttons, "hidden")
    return keyboard


def my_request_confirmation(viber_user, service_request):
    buttons = []
    buttons.append(button(6, 1,  # Columns & Rows
                          f'<font size=22 color="#FFFFFF"><b>Підтвердити майстра</b></font>',
                          # img - картинка (НЕ ОБЯЗАТЕЛЬНО)
                          f'',
                          # bgimg - картинка фона (НЕ ОБЯЗАТЕЛЬНО)
                          f'{config.domain}{settings.STATIC_URL}viber_bot_buttons/6x1/green.png',
                          # actiontype - ТИП ОТВЕТА
                          'reply',
                          # actionbody - ОТВЕТ (дописать ", 0" - прозрачный текст)
                          f'{viber_user.once}&&my_request::{service_request.number}::confirm',
                          ))
    buttons.append(button(6, 1,  # Columns & Rows
                          f'<font size=22 color="#FFFFFF"><b>Відхилити майстра</b></font>',
                          # img - картинка (НЕ ОБЯЗАТЕЛЬНО)
                          f'',
                          # bgimg - картинка фона (НЕ ОБЯЗАТЕЛЬНО)
                          f'{config.domain}{settings.STATIC_URL}viber_bot_buttons/6x1/green.png',
                          # actiontype - ТИП ОТВЕТА
                          'reply',
                          # actionbody - ОТВЕТ (дописать ", 0" - прозрачный текст)
                          f'{viber_user.once}&&my_request::{service_request.number}::reject',
                          ))
    buttons.append(button(6, 1,  # Columns & Rows
                          f'<font size=22 color="#FFFFFF"><b>Відмінити заявку</b></font>',
                          # img - картинка (НЕ ОБЯЗАТЕЛЬНО)
                          f'',
                          # bgimg - картинка фона (НЕ ОБЯЗАТЕЛЬНО)
                          f'{config.domain}{settings.STATIC_URL}viber_bot_buttons/6x1/green.png',
                          # actiontype - ТИП ОТВЕТА
                          'reply',
                          # actionbody - ОТВЕТ (дописать ", 0" - прозрачный текст)
                          f'{viber_user.once}&&my_request::{service_request.number}::cancel',
                          ))
    buttons.append(button_back(f'<font size=22 color="#404040"><b>Назад</b></font>',
                               # img - картинка (НЕ ОБЯЗАТЕЛЬНО)
                               f'',
                               # bgimg - картинка фона (НЕ ОБЯЗАТЕЛЬНО)
                               f'{config.domain}{settings.STATIC_URL}viber_bot_buttons/5x1/gray_light.png',
                               # actionbody - ОТВЕТ (дописать ", 0" - прозрачный текст)
                               f'{viber_user.once}&&my_requests',
                               ))
    buttons.append(button_home(viber_user))
    keyboard = keyboard_def(buttons, "hidden")
    return keyboard


def my_request_done(viber_user, service_request):
    buttons = []
    buttons.append(button(6, 1,  # Columns & Rows
                          f'<font size=22 color="#FFFFFF"><b>Оцінити майстра</b></font>',
                          # img - картинка (НЕ ОБЯЗАТЕЛЬНО)
                          f'',
                          # bgimg - картинка фона (НЕ ОБЯЗАТЕЛЬНО)
                          f'{config.domain}{settings.STATIC_URL}viber_bot_buttons/6x1/green.png',
                          # actiontype - ТИП ОТВЕТА
                          'reply',
                          # actionbody - ОТВЕТ (дописать ", 0" - прозрачный текст)
                          f'{viber_user.once}&&my_request::{service_request.number}::assessment',
                          ))
    buttons.append(button(6, 1,  # Columns & Rows
                          f'<font size=22 color="#FFFFFF"><b>Повідомити про проблему</b></font>',
                          # img - картинка (НЕ ОБЯЗАТЕЛЬНО)
                          f'',
                          # bgimg - картинка фона (НЕ ОБЯЗАТЕЛЬНО)
                          f'{config.domain}{settings.STATIC_URL}viber_bot_buttons/6x1/green.png',
                          # actiontype - ТИП ОТВЕТА
                          'reply',
                          # actionbody - ОТВЕТ (дописать ", 0" - прозрачный текст)
                          f'{viber_user.once}&&my_request::{service_request.number}::problem',
                          ))
    buttons.append(button_back(f'<font size=22 color="#404040"><b>Назад</b></font>',
                               # img - картинка (НЕ ОБЯЗАТЕЛЬНО)
                               f'',
                               # bgimg - картинка фона (НЕ ОБЯЗАТЕЛЬНО)
                               f'{config.domain}{settings.STATIC_URL}viber_bot_buttons/5x1/gray_light.png',
                               # actionbody - ОТВЕТ (дописать ", 0" - прозрачный текст)
                               f'{viber_user.once}&&my_requests',
                               ))
    buttons.append(button_home(viber_user))
    keyboard = keyboard_def(buttons, "hidden")
    return keyboard


def location_region_startswith(viber_user, message):
    buttons = []
    unique_initials = Position.objects.filter(type_code='O').annotate(initial=Left('name', 1)).order_by(
        'initial').values_list('initial', flat=True).distinct()
    unique_initials_count = unique_initials.count()
    sorted_unique_initials = sorted(unique_initials, key=collator.sort_key)

    if unique_initials_count:
        for unique_initial in sorted_unique_initials:
            buttons.append(button(1, 1,  # Columns & Rows
                                  f'<font size=26 color="#FFFFFF"><b>{unique_initial}</b></font>',
                                  # img - картинка (НЕ ОБЯЗАТЕЛЬНО)
                                  f'',
                                  # bgimg - картинка фона (НЕ ОБЯЗАТЕЛЬНО)
                                  f'{config.domain}{settings.STATIC_URL}viber_bot_buttons/1x1/green.png',
                                  # actiontype - ТИП ОТВЕТА
                                  'reply',
                                  # actionbody - ОТВЕТ (дописать ", 0" - прозрачный текст)
                                  f'{viber_user.once}&&{message}::{unique_initial}',
                                  ))

    number_lines = math.ceil(unique_initials_count / 6)
    number_required_buttons = number_lines * 6
    number_empty_buttons = number_required_buttons - unique_initials_count
    for _ in range(number_empty_buttons):
        buttons.append(silent_button(1, 1))

    message_split = message.split("::")
    back_result = "::".join(message_split[:-1])
    buttons.append(button_back(f'<font size=22 color="#404040"><b>Назад</b></font>',
                               # img - картинка (НЕ ОБЯЗАТЕЛЬНО)
                               f'',
                               # bgimg - картинка фона (НЕ ОБЯЗАТЕЛЬНО)
                               f'{config.domain}{settings.STATIC_URL}viber_bot_buttons/5x1/gray_light.png',
                               # actionbody - ОТВЕТ (дописать ", 0" - прозрачный текст)
                               f'{viber_user.once}&&{back_result}',
                               ))
    buttons.append(button_home(viber_user))

    keyboard = keyboard_def(buttons, "hidden")
    return keyboard


def location_region_picker(viber_user, message):
    buttons = []
    positions = Position.objects.filter(name__startswith=f'{message.split("::")[3]}', type_code='O')
    positions_count = positions.count()
    sorted_tree_queryset = sorted(positions, key=lambda x: collator.sort_key(x.name))

    for position in sorted_tree_queryset:
        buttons.append(button(6, 1,  # Columns & Rows
                              f'<font size=22 color="#FFFFFF"><b>{position.name}</b></font>',
                              # img - картинка (НЕ ОБЯЗАТЕЛЬНО)
                              f'',
                              # bgimg - картинка фона (НЕ ОБЯЗАТЕЛЬНО)
                              f'{config.domain}{settings.STATIC_URL}viber_bot_buttons/6x1/green.png',
                              # actiontype - ТИП ОТВЕТА
                              'reply',
                              # actionbody - ОТВЕТ (дописать ", 0" - прозрачный текст)
                              f'{viber_user.once}&&{message}::{position.id}',
                              ))

    message_split = message.split("::")
    back_result = "::".join(message_split[:-1])
    buttons.append(button_back(f'<font size=22 color="#404040"><b>Назад</b></font>',
                               # img - картинка (НЕ ОБЯЗАТЕЛЬНО)
                               f'',
                               # bgimg - картинка фона (НЕ ОБЯЗАТЕЛЬНО)
                               f'{config.domain}{settings.STATIC_URL}viber_bot_buttons/5x1/gray_light.png',
                               # actionbody - ОТВЕТ (дописать ", 0" - прозрачный текст)
                               f'{viber_user.once}&&{back_result}',
                               ))
    buttons.append(button_home(viber_user))

    keyboard = keyboard_def(buttons, "hidden")
    return keyboard


def location_populated_centre_startswith(viber_user, message):
    buttons = []
    region = Position.objects.get(id=message.split('::')[4])
    positions_filter = Q(type_code='M') | Q(type_code='T') | Q(type_code='C') | Q(type_code='X')
    unique_initials = region.get_descendants().filter(positions_filter).annotate(
        initial=Left('name', 1)).order_by('initial').values_list('initial', flat=True).distinct()
    unique_initials_count = unique_initials.count()
    sorted_unique_initials = sorted(unique_initials, key=collator.sort_key)

    if unique_initials_count:
        for unique_initial in sorted_unique_initials:
            buttons.append(button(1, 1,  # Columns & Rows
                                  f'<font size=26 color="#FFFFFF"><b>{unique_initial}</b></font>',
                                  # img - картинка (НЕ ОБЯЗАТЕЛЬНО)
                                  f'',
                                  # bgimg - картинка фона (НЕ ОБЯЗАТЕЛЬНО)
                                  f'{config.domain}{settings.STATIC_URL}viber_bot_buttons/1x1/green.png',
                                  # actiontype - ТИП ОТВЕТА
                                  'reply',
                                  # actionbody - ОТВЕТ (дописать ", 0" - прозрачный текст)
                                  f'{viber_user.once}&&{message}::{unique_initial}::1',
                                  ))

    number_lines = math.ceil(unique_initials_count / 6)
    number_required_buttons = number_lines * 6
    number_empty_buttons = number_required_buttons - unique_initials_count
    for _ in range(number_empty_buttons):
        buttons.append(silent_button(1, 1))

    message_split = message.split("::")
    back_result = "::".join(message_split[:-1])
    buttons.append(button_back(f'<font size=22 color="#404040"><b>Назад</b></font>',
                               # img - картинка (НЕ ОБЯЗАТЕЛЬНО)
                               f'',
                               # bgimg - картинка фона (НЕ ОБЯЗАТЕЛЬНО)
                               f'{config.domain}{settings.STATIC_URL}viber_bot_buttons/5x1/gray_light.png',
                               # actionbody - ОТВЕТ (дописать ", 0" - прозрачный текст)
                               f'{viber_user.once}&&{back_result}',
                               ))
    buttons.append(button_home(viber_user))

    keyboard = keyboard_def(buttons, "hidden")
    return keyboard


def location_populated_centre_picker(viber_user, message):
    buttons = []
    message_split = message.split("::")
    region = Position.objects.get(id=message_split[4])
    positions_filter = (Q(type_code='M') | Q(type_code='T') | Q(type_code='C') | Q(type_code='X')) & Q(
        name__startswith=message_split[5])
    positions = region.get_descendants().filter(positions_filter)
    sorted_tree_queryset = sorted(positions, key=lambda x: collator.sort_key(x.name))

    p = Paginator(sorted_tree_queryset, 20)
    page = p.page(message_split[6])
    message_without_page = "::".join(message_split[:-1])

    if page.has_previous():
        buttons.append(button(2, 1,  # Columns & Rows
                              f'<font size=22 color="#FFFFFF"><b>Перша</b></font>',
                              # img - картинка (НЕ ОБЯЗАТЕЛЬНО)
                              f'{config.domain}{settings.STATIC_URL}viber_bot_buttons/2x1_first_page.png',
                              # bgimg - картинка фона (НЕ ОБЯЗАТЕЛЬНО)
                              f'',
                              # actiontype - ТИП ОТВЕТА
                              'reply',
                              # actionbody - ОТВЕТ
                              f"{viber_user.once}&&{message_without_page}::1", 0
                              ))
        buttons.append(button(4, 1,  # Columns & Rows
                              f'<font size=22 color="#FFFFFF"><b>Попередня сторінка</b></font>',
                              # img - картинка (НЕ ОБЯЗАТЕЛЬНО)
                              f'{config.domain}{settings.STATIC_URL}viber_bot_buttons/6x1_previous_page.png',
                              # bgimg - картинка фона (НЕ ОБЯЗАТЕЛЬНО)
                              f'',
                              # actiontype - ТИП ОТВЕТА
                              'reply',
                              # actionbody - ОТВЕТ
                              f"{viber_user.once}&&{message_without_page}::{page.previous_page_number()}", 0
                              ))

    def location_buttons(name, title, id):
        button = {
            "Columns": 6,
            "Rows": 1,
            "Text": f'<font size=18 color="#FFFFFF"><b>{name}</b></font><br><font size=12 color="#FFFFFF"><b>{title}</b></font>',
            "Image": f'',
            "ImageScaleType": "fit",
            "BgMedia": f'{config.domain}{settings.STATIC_URL}viber_bot_buttons/6x1/green.png',
            "BgMediaScaleType": "fit",
            "BgColor": config.colorBg_button,
            "ActionType": "reply",
            "ActionBody": f"{viber_user.once}&&{message}::{id}"
        }
        return button

    if (region.id == 1 or region.name == 'Автономна Республіка Крим') and message_split[5] == "C":
        buttons.append(location_buttons('Сімферополь', 'Столиця', '2349'))
    elif (region.id == 2 or region.name == 'Вінницька') and message_split[5] == "В":
        buttons.append(location_buttons('Вінниця', 'Обласний центр', '2148'))
    elif (region.id == 3 or region.name == 'Волинська') and message_split[5] == "Л":
        buttons.append(location_buttons('Луцьк', 'Обласний центр', '2274'))
    elif (region.id == 4 or region.name == 'Дніпропетровська') and message_split[5] == "Д":
        buttons.append(location_buttons('Дніпро', 'Обласний центр', '2182'))
    elif (region.id == 5 or region.name == 'Донецька') and message_split[5] == "Д":
        buttons.append(location_buttons('Донецьк', 'Обласний центр', '2189'))
    elif (region.id == 6 or region.name == 'Житомирська') and message_split[5] == "Ж":
        buttons.append(location_buttons('Житомир', 'Обласний центр', '2200'))
    elif (region.id == 7 or region.name == 'Закарпатська') and message_split[5] == "У":
        buttons.append(location_buttons('Ужгород', 'Обласний центр', '2371'))
    elif (region.id == 8 or region.name == 'Запорізька') and message_split[5] == "З":
        buttons.append(location_buttons('Запоріжжя', 'Обласний центр', '2206'))
    elif (region.id == 9 or region.name == 'Івано-Франківська') and message_split[5] == "І":
        buttons.append(location_buttons('Івано-Франківськ', 'Обласний центр', '2220'))
    elif (region.id == 10 or region.name == 'Київська') and message_split[5] == "К":
        buttons.append(location_buttons('Київ', 'Столиця України', '2393'))
    elif (region.id == 11 or region.name == 'Кіровоградська') and message_split[5] == "К":
        buttons.append(location_buttons('Кропивницький', 'Обласний центр', '2265'))
    elif (region.id == 12 or region.name == 'Луганська') and message_split[5] == "Л":
        buttons.append(location_buttons('Луганськ', 'Обласний центр', '2273'))
    elif (region.id == 13 or region.name == 'Львівська') and message_split[5] == "Л":
        buttons.append(location_buttons('Львів', 'Обласний центр', '2276'))
    elif (region.id == 14 or region.name == 'Миколаївська') and message_split[5] == "М":
        buttons.append(location_buttons('Миколаїв', 'Обласний центр', '2284'))
    elif (region.id == 15 or region.name == 'Одеська') and message_split[5] == "О":
        buttons.append(location_buttons('Одеса', 'Обласний центр', '2311'))
    elif (region.id == 16 or region.name == 'Полтавська') and message_split[5] == "П":
        buttons.append(location_buttons('Полтава', 'Обласний центр', '2330'))
    elif (region.id == 17 or region.name == 'Рівненська') and message_split[5] == "Р":
        buttons.append(location_buttons('Рівне', 'Обласний центр', '2336'))
    elif (region.id == 18 or region.name == 'Сумська') and message_split[5] == "С":
        buttons.append(location_buttons('Суми', 'Обласний центр', '2365'))
    elif (region.id == 19 or region.name == 'Тернопільська') and message_split[5] == "Т":
        buttons.append(location_buttons('Тернопіль', 'Обласний центр', '2367'))
    elif (region.id == 20 or region.name == 'Харківська') and message_split[5] == "Х":
        buttons.append(location_buttons('Харків', 'Обласний центр', '2375'))
    elif (region.id == 21 or region.name == 'Херсонська') and message_split[5] == "Х":
        buttons.append(location_buttons('Херсон', 'Обласний центр', '2376'))
    elif (region.id == 22 or region.name == 'Хмельницька') and message_split[5] == "Х":
        buttons.append(location_buttons('Хмельницький', 'Обласний центр', '2377'))
    elif (region.id == 23 or region.name == 'Черкаська') and message_split[5] == "Ч":
        buttons.append(location_buttons('Черкаси', 'Обласний центр', '2382'))
    elif (region.id == 24 or region.name == 'Чернівецька') and message_split[5] == "Ч":
        buttons.append(location_buttons('Чернівці', 'Обласний центр', '2383'))
    elif (region.id == 25 or region.name == 'Чернігівська') and message_split[5] == "Ч":
        buttons.append(location_buttons('Чернігів', 'Обласний центр', '2384'))

    for position in page:
        buttons.append(button(6, 1,  # Columns & Rows
                              f'<font size=18 color="#FFFFFF"><b>{position.name}</b></font><br><font size=12 color="#FFFFFF"><b>{position.parent} громада</b></font>',
                              # img - картинка (НЕ ОБЯЗАТЕЛЬНО)
                              f'',
                              # bgimg - картинка фона (НЕ ОБЯЗАТЕЛЬНО)
                              f'{config.domain}{settings.STATIC_URL}viber_bot_buttons/6x1/green.png',
                              # actiontype - ТИП ОТВЕТА
                              'reply',
                              # actionbody - ОТВЕТ
                              f"{viber_user.once}&&{message}::{position.id}",
                              ))

    if page.has_next():
        buttons.append(button(4, 1,  # Columns & Rows
                              f'<font size=22 color="#FFFFFF"><b>Наступна сторінка</b></font>',
                              # img - картинка (НЕ ОБЯЗАТЕЛЬНО)
                              f'{config.domain}{settings.STATIC_URL}viber_bot_buttons/6x1_next_page.png',
                              # bgimg - картинка фона (НЕ ОБЯЗАТЕЛЬНО)
                              f'',
                              # actiontype - ТИП ОТВЕТА
                              'reply',
                              # actionbody - ОТВЕТ
                              f"{viber_user.once}&&{message_without_page}::{page.next_page_number()}", 0
                              ))
        buttons.append(button(2, 1,  # Columns & Rows
                              f'<font size=22 color="#FFFFFF"><b>Остання</b></font>',
                              # img - картинка (НЕ ОБЯЗАТЕЛЬНО)
                              f'{config.domain}{settings.STATIC_URL}viber_bot_buttons/2x1_last_page.png',
                              # bgimg - картинка фона (НЕ ОБЯЗАТЕЛЬНО)
                              f'',
                              # actiontype - ТИП ОТВЕТА
                              'reply',
                              # actionbody - ОТВЕТ
                              f"{viber_user.once}&&{message_without_page}::{p.num_pages}", 0
                              ))

    back_result = "::".join(message_split[:-2])
    buttons.append(button_back(f'<font size=22 color="#404040"><b>Назад</b></font>',
                               # img - картинка (НЕ ОБЯЗАТЕЛЬНО)
                               f'',
                               # bgimg - картинка фона (НЕ ОБЯЗАТЕЛЬНО)
                               f'{config.domain}{settings.STATIC_URL}viber_bot_buttons/5x1/gray_light.png',
                               # actionbody - ОТВЕТ (дописать ", 0" - прозрачный текст)
                               f'{viber_user.once}&&{back_result}',
                               ))
    buttons.append(button_home(viber_user))

    keyboard = keyboard_def(buttons, "hidden")
    return keyboard


# "Так або Ні"
def yes_no(viber_user, text):
    buttons = []
    buttons.append(
        button_img(3, 2, 'Ні', f'{config.domain}{settings.STATIC_URL}viber_bot_buttons/no.png', 'reply',
                   f"{viber_user.once}&&{text}::no"))
    buttons.append(
        button_img(3, 2, 'Так', f'{config.domain}{settings.STATIC_URL}viber_bot_buttons/yes.png', 'reply',
                   f"{viber_user.once}&&{text}::yes"))
    keyboard = keyboard_def(buttons, "hidden")
    return keyboard


# "До головного меню"
def start(viber_user):
    buttons = []
    buttons.append(button(6, 1,  # Columns & Rows
                          f'<font size=22 color="#404040"><b>До головного меню</b></font>',
                          # img - картинка (НЕ ОБЯЗАТЕЛЬНО)
                          f'',
                          # bgimg - картинка фона (НЕ ОБЯЗАТЕЛЬНО)
                          f'{config.domain}{settings.STATIC_URL}viber_bot_buttons/6x1/gray_light.png',
                          # actiontype - ТИП ОТВЕТА
                          'reply',
                          # actionbody - ОТВЕТ (дописать ", 0" - прозрачный текст)
                          f'{viber_user.once}&&start',
                          ))
    keyboard = keyboard_def(buttons, "hidden")
    return keyboard


# "Налаштування"
def setting(viber_user):
    buttons = []
    buttons.append(button(6, 1,  # Columns & Rows
                          f'<font size=22 color="#FFFFFF"><b>Стати майстром</b></font>',
                          # img - картинка (НЕ ОБЯЗАТЕЛЬНО)
                          f'{config.domain}{settings.STATIC_URL}viber_bot_buttons/6x1_master.png',
                          # bgimg - картинка фона (НЕ ОБЯЗАТЕЛЬНО)
                          f'',
                          # actiontype - ТИП ОТВЕТА
                          'reply',
                          # actionbody - ОТВЕТ (дописать ", 0" - прозрачный текст)
                          f'{viber_user.once}&&master_registration', 0
                          ))
    buttons.append(button(6, 1,  # Columns & Rows
                          f'<font size=22 color="#FFFFFF"><b>Змінити номер телефону</b></font>',
                          # img - картинка (НЕ ОБЯЗАТЕЛЬНО)
                          f'{config.domain}{settings.STATIC_URL}viber_bot_buttons/6x1_change_phone_number.png',
                          # bgimg - картинка фона (НЕ ОБЯЗАТЕЛЬНО)
                          f'',
                          # actiontype - ТИП ОТВЕТА
                          'reply',
                          # actionbody - ОТВЕТ (дописать ", 0" - прозрачный текст)
                          f'{viber_user.once}&&change_phone_number', 0
                          ))
    buttons.append(button_back(f'<font size=22 color="#404040"><b>Назад</b></font>',
                               # img - картинка (НЕ ОБЯЗАТЕЛЬНО)
                               f'',
                               # bgimg - картинка фона (НЕ ОБЯЗАТЕЛЬНО)
                               f'{config.domain}{settings.STATIC_URL}viber_bot_buttons/5x1/gray_light.png',
                               # actionbody - ОТВЕТ (дописать ", 0" - прозрачный текст)
                               f'{viber_user.once}&&start',
                               ))
    buttons.append(button_home(viber_user))
    keyboard = keyboard_def(buttons, "hidden")
    return keyboard


def phone_number(viber_user):
    buttons = []
    buttons.append(button(6, 1,  # Columns & Rows
                          f'<font size=22 color="#404040"><b>Надіслати номер</b></font>',
                          # img - картинка (НЕ ОБЯЗАТЕЛЬНО)
                          f'',
                          # bgimg - картинка фона (НЕ ОБЯЗАТЕЛЬНО)
                          f'{config.domain}{settings.STATIC_URL}viber_bot_buttons/6x1/gray_light.png',
                          # actiontype - ТИП ОТВЕТА
                          'share-phone',
                          # actionbody - ОТВЕТ (дописать ", 0" - прозрачный текст)
                          f'share-phone',
                          ))

    if viber_user.phone_number:
        buttons.append(button_back(f'<font size=22 color="#404040"><b>Назад</b></font>',
                                   # img - картинка (НЕ ОБЯЗАТЕЛЬНО)
                                   f'',
                                   # bgimg - картинка фона (НЕ ОБЯЗАТЕЛЬНО)
                                   f'{config.domain}{settings.STATIC_URL}viber_bot_buttons/5x1/gray_light.png',
                                   # actionbody - ОТВЕТ (дописать ", 0" - прозрачный текст)
                                   f'{viber_user.once}&&setting',
                                   ))
        buttons.append(button_home(viber_user))

    keyboard = keyboard_def(buttons, "regular")
    return keyboard


def start_input(viber_user):
    buttons = []
    buttons.append(button(6, 1,  # Columns & Rows
                          f'<font size=22 color="#404040"><b>До головного меню</b></font>',
                          # img - картинка (НЕ ОБЯЗАТЕЛЬНО)
                          f'',
                          # bgimg - картинка фона (НЕ ОБЯЗАТЕЛЬНО)
                          f'{config.domain}{settings.STATIC_URL}viber_bot_buttons/6x1/gray_light.png',
                          # actiontype - ТИП ОТВЕТА
                          'reply',
                          # actionbody - ОТВЕТ (дописать ", 0" - прозрачный текст)
                          f'{viber_user.once}&&start',
                          ))
    keyboard = keyboard_def(buttons, "regular")
    return keyboard


def skip(viber_user, text):
    buttons = []
    buttons.append(button(6, 1,  # Columns & Rows
                          f'<font size=22 color="#404040"><b>Пропустити</b></font>',
                          # img - картинка (НЕ ОБЯЗАТЕЛЬНО)
                          f'',
                          # bgimg - картинка фона (НЕ ОБЯЗАТЕЛЬНО)
                          f'{config.domain}{settings.STATIC_URL}viber_bot_buttons/6x1/gray_light.png',
                          # actiontype - ТИП ОТВЕТА
                          'reply',
                          # actionbody - ОТВЕТ (дописать ", 0" - прозрачный текст)
                          f'{viber_user.once}&&{text}::skip',
                          ))

    buttons.append(button(6, 1,  # Columns & Rows
                          f'<font size=22 color="#404040"><b>До головного меню</b></font>',
                          # img - картинка (НЕ ОБЯЗАТЕЛЬНО)
                          f'',
                          # bgimg - картинка фона (НЕ ОБЯЗАТЕЛЬНО)
                          f'{config.domain}{settings.STATIC_URL}viber_bot_buttons/6x1/gray_light.png',
                          # actiontype - ТИП ОТВЕТА
                          'reply',
                          # actionbody - ОТВЕТ (дописать ", 0" - прозрачный текст)
                          f'{viber_user.once}&&start',
                          ))

    keyboard = keyboard_def(buttons, "regular")
    return keyboard


# Погодження на реєстрацію для майстрів
def master_registration(viber_user):
    buttons = []
    buttons.append(button(6, 1,  # Columns & Rows
                          f'<font size=22 color="#404040"><b>Погоджуюсь</b></font>',
                          # img - картинка (НЕ ОБЯЗАТЕЛЬНО)
                          f'',
                          # bgimg - картинка фона (НЕ ОБЯЗАТЕЛЬНО)
                          f'{config.domain}{settings.STATIC_URL}viber_bot_buttons/6x1/gray_light.png',
                          # actiontype - ТИП ОТВЕТА
                          'open-url',
                          # actionbody - ОТВЕТ (дописать ", 0" - прозрачный текст)
                          f'{config.domain}/viber_bot/master_registration/{viber_user.viber_id}',
                          ))
    buttons.append(button_back(f'<font size=22 color="#404040"><b>Назад</b></font>',
                               # img - картинка (НЕ ОБЯЗАТЕЛЬНО)
                               f'',
                               # bgimg - картинка фона (НЕ ОБЯЗАТЕЛЬНО)
                               f'{config.domain}{settings.STATIC_URL}viber_bot_buttons/5x1/gray_light.png',
                               # actionbody - ОТВЕТ (дописать ", 0" - прозрачный текст)
                               f'{viber_user.once}&&setting',
                               ))
    buttons.append(button_home(viber_user))
    keyboard = keyboard_def(buttons, "hidden")
    return keyboard


def zero_to_five(viber_user, text):
    buttons = []
    buttons.append(button(1, 1,  # Columns & Rows
                          f'<font size=26 color="#FFFFFF"><b>1</b></font>',
                          # img - картинка (НЕ ОБЯЗАТЕЛЬНО)
                          f'',
                          # bgimg - картинка фона (НЕ ОБЯЗАТЕЛЬНО)
                          f'{config.domain}{settings.STATIC_URL}viber_bot_buttons/1x1/ff4e11.png',
                          # actiontype - ТИП ОТВЕТА
                          'reply',
                          # actionbody - ОТВЕТ (дописать ", 0" - прозрачный текст)
                          f'{viber_user.once}&&{text}::1',
                          ))
    buttons.append(button(1, 1,  # Columns & Rows
                          f'<font size=26 color="#FFFFFF"><b>2</b></font>',
                          # img - картинка (НЕ ОБЯЗАТЕЛЬНО)
                          f'',
                          # bgimg - картинка фона (НЕ ОБЯЗАТЕЛЬНО)
                          f'{config.domain}{settings.STATIC_URL}viber_bot_buttons/1x1/ff8e15.png',
                          # actiontype - ТИП ОТВЕТА
                          'reply',
                          # actionbody - ОТВЕТ (дописать ", 0" - прозрачный текст)
                          f'{viber_user.once}&&{text}::2',
                          ))
    buttons.append(button(1, 1,  # Columns & Rows
                          f'<font size=26 color="#FFFFFF"><b>3</b></font>',
                          # img - картинка (НЕ ОБЯЗАТЕЛЬНО)
                          f'',
                          # bgimg - картинка фона (НЕ ОБЯЗАТЕЛЬНО)
                          f'{config.domain}{settings.STATIC_URL}viber_bot_buttons/1x1/fab733.png',
                          # actiontype - ТИП ОТВЕТА
                          'reply',
                          # actionbody - ОТВЕТ (дописать ", 0" - прозрачный текст)
                          f'{viber_user.once}&&{text}::3',
                          ))
    buttons.append(button(1, 1,  # Columns & Rows
                          f'<font size=26 color="#FFFFFF"><b>4</b></font>',
                          # img - картинка (НЕ ОБЯЗАТЕЛЬНО)
                          f'',
                          # bgimg - картинка фона (НЕ ОБЯЗАТЕЛЬНО)
                          f'{config.domain}{settings.STATIC_URL}viber_bot_buttons/1x1/acb334.png',
                          # actiontype - ТИП ОТВЕТА
                          'reply',
                          # actionbody - ОТВЕТ (дописать ", 0" - прозрачный текст)
                          f'{viber_user.once}&&{text}::4',
                          ))
    buttons.append(button(2, 1,  # Columns & Rows
                          f'<font size=26 color="#FFFFFF"><b>5</b></font>',
                          # img - картинка (НЕ ОБЯЗАТЕЛЬНО)
                          f'',
                          # bgimg - картинка фона (НЕ ОБЯЗАТЕЛЬНО)
                          f'{config.domain}{settings.STATIC_URL}viber_bot_buttons/2x1/69b34c.png',
                          # actiontype - ТИП ОТВЕТА
                          'reply',
                          # actionbody - ОТВЕТ (дописать ", 0" - прозрачный текст)
                          f'{viber_user.once}&&{text}::5',
                          ))
    keyboard = keyboard_def(buttons, "hidden")
    return keyboard


def test():
    buttons = []
