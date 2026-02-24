from django.urls import path
from .views import OrderListView, OrderDetailView, OrderCreateView, OrderHistoryView

app_name = 'orders'

urlpatterns = [
    path('', OrderListView.as_view(), name='order_list'),  # Список заказов
    path('history/', OrderHistoryView.as_view(), name='order_history'),  # История заказов
    path('orders/<int:pk>/', OrderDetailView.as_view(), name='order_detail'),  # Детали заказа
    path('create/', OrderCreateView.as_view(), name='order_create'),  # Создание заказа
]
