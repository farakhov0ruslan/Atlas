import hashlib
import json
import threading
from django.http import JsonResponse, Http404
from datetime import datetime
from django.shortcuts import render
from routes.utils.route_generator import generate_route
from routes.models import Place, RouteCell, Day, Route
from django.db.models import F
from django.utils import timezone

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

    # 2) Пытаемся получить маршрут из сессии
    route = None
    route_json = request.session.get('route')
    if route_json:
        try:
            route = json.loads(route_json)
        except json.JSONDecodeError:
            route = None

    # 3) Если в сессии нет маршрута и пользователь залогинен — подтягиваем последний из БД
    if route is None and request.user.is_authenticated:
        last_route = (
            Route.objects
            .filter(user_id=request.user)
            .order_by('-created_at')
            .first()
        )
        if last_route:
            # строим словарь вида {1: [...], 2: [...], ...}
            route = {}
            days_qs = Day.objects.filter(route_id=last_route).order_by('id')
            for idx, day_obj in enumerate(days_qs, start=1):
                cells = RouteCell.objects.filter(day_id=day_obj).order_by('start_time')
                activities = []
                for cell in cells:
                    activities.append({
                        "id": cell.id,
                        "time": f"{cell.start_time.strftime('%H:%M')}-{cell.end_time.strftime('%H:%M')}",
                        "activity": cell.notes or cell.place_id.name,
                        "place_id": cell.place_id.id,
                    })
                route[idx] = activities
            # обновим количество дней если оно отличается
            days_count = len(route)
            days = [f"День {i}" for i in range(1, days_count + 1)]


    # 4) Если после этого всё ещё нет маршрута — 404 или пустой
    if route is None:
        raise Http404("Маршрут не найден")

    # 5) Подмена place_id на actual Place-объект
    for route_day, activities in route.items():
        for activity in activities:
            pid = activity.get("place_id")
            if pid:
                try:
                    activity["place"] = Place.objects.get(pk=pid)
                except Place.DoesNotExist:
                    activity["place"] = None
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


def generate_route_bg(session_key, user_pk, user_preferences, current_fingerprint):
    from django.contrib.sessions.models import Session
    from django.contrib.sessions.backends.db import SessionStore

    from django.contrib.auth import get_user_model
    User = get_user_model()
    user = None
    if user_pk is not None:
        try:
            user = User.objects.get(pk=user_pk)
        except User.DoesNotExist:
            user = None
    route = generate_route(user, user_preferences)
    # route = ""
    # import time
    # time.sleep(20)
    # ========= НОВОЕ: сохраняем маршрут в БД =========
    if user is not None:
        now = timezone.now()
        # 1) создаём сам маршрут
        route_obj = Route.objects.create(
            user_id=user,
            name=f"Маршрут {now.strftime('%Y-%m-%d %H:%M')}",
            created_at=now,
            updated_at=now,
            days_count=len(route),
        )

        # 2) пробегаем по дням
        for day_index, (day_name, activities) in enumerate(route.items(), start=1):
            # вычисляем минимальное/максимальное время дня из всех активностей
            times = [act.get("time", "") for act in activities if act.get("time")]
            starts = [t.split("-")[0] for t in times if "-" in t]
            ends = [t.split("-")[1] for t in times if "-" in t]

            day_obj = Day.objects.create(
                route_id=route_obj,
                start_time=min(starts) if starts else "00:00",
                end_time=max(ends) if ends else "23:59",
            )

            # 3) сохраняем каждую активность как RouteCell
            for act in activities:
                t = act.get("time", "")
                if "-" in t:
                    start, end = t.split("-")
                else:
                    start = end = t

                place_obj = None
                pid = act.get("place_id")
                if pid:
                    try:
                        place_obj = Place.objects.get(pk=pid)
                    except Place.DoesNotExist:
                        pass

                RouteCell.objects.create(
                    day_id=day_obj,
                    place_id=place_obj,
                    start_time=start,
                    end_time=end,
                    notes=act.get("activity", ""),)
    # ======== конец вставки сохранения в БД ========

    try:

        s = SessionStore(session_key=session_key)
        s['route_status'] = 'completed'
        s['route'] = json.dumps(route)
        s.save()
    except Session.DoesNotExist:
        pass  # Сессия могла истечь или пропасть


def start_route(request):
    # 0) Убедимся, что для гостя уже есть session_key
    if not request.session.session_key:
        request.session.create()

    # 1) Квота для анонимов
    if not request.user.is_authenticated:
        if request.session['routes_left'] <= 0:
            return JsonResponse({
                "status": "no_routes",
                "message": "Пробный маршрут уже использован. Пожалуйста, зарегистрируйтесь."
            }, status=403)
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
        if request.user.is_authenticated:
            request.user.__class__.objects.filter(pk=request.user.pk) \
                .update(max_routes=F('max_routes') - 1)
            request.user.refresh_from_db(fields=['max_routes'])
        else:
            request.session['routes_left'] -= 1

        user_pk = request.user.pk if request.user.is_authenticated else None

        # Запускаем фоновую задачу
        t = threading.Thread(
            target=generate_route_bg,
            args=(
                request.session.session_key,
                user_pk,  # передаём PK пользователя
                user_preferences,
                current_fingerprint
            ),
            daemon=True
        )
        t.start()

        request.session['route_fingerprint'] = current_fingerprint
        request.session["route_status"] = "started"
        return JsonResponse({"status": "started"})

    return JsonResponse({"status": "completed"})


def check_route(request):
    # Возвращаем статус из сессии
    status = request.session.get('route_status', 'no_session')
    route_json = request.session.get('route', 'null')
    try:
        route_data = json.loads(route_json)
    except (TypeError, ValueError):
        route_data = {}

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
