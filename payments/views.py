import datetime
import hmac
import json
import uuid
from django.urls import reverse
from django.http import JsonResponse, HttpResponseForbidden, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from yookassa import Payment, Configuration
from Atlas.settings import YOOKASSA_API_KEY, YOOKASSA_SHOP_ID
from main.models import SubscriptionPlan, Subscription
from django.db.models import Max
from .models import Payment as PaymantModel
from .utils import make_payment_signature, client_ip, is_allowed_yookassa_ip


@csrf_exempt
@require_POST
def payment_view(request):
    user = request.user
    if not user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'Not authenticated'}, status=403)
    try:
        payload = json.loads(request.body.decode('utf-8'))
        increment = payload.get('increment')
        price = payload.get('price')
        duration = payload.get('duration')
        plan_id = payload.get('plan_id')
        try:
            plan = SubscriptionPlan.objects.get(pk=plan_id)
        except (SubscriptionPlan.DoesNotExist, TypeError, ValueError):
            return JsonResponse({'success': False, 'error': 'Неверный план подписки'}, status=400)

        # 2) вычисляем «номер» покупки = max(id) + 1
        last = PaymantModel.objects.aggregate(max_id=Max('id'))['max_id'] or 0
        order_number = last + 1

        # 3) готовим описание
        description = f"Покупка №{order_number} - Пакет «{plan.name}»"
        # Здесь ваша логика создания заказа в YooKassa,
        Configuration.account_id = YOOKASSA_SHOP_ID
        Configuration.secret_key = YOOKASSA_API_KEY

        idempotence_key = str(uuid.uuid4())
        return_url = request.build_absolute_uri(
            reverse('main:index')
        )
        payment = Payment.create({
            "amount": {
                "value": price,
                "currency": "RUB"
            },
            "payment_method_data": {
                "type": "bank_card"
            },
            "confirmation": {
                "type": "redirect",
                "return_url": return_url
            },
            "description": description,
            "capture": True,
        }, idempotence_key)

        print(payment.__dict__.items())
        confirmation_url = payment.confirmation.confirmation_url
        signature = make_payment_signature(payment.id, str(payment.amount.value),
                                           payment.amount.currency)
        PaymantModel.objects.create(
            user=request.user,
            yookassa_id=payment.id,
            amount=payment.amount.value,
            currency=payment.amount.currency,
            description=description,
            test=payment.test,
            status=payment.status,
            refundable=payment.refundable,
            signature=signature,
            subscription_plan=plan
        )

        return JsonResponse({
            'success': True,
            'confirmation_url': confirmation_url
        })
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Неверный формат JSON'}, status=400)
    # except Exception as e:
    #     return JsonResponse({'success': False, 'error': str(e)}, status=500)


@require_POST
@csrf_exempt
def payment_cb(request):
    ip = client_ip(request)
    if not is_allowed_yookassa_ip(ip):
        print(f"Forbidden: unexpected IP {ip}")
        return HttpResponseForbidden(f"Forbidden: unexpected IP {ip}")
    payload = json.loads(request.body)
    payment_id = payload.get("object", {}).get("id")
    new_status = payload.get("object", {}).get("status")
    amount = payload["object"]["amount"]["value"]
    currency = payload["object"]["amount"]["currency"]

    try:
        payment = PaymantModel.objects.get(yookassa_id=payment_id)
    except PaymantModel.DoesNotExist:
        return HttpResponseForbidden("Unknown payment")

    expected_sig = make_payment_signature(payment_id, str(amount), currency)
    if not hmac.compare_digest(expected_sig, payment.signature):
        return HttpResponseForbidden("Bad signature")

    # всё в порядке — обновляем статус
    payment.status = new_status
    update_fields = []

    if new_status == "succeeded":
        payment.status = "succeeded"
        now = datetime.datetime.now()
        payment.paid_at = now
        update_fields += ["status", "paid_at"]

        # создаём подписку и начисляем маршруты
        Subscription.objects.create(
            user=payment.user,
            plan=payment.subscription_plan,
            end_date=now + payment.subscription_plan.duration
        )
        user = payment.user
        user.max_routes += payment.subscription_plan.routes
        user.save(update_fields=["max_routes"])

    elif new_status == "canceled":
        # Отмена — сохраняем статус exactly "canceled"
        payment.status = "canceled"
        update_fields.append("status")

    else:
        # Любой другой статус
        payment.status = new_status
        update_fields.append("status")

    payment.save(update_fields=update_fields)
    return HttpResponse("OK")
