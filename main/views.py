from django.views.generic import TemplateView
from shop.models import ProductShop, CategoryShop
from main.models import Carousel
from shop.mixins import SearchMixin

class IndexView(TemplateView):
    """
    Главная страница сайта.
    Использует SearchMixin ТОЛЬКО для блока поиска.
    """
    template_name = 'main/index.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Базовые данные для главной страницы (всегда отображаются)
        context.update({
            'categories': CategoryShop.objects.all(),
            'carousels': Carousel.objects.prefetch_related('images').all(),
            
            # Используем .exists() один раз для оптимизации
            'bestsellers': ProductShop.objects.filter(is_bestseller=True)[:8],
            'promos': ProductShop.objects.filter(is_promo=True)[:8],
            
            # Поисковый запрос для поля input (пустой по умолчанию)
            'search_query': '',
        })
        
        # --- Блок поиска ---
        search_query = self.request.GET.get('search', '').strip()
        
        if search_query:
            # Если есть поисковый запрос, создаем временный объект миксина
            search_mixin = SearchMixin()
            search_mixin.request = self.request
            
            # Получаем результаты и добавляем их в контекст
            context['search_query'] = search_query
            context['search_results'] = search_mixin.get_search_results()[:12] 
        
        return context