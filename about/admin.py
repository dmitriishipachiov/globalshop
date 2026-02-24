from django.contrib import admin
from .models import PageContentAbout, PageContentContacts


@admin.register(PageContentAbout)
class PageContentAboutAdmin(admin.ModelAdmin):
    """
    Административное представление для модели PageContentAbout.

    Поля, отображаемые в списке объектов:
        title (CharField): Заголовок страницы "О нас".
        content (TextField): Основной текстовый контент страницы.

    Дополнительные настройки:
        list_display: Список полей, которые будут отображаться в интерфейсе администратора.
    """
    list_display = ('title', 'content')


@admin.register(PageContentContacts)
class PageContentContactsAdmin(admin.ModelAdmin):
    """
    Административное представление для модели PageContentContacts.

    Поля, отображаемые в списке объектов:
        content_office (CharField): Адрес офиса.
        content_phone (CharField): Номер телефона.
        content_email (EmailField): Электронная почта.

    Дополнительные настройки:
        list_display: Список полей, которые будут отображаться в интерфейсе администратора.
    """
    list_display = ('content_office', 'content_phone', 'content_email')

