from django.db.models import Q
from shop.models import CategoryShop, ProductShop

class SearchMixin:
    """
    Миксин для добавления логики поиска в представления.
    Выполняет поиск по товарам (название, описание) и категориям.
    """
    search_query = ''
    search_results = None

    def get_search_results(self):
        """
        Выполняет поиск и возвращает QuerySet с результатами.
        """
        self.search_query = self.request.GET.get('search', '').strip()
        
        if not self.search_query:
            return ProductShop.objects.none() # Возвращаем пустой QuerySet, если поиск пустой

        search_query_lower = self.search_query.lower()

        # 1. Поиск по товарам (название и описание)
        product_search = ProductShop.objects.filter(
            Q(title__icontains=self.search_query) | Q(description__icontains=self.search_query)
        )

        # 2. Поиск по категориям (находим ID категорий и ищем товары в них)
        category_ids = CategoryShop.objects.filter(title__icontains=self.search_query).values_list('id', flat=True)
        category_products_search = ProductShop.objects.filter(category_id__in=category_ids)

        # Объединяем результаты и убираем дубликаты
        return (product_search | category_products_search).distinct()

    def get_context_data(self, **kwargs):
        """
        Добавляет результаты поиска в контекст.
        """
        context = super().get_context_data(**kwargs)
        
        # Если атрибуты еще не определены (например, при первом вызове), вычисляем их
        if not hasattr(self, 'search_query'):
            self.search_query = self.request.GET.get('search', '')
        
        if not hasattr(self, 'search_results'):
            self.search_results = self.get_search_results()

        context['search_query'] = self.search_query
        context['search_results'] = self.search_results
        
        return context