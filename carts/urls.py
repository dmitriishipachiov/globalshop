from django.urls import path
from . import views

app_name = 'carts'

urlpatterns = [
    path('', views.CartView.as_view(), name='view_cart'),  # Просмотр корзины
    path('add/<slug:product_slug>/', views.AddToCartView.as_view(), name='add_to_cart'),  # Добавление товара в корзину
    path('remove/<int:item_id>/', views.RemoveFromCartView.as_view(), name='remove_from_cart'),  # Удаление товара из корзины
    path('update/<int:item_id>/', views.UpdateCartView.as_view(), name='update_cart'),  # Обновление количества товара
    path('checkout/', views.CheckoutView.as_view(), name='checkout'),  # Оформление заказа
]
