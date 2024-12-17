from django.shortcuts import render
from django.shortcuts import render
from django.http import HttpResponse
from datetime import datetime
from django.shortcuts import redirect

def survey_redirect(request):
    if request.method == "POST":
        # Получаем данные формы
        city = request.POST.get("city")
        person_count = request.POST.get("person_count")
        budget = request.POST.get("budget", "Не указано")
        departure_date = request.POST.get("departure_date")
        return_date = request.POST.get("return_date")

        # Сохраняем данные в сессии для перенаправления
        request.session['city'] = city
        request.session['person_count'] = person_count
        request.session['budget'] = budget
        request.session['departure_date'] = departure_date
        request.session['return_date'] = return_date

        # Перенаправляем на страницу опроса
        return redirect("survey:survey_index")

    return redirect("your_template_url")


def index(request):
    return render(request, 'main/index.html')
