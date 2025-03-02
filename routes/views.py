import hashlib
import json
from datetime import datetime
from django.shortcuts import render
from routes.utils.route_generator import generate_route
from routes.models import Place
import time




def compute_route_fingerprint(data):
    # Формируем строку из параметров
    data_str = f"""{data.get('selected_categories', '')}
    _{data.get('departure_date', '')}_{data.get('return_date', '')}_
    {data.get('selected_images', '')}_{data.get('preferences', '')}
    """
    # Вычисляем MD5-хэш
    return hashlib.md5(data_str.encode('utf-8')).hexdigest()


def route_page(request):
    # Получаем данные из сессии
    session_data = {
        'city': request.session.get('city', 'Не указано'),
        'departure_date': request.session.get('departure_date', 'Не указано'),
        'return_date': request.session.get('return_date', 'Не указано'),
        'person_count': request.session.get('person_count', 'Не указано'),
        'budget': request.session.get('budget', 'Не указано'),
        'selected_categories': request.session.get('selected_categories', []),
        'selected_images': request.session.get('selected_images', []),
        'preferences': request.POST.get('preferences', request.session.get('preferences', ''))
    }
    request.session['preferences'] = session_data['preferences']
    print(request.session.items())

    # Вычисляем количество дней
    try:
        departure_date = datetime.strptime(session_data['departure_date'], '%Y-%m-%d')
        return_date = datetime.strptime(session_data['return_date'], '%Y-%m-%d')
        days_count = (return_date - departure_date).days + 1
        days = [f"День {i + 1}" for i in range(days_count)]
    except ValueError:
        days_count = 0
        days = []

    # Текущий день из параметра GET
    current_day_index = int(request.GET.get('day', 1)) - 1
    current_day = days[current_day_index] if 0 <= current_day_index < days_count else "Не указано"

    # Вычисляем отпечаток текущих параметров маршрута
    current_fingerprint = compute_route_fingerprint(session_data)
    saved_fingerprint = request.session.get('route_fingerprint')
    print(current_fingerprint, saved_fingerprint)

    # Проверяем, есть ли уже маршрут в сессии
    route_json = request.session.get('route')
    if route_json:
        try:
            route = json.loads(route_json)
        except json.JSONDecodeError:
            route = None
    else:
        route = None

    # Если маршрут отсутствует или параметры изменились, генерируем новый маршрут
    if not route or current_fingerprint != saved_fingerprint:
        user_preferences = f"""
            Я хочу чтобы было больше тегов {session_data['selected_images'] + session_data['selected_categories']}. {session_data['preferences']}. Поездка на {days_count} дней
            """
        route = generate_route(user_preferences)
        # time.sleep(15)  # задержка на 5 секунд
        request.session['route'] = json.dumps(route)
        request.session['route_fingerprint'] = current_fingerprint

    # Получаем места по идентификатору
    for route_day in route:
        for activity in route[route_day]:
            if activity["place_id"]:
                activity["place"] = Place.objects.get(id=activity["place_id"])
            else:
                activity["place"] = None

    context = {
        "title": "Ваш маршрут",
        "city": session_data['city'],
        "days_count": days_count,
        "current_day_index": current_day_index,
        "current_day": current_day,
        "days": days,
        "person_count": session_data['person_count'],
        "budget": session_data['budget'],
        "route": route
    }

    return render(request, 'routes/route_page.html', context)
