import pytz

from . import config
from .models import ViberUser, Service, ServiceRequest
from django.db.models import F

def button_def(text, actiontype, actionbody):
    button = {
        "Columns": 6,
        "Rows": 1,
        "Text": f"<font size=25 color=\"{config.colorTxt_button}\"><b>{text}</b></font>",
        "BgColor": config.colorBg_button,
        "TextSize": "large",
        "TextHAlign": "center",
        "TextVAlign": "middle",
        "ActionType": actiontype,
        "ActionBody": actionbody,
    }
    return button


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


def keyboard_def(buttons, іnputfieldstate):
    keyboard = {
        "Type": "keyboard",
        "DefaultHeight": "false",
        "BgColor": config.colorBg_keyboard,
        "Buttons": buttons,
        "InputFieldState": іnputfieldstate
    }
    return keyboard


# Клавиатурки:
def start_menu(viber_user):
    buttons = []

    service_requests = ServiceRequest.objects.filter(executors=viber_user)
    count_service_requests = len(service_requests)
    if service_requests:
        buttons.append(button_def(f'Заявки ({count_service_requests})', 'reply', 'master_service_requests'))

    buttons.append(button_img(6, 1, 'Послуги', 'http://127.0.0.1:8000/media/viber_bot_buttons/main_service.png', 'reply', 'service'))
    buttons.append(button_img(6, 1, 'Магазин', 'http://127.0.0.1:8000/media/viber_bot_buttons/main_market.png', 'open-url', 'https://market.104.ua/ua/'))
    buttons.append(button_img(6, 1, 'Налаштування', 'http://127.0.0.1:8000/media/viber_bot_buttons/main_settings.png', 'reply', 'setting'))

    keyboard = keyboard_def(buttons, "hidden")
    return keyboard


def service_0():
    buttons = []
    services = Service.objects.filter(parent__isnull=True).order_by('priority')
    for service in services:
        buttons.append(button_img(service.columns, service.rows, f"{service.name}", f"{config.domain}{service.image.url}", 'reply', f"service::{service.id}"))
    buttons.append(button_img(6, 1, 'Стан заявок', "http://127.0.0.1:8000/media/viber_bot_buttons/status_service_request.png", 'reply', "status_service_request"))
    buttons.append(button_img(6, 1, 'Назад', "http://127.0.0.1:8000/media/viber_bot_buttons/main_back.png", 'reply', "start"))
    keyboard = keyboard_def(buttons, "hidden")
    return keyboard


def service_1(service_id):
    buttons = []
    services = Service.objects.filter(parent=service_id).order_by('priority')
    if services:
        text = f'Ви обрали {services[0].parent}. Оберіть послугу.'

        for service in services:
            buttons.append(button_img(service.columns, service.rows, f"{service.name}", f"{config.domain}{service.image.url}", 'reply', f"service::{service.id}"))
        # Додавання кнопки "назад"
        if services[0].parent.parent:
            buttons.append(button_img(6, 1, 'Назад', "http://127.0.0.1:8000/media/viber_bot_buttons/main_back.png", 'reply', f"service::{services[0].parent.parent.id}"))
        else:
            buttons.append(button_img(6, 1, 'Назад', "http://127.0.0.1:8000/media/viber_bot_buttons/main_back.png", 'reply', "service"))
    else:
        services = Service.objects.get(id=service_id)
        text = f'Ви обрали {services}.\nНадайте місце де буде відбуватися послуга.'
        buttons.append(button_img(6, 1, 'Надати геолокацію', "http://127.0.0.1:8000/media/viber_bot_buttons/geolocation.png", "location-picker", f"service::{service_id}::location"))
        if services.parent:
            buttons.append(button_img(6, 1, 'Назад', "http://127.0.0.1:8000/media/viber_bot_buttons/main_back.png", 'reply', f"service::{services.parent.id}"))
        else:
            buttons.append(button_img(6, 1, 'Назад', "http://127.0.0.1:8000/media/viber_bot_buttons/main_back.png", 'reply', "service"))

    keyboard = keyboard_def(buttons, "hidden")
    return text, keyboard


def yes_no(text):
    buttons = []
    buttons.append(button_img(3, 2, 'Ні', "http://127.0.0.1:8000/media/viber_bot_buttons/no.png", 'reply', f"{text}::no"))
    buttons.append(button_img(3, 2, 'Так', "http://127.0.0.1:8000/media/viber_bot_buttons/yes.png", 'reply', f"{text}::yes"))
    keyboard = keyboard_def(buttons, "hidden")
    return keyboard


def start():
    buttons = []
    buttons.append(button_img(6, 1, 'До головного меню', "http://127.0.0.1:8000/media/viber_bot_buttons/main.png", 'reply', "start"))
    keyboard = keyboard_def(buttons, "hidden")
    return keyboard


def setting():
    buttons = []
    buttons.append(button_img(6, 1, 'Стати майстром', "http://127.0.0.1:8000/media/viber_bot_buttons/master.png", 'reply', "master_registration"))
    buttons.append(button_img(6, 1, 'Змінити мову', "http://127.0.0.1:8000/media/viber_bot_buttons/language.png", 'reply', "change_language"))
    buttons.append(button_img(6, 1, 'Назад', "http://127.0.0.1:8000/media/viber_bot_buttons/main_back.png", 'reply', "start"))
    buttons.append(button_def('test', 'reply', 'test'))
    keyboard = keyboard_def(buttons, "hidden")
    return keyboard


def master_registration(viber_id):
    buttons = []
    buttons.append(button_img(6, 1, 'Погоджуюсь', "http://127.0.0.1:8000/media/viber_bot_buttons/agree.png", "open-url", f"http://127.0.0.1:8000/viber_bot/master_registration/{viber_id}"))
    buttons.append(button_img(6, 1, 'До головного меню', "http://127.0.0.1:8000/media/viber_bot_buttons/main.png", 'reply', "start"))
    keyboard = keyboard_def(buttons, "hidden")
    return keyboard


def master_service_requests(service_requests):
    buttons = []
    for request in service_requests:
        buttons.append(button_def(f'{request.number}', 'reply', f'master_service_request::{request.number}'))
    buttons.append(button_img(6, 1, 'Назад', "http://127.0.0.1:8000/media/viber_bot_buttons/main_back.png", 'reply', "start"))
    keyboard = keyboard_def(buttons, "hidden")
    return keyboard

def master_service_request(service_request):
    buttons = []
    buttons.append(button_def(f'Взяти в роботу', 'reply', f'master_service_request::{service_request.number}::yes'))
    buttons.append(button_img(6, 1, 'Назад', "http://127.0.0.1:8000/media/viber_bot_buttons/main_back.png", 'reply', "master_service_requests"))
    keyboard = keyboard_def(buttons, "hidden")
    return keyboard