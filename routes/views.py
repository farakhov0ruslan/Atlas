import random
from datetime import datetime, timedelta

from django.shortcuts import render

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
    places = Place.objects.all()

    context = {
        "title": "Ваш маршрут",
        "places": places,
        "city": city,
        "days_count": days_count,
        "current_day_index": current_day_index,
        "current_day": current_day,
        "days": days,
        "departure_date": departure_date.strftime('%Y-%m-%d') if days_count else "Не указано",
        "return_date": return_date.strftime('%Y-%m-%d') if days_count else "Не указано",
        "person_count": person_count,
        "budget": budget,
        "route": {
            '1 день': [{'time': '08:00-09:00', 'activity': 'Завтрак', 'place': places.filter(id=8)[0]},
                       {'time': '09:00-12:00', 'activity': 'Прогулки', 'place': places.filter(id=9)[0]},
                       {'time': '12:00-14:00', 'activity': 'Обед', 'place': places.filter(id=10)[0]},
                       {'time': '14:00-16:00', 'activity': 'Шоппинг', 'place': places.filter(id=11)[0]},
                       {'time': '16:00-18:00', 'activity': 'Искусство', 'place': places.filter(id=12)[0]},
                       {'time': '18:00-20:00', 'activity': 'Вкусно поесть', 'place': places.filter(id=13)[0]}],
            '2 день': [{'time': '08:00-09:00', 'activity': 'Завтрак', 'tags': ['Еда']},
                       {'time': '09:00-13:00', 'activity': 'Экскурсии', 'tags': ['Экскурсии']},
                       {'time': '13:00-15:00', 'activity': 'Обед', 'tags': ['Еда']},
                       {'time': '15:00-17:00', 'activity': 'Музеи', 'tags': ['Музеи']},
                       {'time': '17:00-20:00', 'activity': 'Бар', 'tags': ['Бары']}]
        },
    }

    return render(request, 'routes/route_page.html', context)
