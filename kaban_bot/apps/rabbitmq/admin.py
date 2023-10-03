from django.contrib import admin

from django.db.models import QuerySet
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
    actions = ['packages_processing']

    @admin.action(description='Пакети в в очікування обробки/відправки')
    def packages_processing(self, request, queryset):
        for item in queryset:
            if item.direction == '0':
                item.status_code = 1
                item.save()
            elif item.direction == '1':
                item.status_code = 3
                item.save()

        self.message_user(request, f'Выполнено кастомное действие для {queryset.count()} записей.')