from django.db import models

class PageContentAbout(models.Model):
    """
    Модель для хранения контента страницы "О нас".

    Meta:
        verbose_name (str):Название модели в административной панели Django.

    """
    PAGE_TYPES = (
        ('about', 'About Page'),
    )

    title = models.CharField(max_length=255)
    content = models.TextField()
    page_type = models.CharField(max_length=20, choices=PAGE_TYPES)

    class Meta:
        verbose_name = 'О нас'

    def __str__(self):
        """
        Возвращает строковое представление объекта модели.

        """
        return f"{self.title} ({self.get_page_type_display()})"


class PageContentContacts(models.Model):
    """
    Модель для хранения контактной информации.

    Meta:
        verbose_name (str): Название модели в административной панели Django.

    Методы:
        __str__: Возвращает строковое представление объекта модели.
    """
    PAGE_TYPES = (
        ('contacts', 'Contacts Page'),
    )

    content_office = models.CharField(
        max_length=255, blank=True, null=True, verbose_name='Адрес'
    )
    content_phone = models.CharField(
        max_length=25, blank=True, null=True, verbose_name='Телефон'
    )
    content_email = models.EmailField(
        max_length=125, blank=True, null=True, verbose_name='Электронная почта'
    )
    page_type = models.CharField(
        max_length=20, choices=PAGE_TYPES, verbose_name='Выберите страницу'
    )

    class Meta:
        verbose_name = 'Контакты'

    def __str__(self):
        """
        Возвращает строковое представление объекта модели.
        """
        return f"{self.content_office} ({self.get_page_type_display()})"