from django.utils.http import urlencode
from django.shortcuts import get_object_or_404
from django.views.generic import ListView, DetailView, TemplateView, View
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from shop.mixins import SearchMixin
from shop.models import CategoryShop, ProductShop, SubcategoryShop
import json
import os
from django.conf import settings


class ShopListView(SearchMixin, ListView):
    """
    Отображает список товаров с фильтрацией, поиском и сортировкой.
    Логика разделена: сначала фильтрация, затем поиск, затем сортировка.
    """
    model = ProductShop
    template_name = 'shop/products.html'
    paginate_by = 6
    context_object_name = 'products'
    default_ordering = '-pk'  # Дефолтная сортировка по ID (новые товары)

    def get_queryset(self):
        """
        1. Получает базовый список товаров.
        2. Применяет фильтрацию по категории/подкатегории.
        3. Применяет поиск (если есть запрос).
        4. Применяет сортировку.
        """
        # 1. Базовый QuerySet с дефолтной сортировкой для пагинации
        queryset = super().get_queryset().order_by(self.default_ordering)
        
        # 2. Фильтрация по категориям (НЕ перезаписываем queryset, а фильтруем!)
        category_slug = self.request.GET.get('category')
        subcategory_slug = self.request.GET.get('subcategory')
        
        if subcategory_slug:
            queryset = queryset.filter(subcategory__slug=subcategory_slug)
        elif category_slug:
            queryset = queryset.filter(category__slug=category_slug)

        # 3. Поиск (вызываем метод из миксина)
        search_query = self.request.GET.get('search', '').strip()
        if search_query:
            # Если есть поиск, заменяем queryset на результаты поиска
            queryset = self.get_search_results()
            # Важно: после поиска нужно применить фильтрацию категорий заново,
            # так как поиск возвращает все товары, а нам нужны только из выбранной категории.
            if category_slug:
                queryset = queryset.filter(category__slug=category_slug)
            elif subcategory_slug:
                queryset = queryset.filter(subcategory__slug=subcategory_slug)

        # 4. Сортировка (применяем в самом конце)
        sort_by = self.request.GET.get('sorting', 'created-desc')
        
        # Исправляем ошибку FieldError: используем 'pk' вместо 'created'
        sort_map = {
            'title-asc': 'title',
            'title-desc': '-title',
            'price-asc': 'price',
            'price-desc': '-price',
            'created-asc': 'pk',      # Сортировка по ID (старые -> новые)
            'created-desc': '-pk',    # Сортировка по ID (новые -> старые)
        }
        
        order_field = sort_map.get(sort_by, '-pk')
        
        return queryset.order_by(order_field)

    def get_context_data(self, **kwargs):
        """
        Добавляет данные для шаблона: фильтры, пагинацию, состояние поиска.
        """
        context = super().get_context_data(**kwargs)
        
        # Сохраняем параметры для пагинации (кроме page)
        query_params = self.request.GET.copy()
        query_params.pop('page', None)
        
        context.update({
            'title': 'Магазин',
            'categories': CategoryShop.objects.all(),
            'subcategories': SubcategoryShop.objects.all(),
            'query_params': urlencode(query_params),
            
            # Текущая сортировка для отображения в <select>
            'sorting': self.request.GET.get('sorting', 'created-desc'),
            
            # Поисковый запрос для поля input
            'search_query': self.request.GET.get('search', ''),
            
            # Безопасное получение фильтров для подсветки в меню (без 404)
            'selected_category': CategoryShop.objects.filter(slug=self.request.GET.get('category')).first(),
            'selected_subcategory': SubcategoryShop.objects.filter(slug=self.request.GET.get('subcategory')).first(),
        })
        
        return context


class ProductDetailView(DetailView):
    model = ProductShop
    template_name = 'shop/details.html'
    context_object_name = 'product'
    slug_url_kwarg = 'product_slug'
    slug_field = 'slug'

    def get_object(self, queryset=None):
        return get_object_or_404(ProductShop, slug=self.kwargs.get('product_slug'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        context.update({
            'title': f'Товар: {self.object.title}',
            'images': self.object.images.all(),
            
            # Для хлебных крошек / навигации
            'selected_category': self.object.category,
            'selected_subcategory': self.object.subcategory,
            
            # Рекомендуемые товары из той же категории (кроме текущего)
            'related_products': ProductShop.objects.filter(
                category=self.object.category
            ).exclude(id=self.object.id)[:4],
            
            'categories': CategoryShop.objects.all(),
        })
        
        return context


class CategoryListView(ListView):
    """
    Класс-представление для отображения списка товаров в выбранной категории.

    Attributes:
        model (ProductShop): Модель данных для товаров.
        template_name (str): Имя шаблона для отображения списка товаров в категории.
        paginate_by (int): Количество товаров на странице.
        context_object_name (str): Имя переменной контекста для списка товаров.

    Methods:
        get_queryset(): Возвращает queryset товаров в выбранной категории.
        get_context_data(**kwargs): Добавляет дополнительные данные в контекст шаблона.
    """
    model = ProductShop
    template_name = 'shop/products.html'
    paginate_by = 6
    context_object_name = 'products'

    def get_queryset(self):
        """
        Возвращает queryset товаров, принадлежащих к выбранной категории.

        Returns:
            QuerySet: Отфильтрованный queryset товаров.
        """
        category_slug = self.kwargs['category_slug']
        category = get_object_or_404(CategoryShop, slug=category_slug)
        return ProductShop.objects.filter(category=category).order_by('pk')

    def get_context_data(self, **kwargs):
        """
        Добавляет дополнительные данные в контекст шаблона.

        Returns:
            dict: Словарь с данными для передачи в шаблон.
        """
        context = super().get_context_data(**kwargs)
        category_slug = self.kwargs['category_slug']
        category = get_object_or_404(CategoryShop, slug=category_slug)
        context['title'] = f'Категория: {category.title}'
        context['category'] = category
        context['categories'] = CategoryShop.objects.all()
        context['subcategories'] = SubcategoryShop.objects.all()
        context['selected_category'] = category
        context['selected_subcategory'] = None
        return context


class FavoriteToggleView(LoginRequiredMixin, View):
    def post(self, request, product_slug):
        product = get_object_or_404(ProductShop, slug=product_slug)
        
        is_favorited = product in request.user.favorite_products.all()
        
        if is_favorited:
            request.user.favorite_products.remove(product)
        else:
            request.user.favorite_products.add(product)
        
        return JsonResponse({
            'is_favorited': not is_favorited,
            'count': request.user.favorite_products.count()
        })


class FavoriteListView(LoginRequiredMixin, TemplateView):
    """
    Класс-представление для отображения списка избранных товаров.

    Attributes:
        template_name (str): Имя шаблона для отображения списка избранных товаров.

    Methods:
        get_context_data(**kwargs): Добавляет дополнительные данные в контекст шаблона.
    """
    template_name = 'shop/favorites.html'

    def get_context_data(self, **kwargs):
        """
        Добавляет дополнительные данные в контекст шаблона.

        Returns:
            dict: Словарь с данными для передачи в шаблон.
        """
        context = super().get_context_data(**kwargs)
        context['title'] = 'Избранные товары'
        context['user'] = self.request.user
        return context

class FavoriteCountView(LoginRequiredMixin, View):
    """
    Класс-представление для получения количества избранных товаров.

    Methods:
        get(self, request): Возвращает количество избранных товаров пользователя.
    """

    def get(self, request):
        """
        Обрабатывает GET-запрос для получения количества избранных товаров.

        Args:
            request (HttpRequest): Запрос пользователя.

        Returns:
            JsonResponse: JSON-ответ с количеством избранных товаров.
        """
        user = request.user
        favorites_count = user.favorite_products.count()
        return JsonResponse({'favorites_count': favorites_count})

class ProductsJsonView(View):
    def get(self, request):
        json_file_path = os.path.join(settings.BASE_DIR, 'static', 'products.json')
        
        try:
            with open(json_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            return HttpResponse(
                json.dumps(data),
                content_type='application/json; charset=utf-8'
            )
            
        except FileNotFoundError:
            return JsonResponse(
                {'error': 'Файл products.json не найден.'},
                status=404,
                json_dumps_params={'ensure_ascii': False}
            )
