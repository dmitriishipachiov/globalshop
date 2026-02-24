from django.contrib import admin
from .models import Cart, CartItem


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    """
    Администрируем модель корзины.
    """
    list_display = ('id', 'user')
    list_filter = ()
    search_fields = ('user__username',)
    date_hierarchy = None

    fieldsets = (
        (None, {
            'fields': ('user',)
        }),
    )


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    """
    Администрируем модель элементов корзины.
    """
    list_display = ('id', 'cart', 'product', 'quantity', 'price')
    list_filter = ('cart', 'product')
    search_fields = ('cart__user__username', 'product__name')

    fieldsets = (
        (None, {
            'fields': ('cart', 'product', 'quantity', 'price')
        }),
    )
