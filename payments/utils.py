# payments/utils.py
import hmac
import hashlib
from django.conf import settings
import ipaddress


def make_payment_signature(payment_id: str, amount: str, currency: str) -> str:
    """
    Собирает строку из полей и возвращает HMAC-SHA256 hex.
    """
    # например: "payment_id|amount|currency"
    data = f"{payment_id}|{amount}|{currency}"
    # используем секрет из настроек
    secret = settings.SECRET_KEY.encode('utf-8')
    return hmac.new(secret, data.encode('utf-8'), hashlib.sha256).hexdigest()


# Список доверенных диапазонов и отдельных адресов ЮKassa
ALLOWED_YOOKASSA_IPS = [
    '185.71.76.0/27',
    '185.71.77.0/27',
    '77.75.153.0/25',
    '77.75.156.11/32',
    '77.75.156.35/32',
    '77.75.154.128/25',
    '2a02:5180::/32',
]


def client_ip(request):
    ip = request.META.get('REMOTE_ADDR')
    # Если же запросы идут через nginx/LoadBalancer:
    xfwd = request.META.get('HTTP_X_FORWARDED_FOR')
    # print(xfwd)
    if xfwd:
        ip = xfwd.split(',')[0].strip()
    return ip


def is_allowed_yookassa_ip(ip_str: str) -> bool:
    try:
        addr = ipaddress.ip_address(ip_str)
    except ValueError:
        return False
    for net in ALLOWED_YOOKASSA_IPS:
        if addr in ipaddress.ip_network(net):
            return True
    return False
