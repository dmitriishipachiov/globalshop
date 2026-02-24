from django.db import models

class Carousel(models.Model):
    """
    Модель, представляющая текст на изображении в карусели.

    """
    title = models.CharField(max_length=30, unique=True, null=True, verbose_name='Заголовок')
    content = models.CharField(max_length=30, unique=True, null=True, verbose_name='Контент')

    class Meta:
        db_table = 'Carousel'
        verbose_name = 'Карусель'
        verbose_name_plural = 'Карусели'

    def __str__(self):
        return self.title
    

class CarouselImage(models.Model):
    """
    Модель, представляющая изображения в карусели.

    """

    carousel = models.ForeignKey(
        to=Carousel, on_delete=models.CASCADE, related_name='images', verbose_name='Картинка'
    )
    image = models.ImageField(upload_to='Carousel_images', verbose_name='Изображение')

    class Meta:
        verbose_name = 'Изображение карусели'
        verbose_name_plural = 'Изображения карусели'

    def __str__(self):
        return f'Изображение для карусели: {self.carousel.title}'