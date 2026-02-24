from django.views.generic import ListView, DetailView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.http import HttpResponseForbidden
from django.urls import reverse_lazy
from django.contrib import messages
from django.utils.translation import gettext as _
from django.shortcuts import redirect

from .models import Order, OrderItem
from .forms import OrderForm

class OrderListView(LoginRequiredMixin, ListView):
    model = Order
    template_name = 'orders/order_list.html'
    paginate_by = 10
    ordering = ['-created_at']

    def get_queryset(self):
        queryset = super().get_queryset()
        # Только администраторы видят все заказы, обычные пользователи - только свои
        if not self.request.user.is_staff:
            queryset = queryset.filter(user=self.request.user)
        return queryset

class OrderHistoryView(OrderListView):
    template_name = 'orders/order_history.html'
    context_object_name = 'orders'

class OrderDetailView(LoginRequiredMixin, DetailView):
    model = Order
    template_name = 'orders/order_detail.html'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        # Проверяем права доступа
        if not self.request.user.is_staff and obj.user != self.request.user:
            raise HttpResponseForbidden(_("У вас нет разрешения на просмотр этого заказа."))
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Автоматически добавляем элементы заказа в контекст
        order = self.get_object()
        context['order_items'] = order.items.all()
        context['discount'] = order.discount

        # Добавляем адрес, если он существует
        if order.address:
            context['address'] = order.address

        return context

class OrderCreateView(LoginRequiredMixin, CreateView):
    model = Order
    form_class = OrderForm
    template_name = 'orders/order_form.html'
    success_url = reverse_lazy('orders:order_list')

    def form_valid(self, form):
        # Сохраняем пользователя в заказ
        form.instance.user = self.request.user

        return super().form_valid(form)
    