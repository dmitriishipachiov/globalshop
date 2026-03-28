import re
from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate
from .models import User
from accounts.validators import validate_phone_number


class RegistrationForm(forms.Form):
    phone_number = forms.CharField(
        max_length=15,
        validators=[validate_phone_number],
        label='Номер телефона'
    )
    first_name = forms.CharField(max_length=15, label='Ваше имя')
    password1 = forms.CharField(label='Пароль', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Подтверждение пароля', widget=forms.PasswordInput)

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 != password2:
            raise ValidationError("Пароли не совпадают")
        return password2

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if User.objects.filter(phone_number=phone_number).exists():
            raise ValidationError("Пользователь с таким номером телефона уже существует.")
        return phone_number

    def save(self, commit=True):
        user = User.objects.create_user(
            phone_number=self.cleaned_data['phone_number'],
            first_name=self.cleaned_data['first_name'],
            password=self.cleaned_data['password1']
        )
        return user

class LoginForm(forms.Form):
    phone_number = forms.CharField(max_length=15)
    password = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        phone_number = cleaned_data.get('phone_number')
        password = cleaned_data.get('password')

        user = authenticate(phone_number=phone_number, password=password)
        if not user:
            raise forms.ValidationError("Неверный номер телефона или пароль.")

        cleaned_data['user'] = user
        return cleaned_data

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'email', 'phone_number'
        ]

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise ValidationError("Пользователь с таким email уже существует.")
        return email