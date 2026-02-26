from django.utils.http import urlencode
from django.shortcuts import get_object_or_404
from django.views.generic import ListView, DetailView, TemplateView
from django.views import View
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from shop.models import CategoryShop, ProductShop, SubcategoryShop
import json
import os
from django.conf import settings


class ShopListView(ListView):
    """
    Класс-представление для отображения списка товаров.

    Attributes:
        model (ProductShop): Модель данных для товаров.
        template_name (str): Имя шаблона для отображения списка товаров.
        paginate_by (int): Количество товаров на странице.
        context_object_name (str): Имя переменной контекста для списка товаров.

    Methods:
        get_queryset(): Возвращает queryset товаров в зависимости от выбранной категории или подкатегории.
        get_context_data(**kwargs): Добавляет дополнительные данные в контекст шаблона.
    """
    model = ProductShop
    template_name = 'shop/products.html'
    paginate_by = 6
    context_object_name = 'products'

    def get_queryset(self):
        """
        Фильтрует товары по выбранной категории, подкатегории или поисковому запросу.

        Returns:
            QuerySet: Отфильтрованный queryset товаров.
        """
        category_slug = self.request.GET.get('category', None)
        subcategory_slug = self.request.GET.get('subcategory', None)
        search_query = self.request.GET.get('search', None)

        queryset = super().get_queryset()

        # Apply search filter if search query is provided
        if search_query:
            # First, try to find exact category or subcategory matches
            category_matches = CategoryShop.objects.filter(title__icontains=search_query)
            subcategory_matches = SubcategoryShop.objects.filter(title__icontains=search_query)

            # Build Q objects for category and subcategory filtering
            category_q = Q()
            for category in category_matches:
                category_q |= Q(category=category)

            subcategory_q = Q()
            for subcategory in subcategory_matches:
                subcategory_q |= Q(subcategory=subcategory)

            # Combine all search conditions
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(description__icontains=search_query) |
                category_q |
                subcategory_q
            )

        # Apply category/subcategory filters
        if subcategory_slug:
            subcategory = get_object_or_404(SubcategoryShop, slug=subcategory_slug)
            queryset = queryset.filter(subcategory=subcategory)
        elif category_slug:
            category = get_object_or_404(CategoryShop, slug=category_slug)
            queryset = queryset.filter(category=category)

        return queryset.order_by('pk')

    def get_context_data(self, **kwargs):
        """
        Добавляет дополнительные данные в контекст шаблона.

        Returns:
            dict: Словарь с данными для передачи в шаблон.
        """
        context = super().get_context_data(**kwargs)
        context['title'] = 'Магазин'
        context['categories'] = CategoryShop.objects.all()
        context['subcategories'] = SubcategoryShop.objects.all()

        # Safely get selected category without raising 404
        category_slug = self.request.GET.get('category')
        if category_slug:
            try:
                context['selected_category'] = CategoryShop.objects.get(slug=category_slug)
            except CategoryShop.DoesNotExist:
                context['selected_category'] = None
        else:
            context['selected_category'] = None

        # Safely get selected subcategory without raising 404
        subcategory_slug = self.request.GET.get('subcategory')
        if subcategory_slug:
            try:
                context['selected_subcategory'] = SubcategoryShop.objects.get(slug=subcategory_slug)
            except SubcategoryShop.DoesNotExist:
                context['selected_subcategory'] = None
        else:
            context['selected_subcategory'] = None

        # Add search query to context
        search_query = self.request.GET.get('search', '')
        context['search_query'] = search_query

        # Передаем текущие параметры запроса для пагинации
        query_params = self.request.GET.copy()
        if 'page' in query_params:
            del query_params['page']
        context['query_params'] = urlencode(query_params)

        return context


class ProductDetailView(DetailView):
    """
    Класс-представление для отображения детальной информации о товаре.

    Attributes:
        model (ProductShop): Модель данных для товаров.
        template_name (str): Имя шаблона для отображения детальной информации о товаре.
        context_object_name (str): Имя переменной контекста для товара.
        slug_url_kwarg (str): Имя параметра URL для slug товара.
        slug_field (str): Имя поля модели для фильтрации по slug.

    Methods:
        get_object(): Возвращает объект товара по slug.
        get_context_data(**kwargs): Добавляет дополнительные данные в контекст шаблона.
    """
    model = ProductShop
    template_name = 'shop/details.html'
    context_object_name = 'product'
    slug_url_kwarg = 'product_slug'
    slug_field = 'slug'

    def get_object(self, queryset=None):
        """
        Возвращает объект товара по slug.

        Returns:
            ProductShop: Объект товара.
        """
        return get_object_or_404(ProductShop, slug=self.kwargs.get('product_slug'))

    def get_context_data(self, **kwargs):
        """
        Добавляет дополнительные данные в контекст шаблона.

        Returns:
            dict: Словарь с данными для передачи в шаблон.
        """
        context = super().get_context_data(**kwargs)
        context['title'] = f'Товар: {self.object.title}'
        context['images'] = self.object.images.all()
        context['categories'] = CategoryShop.objects.all()
        context['subcategories'] = SubcategoryShop.objects.all()

        # Add selected category and subcategory to context
        context['selected_category'] = self.object.category
        context['selected_subcategory'] = self.object.subcategory

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
    """
    Класс-представление для добавления/удаления товаров из избранного.

    Methods:
        post(self, request, product_slug): Обрабатывает POST-запрос для добавления/удаления товара из избранного.
    """

    def post(self, request, product_slug):
        """
        Обрабатывает POST-запрос для добавления или удаления товара из избранного.

        Args:
            request (HttpRequest): Запрос пользователя.
            product_slug (str): Slug товара.

        Returns:
            JsonResponse: JSON-ответ с информацией о статусе избранного товара.
        """
        product = get_object_or_404(ProductShop, slug=product_slug)
        user = request.user

        if product in user.favorite_products.all():
            user.favorite_products.remove(product)
            is_favorited = False
        else:
            user.favorite_products.add(product)
            is_favorited = True

        return JsonResponse({'is_favorited': is_favorited})


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
    """
    Класс-представление для отдачи статического файла products.json.

    Methods:
        get(self, request): Возвращает содержимое файла products.json.
    """

    def get(self, request):
        """
        Обрабатывает GET-запрос для возврата содержимого файла products.json.

        Args:
            request (HttpRequest): Запрос пользователя.

        Returns:
            HttpResponse: JSON-ответ с содержимым файла products.json.
        """
        # Try to find the file in products directory first
        json_file_path = os.path.join(settings.BASE_DIR, 'products', 'products.json')

        # If not found, try static directory as fallback
        if not os.path.exists(json_file_path):
            json_file_path = os.path.join(settings.BASE_DIR, 'static', 'products.json')

        # If STATIC_ROOT is set, also try there
        if hasattr(settings, 'STATIC_ROOT') and settings.STATIC_ROOT:
            alternative_path = os.path.join(settings.STATIC_ROOT, 'products.json')
            if os.path.exists(alternative_path):
                json_file_path = alternative_path

        try:
            with open(json_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return HttpResponse(json.dumps(data), content_type='application/json')
        except (FileNotFoundError, json.JSONDecodeError) as e:
            return HttpResponse(json.dumps({'error': 'File not found or invalid JSON'}), content_type='application/json', status=404)
