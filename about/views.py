from django.views.generic import ListView
from .models import PageContentAbout, PageContentContacts


class PageContentAboutView(ListView):
    """
    Представление для отображения контента страницы "О нас".

    Атрибуты:
        template_name (str): Путь к шаблону для отображения страницы.
        model (Model): Модель, используемая для получения данных.
        context_object_name (str): Имя переменной контекста, передаваемой в шаблон.

    Методы:
        get_template_about: Возвращает список шаблонов в зависимости от типа страницы.
        get_queryset: Возвращает queryset объектов модели, отфильтрованных по типу страницы.
    """
    template_name = 'about/about.html'
    model = PageContentAbout
    context_object_name = 'page_contents'

    def get_template_about(self):
        """
        Определяет шаблон для отображения страницы "О нас".

        Returns:
            list: Список путей к шаблонам. По умолчанию используется 'about/about.html'.
        """
        page_type = self.kwargs.get('page_type', 'about')
        if page_type == 'about':
            return ['about/about.html']
        return ['about/about.html']

    def get_queryset(self):
        """
        Возвращает queryset объектов модели PageContentAbout, отфильтрованных по типу страницы.

        Returns:
            QuerySet: Фильтрованный queryset объектов модели PageContentAbout.
        """
        page_type = self.kwargs.get('page_type', 'about')
        return PageContentAbout.objects.filter(page_type=page_type)


class PageContentContactsView(ListView):
    """
    Представление для отображения контактной информации.

    Атрибуты:
        template_name (str): Путь к шаблону для отображения страницы контактов.
        model (Model): Модель, используемая для получения данных.
        context_object_name (str): Имя переменной контекста, передаваемой в шаблон.

    Методы:
        get_template_contacts: Возвращает список шаблонов в зависимости от типа страницы.
        get_queryset: Возвращает queryset объектов модели, отфильтрованных по типу страницы.
    """
    template_name = 'about/contacts.html'
    model = PageContentContacts
    context_object_name = 'page_contents'

    def get_template_contacts(self):
        """
        Определяет шаблон для отображения страницы контактов.

        Returns:
            list: Список путей к шаблонам. По умолчанию используется 'about/contacts.html'.
        """
        page_type = self.kwargs.get('page_type', 'contacts')
        if page_type == 'contacts':
            return ['about/contacts.html']
        return ['about/contacts.html']

    def get_queryset(self):
        """
        Возвращает queryset объектов модели PageContentContacts, отфильтрованных по типу страницы.

        Returns:
            QuerySet: Фильтрованный queryset объектов модели PageContentContacts.
        """
        page_type = self.kwargs.get('page_type', 'contacts')
        return PageContentContacts.objects.filter(page_type=page_type)