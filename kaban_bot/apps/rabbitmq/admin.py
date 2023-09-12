from django.contrib import admin

from .models import RabbitPackage
from .management.commands import package_handler

# Register your models here.
@admin.register(RabbitPackage)
class RabbitPackagesAdmin(admin.ModelAdmin):
    list_display = ['type', 'direction', 'createdon', 'status_code']
    list_filter = ('type', 'direction', 'status_code')
    readonly_fields = ('createdon',)
    fieldsets = (
        ('Загальна інформація', {
            'fields': ('createdon', 'direction', 'priority', 'identifier', 'version', 'operation', 'status_code'),
        }),
        ('Пакет', {
            'fields': ('type', 'contentType', 'body', 'last_error'),
        }),
    )