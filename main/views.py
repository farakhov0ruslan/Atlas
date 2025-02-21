from django.contrib.auth import logout
from .forms import UserRegistrationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse

# def survey_redirect(request):
#     if request.method == "POST":
#         # Получаем данные формы
#         city = request.POST.get("city")
#         person_count = request.POST.get("person_count")
#         budget = request.POST.get("budget", "Не указано")
#         departure_date = request.POST.get("departure_date")
#         return_date = request.POST.get("return_date")
#
#         # Сохраняем данные в сессии для перенаправления
#         request.session['city'] = city
#         request.session['person_count'] = person_count
#         request.session['budget'] = budget
#         request.session['departure_date'] = departure_date
#         request.session['return_date'] = return_date
#
#         # Перенаправляем на страницу опроса
#         return redirect("survey:survey_index")
#     return redirect("your_template_url")


def index(request):
    return render(request, 'main/index.html', {'user': request.user})


def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()  # Сохраняем пользователя
            login(request, user)  # Логиним пользователя
            # Возвращаем успешный ответ с редиректом на главную страницу
            return JsonResponse({'success': True, 'redirect_url': '/'})  # Перенаправляем на главную страницу
        else:
            errors = {}
            for field, error_list in form.errors.items():
                errors[field] = error_list  # Собираем ошибки для каждого поля
            return JsonResponse({'success': False, 'errors': errors})  # Отправляем ошибки на фронт
    else:
        form = UserRegistrationForm()

    return render(request, 'main/index.html', {'form': form})


@login_required
def profile(request):
    return render(request, 'main/profile.html')

def custom_logout(request):
    logout(request)  # Завершаем сессию пользователя
    return redirect('main:index')  # Перенаправляем на главную страницу

def login_view(request):
    if request.method == "POST":
        email = request.POST.get('email')  # Получаем email
        password = request.POST.get('password')  # Получаем пароль

        # Аутентификация по email, а не username
        user = authenticate(request, email=email, password=password)

        if user is not None:
            login(request, user)  # Логиним пользователя
            return JsonResponse({"success": True, "redirect_url": '/'})  # Возвращаем JSON для успешного входа
        else:
            # Если аутентификация не прошла
            return JsonResponse({"success": False, "errors": {"email": "Неверные данные для входа.", "password": "Неверные данные для входа."}})

    return render(request, 'main/index.html')


def save_location_to_session(request):
    """
    Сохраняет геопозицию в сессии Django.
    """
    if request.method == "POST":
        lat = request.POST.get("lat")
        lon = request.POST.get("lon")

        if lat and lon:
            request.session["latitude"] = lat
            request.session["longitude"] = lon
            return JsonResponse({"success": True, "message": "Геопозиция сохранена в сессии."})

    return JsonResponse({"success": False, "message": "Ошибка сохранения геопозиции."})


@login_required
def save_location_to_db(request):
    """
    Сохраняет геопозицию в БД для авторизованных пользователей.
    """
    if request.method == "POST":
        lat = request.POST.get("lat")
        lon = request.POST.get("lon")

        if lat and lon:
            request.user.latitude = lat
            request.user.longitude = lon
            request.user.save()
            return JsonResponse({"success": True, "message": "Геопозиция обновлена в базе данных."})

    return JsonResponse({"success": False, "message": "Ошибка обновления геопозиции."})


def get_user_location(request):
    """
    Возвращает геолокацию пользователя (из БД, если авторизован, или из сессии).
    """
    if request.user.is_authenticated:
        latitude = getattr(request.user, "latitude", None)
        longitude = getattr(request.user, "longitude", None)

        if latitude is not None and longitude is not None:
            return JsonResponse({
                "latitude": latitude,
                "longitude": longitude
            })

    # Если пользователь не авторизован, пробуем взять из сессии
    latitude = request.session.get("latitude")
    longitude = request.session.get("longitude")

    if latitude and longitude:
        return JsonResponse({"latitude": latitude, "longitude": longitude})

    return JsonResponse({"latitude": None, "longitude": None})
