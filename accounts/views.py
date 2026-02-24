from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages

from accounts.models import User
from .forms import RegistrationForm, LoginForm, UserForm
from orders.forms import OrderForm
from orders.models import Address

# Базовый класс для упрощения функционала аутентификации
class BaseAuthView(View):
    """Базовый класс для реализации общих функций аутентификации."""
    
    def get_redirect_url(self):
        """Стандартный метод переадресации после успешного входа."""
        return redirect('/')

# Регистрация пользователя
class RegisterView(BaseAuthView):
    template_name = 'accounts/register.html'

    def get(self, request):
        """GET-запрос возвращает форму регистрации."""
        form = RegistrationForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        """POST-запрос обрабатывает отправленную форму регистрации"""
        form = RegistrationForm(request.POST)
        if form.is_valid():
            # Извлекаем очищенные данные из формы
            cleaned_data = form.cleaned_data
            
            # Создаем нового пользователя
            user = User.objects.create_user(
                phone_number=cleaned_data['phone_number'],
                first_name=cleaned_data['first_name'],
            )
            user.set_password(cleaned_data['password1'])  # Безопасная установка пароля
            user.save()
            login(request, user)
            if form.cleaned_data.get('is_checkout_registration'):
                return redirect('accounts:profile')
            return self.get_redirect_url()
        return render(request, self.template_name, {'form': form})

# Вход пользователя
class LoginView(BaseAuthView):
    template_name = 'accounts/login.html'

    def get(self, request):
        """GET-запрос возвращает форму входа."""
        form = LoginForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        """POST-запрос обрабатывает отправленную форму входа."""
        form = LoginForm(request.POST)
        if form.is_valid():
            user = form.cleaned_data['user']
            login(request, user)
            return self.get_redirect_url()
        return render(request, self.template_name, {'form': form})

# Выход пользователя
class LogoutView(BaseAuthView):
    def get(self, request):
        """GET-запрос производит выход пользователя из системы."""
        logout(request)
        return redirect('accounts:login')

    def post(self, request):
        """POST-запрос производит выход пользователя из системы."""
        logout(request)
        return redirect('accounts:login')

# Управление адресом пользователя
class AddressView(LoginRequiredMixin, BaseAuthView):
    template_name = 'accounts/address.html'

    def get(self, request):
        """GET-запрос возвращает страницу управления адресом."""
        addresses = Address.objects.filter(user=request.user).order_by('-created_at')

        # Фильтруем только уникальные и непустые адреса
        unique_addresses = []
        seen_addresses = set()

        for addr in addresses:
            # Проверяем, что адрес не пустой (хотя бы город и улица заполнены)
            if addr.city and addr.street:
                # Создаем уникальный ключ для адреса
                address_key = (addr.city, addr.street, addr.house, addr.building, addr.apartment, addr.postal_code)
                if address_key not in seen_addresses:
                    seen_addresses.add(address_key)
                    unique_addresses.append(addr)

        if unique_addresses:
            form = OrderForm(instance=unique_addresses.first())
        else:
            form = OrderForm()
        return render(request, self.template_name, {'form': form, 'addresses': unique_addresses})

    def post(self, request):
        """POST-запрос сохраняет новый или обновляет существующий адрес пользователя."""
        form = OrderForm(request.POST)
        if form.is_valid():
            address, _ = Address.objects.update_or_create(user=request.user, defaults={
                'city': form.cleaned_data['city'],
                'street': form.cleaned_data['street'],
                'house': form.cleaned_data['house'],
                'building': form.cleaned_data['building'],
                'apartment': form.cleaned_data['apartment'],
                'postal_code': form.cleaned_data['postal_code'],
            })
            return self.get_redirect_url()
        return render(request, self.template_name, {'form': form})

# Профиль пользователя
class UserView(LoginRequiredMixin, BaseAuthView):
    template_name = 'accounts/profile.html'

    def get(self, request):
        """GET-запрос возвращает профиль пользователя с информацией о заказах и избранных продуктах."""
        form = UserForm(instance=request.user)
        orders = request.user.orders.all()
        favorite_products = request.user.favorite_products.all()

        # Получить адреса пользователя
        addresses = Address.objects.filter(user=request.user).order_by('-created_at')

        # Фильтруем только уникальные и непустые адреса
        unique_addresses = []
        seen_addresses = set()

        for addr in addresses:
            # Проверяем, что адрес не пустой (хотя бы город и улица заполнены)
            if addr.city and addr.street:
                # Создаем уникальный ключ для адреса
                address_key = (addr.city, addr.street, addr.house, addr.building, addr.apartment, addr.postal_code)
                if address_key not in seen_addresses:
                    seen_addresses.add(address_key)
                    unique_addresses.append(addr)

        address = unique_addresses[0] if unique_addresses else None

        return render(request, self.template_name, {
            'form': form,
            'orders': orders,
            'favorite_products': favorite_products,
            'address': address,
            'addresses': unique_addresses,
        })

    def post(self, request):
        """POST-запрос обновляет профиль пользователя."""
        if request.POST.get('receive_notifications') == 'on':
            request.user.receive_notifications = True
        else:
            request.user.receive_notifications = False
        request.user.save()

        form = UserForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return self.get_redirect_url()
        return render(request, self.template_name, {
            'form': form,
            'orders': request.user.orders.all(),
            'favorite_products': request.user.favorite_products.all(),
            'address': Address.objects.filter(user=request.user).first(),
        })
