from django.contrib import admin
from django.db import models
from mptt.admin import MPTTModelAdmin, DraggableMPTTAdmin
from .models import ViberUser, Service, Position, ServiceRequest, UploadedFile, PriceList, Price
from django import forms
from django.contrib.admin.widgets import FilteredSelectMultiple
from mptt.forms import TreeNodeChoiceField


# Register your models here.


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

@admin.register(ViberUser)
class ViberUserAdmin(admin.ModelAdmin):
    list_display = ['viber_id', 'phone_number', 'full_name', 'executor', 'createdon', 'status_code']
    form = ViberUserForm
    fieldsets = (
        (None, {
            'fields': ('full_name', 'phone_number', 'executor', 'viber_id', 'system_administrator'),
        }),
        ('Рейтинг', {
            'classes': ('collapse',),
            'fields': ('customer_rating', 'executor_rating'),
        }),
        ('Advanced Options', {
            'classes': ('collapse',),
            'fields': ('position', 'service'),
        }),
        ('Костыли', {
            'classes': ('wide',),
            'fields': ('once', 'menu', 'address'),
        }),
    )




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

@admin.register(ServiceRequest)
class ServiceRequestAdmin(admin.ModelAdmin):
    list_display = ['number', 'customer', 'createdon', 'status_code']
    form = ServiceRequestForm
    fieldsets = (
        (None, {
            'fields': ('number', 'customer', 'status_code', 'modifiedon',),
        }),
        ('Додаткові дані про заявку:', {
            'classes': ('wide',),
            'fields': ('position', 'address', 'service', 'price'),
        }),
        ('Виконавці', {
            'classes': ('wide',),
            'fields': ('executors', 'rejected_executors'),
        }),
    )
    readonly_fields = ('modifiedon',)




class PositionChildrenInline(admin.TabularInline):
    model = Position
    fk_name = 'parent'
    extra = 0
    fields = ['name', 'codifier']
    ordering = ['name']

@admin.register(Position)
class PositionAdmin(DraggableMPTTAdmin):
    list_filter = ('type_code', 'status_code')
    search_fields = ['name', 'codifier']
    inlines = [PositionChildrenInline]




class ServiceChildrenInline(admin.TabularInline):
    model = Service
    fk_name = 'parent'
    extra = 0
    fields = ['name', 'priority']
    ordering = ['priority']

@admin.register(Service)
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




@admin.register(UploadedFile)
class UploadedFileAdmin(admin.ModelAdmin):
    list_display = ['createdon']




class PriceListInline(admin.TabularInline):
    model = Price
    fk_name = 'price_list'
    extra = 0
    fields = ['service', 'price']
    ordering = ['service']

@admin.register(PriceList)
class PriceListAdmin(admin.ModelAdmin):
    list_display = ['name', 'createdon', 'status_code']
    inlines = [PriceListInline]
    list_filter = ('status_code',)
    readonly_fields = ('createdon',)




@admin.register(Price)
class PriceAdmin(admin.ModelAdmin):
    list_display = ['createdon', 'status_code', 'price_list', 'service', 'price']
    list_filter = ('status_code',)
    readonly_fields = ('createdon',)
