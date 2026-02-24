from django import template

register = template.Library()


@register.filter
def multiply(value, arg):
    return value * arg

@register.filter
def format_thousands(value):
    try:
        value = float(value)
        # Форматируем с двумя знаками после запятой и пробелом между тысячами
        return '{:,.2f}'.format(value).replace(',', ' ').replace('.', ',')
    except (ValueError, TypeError):
        return value
