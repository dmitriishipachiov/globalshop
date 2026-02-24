from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Address, User

@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'city', 'street', 'house'
    )  # показываем полезные поля адреса
    list_filter = ('city',)  # фильтр по городу
    search_fields = ('id', 'city', 'street')  # поиск по ключевым полям

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('phone_number', 'email', 'is_staff')
    fieldsets = (
        (None, {'fields': ('phone_number', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('phone_number', 'first_name', 'last_name', 'email', 'password1', 'password2'),
        }),
    )
    ordering = ('phone_number',)
