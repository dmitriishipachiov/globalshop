from django.apps import AppConfig

class OrdersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'orders'
    verbose_name = 'Заказы'

    def ready(self):
        # Импортируем сигналы для их регистрации
        import orders.signals  # noqa: F401
