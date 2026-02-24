from shop.models import ProductShop, CategoryShop
from django.views.generic import ListView, TemplateView
from main.models import Carousel, CarouselImage


class IndexView(TemplateView):
    """
    Представление для отображения главной страницы.

    Attributes:
        template_name (str): Путь к шаблону HTML для отображения главной страницы.

    Methods:
        get_context_data: Добавляет дополнительные данные в контекст шаблона.
            - bestsellers: Список товаров, помеченных как бестселлеры. Если таких товаров нет, возвращается пустой список.
            - promos: Список товаров, помеченных как акционные. Если таких товаров нет, возвращается пустой список.

    Usage:
        Контекст используется в шаблоне для отображения списка бестселлеров, акционных товаров и иконок брендов.
    """
    template_name = 'main/index.html'
    
    def get_context_data(self, **kwargs):
        """
        Расширяет контекст данных для шаблона главной страницы.

        Args:
            **kwargs: Дополнительные аргументы, передаваемые в родительский метод.

        Returns:
            dict: Словарь с данными контекста, включающий:
                - bestsellers: Товары-бестселлеры.
                - promos: Акционные товары.
                - images: Иконки брендов.
        """
        context = super().get_context_data(**kwargs)
        
        categories = CategoryShop.objects.all()

        # Получаем список бестселлеров
        bestsellers = (
            ProductShop.objects.filter(is_bestseller=True)
            if ProductShop.objects.filter(is_bestseller=True).exists()
            else []
        )
        
        # Получаем список акционных товаров
        promos = (
            ProductShop.objects.filter(is_promo=True)
            if ProductShop.objects.filter(is_promo=True).exists()
            else []
        )
        
        # Получаем карусели с изображениями (используем prefetch_related для оптимизации)
        carousels = Carousel.objects.prefetch_related('images').all()

        # Добавляем данные в контекст
        context['bestsellers'] = bestsellers
        context['promos'] = promos
        context['categories'] = categories
        context['carousels'] = carousels

        return context
