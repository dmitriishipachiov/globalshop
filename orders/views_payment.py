from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.conf import settings
from yookassa import Configuration, Payment
from orders.models import Order
import json

@csrf_exempt
def yookassa_webhook(request):
    """Обработчик вебхука от ЮКасса"""
    if request.method == 'POST':
        try:
            event = json.loads(request.body)
            
            if event['event'] == 'payment.succeeded':
                payment_object = event['object']
                order_id = payment_object['metadata']['order_id']
                
                # Находим заказ и меняем статус на Оплачен
                order = Order.objects.get(id=order_id)
                order.status = 'paid'
                order.save()
                
                return HttpResponse(status=200)
                
        except Exception as e:
            return HttpResponse(status=400)
    
    return HttpResponse(status=405)


def payment_success(request, order_id):
    """Страница успешной оплаты"""
    order = Order.objects.get(id=order_id)
    return HttpResponse(f"""
    <html>
        <head><title>Оплата прошла успешно</title></head>
        <body style="text-align:center; padding-top:100px; font-family: Arial;">
            <h1 style="color: green;">✅ Оплата прошла успешно!</h1>
            <h2>Заказ #{order_id} оплачен</h2>
            <p>Наш менеджер свяжется с вами в ближайшее время для уточнения деталей доставки</p>
            <a href="/" style="display:inline-block; margin-top:20px; padding:10px 20px; background:#007bff; color:white; text-decoration:none; border-radius:5px;">Вернуться на главную</a>
        </body>
    </html>
    """)


def payment_fail(request, order_id):
    """Страница неудачной оплаты"""
    return HttpResponse(f"""
    <html>
        <head><title>Ошибка оплаты</title></head>
        <body style="text-align:center; padding-top:100px; font-family: Arial;">
            <h1 style="color: red;">❌ Оплата не прошла</h1>
            <h2>Заказ #{order_id} не был оплачен</h2>
            <p>Попробуйте повторить оплату или выберите другой способ оплаты</p>
            <a href="/cart/checkout/" style="display:inline-block; margin-top:20px; padding:10px 20px; background:#007bff; color:white; text-decoration:none; border-radius:5px;">Вернуться к оформлению заказа</a>
        </body>
    </html>
    """)