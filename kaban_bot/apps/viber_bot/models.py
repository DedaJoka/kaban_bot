from django.db import models
from mptt.models import MPTTModel, TreeForeignKey
from django.core.validators import MinValueValidator, MaxValueValidator


# Create your models here.

class Position(MPTTModel):
    # Стандартні поля
    createdon = models.DateTimeField("Дата створення", auto_now_add=True, blank=True)
    status_code_set = (('0', 'Активований'), ('1', 'Деактивований'))
    status_code = models.CharField(verbose_name="Стан", choices=status_code_set, max_length=1, default=0)

    # Кастомні поля
    name = models.CharField(verbose_name="Назва", max_length=19, blank=True)
    codifier = models.CharField(verbose_name="Кодифікатор", max_length=100, blank=True, unique=True)
    parent = TreeForeignKey('self', verbose_name="Батьківське розташування", on_delete=models.CASCADE, null=True, blank=True, related_name='children')

    type_code_set = (('O', 'Область або АРК'),
                     ('K', 'Місто, що має спеціальний статус'),
                     ('P', 'Район в області або в АРК'),
                     ('H', 'Територіальна громада'),
                     ('M', 'Місто'),
                     ('T', 'Селище міського типу'),
                     ('C', 'Село'),
                     ('X', 'Селище'),
                     ('B', 'Район в місті'))
    type_code = models.CharField(verbose_name="Тип", choices=type_code_set, max_length=1, null=True, blank=True)

    class Meta:
        app_label = 'viber_bot'
        verbose_name = 'Розташування'
        verbose_name_plural = 'Розташування'

    class MPTTMeta:
        order_insertion_by = ['name']

    def __str__(self):
        return self.name


class Service(MPTTModel):
    # Стандартні поля
    createdon = models.DateTimeField("Дата створення", auto_now_add=True, blank=True)
    status_code_set = (('0', 'Активований'), ('1', 'Деактивований'))
    status_code = models.CharField(verbose_name="Стан", choices=status_code_set, max_length=1, default=0)

    # Кастомні поля
    name = models.CharField(verbose_name="Назва", max_length=100, blank=True)
    parent = TreeForeignKey('self', verbose_name="Батьківська послуга", on_delete=models.CASCADE, null=True, blank=True,
                            related_name='children')
    image = models.FileField(verbose_name="Зображення", upload_to='viber_bot_buttons/')
    columns = models.PositiveSmallIntegerField(
        verbose_name="Колонки",
        default=1,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(6)
        ]
    )
    rows = models.PositiveSmallIntegerField(
        verbose_name="Рядки",
        default=1,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(2)
        ]
    )
    priority = models.PositiveSmallIntegerField(verbose_name="Пріорітет", default=1)

    class Meta:
        app_label = 'viber_bot'
        verbose_name = 'Послуга'
        verbose_name_plural = 'Послуги'

    class MPTTMeta:
        order_insertion_by = ['name']

    def __str__(self):
        return self.name

    def get_children_names(self):
        return ', '.join(child.name for child in self.get_children())


class ViberUser(models.Model):
    # Стандартні поля
    createdon = models.DateTimeField("Дата створення", auto_now_add=True, blank=False)
    status_code_set = (('0', 'Активований'), ('1', 'Деактивований'))
    status_code = models.CharField(verbose_name="Стан", choices=status_code_set, max_length=1, default=0)

    # Кастомні поля
    viber_id = models.CharField(verbose_name="Вайбер ідентифікатор", max_length=100, blank=False)
    full_name = models.CharField(verbose_name="ПІБ", max_length=100, blank=True)
    phone_number = models.CharField("Телефон", max_length=13, blank=True, null=True)
    menu = models.CharField(verbose_name="Меню", max_length=100, blank=True)
    address = models.CharField(verbose_name="Адреса", max_length=400, blank=True, null=True)
    position = models.ManyToManyField(Position, verbose_name="Розташування", related_name='viber_user_position')
    service = models.ManyToManyField(Service, verbose_name="Послуги", related_name='viber_user_service')
    executor = models.BooleanField(verbose_name="Виконавець", default=False)
    customer_rating = models.FloatField(
        verbose_name="Рейтинг клієнта",
        validators=[MinValueValidator(0.0), MaxValueValidator(5.0)],
        blank=True, null=True
    )
    executor_rating = models.FloatField(
        verbose_name="Рейтинг майстра",
        validators=[MinValueValidator(0.0), MaxValueValidator(5.0)],
        blank=True, null=True
    )


    class Meta:
        app_label = 'viber_bot'
        verbose_name = 'Користувач Viber'
        verbose_name_plural = 'Користувачі Viber'

    def __str__(self):
        return self.full_name


class ServiceRequest(models.Model):
    # Стандартні поля
    createdon = models.DateTimeField("Дата створення", auto_now_add=True, blank=True)
    modifiedon = models.DateTimeField("Дата змін", auto_now_add=True, blank=True)
    status_code_set = (('0', 'Створена'),
                       ('1', 'В роботі'),
                       ('2', 'Виконана'),
                       ('3', 'Скасована'),
                       ('4', 'Очікування майстра'),
                       ('5', 'Очікування підтвердження'),
                       ('6', 'В роботі (Підтверджений майстер)'),
                       ('7', 'Уточнення (від майстра)'),
                       ('8', 'Уточнення (від клієнта)'),
                       ('9', 'Завершено'),)
    status_code = models.CharField(verbose_name="Стан", choices=status_code_set, max_length=1, default=0)

    # Кастомні поля
    number = models.CharField(verbose_name="Номер", max_length=19, blank=True)
    customer = models.ForeignKey(ViberUser, verbose_name="Замовник", on_delete=models.CASCADE, related_name='service_requests_customer')
    executors = models.ManyToManyField(ViberUser, verbose_name="Виконавці", related_name='service_requests_executors')
    rejected_executors = models.ManyToManyField(ViberUser, verbose_name="Відхилені Виконавці", related_name='service_requests_rejected_executors', blank=True)
    address = models.CharField(verbose_name="Адреса", max_length=400, blank=True, null=True)
    position = models.ForeignKey(Position, verbose_name="Населений пункт", on_delete=models.CASCADE, related_name='service_requests_position')
    service = models.ForeignKey(Service, verbose_name="Послуга", on_delete=models.CASCADE, related_name='service_requests_service')
    confirmed = models.BooleanField(verbose_name="Підтверджена", default=False)


    class Meta:
        app_label = 'viber_bot'
        verbose_name = 'Заявка'
        verbose_name_plural = 'Заявки'


class UploadedFile(models.Model):
    # Стандартні поля
    createdon = models.DateTimeField("Дата створення", auto_now_add=True, blank=True)
    status_code_set = (('0', 'Активований'), ('1', 'Деактивований'))
    status_code = models.CharField(verbose_name="Стан", choices=status_code_set, max_length=1, default=0)

    file = models.FileField(verbose_name="Файл", upload_to='uploads_viber_bot/')
    file_name = models.CharField(verbose_name="Назва файлу", max_length=100, blank=False)
    user_viber_id = models.CharField(verbose_name="Вайбер ідентифікатор", max_length=100, blank=False)

