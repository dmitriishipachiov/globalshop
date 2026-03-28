import re
from django.core.exceptions import ValidationError

def validate_phone_number(value):
    pattern = r'^(\+7|8)\d{10}$'
    if not re.match(pattern, value):
        raise ValidationError("Некорректный формат номера телефона. Пример: +79991234567 или 89991234567.")