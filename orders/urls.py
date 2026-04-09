from django.urls import path
from .views import OrderListView, OrderDetailView, OrderHistoryView
from .views_payment import yookassa_webhook, payment_success, payment_fail

app_name = 'orders'

urlpatterns = [
    path('', OrderListView.as_view(), name='order_list'),  # Список заказов
    path('history/', OrderHistoryView.as_view(), name='order_history'),  # История заказов
    path('orders/<int:pk>/', OrderDetailView.as_view(), name='order_detail'),  # Детали заказа
    
    # ЮКасса Оплата
    path('payment/webhook/', yookassa_webhook, name='payment_webhook'),
    path('payment/success/<int:order_id>/', payment_success, name='payment_success'),
    path('payment/fail/<int:order_id>/', payment_fail, name='payment_fail'),
]
