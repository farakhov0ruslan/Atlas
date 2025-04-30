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

    all_places = Place.objects.all()

    context = {
        "title": "Ваш маршрут",
        "city": session_data['city'],
        "days_count": session_data['days_count'],
        "current_day_index": int(request.GET.get('day', 1)) - 1,
        "current_day": days[0] if days else "Не указано",
        "days": days,
        "person_count": session_data['person_count'],
        "budget": session_data['budget'],
        "route": route,
        'all_places': all_places,
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

def replace_place(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            activity_id = data.get('activity_id')
            new_place_id = data.get('new_place_id')
            new_activity_name = data.get('new_activity_name')  # Получаем новое название события
            print("Получены данные:", activity_id, new_place_id, new_activity_name)

            # Извлекаем маршрут из сессии
            route_json = request.session.get('route')
            if not route_json:
                return JsonResponse({'error': 'Маршрут не найден в сессии.'}, status=400)
            route = json.loads(route_json)
            print("Маршрут до обновления:", route)

            updated = False
            # Проходим по всем дням маршрута
            for day_key, activities in route.items():
                for activity in activities:
                    # Ищем активность по уникальному ключу "id"
                    if str(activity.get("id")) == str(activity_id):
                        # Обновляем идентификатор места
                        activity["place_id"] = new_place_id
                        # Получаем новый объект Place
                        new_place = Place.objects.get(id=new_place_id)
                        # Обновляем данные о новом месте
                        activity["place"] = {
                            "name": new_place.name,
                            "short_description": new_place.short_description,
                            "full_description": new_place.full_description,
                            "address": new_place.address,
                            "image_url": new_place.image.url if new_place.image else '',
                            "reviews": new_place.reviews,
                            "slug": new_place.slug,
                            "contacts": new_place.contacts,
                        }
                        # Обновляем название события, если пользователь ввёл новое название
                        if new_activity_name:
                            activity["activity"] = new_activity_name
                        updated = True
                        print(f"Активность {activity_id} обновлена в дне {day_key}")
                        break
                if updated:
                    break

            if not updated:
                print("Активность не найдена")
                return JsonResponse({'error': 'Активность не найдена'}, status=404)

            # Сохраняем обновленный маршрут обратно в сессию
            request.session['route'] = json.dumps(route)
            request.session.modified = True
            print("Маршрут после обновления:", route)

            return JsonResponse({'status': 'ok'}, status=200)
        except Exception as e:
            print("Ошибка в replace_place:", str(e))
            return JsonResponse({'error': str(e)}, status=400)
    else:
        return JsonResponse({'error': 'Invalid method'}, status=405)
