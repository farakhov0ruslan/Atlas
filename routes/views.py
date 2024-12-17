import random

from django.shortcuts import render

from routes.models import Place


def route_page(request):
    # Получаем данные из сессии
    city = request.session.get('city', 'Не указано')
    departure_date = request.session.get('departure_date', 'Не указано')
    return_date = request.session.get('return_date', 'Не указано')
    person_count = request.session.get('person_count', 'Не указано')
    budget = request.session.get('budget', 'Не указано')
    selected_buttons = request.session.get('selected_buttons', [])
    selected_images = request.session.get('selected_images', [])

    # Получаем места в зависимости от выбранных категорий
    places = Place.objects.all()
    if selected_buttons:
        places = places.filter(category__in=selected_buttons)

    context = {
        "title": "Ваш маршрут",
        "places": places,
        "city": city,
        "departure_date": departure_date,
        "return_date": return_date,
        "person_count": person_count,
        "budget": budget,
        "selected_buttons": selected_buttons,
        "selected_images": selected_images,
    }

    return render(request, 'routes/route_page.html', context)

