from django.contrib import admin
from .models import Order, OrderItem

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'user', 'address', 'status', 'created_at', 'total_cost'
    )  # отображаем ключевую информацию заказа
    list_filter = ('status', 'created_at')  # фильтры по статусу и дате создания
    search_fields = ('user__username',)  # расширенный поиск
    readonly_fields = ('total_cost',)  # общее значение заказа нельзя менять вручную

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'order', 'product', 'quantity'
    )  # показываем элементы заказа
    list_filter = ('order',)  # можем фильтровать по заказу
    search_fields = ('order__id', 'product__name')  # поиск по номеру заказа и названию товара
