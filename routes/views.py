from datetime import datetime
from django.shortcuts import render
from routes.utils.route_generator import generate_route
from routes.models import Place
import json


def route_page(request):
    # Получаем данные из сессии
    city = request.session.get('city', 'Не указано')
    departure_date = request.session.get('departure_date', 'Не указано')
    return_date = request.session.get('return_date', 'Не указано')
    person_count = request.session.get('person_count', 'Не указано')
    budget = request.session.get('budget', 'Не указано')
    selected_categories = request.session.get('selected_categories', [])
    selected_images = request.session.get('selected_images', [])
    # Получаем предпочтения из сессии по ключу 'preferences'
    if request.method == "POST":
        preferences = request.POST.get('preferences', '')
        request.session['preferences'] = preferences

    print(request.session.items())

    # Вычисляем количество дней
    try:
        departure_date = datetime.strptime(departure_date, '%Y-%m-%d')
        return_date = datetime.strptime(return_date, '%Y-%m-%d')
        days_count = (return_date - departure_date).days + 1  # Количество дней
        print(days_count)
        days = [f"День {i + 1}" for i in
                range(days_count)]  # Формируем список "День 1", "День 2" и т.д.
    except ValueError:
        days_count = 0
        days = []

    # Текущий день из параметра GET
    current_day_index = int(request.GET.get('day', 1)) - 1
    if 0 <= current_day_index < days_count:
        current_day = days[current_day_index]
    else:
        current_day = "Не указано"

    # Получаем места в зависимости от выбранных категорий

    # Проверяем, есть ли уже маршрут в сессии
    route_json = request.session.get('route')
    if route_json:
        # Загружаем маршрут из сессии
        try:
            route = json.loads(route_json)
        except json.JSONDecodeError:
            route = None
    else:
        route = None

    if not route:
        print()
        user_preferences = f"""
            Я хочу завтрак каждый день. Поездка на {days_count} дней
            """
        route = generate_route(user_preferences)
        # Сохраняем маршрут в сессии как JSON
        request.session['route'] = json.dumps(route)

    for route_day in route:
        for activity in route[route_day]:
            if activity["place_id"]:
                activity["place"] = Place.objects.get(id=activity["place_id"])
            else:
                activity["place"] = None

    context = {
        "title": "Ваш маршрут",
        "city": city,
        "days_count": days_count,
        "current_day_index": current_day_index,
        "current_day": current_day,
        "days": days,
        "departure_date": departure_date.strftime('%Y-%m-%d') if days_count else "Не указано",
        "return_date": return_date.strftime('%Y-%m-%d') if days_count else "Не указано",
        "person_count": person_count,
        "budget": budget,
        "route": route
    }

    return render(request, 'routes/route_page.html', context)
