from datetime import datetime
from django.shortcuts import render
from routes.utils.route_generator import generate_route
from routes.models import Place


def route_page(request):
    # Получаем данные из сессии
    city = request.session.get('city', 'Не указано')
    departure_date = request.session.get('departure_date', 'Не указано')
    return_date = request.session.get('return_date', 'Не указано')
    person_count = request.session.get('person_count', 'Не указано')
    budget = request.session.get('budget', 'Не указано')

    # Вычисляем количество дней
    try:
        departure_date = datetime.strptime(departure_date, '%Y-%m-%d')
        return_date = datetime.strptime(return_date, '%Y-%m-%d')
        days_count = (return_date - departure_date).days + 1  # Количество дней
        days = [f"День {i + 1}" for i in range(days_count)]  # Формируем список "День 1", "День 2" и т.д.
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
    user_preferences = f"""
    Я хочу завтрак каждый день. Поездка на {days_count} дней
    """
    route = generate_route(user_preferences)


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
