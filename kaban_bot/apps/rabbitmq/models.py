from django.db import models

# Create your models here.

class RabbitPackage(models.Model):
    # Стандартні поля
    createdon = models.DateTimeField("Дата створення", auto_now_add=True, blank=True)
    status_code_set = (('0', 'Чернетка'),
                       ('1', 'Очікує обробки'),
                       ('2', 'Оброблено'),
                       ('3', 'Очікує відправки'),
                       ('4', 'Відправлено'),
                       ('5', 'Помилка'))
    status_code = models.CharField(verbose_name="Стан", choices=status_code_set, max_length=1, default=0)

    # Кастомні поля
    identifier = models.CharField(verbose_name="Ідентифікатор", max_length=64)
    direction_set = (('0', 'Вхідний'),
                     ('1', 'Вихідний'))
    direction = models.CharField(verbose_name="Напрямок", choices=direction_set, max_length=1)
    body = models.TextField(verbose_name="Тіло пакету")
    version = models.CharField(verbose_name="Версія", max_length=32)
    priority = models.PositiveSmallIntegerField(verbose_name="Пріорітет")
    type = models.CharField(verbose_name="Тип", max_length=64)
    contentType = models.CharField(verbose_name="Тип вмісту", max_length=32)
    operation = models.CharField(verbose_name="Операція", max_length=16)
    last_error = models.TextField(verbose_name="Остання помилка", max_length=5000, blank=True, null=True)


    class Meta:
        verbose_name = 'Rabbit: Пакет'
        verbose_name_plural = 'Rabbit: Пакети'

    def __str__(self):
        return self.type