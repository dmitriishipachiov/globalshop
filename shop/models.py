from django.db import models


class CategoryShop(models.Model):
    """
    Модель, представляющая категорию товаров в магазине.

    Attributes:
        title (CharField): Название категории. Уникальное поле длиной до 200 символов.
        slug (SlugField): URL-идентификатор категории. Уникальное поле длиной до 200 символов, может быть пустым.

    Meta:
        db_table (str): Имя таблицы в базе данных.
        verbose_name (str): читаемое имя модели в единственном числе.
        verbose_name_plural (str): читаемое имя модели во множественном числе.

    Methods:
        __str__: Возвращает название категории.
    """
    title = models.CharField(max_length=200, unique=True, verbose_name='Название категории')
    slug = models.SlugField(max_length=200, unique=True, null=True, blank=True, verbose_name='URL')

    class Meta:
        db_table = 'CategoryShop'
        verbose_name = 'Категорию'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.title


class SubcategoryShop(models.Model):
    """
    Модель, представляющая подкатегорию товаров в магазине.

    Attributes:
        title (CharField): Название подкатегории. Уникальное поле длиной до 200 символов.
        slug (SlugField): URL-идентификатор подкатегории. Уникальное поле длиной до 200 символов, может быть пустым.
        category (ForeignKey): Связь с моделью CategoryShop, указывающая на родительскую категорию.

    Meta:
        db_table (str): Имя таблицы в базе данных.
        verbose_name (str): читаемое имя модели в единственном числе.
        verbose_name_plural (str): читаемое имя модели во множественном числе.

    Methods:
        __str__: Возвращает название подкатегории.
    """
    title = models.CharField(max_length=200, unique=True, verbose_name='Название подкатегории')
    slug = models.SlugField(max_length=200, unique=True, null=True, blank=True, verbose_name='URL')
    category = models.ForeignKey(
        to=CategoryShop, on_delete=models.CASCADE, related_name='subcategories', verbose_name='Категория'
    )

    class Meta:
        db_table = 'SubcategoryShop'
        verbose_name = 'Подкатегория'
        verbose_name_plural = 'Подкатегории'

    def __str__(self):
        return self.title


class ProductShop(models.Model):
    """
    Модель, представляющая товар в магазине.

    Attributes:
        title (CharField): Название товара. Уникальное поле длиной до 150 символов.
        description (TextField): Описание товара. Может быть пустым.
        slug (SlugField): URL-идентификатор товара. Уникальное поле длиной до 250 символов, может быть пустым.
        price (DecimalField): Цена товара. По умолчанию 0.00.
        discount (DecimalField): Скидка на товар в процентах. По умолчанию 0.00.
        quantity (PositiveIntegerField): Количество товара на складе. По умолчанию 0.
        category (ForeignKey): Связь с моделью CategoryShop, указывающая на категорию товара.
        subcategory (ForeignKey): Связь с моделью SubcategoryShop, указывающая на подкатегорию товара. Может быть пустой.
        is_bestseller (BooleanField): Флаг "Хит продаж". По умолчанию False.
        is_promo (BooleanField): Флаг "Акция". По умолчанию False.

    Meta:
        db_table (str): Имя таблицы в базе данных.
        verbose_name (str): читаемое имя модели в единственном числе.
        verbose_name_plural (str): читаемое имя модели во множественном числе.

    Methods:
        __str__: Возвращает строковое представление товара с указанием его количества.
        sell_price: Вычисляет и возвращает цену товара с учетом скидки.
    """
    title = models.CharField(max_length=150, unique=True, verbose_name='Название товара')
    description = models.TextField(blank=True, null=True, verbose_name='Описание товара')
    slug = models.SlugField(max_length=250, unique=True, blank=True, null=True, verbose_name='URL')
    price = models.DecimalField(default=0.00, max_digits=7, decimal_places=2, verbose_name='Цена')
    discount = models.DecimalField(default=0.00, max_digits=4, decimal_places=2, verbose_name='Скидка в %')
    quantity = models.PositiveIntegerField(default=0, verbose_name='Количество')
    category = models.ForeignKey(to=CategoryShop, on_delete=models.PROTECT, verbose_name='Категория товара')
    subcategory = models.ForeignKey(
        to=SubcategoryShop, on_delete=models.PROTECT, verbose_name='Подкатегория товара', null=True, blank=True
    )
    is_bestseller = models.BooleanField(default=False, verbose_name='Хит продаж')
    is_promo = models.BooleanField(default=False, verbose_name='Акция')

    class Meta:
        db_table = 'ProductShop'
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'

    def __str__(self):
        return f'{self.title} Количество - {self.quantity}'

    def sell_price(self):
        """
        Вычисляет цену товара с учетом скидки.

        Returns:
            Decimal: Цена товара после применения скидки (если скидка указана).
        """
        if self.discount:
            return round(self.price - self.price * self.discount / 100, 2)
        return self.price


class ProductImage(models.Model):
    """
    Модель, представляющая изображения товаров.

    Attributes:
        product (ForeignKey): Связь с моделью ProductShop, указывающая на товар.
        image (ImageField): Изображение товара, загружается в директорию 'shop_images'.
        slug (SlugField): URL-идентификатор изображения. Уникальное поле длиной до 250 символов, может быть пустым.

    Meta:
        verbose_name (str): читаемое имя модели в единственном числе.
        verbose_name_plural (str): читаемое имя модели во множественном числе.

    Methods:
        __str__: Возвращает строковое представление изображения с указанием товара.
    """
    product = models.ForeignKey(
        to=ProductShop, on_delete=models.CASCADE, related_name='images', verbose_name='Товар'
    )
    image = models.ImageField(upload_to='shop_images', verbose_name='Изображение')
    slug = models.SlugField(max_length=250, unique=True, blank=True, null=True, verbose_name='URL')

    class Meta:
        verbose_name = 'Изображение товара'
        verbose_name_plural = 'Изображения товаров'

    def __str__(self):
        return f'Изображение для товара: {self.product.title}'