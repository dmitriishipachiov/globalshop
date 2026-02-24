from typing import Any, Dict, Optional

from django.views.generic import View, TemplateView
from django.urls import reverse_lazy
from django.http import JsonResponse, HttpRequest, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.contrib.auth import get_user_model, login
from django.contrib.auth.base_user import AbstractBaseUser
from django.db import transaction

from orders.forms import OrderForm
from accounts.models import User
from carts.models import Cart, CartItem
from shop.models import ProductShop
from orders.models import Address, Order, OrderItem

User = get_user_model()

class CartView(TemplateView):
    """
    Представление для отображения корзины пользователя.
    """
    template_name = 'carts/cart.html'

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)

        # Получаем корзину
        cart = Cart.get_or_create_cart(self.request)

        context['cart'] = cart
        context['cart_items'] = cart.items.all()
        context['total_sum'] = cart.total_price
        context['total_quantity'] = sum(item.quantity for item in cart.items.all())
        return context

class AddToCartView(View):
    """
    Представление для добавления товара в корзину.
    """

    def get(self, request: HttpRequest, product_slug: str) -> HttpResponse:
        return self.post(request, product_slug)

    def post(self, request: HttpRequest, product_slug: str) -> HttpResponse:
        product = get_object_or_404(ProductShop, slug=product_slug)

        # Получаем корзину
        cart = Cart.get_or_create_cart(request)

        if product.quantity == 0:
            messages.warning(request, 'Товар закончился.')
            return redirect('carts:view_cart')

        cart_item, item_created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'price': product.sell_price(), 'quantity': 1}
        )
        if not item_created and cart_item.quantity < product.quantity:
            cart_item.quantity += 1
            cart_item.price = product.sell_price()
            cart_item.save()
        elif item_created and product.quantity > 0:
            cart_item.quantity = 1
            cart_item.price = product.sell_price()
            cart_item.save()
        else:
            messages.warning(request, 'Максимальное количество товара достигнуто.')

        return redirect('carts:view_cart')

class RemoveFromCartView(View):
    """
    Представление для удаления товара из корзины.
    """
    def post(self, request: HttpRequest, item_id: int) -> JsonResponse:
        # Получаем корзину
        cart = Cart.get_or_create_cart(request)

        try:
            cart_item = cart.items.get(pk=item_id)
            cart_item.delete()
        except CartItem.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Товар не найден.'})

        # Возвращаем обновленные данные корзины
        data = {
            'success': True,
            'total_sum': cart.total_price,
            'total_quantity': sum(item.quantity for item in cart.items.all()),
        }
        return JsonResponse(data)

class UpdateCartView(View):
    """
    Обновление количества товара в корзине на основе delta.
    """

    def post(self, request, item_id):
        try:
            delta = int(request.POST.get('quantity_delta'))
            if delta == 0:
                return JsonResponse({'success': False, 'error': 'Delta не может быть нулевым.'})

            # Получаем корзину
            cart = Cart.get_or_create_cart(request)

            cart_item = get_object_or_404(cart.items, id=item_id)
            product = cart_item.product
            new_quantity = cart_item.quantity + delta

            if new_quantity <= 0:
                cart_item.delete()
            elif new_quantity > product.quantity:
                return JsonResponse({'success': False, 'error': 'Недостаточно товара на складе.'})
            else:
                cart_item.quantity = new_quantity
                cart_item.price = product.sell_price()
                cart_item.save()

            # Возвращаем обновленные данные корзины
            data = {
                'success': True,
                'total_sum': cart.total_price,
                'total_quantity': sum(item.quantity for item in cart.items.all()),
            }
            return JsonResponse(data)

        except ValueError:
            return JsonResponse({'success': False, 'error': 'Невалидное значение delta.'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

class CheckoutView(SuccessMessageMixin, View):
    """
    Представление для оформления заказа.
    """
    success_message = 'Ваш заказ успешно оформлен!'

    def get(self, request: HttpRequest) -> HttpResponse:
        cart = self._get_cart(request)
        
        initial_data = self._get_initial_form_data(request, cart)
        form = OrderForm(initial=initial_data)
        
        return render(request, 'carts/checkout.html', {'cart': cart, 'form': form})

    def post(self, request: HttpRequest) -> HttpResponse:
        cart = self._get_cart(request)
        
        if not cart.items.exists():
            messages.error(request, 'Корзина пуста.')
            return redirect('carts:view_cart')

        form = OrderForm(request.POST)
        if not form.is_valid():
            # Отображение конкретных ошибок формы
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
            return render(request, 'carts/checkout.html', {'cart': cart, 'form': form})

        try:
            with transaction.atomic():
                user = self._create_or_get_user(request, form)
                order = self._create_order(request, form, cart, user)
                self._process_order_items(cart, order)
                self._clear_cart_and_session(cart, request, user)
                
                messages.success(request, self.success_message)
                if user:
                    # Если пользователь был создан, нужно его авторизовать
                    login(request, user)
                return redirect('orders:order_detail', pk=order.pk)
        except Exception as e:
            messages.error(request, f'Ошибка оформления заказа: {str(e)}')
            return render(request, 'carts/checkout.html', {'cart': cart, 'form': form})

    def _get_cart(self, request: HttpRequest) -> Cart:
        """Получает корзину пользователя."""
        if request.user.is_authenticated:
            cart, created = Cart.objects.get_or_create(user=request.user)
        else:
            session_id = request.session.session_key
            if not session_id:
                messages.error(request, 'Ошибка сессии.')
                return redirect('carts:view_cart')
            cart, created = Cart.objects.get_or_create(session_id=session_id)
        return cart

    def _get_initial_form_data(self, request: HttpRequest, cart: Cart) -> Dict[str, Any]:
        """Получает начальные данные для формы из профиля пользователя."""
        initial_data = {}
        
        if request.user.is_authenticated:
            # Получаем адреса пользователя, если они существуют
            addresses = Address.objects.filter(user=request.user).order_by('-created_at')
            if addresses.exists():
                # Если есть адреса, используем последний добавленный
                address = addresses.first()
                initial_data = {
                    'first_name': request.user.first_name,
                    'last_name': request.user.last_name,
                    'email': request.user.email,
                    'phone': request.user.phone_number,
                    'city': address.city,
                    'street': address.street,
                    'house': address.house,
                    'building': address.building,
                    'apartment': address.apartment,
                    'postal_code': address.postal_code,
                }
            else:
                # Если адресов нет, заполняем только основные данные пользователя
                initial_data = {
                    'first_name': request.user.first_name,
                    'last_name': request.user.last_name,
                    'email': request.user.email,
                    'phone': request.user.phone_number,
                }
        return initial_data

    def _create_or_get_user(self, request: HttpRequest, form: OrderForm) -> Optional[AbstractBaseUser]:
        """Создает нового пользователя или возвращает существующего."""
        user = None
        if not request.user.is_authenticated:
            phone_number = form.cleaned_data.get('phone', '')
            # first_name = form.cleaned_data.get('first_name', '')
            # last_name = form.cleaned_data.get('last_name', '')
            # email = form.cleaned_data.get('email', '')

            # Создаем нового пользователя
            password = form.cleaned_data.get('password', '')
            password2 = form.cleaned_data.get('password2', '')
            if password and password == password2:  # Если пароли совпадают, создаем пользователя
                user = User.objects.create_user(
                    phone_number=phone_number,
                    password=password,
                    # first_name=first_name,
                    # last_name=last_name,
                    # email=email
                )
            else:
                messages.error(request, 'Пароли не совпадают.')
                raise ValueError('Passwords do not match')
        
        # Если пользователь авторизован или только что создан, привязываем корзину к нему
        if user:
            cart = self._get_cart(request)
            cart.user = user
            cart.session_id = None  # Удаляем session_id
            cart.save()
            
        return user

    def _create_order(self, request: HttpRequest, form: OrderForm, cart: Cart, user: Optional[AbstractBaseUser]) -> Order:
        """Создает заказ."""
        # Создайте или получите адрес
        address_data = {
            'city': form.cleaned_data['city'],
            'street': form.cleaned_data['street'],
            'house': form.cleaned_data['house'],
            'building': form.cleaned_data['building'],
            'apartment': form.cleaned_data['apartment'],
            'postal_code': form.cleaned_data['postal_code'],
        }

        # Если пользователь аутентифицирован, связать адрес с пользователем
        if request.user.is_authenticated:
            address_data['user'] = request.user
        elif user:  # Если пользователь был создан
            address_data['user'] = user

        # Проверяем, существует ли уже такой адрес у пользователя
        current_user = user or request.user
        if current_user.is_authenticated:
            # Ищем существующий адрес с такими же данными
            existing_address = Address.objects.filter(
                user=current_user,
                city=address_data['city'],
                street=address_data['street'],
                house=address_data['house'],
                building=address_data['building'],
                apartment=address_data['apartment'],
                postal_code=address_data['postal_code']
            ).first()

            if existing_address:
                address = existing_address
            else:
                # Создаем новый адрес только если такого еще нет
                address = Address.objects.create(**address_data)
        else:
            # Для неавторизованных пользователей всегда создаем новый адрес
            address = Address.objects.create(**address_data)

        # Создать заказ
        order = form.save(commit=False)
        order.user = user or request.user
        order.address = address
        order.payment_method = form.cleaned_data['payment_method']
        
        # Обновляем профиль пользователя (для всех случаев: авторизован или нет)
        current_user = user or request.user
        if current_user.is_authenticated:
            update_fields = []
            first_name = form.cleaned_data.get('first_name', '').strip()
            last_name = form.cleaned_data.get('last_name', '').strip()
            email = form.cleaned_data.get('email', '').strip()

            if first_name and current_user.first_name!= first_name:
                current_user.first_name = first_name
                update_fields.append('first_name')
            if last_name and current_user.last_name != last_name:
                current_user.last_name = last_name
                update_fields.append('last_name')
            if email and current_user.email != email:
                current_user.email = email
                update_fields.append('email')

            if update_fields:
                current_user.save(update_fields=update_fields)

        order.save()
                
        return order

    def _process_order_items(self, cart: Cart, order: Order) -> None:
        """Обрабатывает элементы заказа."""
        for item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity
            )
            item.product.quantity -= item.quantity
            item.product.save()

    def _clear_cart_and_session(self, cart: Cart, request: HttpRequest, user: Optional[AbstractBaseUser]) -> None:
        """Очищает корзину и сессию."""
        cart.items.all().delete()
        
        # Очищаем сессию после оформления заказа для неавторизованных пользователей
        if not user and not request.user.is_authenticated:
            request.session.flush()
