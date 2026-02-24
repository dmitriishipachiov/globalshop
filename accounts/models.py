from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth.models import BaseUserManager
from django.db.models.signals import post_save
from django.dispatch import receiver
from phonenumber_field.modelfields import PhoneNumberField


class Address(models.Model):
    """
    Модель для хранения адресов покупателей.

    Attributes:
        user (ForeignKey): Связь с пользователем, которому принадлежит адрес.
        city (CharField): Город. Может быть пустым.
        street (CharField): Улица. Может быть пустой.
        house (CharField): Номер дома. Может быть пустым.
        building (CharField): Корпус. Может быть пустым.
        apartment (CharField): Квартира. Может быть пустой.
        postal_code (CharField): Почтовый индекс. Может быть пустым.
        created_at (DateTimeField): Дата и время добавления адреса.

    Methods:
        __str__: Возвращает строковое представление адреса.
        clean: Очищает и нормализует данные перед сохранением.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='Покупатель'
    )
    city = models.CharField(max_length=100, blank=True, null=True, verbose_name='Город')
    street = models.CharField(max_length=100, blank=True, null=True, verbose_name='Улица')
    house = models.CharField(max_length=10, blank=True, null=True, verbose_name='Дом')
    building = models.CharField(max_length=10, blank=True, null=True, verbose_name='Корпус')
    apartment = models.CharField(max_length=10, blank=True, null=True, verbose_name='Квартира')
    postal_code = models.CharField(max_length=10, blank=True, null=True, verbose_name='Индекс')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата добавления')

    def __str__(self):
        """
        Возвращает строковое представление адреса.

        Returns:
            str: Строковое представление адреса в формате "Город, Улица, дом X корпус Y, кв.Z".
        """
        return f"{self.city}, {self.street}, дом {self.house}{' корпус '+self.building if self.building else ''}, кв.{self.apartment or '-'}"

    def clean(self):
        """
        Очищает и нормализует данные перед сохранением.

        - Приводит значения полей 'city' и 'street' к верхнему регистру.
        """
        super().clean()
        for field in ['city', 'street']:
            value = getattr(self, field).strip() if hasattr(self, field) else ''
            setattr(self, field, value.upper())

    class Meta:
        db_table = 'address'
        verbose_name = 'Адреса'


class CustomUserManager(BaseUserManager):
    """
    Менеджер пользователей для модели User.

    Methods:
        create_user: Создает и сохраняет обычного пользователя.
        create_superuser: Создает и сохраняет суперпользователя.
    """

    def create_user(self, phone_number, password=None, **extra_fields):
        """
        Создает и сохраняет обычного пользователя.

        Args:
            phone_number (str): Номер телефона пользователя.
            password (str, optional): Пароль пользователя. По умолчанию None.
            **extra_fields: Дополнительные поля пользователя.

        Raises:
            ValueError: Если номер телефона не указан.

        Returns:
            User: Созданный пользователь.
        """
        if not phone_number:
            raise ValueError('Поле «Номер телефона» должно быть заполнено.')
        user = self.model(phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, password=None, **extra_fields):
        """
        Создает и сохраняет суперпользователя.

        Args:
            phone_number (str): Номер телефона пользователя.
            password (str, optional): Пароль пользователя. По умолчанию None.
            **extra_fields: Дополнительные поля пользователя.

        Returns:
            User: Созданный суперпользователь.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(phone_number, password, **extra_fields)


class User(AbstractUser):
    """
    Расширенная модель пользователя.

    Attributes:
        phone_number (PhoneNumberField): Уникальный номер телефона пользователя.
        username (None): Отключенное поле имени пользователя.
        first_name (CharField): Имя пользователя. Может быть пустым.
        last_name (CharField): Фамилия пользователя. Может быть пустой.
        email (EmailField): Email пользователя. Может быть пустым.
        favorite_products (ManyToManyField): Избранные товары пользователя.

    Meta:
        USERNAME_FIELD (str): Поле, используемое как уникальный идентификатор.
        REQUIRED_FIELDS (list): Список обязательных полей при создании пользователя через createsuperuser.

    Methods:
        __str__: Возвращает строковое представление пользователя.
    """
    phone_number = PhoneNumberField(unique=True)
    first_name = models.CharField(max_length=150, blank=True, verbose_name="Имя")
    username = None

    USERNAME_FIELD = 'phone_number'  # Используем номер телефона как уникальный идентификатор
    REQUIRED_FIELDS = []

    last_name = models.CharField(max_length=150, blank=True, verbose_name="Фамилия")
    email = models.EmailField(blank=True, verbose_name="Email")
    favorite_products = models.ManyToManyField(
        'shop.ProductShop',
        blank=True,
        related_name='favorited_by'
    )
    receive_notifications = models.BooleanField(default=True)
    
    objects = CustomUserManager()

    def __str__(self):
        """
        Возвращает строковое представление пользователя.

        Returns:
            str: Номер телефона пользователя.
        """
        return str(self.phone_number)


@receiver(post_save, sender=User)
def create_address(sender, instance, created, **kwargs):
    """
    Сигнал для автоматического создания адреса при создании нового пользователя.

    Args:
        sender (Model): Модель, отправившая сигнал.
        instance (User): Экземпляр пользователя.
        created (bool): Флаг, указывающий, был ли пользователь только что создан.
        **kwargs: Дополнительные аргументы сигнала.
    """
    if created:
        Address.objects.create(user=instance)
        