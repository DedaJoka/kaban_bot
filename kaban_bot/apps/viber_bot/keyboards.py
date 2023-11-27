import pytz

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

    # Київська
    if region.id == 24:
        buttons.append(button(6, 1,  # Columns & Rows
                              f'<font size=18 color="#FFFFFF"><b>Київ</b></font><br><font size=12 color="#FFFFFF"><b>Столиця України</b></font>',
                              # img - картинка (НЕ ОБЯЗАТЕЛЬНО)
                              f'',
                              # bgimg - картинка фона (НЕ ОБЯЗАТЕЛЬНО)
                              f'{config.domain}{settings.STATIC_URL}viber_bot_buttons/6x1/green.png',
                              # actiontype - ТИП ОТВЕТА
                              'reply',
                              # actionbody - ОТВЕТ
                              f"{viber_user.once}&&{message}::7",
                              ))
    elif region.id == 49:
        buttons.append(button(6, 1,  # Columns & Rows
                              f'<font size=18 color="#FFFFFF"><b>Київ</b></font><br><font size=12 color="#FFFFFF"><b>Столиця України</b></font>',
                              # img - картинка (НЕ ОБЯЗАТЕЛЬНО)
                              f'',
                              # bgimg - картинка фона (НЕ ОБЯЗАТЕЛЬНО)
                              f'{config.domain}{settings.STATIC_URL}viber_bot_buttons/6x1/green.png',
                              # actiontype - ТИП ОТВЕТА
                              'reply',
                              # actionbody - ОТВЕТ
                              f"{viber_user.once}&&{message}::7",
                              ))

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
    buttons.append(
        button_img(6, 1, 'Стати майстром', f'{config.domain}{settings.STATIC_URL}viber_bot_buttons/master.png', 'reply',
                   f'{viber_user.once}&&master_registration'))
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
                          f'<font size=22 color="#404040"><b>Пропустить</b></font>',
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
