from django.dispatch import receiver
from django.db.models.signals import pre_save
from django.contrib import messages
from django.utils.translation import gettext_lazy as _

from .models import Order

@receiver(pre_save, sender=Order)
def notify_on_status_change(sender, instance, **kwargs):
    """
    Отправляет уведомление пользователю при изменении статуса заказа.
    """
    previous_instance = sender.objects.filter(pk=instance.pk).first()
    if previous_instance and previous_instance.status != instance.status:
        message_map = {
            'processing': _('Заказ принят в обработку.'),
            'shipped': _('Заказ отправлен в доставку.'),
            'completed': _('Заказ выполнен.'),
            'cancelled': _('Заказ отменён.'),
        }
        notification_text = message_map.get(instance.status, _('Изменился статус заказа.'))
        messages.info(previous_instance.user, notification_text)
        