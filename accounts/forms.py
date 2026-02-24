from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate
from .models import User

class RegistrationForm(forms.ModelForm):
        phone_number = forms.CharField(max_length=15)
        first_name = forms.CharField(max_length=15)
        password1 = forms.CharField(label='Пароль', widget=forms.PasswordInput)
        password2 = forms.CharField(label='Подтверждение пароля', widget=forms.PasswordInput)
        class Meta:
            model = User
            fields = ['phone_number', 'first_name', 'password1', 'password2']

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
