from django.db import models
from django.conf import settings
from django.forms import ValidationError
from shop.models import ProductShop


class CartMixin:
    """
    Базовый класс для работы с корзиной.

    Methods:
        get_or_create_cart(request): Получает или создаёт корзину для пользователя или сессии.
    """

    @staticmethod
    def get_or_create_cart(request):
        """
        Получает или создаёт корзину для пользователя или сессии.

        Args:
            request (HttpRequest): Запрос пользователя.

        Returns:
            Cart: Экземпляр корзины.
        """
        if request.user.is_authenticated:
            cart, created = Cart.objects.get_or_create(user=request.user)
        else:
            session_id = request.session.session_key
            if not session_id:
                request.session.save()
                session_id = request.session.session_key
            cart, created = Cart.objects.get_or_create(session_id=session_id)
        return cart


class Cart(models.Model, CartMixin):
    """
    Модель корзины пользователя.

    Attributes:
        user (ForeignKey): Связь с пользователем. Может быть пустой для неавторизованных пользователей.
        created_at (DateTimeField): Дата и время создания корзины.
        updated_at (DateTimeField): Дата и время последнего обновления корзины.
        session_id (CharField): Идентификатор сессии для неавторизованных пользователей.

    Meta:
        db_table (str): Имя таблицы в базе данных.
        verbose_name (str): читаемое имя модели в единственном числе.
        verbose_name_plural (str): читаемое имя модели во множественном числе.
        indexes (list): Индексы для оптимизации запросов.
        constraints (list): Ограничения для обеспечения уникальности данных.

    Properties:
        total_price: Возвращает итоговую стоимость всех товаров в корзине.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='cart_orders',
        verbose_name='Покупатель',
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')

    # Поле для хранения сессионного ID (для неавторизованных пользователей)
    session_id = models.CharField(max_length=40, null=True, blank=True, verbose_name='Session ID')

    class Meta:
        db_table = 'cart'
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзина'
        indexes = [
            models.Index(fields=['created_at']),
            models.Index(fields=['updated_at']),
        ]
        constraints = [
            models.UniqueConstraint(fields=['user'], condition=models.Q(user__isnull=False), name='unique_user'),
            models.UniqueConstraint(fields=['session_id'], condition=models.Q(session_id__isnull=False), name='unique_session_id'),
        ]

    @property
    def total_price(self):
        """
        Рассчитывает итоговую стоимость корзины с использованием агрегаций базы данных.

        Returns:
            Decimal: Итоговая стоимость всех товаров в корзине.
        """
        from django.db.models import Sum, F
        result = self.items.aggregate(total=Sum(F('quantity') * F('price')))
        total = result['total'] or 0
        return total


class CartItem(models.Model):
    """
    Модель позиции корзины.

    Attributes:
        cart (ForeignKey): Связь с корзиной.
        product (ForeignKey): Связь с товаром.
        quantity (PositiveIntegerField): Количество товара в корзине.
        price (DecimalField): Цена товара на момент добавления в корзину.

    Methods:
        clean(): Проверяет наличие достаточного количества товара на складе.
        save(*args, **kwargs): Сохраняет позицию корзины после прохождения проверок.

    Properties:
        total_price: Возвращает общую стоимость текущего товара в корзине.
    """
    cart = models.ForeignKey(
        'carts.Cart',
        related_name='items',
        on_delete=models.CASCADE,
        verbose_name='Корзина'
    )
    product = models.ForeignKey(
        ProductShop,
        on_delete=models.CASCADE,
        related_name='cart_order_items',
        verbose_name='Товар'
    )
    quantity = models.PositiveIntegerField(default=1, verbose_name='Количество')
    price = models.DecimalField(max_digits=8, decimal_places=2, verbose_name='Цена')

    def clean(self):
        """
        Проверяет наличие достаточного количества товара на складе.

        Raises:
            ValidationError: Если количество товара в корзине превышает доступное на складе
                           или если товар не указан.
        """
        if self.product is None:
            raise ValidationError('Товар не указан.')

        if self.quantity > self.product.quantity:
            raise ValidationError(f'Недостаточно товара "{self.product.title}" на складе.')

    def save(self, *args, **kwargs):
        """
        Сохраняет позицию корзины после прохождения проверок.

        Args:
            *args: Дополнительные аргументы.
            **kwargs: Дополнительные именованные аргументы.
        """
        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def total_price(self):
        """
        Возвращает общую стоимость текущего товара в корзине.

        Returns:
            Decimal: Общая стоимость товара (цена * количество).
        """
        return self.price * self.quantity

    class Meta:
        verbose_name = 'Позиция корзины'
        verbose_name_plural = 'Позиции корзины'
        indexes = [
            models.Index(fields=['product_id']),  # Индекс для быстрой выборки товаров
        ]
