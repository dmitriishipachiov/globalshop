from django.contrib import admin
from .models import Carousel, CarouselImage

class CarouselImageInline(admin.TabularInline):
    """
    Класс для отображения изображений в карусели внутри административной панели.
    """
    model = CarouselImage
    # extra = 3  # Количество дополнительных полей для добавления новых изображений
    verbose_name = 'Изображение'
    verbose_name_plural = 'Изображения'

@admin.register(Carousel)
class CarouselAdmin(admin.ModelAdmin):
    """
    Класс для управления каруселью в административной панели.
    """
    list_display = ('title', 'content')  # Поля, отображаемые в списке каруселей
    search_fields = ('title',)  # Поля для поиска
    inlines = [CarouselImageInline]  # Отображение изображений внутри карусели

@admin.register(CarouselImage)
class CarouselImageAdmin(admin.ModelAdmin):
    """
    Класс для управления изображениями в административной панели.
    """
    list_display = ('carousel', 'image') # Поля, отображаемые в списке изображений карусели
    search_fields = ('carousel__title',)  # Поиск по заголовку карусели
