import json
import re
import geocoder
import os
import base64




from django.http import HttpResponseBadRequest, HttpResponse
from viberbot.api.messages import TextMessage
from datetime import date, datetime
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
viber = Api(bot_configuration)


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


# Функція обробки event == 'conversation_started' and 'subscribed'
def conversation_started(request_dict):
    viber_id = request_dict['user']['id']
    response_message = TextMessage(text='Привітальне слово + короткий опис функціоналу',
                                   min_api_version=4)
    viber.send_messages(viber_id, [response_message])

    # Перевірка наявності користувача у базі
    if ViberUser.objects.filter(viber_id=viber_id).exists():
        viber_user = ViberUser.objects.get(viber_id=viber_id)
        keyboard = keyboards.start_menu(viber_user)
        response_message = TextMessage(
            text=f'Вітаємо {viber_user.full_name}. Для продовження скористайтесь контекстним меню.',
            keyboard=keyboard,
            min_api_version=6)
        viber.send_messages(viber_id, [response_message])
    else:
        viber_user = ViberUser(viber_id=viber_id, menu='registration')
        viber_user.save()
        response_message = TextMessage(text='Введіть Ваше прізвище, ім’я, по батькові у називному відмінку',
                                       min_api_version=4)
        viber.send_messages(viber_id, [response_message])


# Функція обробки event == 'message'
def message(request_dict):
    # Отримуємо інформацію
    message_type = request_dict['message']['type']
    message_text = request_dict['message']['text']
    viber_id = request_dict['sender']['id']
    viber_user = ViberUser.objects.get(viber_id=viber_id)

    print(f'\n\nПришло: {message_text}\n\n')

    if message_type == 'text':
        if viber_user.menu == 'registration':
            save_menu(viber_user, message_text)
            registration(message_text, viber_user)
        elif message_text == 'start':
            save_menu(viber_user, message_text)
            keyboard = keyboards.start_menu(viber_user)
            response_message = TextMessage(
                text=f'Для продовження скористайтесь контекстним меню.',
                keyboard=keyboard,
                min_api_version=6)
            viber.send_messages(viber_user.viber_id, [response_message])
        elif message_text == 'setting':
            save_menu(viber_user, message_text)
            setting(viber_user)
        elif message_text == 'service':
            save_menu(viber_user, message_text)
            service_0(viber_user)
        elif re.match(r'^service::\d{1,2}$', message_text):
            save_menu(viber_user, message_text)
            service_1(viber_user, message_text.split('::')[1])
        elif re.match(r'^service::\d{1,2}::location::\d{1,2}::(?:yes|no)$', message_text):
            save_menu(viber_user, message_text)
            verification_service_request(viber_user)
        elif message_text == 'status_service_request':
            save_menu(viber_user, message_text)
            status_service_request(viber_user)
        elif message_text == 'master_registration':
            save_menu(viber_user, message_text)
            keyboard = keyboards.master_registration(viber_id)
            response_message = TextMessage(
                text=f'Для того щоб стати майстром Вам необхідно буде надати більш детальну інформацію про себе та свої навички. Чи походжуєтесь на обробку інформації?',
                keyboard=keyboard,
                min_api_version=6)
            viber.send_messages(viber_user.viber_id, [response_message])
        elif message_text == 'master_service_requests':
            save_menu(viber_user, message_text)
            master_service_requests(viber_user)
        elif re.match(r'^master_service_request::VSR-\d{1,4}-\d{1,2}-\d{1,2}-\d{1,6}$', message_text):
            service_inumber = message_text.split('::')[1]
            service_request = ServiceRequest.objects.get(number=service_inumber)
            master_service_request(viber_user, service_request)
        elif message_text == 'test':
            print(json.dumps(nodeToJSON(Position, None), ensure_ascii=False))
    elif message_type == 'location':
        if re.match(r'^service::\d{1,2}::location$', message_text):
            lat = request_dict['message']['location']['lat']
            lon = request_dict['message']['location']['lon']
            address = request_dict['message']['location']['address']
            print(lat, lon)
            create_service_request(viber_user, message_text, lat, lon, address)


# Функції для діалогів
def registration(message_text, viber_user):
    viber_user.full_name = message_text
    viber_user.menu = 'start'
    viber_user.save()

    keyboard = keyboards.start_menu(viber_user)
    response_message = TextMessage(
        text=f'Вітаємо {viber_user.full_name}. Для продовження скористайтесь контекстним меню.',
        keyboard=keyboard,
        min_api_version=6)
    viber.send_messages(viber_user.viber_id, [response_message])

# Послуги
def service_0(viber_user):
    keyboard = keyboards.service_0()
    response_message = TextMessage(
        text=f'Оберіть послугу',
        keyboard=keyboard,
        min_api_version=6)
    viber.send_messages(viber_user.viber_id, [response_message])

# Послуги дочірні
def service_1(viber_user, service_id):
    keyboard = keyboards.service_1(service_id)
    response_message = TextMessage(
        text=keyboard[0],
        keyboard=keyboard[1],
        min_api_version=6)
    viber.send_messages(viber_user.viber_id, [response_message])

# Стан заявок
def status_service_request(viber_user):
    service_requests = ServiceRequest.objects.filter(customer=viber_user)
    text = ""
    if service_requests == None:
        text = "Від вас заявок не знайдено"
    for request in service_requests:
        status_text = request.get_status_code_display()
        request_text = f'Номер заявки: {request.number}\nСтатус заявки: {status_text}\n\n'
        text = text + request_text

    keyboard = keyboards.service_0()
    response_message = TextMessage(
        text=text,
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
    viber.send_messages(viber_user.viber_id, [response_message])

# Функція записує меню у вайбер-користувача
def save_menu(viber_user, menu):
    viber_user.menu = menu
    viber_user.save()

# Функція обробки створення заявки
def create_service_request(viber_user, message_text, lat, lon, address):
    location = geocoder.osm([lat, lon], method='reverse')

    # location_info = location.raw
    # print(location_info)

    city = location.city
    town = location.town
    code_ua = location.raw['address']['ISO3166-2-lvl4'].replace("-", "")
    if city:
        position = Position.objects.filter(name=city, codifier__startswith=code_ua)
    elif town:
        position = Position.objects.filter(name=city, codifier__startswith=code_ua)

    if position:
        viber_user.address = address
        viber_user.save()
        service = Service.objects.get(id=message_text.split('::')[1])
        keyboard = keyboards.yes_no(message_text + '::' + str(position[0].id))
        response_message = TextMessage(
            text=f'Ви підтверджуєте заявку?\nПослуга: {service.name}\nМісце проведення: {address}',
            keyboard=keyboard,
            min_api_version=6)
        viber.send_messages(viber_user.viber_id, [response_message])
    else:
        print("НЕ НАШЛИ РАСПОЛОЖЕНИЕ")

# Функція обробки кнопки "підтвердження" на створення заявку
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
        service_request = ServiceRequest(number=number, customer=viber_user, address=viber_user.address, position=position, service=service)
        service_request.save()

        keyboard = keyboards.start()
        response_message = TextMessage(text=f'Ваша заявка створена!\nНомер заявки: {number}',
                                       keyboard=keyboard,
                                       min_api_version=6)
        viber.send_messages(viber_user.viber_id, [response_message])

        service_request_handler(service_request)

# Функція яка додає виконавців і оповіщує їх про створення нової заяки
def service_request_handler(service_request):
    print(service_request.position)
    executors = ViberUser.objects.filter(executor=True, position=service_request.position, service=service_request.service)

    for executor in executors:
        service_request.executors.add(executor)
        keyboard = keyboards.start_menu(executor)
        response_message = TextMessage(
            text=f'Вам доступна нова заявка для обробки.',
            keyboard=keyboard,
            min_api_version=6)
        viber.send_messages(executor.viber_id, [response_message])

# Заявки для майстрів
def master_service_requests(viber_user):
    service_requests = ServiceRequest.objects.filter(executors=viber_user, status_code=0)
    text = ""
    for request in service_requests:
        status_text = request.get_status_code_display()
        request_text = f'Номер заявки: {request.number}\nПослуга: {request.service}\n\n'
        text = text + request_text

    keyboard = keyboards.master_service_requests(service_requests)
    response_message = TextMessage(
        text=text,
        keyboard=keyboard,
        min_api_version=6)
    viber.send_messages(viber_user.viber_id, [response_message])

# Конкретна заявка для майстра
def master_service_request(viber_user, service_request):
    keyboard = keyboards.master_service_request(service_request)
    text = f'Номер заявки: {service_request.number}\nПослуга: {service_request.service}\nЗаявник: {service_request.customer.full_name}\nСередня оцінка замовника: {service_request.customer.customer_rating}\n'
    response_message = TextMessage(
        text=text,
        keyboard=keyboard,
        min_api_version=6)
    viber.send_messages(viber_user.viber_id, [response_message])

# Функція обробки кнопки "погодження" на реєстрацію майстра
def master_registration_page_view(request, viber_id):
    # services = Service.objects.filter()
    viber_user = ViberUser.objects.get(viber_id=viber_id)
    services = json.dumps(nodeToJSON(Service, None), ensure_ascii=False)
    position = json.dumps(nodeToJSON(Position, None), ensure_ascii=False)
    return render(request, 'master_registration_page.html', {'user': viber_user, 'services': services, 'position': position})

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
        print(json_body)

        new_package = CustomCreate.create_package(form_data["viber_id"], 'INSERT', "application/json", 'kvb_master', json_body)


        # Перенаправлення на сторінку "дякуємо за реєстрацію"
        return redirect('https://www.google.com.ua/')