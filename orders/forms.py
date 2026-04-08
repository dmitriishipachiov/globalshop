from django import forms
from django.core.validators import RegexValidator
from orders.models import Order

class OrderForm(forms.ModelForm):
    phone_validator = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Введите корректный номер телефона (например, +79123456789 или 89123456789)"
    )

    first_name = forms.CharField(label="Имя", widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Введите имя',
        'maxlength': 150
    }))

    last_name = forms.CharField(label="Фамилия", widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Введите фамилию',
        'maxlength': 150
    }))

    email = forms.EmailField(label="Email", widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': 'Введите email'
    }))

    phone = forms.CharField(
        label="Телефон",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите номер телефона (например, +79123456789)'
        }),
        validators=[phone_validator]
    )

    password = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите пароль',
            'maxlength': 128
        }),
        required=False
    )

    password2 = forms.CharField(
        label='Подтверждение пароля',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Повторите ваш пароль',
            'maxlength': 128
        }),
        required=False
    )

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password2 = cleaned_data.get("password2")

        if password and password2 and password != password2:
            self.add_error('password2', "Пароли не совпадают")

        return cleaned_data

    city = forms.CharField(label="Город", widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Введите город',
        'maxlength': 100
    }))

    street = forms.CharField(label="Улица", widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Введите улицу',
        'maxlength': 100
    }))

    house = forms.CharField(label="Дом", widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Введите номер дома',
        'maxlength': 10
    }))

    building = forms.CharField(label="Корпус", widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Корпус (если имеется)',
        'style': 'color:#ccc;'
    }), required=False)

    apartment = forms.CharField(label="Квартира", widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Введите квартиру',
        'maxlength': 10
    }), required=False)

    postal_code = forms.CharField(label="Почтовый индекс", widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Введите почтовый индекс',
        'maxlength': 10
    }), required=False)

    payment_method = forms.ChoiceField(label="Способ оплаты", choices=[
        ('cash', 'Наличными'),
        ('card', 'Картой онлайн')
    ], widget=forms.RadioSelect(attrs={'class': 'form-check-input'}))

    agree_to_terms = forms.BooleanField(
        required=True,
        label="Я принимаю пользовательское соглашение",
        error_messages={'required': 'Вы должны принять пользовательское соглашение.'}
    )

    class Meta:
        model = Order
        fields = [
            'first_name', 'last_name', 'email', 'phone', 'city', 'street',
            'house', 'building', 'apartment', 'postal_code', 'payment_method', 'agree_to_terms'
        ]