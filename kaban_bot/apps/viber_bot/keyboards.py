import pytz

from datetime import date, datetime, timedelta
from . import config
from django.conf import settings
from .models import ViberUser, Service, ServiceRequest
from django.db.models import F, Q
from pyuca import Collator
from django.core.paginator import Paginator

collator = Collator()


def button_def(text, actiontype, actionbody, bgcolor):
    button = {
        "Columns": 6,
        "Rows": 1,
        "Text": f"<font size=25 color=\"{config.colorTxt_button}\"><b>{text}</b></font>",
        "BgColor": bgcolor,
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


def button_img_text(columns, rows, text, text_color, img, actiontype, actionbody):
    button = {
        "Columns": columns,
        "Rows": rows,
        "Text": f"<font size=22 color=\"{text_color}\"><b>{text}</b></font>",
        "Image": img,
        "ImageScaleType": "fit",
        "BgColor": config.colorBg_button,
        "ActionType": actiontype,
        "ActionBody": actionbody,
    }
    return button


def button(columns, rows, text, img, bgimg, actiontype, actionbody):
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
    }
    return button


# buttons.append(button(6, 1, # Columns & Rows
#                       # text
#                       f'<font size=22 color="#FFFFFF"><b>СюдаПисатьТекст</b></font>',
#                       # img - картинка (НЕ ОБЯЗАТЕЛЬНО)
#                       f'{config.domain}{settings.STATIC_URL}viber_bot_buttons/6x1_green.png',
#                       # bgimg - картинка фона (НЕ ОБЯЗАТЕЛЬНО)
#                       f'{config.domain}{settings.STATIC_URL}viber_bot_buttons/6x1_green.png',
#                       # actiontype - ТИП ОТВЕТА
#                       'reply',
#                       # actionbody - ОТВЕТ
#                       f"СюдаПистьОтвет"
#                       ))

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

    if viber_user.executor:
        buttons.append(
            button_img(6, 1, 'Заявки', f'{config.domain}{settings.STATIC_URL}viber_bot_buttons/master_requests.png',
                       'reply', 'master_requests'))

    buttons.append(
        button_img(6, 1, 'Послуги', f'{config.domain}{settings.STATIC_URL}viber_bot_buttons/main_service.png', 'reply',
                   'service'))
    buttons.append(button_img(6, 1, 'Магазин', f'{config.domain}{settings.STATIC_URL}viber_bot_buttons/main_market.png',
                              'open-url', 'https://ecotherm.com.ua/'))
    buttons.append(
        button_img(6, 1, 'Налаштування', f'{config.domain}{settings.STATIC_URL}viber_bot_buttons/main_settings.png',
                   'reply', 'setting'))
    if viber_user.system_administrator:
        buttons.append(button_def('test', 'reply', 'test', config.colorBg_button))

    keyboard = keyboard_def(buttons, "hidden")
    return keyboard


# МАСТЕРОВ:

# "Заявки" для майстрів
def master_requests(viber_user):
    buttons = []

    service_requests = ServiceRequest.objects.filter(executors=viber_user, status_code=4)
    count_service_requests = len(service_requests)
    buttons.append(button_img_text(6, 1, f'Доступні заявки ({count_service_requests})', '#ffffff',
                                   f'{config.domain}{settings.STATIC_URL}viber_bot_buttons/6x1_blue.png', 'reply',
                                   'master_service_requests_available'))

    confirmed_service_requests = ServiceRequest.objects.filter(executors=viber_user, status_code=6)
    count_confirmed_service_requests = len(confirmed_service_requests)
    buttons.append(button_img_text(6, 1, f'Підтверджені заявки ({count_confirmed_service_requests})', '##1e1e1e',
                                   f'{config.domain}{settings.STATIC_URL}viber_bot_buttons/6x1_yellow.png', 'reply',
                                   'master_service_requests_confirmed'))

    buttons.append(button_img_text(6, 1, f'До головного меню', '#1e1e1e',
                                   f'{config.domain}{settings.STATIC_URL}viber_bot_buttons/6x1_gray.png', 'reply',
                                   'start'))

    keyboard = keyboard_def(buttons, "hidden")
    return keyboard


# "Доступні заявки" для майстрів
def master_service_requests(prefix, service_requests):
    buttons = []
    for request in service_requests:
        buttons.append(button_img_text(6, 1, f'{request.number}', '#ffffff',
                                       f'{config.domain}{settings.STATIC_URL}viber_bot_buttons/6x1_blue.png', 'reply',
                                       f'master_service_request_{prefix}::{request.number}'))
    buttons.append(button_img_text(6, 1, f'Назад', '#1e1e1e',
                                   f'{config.domain}{settings.STATIC_URL}viber_bot_buttons/6x1_gray.png', 'reply',
                                   f'master_requests'))
    keyboard = keyboard_def(buttons, "hidden")
    return keyboard


# Конкретна заявка для майстрів
def master_service_request(prefix, service_request):
    buttons = []
    if prefix == 'available':
        buttons.append(button_img_text(6, 1, f'Відгукнутися', '#ffffff',
                                       f'{config.domain}{settings.STATIC_URL}viber_bot_buttons/6x1_blue.png', 'reply',
                                       f'master_service_request::{service_request.number}::respond'))
    elif prefix == 'confirmed':
        buttons.append(button_img_text(6, 1, f'Позначити як виконану', '#ffffff',
                                       f'{config.domain}{settings.STATIC_URL}viber_bot_buttons/6x1_blue.png', 'reply',
                                       f'master_service_request::{service_request.number}::done'))
        buttons.append(button_img_text(6, 1, f'Повідомити про проблему', '#ffffff',
                                       f'{config.domain}{settings.STATIC_URL}viber_bot_buttons/6x1_blue.png', 'reply',
                                       f'master_service_request::{service_request.number}::problem'))
    buttons.append(button_img_text(6, 1, f'Назад', '#1e1e1e',
                                   f'{config.domain}{settings.STATIC_URL}viber_bot_buttons/6x1_gray.png', 'reply',
                                   f'master_service_requests_{prefix}'))

    keyboard = keyboard_def(buttons, "hidden")
    return keyboard


# Погодження на реєстрацію для майстрів
def master_registration(viber_id):
    buttons = []
    buttons.append(
        button_img(6, 1, 'Погоджуюсь', f'{config.domain}{settings.STATIC_URL}viber_bot_buttons/agree.png', "open-url",
                   f'{config.domain}/viber_bot/master_registration/{viber_id}'))
    buttons.append(
        button_img(6, 1, 'До головного меню', f'{config.domain}{settings.STATIC_URL}viber_bot_buttons/main.png',
                   'reply', "start"))
    keyboard = keyboard_def(buttons, "hidden")
    return keyboard


# КЛИЕНТОВ:

# "Послуги"
def service_0():
    buttons = []
    services = Service.objects.filter(parent__isnull=True).order_by('priority')
    for service in services:
        buttons.append(
            button_img(service.columns, service.rows, f"{service.name}", f"{config.domain}{service.image.url}", 'reply',
                       f"service::{service.id}"))
    buttons.append(
        button_img(6, 1, 'Мої заявки', f'{config.domain}{settings.STATIC_URL}viber_bot_buttons/my_requests.png',
                   'reply', "my_requests"))
    buttons.append(
        button_img(6, 1, 'Назад', f'{config.domain}{settings.STATIC_URL}viber_bot_buttons/main_back.png', 'reply',
                   "start"))
    keyboard = keyboard_def(buttons, "hidden")
    return keyboard


# "Послуги дочірні"
def service_1(service_id):
    buttons = []
    services = Service.objects.filter(parent=service_id).order_by('priority')
    if services:
        text = f'Ви обрали "{services[0].parent}". Оберіть послугу.'

        for service in services:
            buttons.append(
                button_img(service.columns, service.rows, f"{service.name}", f"{config.domain}{service.image.url}",
                           'reply', f"service::{service.id}"))
        # Додавання кнопки "назад"
        if services[0].parent.parent:
            buttons.append(
                button_img(6, 1, 'Назад', f'{config.domain}{settings.STATIC_URL}viber_bot_buttons/main_back.png',
                           'reply', f"service::{services[0].parent.parent.id}"))
        else:
            buttons.append(
                button_img(6, 1, 'Назад', f'{config.domain}{settings.STATIC_URL}viber_bot_buttons/main_back.png',
                           'reply', "service"))
    else:
        services = Service.objects.get(id=service_id)
        text = f'Ви обрали "{services}".\nНадайте місце, де буде відбуватися послуга. Ви можете надати свою геолокацію або ввести адресу по єтапно.'
        buttons.append(button_img(6, 1, 'Надати геолокацію',
                                  f'{config.domain}{settings.STATIC_URL}viber_bot_buttons/geolocation.png',
                                  "location-picker", f"service::{service_id}::location"))
        buttons.append(button_img(6, 1, 'Вказати власноруч',
                                  f'{config.domain}{settings.STATIC_URL}viber_bot_buttons/geolocation_manual.png',
                                  "reply", f"service::{service_id}::location_manual"))
        if services.parent:
            buttons.append(
                button_img(6, 1, 'Назад', f'{config.domain}{settings.STATIC_URL}viber_bot_buttons/main_back.png',
                           'reply', f"service::{services.parent.id}"))
        else:
            buttons.append(
                button_img(6, 1, 'Назад', f'{config.domain}{settings.STATIC_URL}viber_bot_buttons/main_back.png',
                           'reply', "service"))

    keyboard = keyboard_def(buttons, "hidden")
    return text, keyboard


# "Мої заявки"
def my_requests(viber_user):
    buttons = []
    fourteen_days_ago = datetime.now() - timedelta(days=14)
    excluded_status_codes = [3, 7, 8, 9]
    service_requests = ServiceRequest.objects.filter(
        Q(customer=viber_user) &
        ~Q(status_code__in=excluded_status_codes) &
        Q(modifiedon__gte=fourteen_days_ago)
    )

    for request in service_requests:
        buttons.append(button_img_text(6, 1, f'{request.number}', '#ffffff',
                                       f'{config.domain}{settings.STATIC_URL}viber_bot_buttons/6x1_green.png', 'reply',
                                       f'my_request::{request.number}'))
    buttons.append(button_img_text(6, 1, f'Назад', '#1e1e1e',
                                   f'{config.domain}{settings.STATIC_URL}viber_bot_buttons/6x1_gray.png', 'reply',
                                   'service'))
    keyboard = keyboard_def(buttons, "hidden")
    return keyboard


def my_request_cancel(service_request):
    buttons = []
    buttons.append(button_img_text(6, 1, f'Відмінити заявку', '#ffffff',
                                   f'{config.domain}{settings.STATIC_URL}viber_bot_buttons/6x1_green.png', 'reply',
                                   f'my_request::{service_request.number}::cancel'))
    buttons.append(button_img_text(6, 1, f'Назад', '#1e1e1e',
                                   f'{config.domain}{settings.STATIC_URL}viber_bot_buttons/6x1_gray.png', 'reply',
                                   f'my_requests'))
    keyboard = keyboard_def(buttons, "hidden")
    return keyboard


def my_request_confirmation(service_request):
    buttons = []
    buttons.append(button_img_text(6, 1, f'Підтвердити майстра', '#ffffff',
                                   f'{config.domain}{settings.STATIC_URL}viber_bot_buttons/6x1_green.png', 'reply',
                                   f'my_request::{service_request.number}::confirm'))
    buttons.append(button_img_text(6, 1, f'Відхилити майстра', '#ffffff',
                                   f'{config.domain}{settings.STATIC_URL}viber_bot_buttons/6x1_green.png', 'reply',
                                   f'my_request::{service_request.number}::reject'))
    buttons.append(button_img_text(6, 1, f'Відмінити заявку', '#ffffff',
                                   f'{config.domain}{settings.STATIC_URL}viber_bot_buttons/6x1_green.png', 'reply',
                                   f'my_request::{service_request.number}::cancel'))
    buttons.append(button_img_text(6, 1, f'Назад', '#1e1e1e',
                                   f'{config.domain}{settings.STATIC_URL}viber_bot_buttons/6x1_gray.png', 'reply',
                                   f'my_requests'))
    keyboard = keyboard_def(buttons, "hidden")
    return keyboard


def my_request_done(service_request):
    buttons = []
    buttons.append(button_img_text(6, 1, f'Оцінити майстра', '#ffffff',
                                   f'{config.domain}{settings.STATIC_URL}viber_bot_buttons/6x1_green.png', 'reply',
                                   f'my_request::{service_request.number}::assessment'))
    buttons.append(button_img_text(6, 1, f'Повідомити про проблему', '#ffffff',
                                   f'{config.domain}{settings.STATIC_URL}viber_bot_buttons/6x1_green.png', 'reply',
                                   f'my_request::{service_request.number}::problem'))
    buttons.append(button_img_text(6, 1, f'Назад', '#1e1e1e',
                                   f'{config.domain}{settings.STATIC_URL}viber_bot_buttons/6x1_gray.png', 'reply',
                                   f'my_requests'))
    keyboard = keyboard_def(buttons, "hidden")
    return keyboard


def location_region_startswith(unique_initials, message_text):
    buttons = []
    unique_initials_count = unique_initials.count()
    sorted_unique_initials = sorted(unique_initials, key=collator.sort_key)
    if unique_initials_count:
        for unique_initial in sorted_unique_initials:
            buttons.append(button(1, 1,  # Columns & Rows
                                  # text
                                  f'<font size=22 color="#FFFFFF"><b>{unique_initial}</b></font>',
                                  # img - картинка (НЕ ОБЯЗАТЕЛЬНО)
                                  f'',
                                  # bgimg - картинка фона (НЕ ОБЯЗАТЕЛЬНО)
                                  f'{config.domain}{settings.STATIC_URL}viber_bot_buttons/1x1/69b34c.png',
                                  # actiontype - ТИП ОТВЕТА
                                  'reply',
                                  # actionbody - ОТВЕТ
                                  f"{message_text}::{unique_initial}"
                                  ))

    text_split = message_text.split("::")
    back_result = "::".join(text_split[:-1])
    buttons.append(button(6, 1,  # Columns & Rows
                          # text
                          f'<font size=22 color="#404040"><b>Назад</b></font>',
                          # img - картинка (НЕ ОБЯЗАТЕЛЬНО)
                          f'',
                          # bgimg - картинка фона (НЕ ОБЯЗАТЕЛЬНО)
                          f'{config.domain}{settings.STATIC_URL}viber_bot_buttons/6x1_gray.png',
                          # actiontype - ТИП ОТВЕТА
                          'reply',
                          # actionbody - ОТВЕТ
                          f"{back_result}"
                          ))

    keyboard = keyboard_def(buttons, "hidden")
    return keyboard


def location_region_picker(positions, message_text):
    buttons = []
    positions_count = positions.count()
    sorted_tree_queryset = sorted(positions, key=lambda x: collator.sort_key(x.name))

    for position in sorted_tree_queryset:
        buttons.append(button(6, 1,  # Columns & Rows
                              # text
                              f'<font size=22 color="#FFFFFF"><b>{position.name}</b></font>',
                              # img - картинка (НЕ ОБЯЗАТЕЛЬНО)
                              f'',
                              # bgimg - картинка фона (НЕ ОБЯЗАТЕЛЬНО)
                              f'{config.domain}{settings.STATIC_URL}viber_bot_buttons/6x1_green.png',
                              # actiontype - ТИП ОТВЕТА
                              'reply',
                              # actionbody - ОТВЕТ
                              f"{message_text}::{position.id}"
                              ))

    text_split = message_text.split("::")
    back_result = "::".join(text_split[:-1])
    buttons.append(button(6, 1,  # Columns & Rows
                          # text
                          f'<font size=22 color="#404040"><b>Назад</b></font>',
                          # img - картинка (НЕ ОБЯЗАТЕЛЬНО)
                          f'',
                          # bgimg - картинка фона (НЕ ОБЯЗАТЕЛЬНО)
                          f'{config.domain}{settings.STATIC_URL}viber_bot_buttons/6x1_gray.png',
                          # actiontype - ТИП ОТВЕТА
                          'reply',
                          # actionbody - ОТВЕТ
                          f"{back_result}"
                          ))

    keyboard = keyboard_def(buttons, "hidden")
    return keyboard


def location_populated_centre_startswith(unique_initials, message_text):
    buttons = []
    unique_initials_count = unique_initials.count()
    sorted_unique_initials = sorted(unique_initials, key=collator.sort_key)
    if unique_initials_count:
        for unique_initial in sorted_unique_initials:
            buttons.append(button(1, 1,  # Columns & Rows
                                  # text
                                  f'<font size=22 color="#FFFFFF"><b>{unique_initial}</b></font>',
                                  # img - картинка (НЕ ОБЯЗАТЕЛЬНО)
                                  f'',
                                  # bgimg - картинка фона (НЕ ОБЯЗАТЕЛЬНО)
                                  f'{config.domain}{settings.STATIC_URL}viber_bot_buttons/1x1/69b34c.png',
                                  # actiontype - ТИП ОТВЕТА
                                  'reply',
                                  # actionbody - ОТВЕТ
                                  f"{message_text}::{unique_initial}::1"
                                  ))

    text_split = message_text.split("::")
    back_result = "::".join(text_split[:-1])
    buttons.append(button(6, 1,  # Columns & Rows
                          # text
                          f'<font size=22 color="#404040"><b>Назад</b></font>',
                          # img - картинка (НЕ ОБЯЗАТЕЛЬНО)
                          f'',
                          # bgimg - картинка фона (НЕ ОБЯЗАТЕЛЬНО)
                          f'{config.domain}{settings.STATIC_URL}viber_bot_buttons/6x1_gray.png',
                          # actiontype - ТИП ОТВЕТА
                          'reply',
                          # actionbody - ОТВЕТ
                          f"{back_result}"
                          ))

    keyboard = keyboard_def(buttons, "hidden")
    return keyboard


def location_populated_centre_picker(positions, message_text):
    buttons = []
    sorted_tree_queryset = sorted(positions, key=lambda x: collator.sort_key(x.name))
    p = Paginator(sorted_tree_queryset, 20)
    page = p.page(message_text.split('::')[6])
    message_text_split = message_text.split("::")
    message_text_without_page = "::".join(message_text_split[:-1])

    if page.has_previous():
        buttons.append(button(6, 1,  # Columns & Rows
                              # text
                              f'<font size=22 color="#FFFFFF"><b>⬅ Попередня сторінка</b></font>',
                              # img - картинка (НЕ ОБЯЗАТЕЛЬНО)
                              f'',
                              # bgimg - картинка фона (НЕ ОБЯЗАТЕЛЬНО)
                              f'{config.domain}{settings.STATIC_URL}viber_bot_buttons/6x1_green.png',
                              # actiontype - ТИП ОТВЕТА
                              'reply',
                              # actionbody - ОТВЕТ
                              f"{message_text_without_page}::{page.previous_page_number()}"
                              ))

    for position in page:
        buttons.append(button(6, 1,  # Columns & Rows
                              # text
                              f'<font size=18 color="#FFFFFF"><b>{position.name}</b></font><br><font size=12 color="#FFFFFF"><b>{position.parent} громада</b></font>',
                              # img - картинка (НЕ ОБЯЗАТЕЛЬНО)
                              f'',
                              # bgimg - картинка фона (НЕ ОБЯЗАТЕЛЬНО)
                              f'{config.domain}{settings.STATIC_URL}viber_bot_buttons/6x1_green.png',
                              # actiontype - ТИП ОТВЕТА
                              'reply',
                              # actionbody - ОТВЕТ
                              f"{message_text}::{position.id}"
                              ))

    if page.has_next():
        buttons.append(button(6, 1,  # Columns & Rows
                              # text
                              f'<font size=22 color="#FFFFFF"><b>Наступна сторінка ➡</b></font>',
                              # img - картинка (НЕ ОБЯЗАТЕЛЬНО)
                              f'',
                              # bgimg - картинка фона (НЕ ОБЯЗАТЕЛЬНО)
                              f'{config.domain}{settings.STATIC_URL}viber_bot_buttons/6x1_green.png',
                              # actiontype - ТИП ОТВЕТА
                              'reply',
                              # actionbody - ОТВЕТ
                              f"{message_text_without_page}::{page.next_page_number()}"
                              ))

    back_result = "::".join(message_text_split[:-2])
    buttons.append(button(6, 1,  # Columns & Rows
                          # text
                          f'<font size=22 color="#404040"><b>Назад</b></font>',
                          # img - картинка (НЕ ОБЯЗАТЕЛЬНО)
                          f'',
                          # bgimg - картинка фона (НЕ ОБЯЗАТЕЛЬНО)
                          f'{config.domain}{settings.STATIC_URL}viber_bot_buttons/6x1_gray.png',
                          # actiontype - ТИП ОТВЕТА
                          'reply',
                          # actionbody - ОТВЕТ
                          f"{back_result}"
                          ))

    keyboard = keyboard_def(buttons, "hidden")
    return keyboard


# "Так або Ні"
def yes_no(text):
    buttons = []
    buttons.append(
        button_img(3, 2, 'Ні', f'{config.domain}{settings.STATIC_URL}viber_bot_buttons/no.png', 'reply', f"{text}::no"))
    buttons.append(button_img(3, 2, 'Так', f'{config.domain}{settings.STATIC_URL}viber_bot_buttons/yes.png', 'reply',
                              f"{text}::yes"))
    keyboard = keyboard_def(buttons, "hidden")
    return keyboard


# "До головного меню"
def start():
    buttons = []
    buttons.append(
        button_img(6, 1, 'До головного меню', f'{config.domain}{settings.STATIC_URL}viber_bot_buttons/main.png',
                   'reply', "start"))
    keyboard = keyboard_def(buttons, "hidden")
    return keyboard


# "Налаштування"
def setting():
    buttons = []
    buttons.append(
        button_img(6, 1, 'Стати майстром', f'{config.domain}{settings.STATIC_URL}viber_bot_buttons/master.png', 'reply',
                   "master_registration"))
    # buttons.append(button_img(6, 1, 'Змінити мову', f'{config.domain}{settings.STATIC_URL}viber_bot_buttons/language.png', 'reply', "change_language"))
    buttons.append(button_img(6, 1, 'Змінити номер телефону',
                              f'{config.domain}{settings.STATIC_URL}viber_bot_buttons/change_phone_number_1.png',
                              'reply', "change_phone_number"))
    buttons.append(
        button_img(6, 1, 'Назад', f'{config.domain}{settings.STATIC_URL}viber_bot_buttons/main_back.png', 'reply',
                   "start"))
    keyboard = keyboard_def(buttons, "hidden")
    return keyboard


def phone_number(viber_user):
    buttons = []
    buttons.append(button_def("Надіслати номер", "share-phone", "share_phone", config.colorBg_button))
    if viber_user.phone_number:
        buttons.append(
            button_img(6, 1, 'Назад', f'{config.domain}{settings.STATIC_URL}viber_bot_buttons/main_back.png', 'reply',
                       f'setting'))

    keyboard = keyboard_def(buttons, "regular")
    return keyboard


def zero_to_five(text):
    buttons = []
    buttons.append(
        button_img_text(1, 1, f'1', '#ffffff', f'{config.domain}{settings.STATIC_URL}viber_bot_buttons/1x1/ff4e11.png',
                        'reply', f"{text}::1"))
    buttons.append(
        button_img_text(1, 1, f'2', '#ffffff', f'{config.domain}{settings.STATIC_URL}viber_bot_buttons/1x1/ff8e15.png',
                        'reply', f"{text}::2"))
    buttons.append(
        button_img_text(1, 1, f'3', '#ffffff', f'{config.domain}{settings.STATIC_URL}viber_bot_buttons/1x1/fab733.png',
                        'reply', f"{text}::3"))
    buttons.append(
        button_img_text(1, 1, f'4', '#ffffff', f'{config.domain}{settings.STATIC_URL}viber_bot_buttons/1x1/acb334.png',
                        'reply', f"{text}::4"))
    buttons.append(button_img_text(2, 1, f'5', '#ffffff',
                                   f'{config.domain}{settings.STATIC_URL}viber_bot_buttons/2x1/69b34c_1.png', 'reply',
                                   f"{text}::5"))
    keyboard = keyboard_def(buttons, "hidden")
    return keyboard
