import hashlib
import json
import threading
from django.http import JsonResponse
from datetime import datetime
from django.shortcuts import render
from routes.utils.route_generator import generate_route
from routes.models import Place


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
        'days_count': request.session.get('days_count', 0),
        'person_count': request.session.get('person_count', 'Не указано'),
        'budget': request.session.get('budget', 'Не указано'),
        'selected_categories': request.session.get('selected_categories', []),
        'selected_images': request.session.get('selected_images', []),
        'preferences': request.session.get('preferences', ''),
    }
    print(request.session.items())

    days = [f"День {i + 1}" for i in range(session_data['days_count'])]

    # Вычисляем количество дней




    # Проверяем, есть ли уже маршрут в сессии
    route_json = request.session.get('route')
    if route_json:
        try:
            route = json.loads(route_json)
        except json.JSONDecodeError:
            route = None
    else:
        route = None


    # Если маршрут уже готов, подставляем объекты Place по идентификатору
    for route_day in route:
        for activity in route[route_day]:
            if activity.get("place_id"):
                activity["place"] = Place.objects.get(id=activity["place_id"])
            else:
                activity["place"] = None

    context = {
        "title": "Ваш маршрут",
        "city": session_data['city'],
        "days_count": session_data['days_count'],
        "current_day_index": int(request.GET.get('day', 1)) - 1,
        "current_day": days[0] if days else "Не указано",
        "days": days,
        "person_count": session_data['person_count'],
        "budget": session_data['budget'],
        "route": route
    }
    return render(request, 'routes/route_page.html', context)


def generate_route_bg(session_key, user_preferences, current_fingerprint):
    from django.contrib.sessions.models import Session
    from django.contrib.sessions.backends.db import SessionStore

    route = generate_route(user_preferences)
    # route = ""
    # import time
    # time.sleep(20)
    try:

        s = SessionStore(session_key=session_key)
        s['route_status'] = 'completed'
        s['route'] = json.dumps(route)
        s.save()
    except Session.DoesNotExist:
        pass  # Сессия могла истечь или пропасть


def start_route(request):
    # Из сессии получаем необходимые данные

    selected_categories = request.session.get('selected_categories', [])
    selected_images = request.session.get('selected_images', [])
    preferences = request.session.get('preferences', '')
    departure_date = request.session.get('departure_date', 'Не указано')
    return_date = request.session.get('return_date', 'Не указано')

    # Допустим, вычисляем количество дней, если нужно
    try:
        departure_date = datetime.strptime(departure_date, '%Y-%m-%d')
        return_date = datetime.strptime(return_date, '%Y-%m-%d')
        days_count = (return_date - departure_date).days + 1
        request.session["days_count"] = days_count
    except ValueError:
        days_count = 0

    # Вычисляем пользовательский запрос и фингерпринт
    user_preferences = (
        f"Я хочу чтобы было больше тегов {selected_images + selected_categories}. "
        f"{preferences}. Поездка на {days_count} дней"
    )
    print(user_preferences)

    current_fingerprint = compute_route_fingerprint(request.session)

    route_json = request.session.get('route')
    if route_json:
        try:
            route = json.loads(route_json)
        except json.JSONDecodeError:
            route = None
    else:
        route = None

    saved_fingerprint = request.session.get('route_fingerprint')
    # Если маршрут отсутствует или параметры изменились ищем маршрут иначе completed
    if not route or current_fingerprint != saved_fingerprint:
        # Запускаем фоновую задачу
        t = threading.Thread(
            target=generate_route_bg,
            args=(request.session.session_key, user_preferences, current_fingerprint),
            daemon=True
        )
        t.start()

        request.session["route_status"] = "started"
        return JsonResponse({"status": "started"})

    return JsonResponse({"status": "completed"})


def check_route(request):
    # Возвращаем статус из сессии
    status = request.session.get('route_status', 'no_session')
    route_data = request.session.get('route_data', {})

    return JsonResponse({
        "status": status,
        "route_data": route_data
    })
