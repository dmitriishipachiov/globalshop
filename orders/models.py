from django.db import models
from django.contrib.auth import get_user_model
from accounts.models import Address
from shop.models import ProductShop
from django.db.models.signals import post_save
from django.dispatch import receiver

User = get_user_model()

class Order(models.Model):
    """Представляет заказ пользователя."""
    STATUS_CHOICES = [
        ('pending', 'В обработке'),
        ('completed', 'Завершен'),
        ('canceled', 'Отменён'),
        ('paid', 'Оплачен'),
    ]
    PAYMENT_METHODS = [
        ('cash', 'Наличные'),
        ('credit_card', 'Кредитная карта'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders', verbose_name='Покупатель')
    address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Адрес доставки')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='Статус заказа')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    payment_method = models.CharField(max_length=50, choices=PAYMENT_METHODS, verbose_name='Способ оплаты')
    
    def __str__(self):
        return f"Order {self.id} by {self.user.username}"
    
    class Meta:
        db_table = 'orders'
        verbose_name = 'Заказы'

    @property
    def total_cost(self):
        """Возвращает общую стоимость заказа исходя из товаров и их количеств."""
        total = sum(item.subtotal for item in self.items.all())

        # Apply any order-level discounts here if needed
        # For now, we'll just return the total as calculated
        return total

    @property
    def discount(self):
        """Возвращает скидку на заказ."""
        # Для начала просто возвращаем 0, так как скидка не реализована
        return 0

    @property
    def is_paid(self):
        """Логическое свойство для отслеживания оплаченности заказа."""
        return self.status == 'paid'

class OrderItem(models.Model):
    """Элемент заказа (позиция в заказе)."""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', verbose_name='Заказ')
    product = models.ForeignKey(ProductShop, on_delete=models.PROTECT, verbose_name='Товар')
    quantity = models.PositiveIntegerField(verbose_name='Количество')

    def __str__(self):
        return f"{self.quantity} x {self.product.title} в Заказе #{self.order.id}"

    @property
    def subtotal(self):
        """Возвращает полную стоимость позиции (количество × цена товара с учетом скидки)."""
        return self.quantity * self.product.sell_price()

# Срабатывание сигнала при изменении позиций заказа
@receiver(post_save, sender=OrderItem)
def update_order_total_cost(sender, instance, **kwargs):
    """Обновляет общую стоимость заказа при изменении элементов."""
    pass  # Общая стоимость является property и автоматически пересчитывается
