from django.contrib import admin
from django.db import models
from mptt.admin import MPTTModelAdmin, DraggableMPTTAdmin
from .models import ViberUser, Service, Position, ServiceRequest, UploadedFile
from django import forms
from django.contrib.admin.widgets import FilteredSelectMultiple
from mptt.forms import TreeNodeChoiceField



# Register your models here.

class ServiceChildrenInline(admin.TabularInline):
    model = Service
    fk_name = 'parent'
    extra = 0
    fields = ['name', 'priority']
    ordering = ['priority']


class ViberUserForm(forms.ModelForm):
    # Определяем форму с виджетом FilteredSelectMultiple для поля ManyToManyField 'position'
    position = forms.ModelMultipleChoiceField(
        queryset=Position.objects.all(),
        widget=FilteredSelectMultiple("Розташування", is_stacked=False),
        required=False,
    )

    service = forms.ModelMultipleChoiceField(
        queryset=Service.objects.all(),
        widget=FilteredSelectMultiple("Послуги", is_stacked=False),
        required=False,
    )

    class Meta:
        model = ViberUser
        fields = '__all__'

class ViberUserAdmin(admin.ModelAdmin):
    list_display = ['viber_id', 'full_name', 'executor', 'createdon', 'status_code']
    form = ViberUserForm
    fieldsets = (
        (None, {
            'fields': ('full_name', 'phone_number', 'executor', 'viber_id', 'menu', 'system_administrator'),
        }),
        ('Рейтинг', {
            'classes': ('collapse',),
            'fields': ('customer_rating', 'executor_rating'),
        }),
        ('Advanced Options', {
            'classes': ('collapse',),
            'fields': ('position', 'service'),
        }),
    )
admin.site.register(ViberUser, ViberUserAdmin)



class ServiceRequestForm(forms.ModelForm):
    # Определяем форму с виджетом FilteredSelectMultiple для поля ManyToManyField 'executors'
    executors = forms.ModelMultipleChoiceField(
        queryset=ViberUser.objects.all(),
        widget=FilteredSelectMultiple("Виконавці", is_stacked=False),
        required=False,
    )
    # Определяем форму с виджетом FilteredSelectMultiple для поля ManyToManyField 'rejected_executors'
    rejected_executors = forms.ModelMultipleChoiceField(
        queryset=ViberUser.objects.all(),
        widget=FilteredSelectMultiple("Відхилені виконавці", is_stacked=False),
        required=False,
    )

    class Meta:
        model = ServiceRequest
        fields = '__all__'

class ServiceRequestAdmin(admin.ModelAdmin):
    list_display = ['number', 'customer', 'createdon', 'status_code']
    form = ServiceRequestForm
    fieldsets = (
        (None, {
            'fields': ('number', 'customer', 'status_code', 'modifiedon',),
        }),
        ('Додаткові дані про заявку:', {
            'classes': ('wide',),
            'fields': ('position', 'address', 'service'),
        }),
        ('Виконавці', {
            'classes': ('wide',),
            'fields': ('executors', 'rejected_executors'),
        }),
    )
    readonly_fields = ('modifiedon',)
admin.site.register(ServiceRequest, ServiceRequestAdmin)


class PositionAdmin(DraggableMPTTAdmin):
    list_filter = ('type_code',)
admin.site.register(Position, PositionAdmin)


class ServiceAdmin(DraggableMPTTAdmin):
    list_display = ('tree_actions', 'indented_title', 'productnumber', 'priority')
    list_display_links = ('indented_title',)
    fieldsets = (
        ('Загальна інформація', {
            'fields': ('status_code', 'name', 'productnumber', 'parent'),
        }),
        ('Налаштування кнопки', {
            'fields': ('priority', 'image', 'rows', 'columns',),
        }),
    )
    inlines = [ServiceChildrenInline]
    # ordering = ['tree_id', 'level', 'priority']
admin.site.register(Service, ServiceAdmin)


class UploadedFileAdmin(admin.ModelAdmin):
    list_display = ['createdon']
admin.site.register(UploadedFile, UploadedFileAdmin)