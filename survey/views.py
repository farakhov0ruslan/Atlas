from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from django.templatetags.static import static
import json

def survey_view(request):
    if request.method == "POST":
        if 'city' in request.POST:
            request.session['city'] = request.POST.get('city', 'Не указано')
        if 'person_count' in request.POST:
            request.session['person_count'] = request.POST.get('person_count', 'Не указано')
        if 'budget' in request.POST:
            request.session['budget'] = request.POST.get('budget', 'Не указано')
        if 'departure_date' in request.POST:
            request.session['departure_date'] = request.POST.get('departure_date', 'Не указано')
        if 'return_date' in request.POST:
            request.session['return_date'] = request.POST.get('return_date', 'Не указано')
        print(request.session.items())
        # Если пришёл POST с первой страницы (кнопки)
        selected_categories = request.POST.get('selected_categories')
        if selected_categories:
            request.session['selected_categories'] = json.loads(selected_categories)
        # Если пришёл POST со второй страницы (изображения)
        selected_images = request.POST.get('selected_images')
        if selected_images:
            request.session['selected_images'] = json.loads(selected_images)

    # Пример данных для страниц опроса
    pages_content = [
        {
            'title': 'Выберите наиболее интересные категории мест или активностей, которые вы хотите включить в план поездки',
            'type': 'buttons',
            'data': [
                'Бары', 'Музыка', 'Шоппинг', 'Экстрим', 'Достопримечательности',
                'Искусство', 'Музеи', 'Гулять', 'Инстаграмные места', 'Экскурсии', 'Вкусно поесть'
            ]
        },
        {
            'title': 'Как вы видите вашу поездку? (выберите картинки)',
            'type': 'images',
            'data': [
                {'src': static('deps/images/survey/бары опросник.jpg'), 'alt': 'Бары'},
                {'src': static('deps/images/survey/вкусно поесть опросник.jpg'),
                 'alt': 'Вкусно поесть'},
                {'src': static('deps/images/survey/достопримечательности опросник.jpg'),
                 'alt': 'Достопримечательности'},
                {'src': static('deps/images/survey/музеи опросник.jpg'), 'alt': 'Музеи'},
                {'src': static('deps/images/survey/музыка опросник.jpeg'), 'alt': 'Музыка'},
                {'src': static('deps/images/survey/экстрим опросник.jpg'), 'alt': 'Экстрим'}
            ]
        },
        {
            'title': 'Укажите ваши пожелания (например: "Я хочу завтрак каждый день. Хочу вечер второго дня в баре.")',
            'type': 'text'
        }
    ]

    # Пагинация
    paginator = Paginator(pages_content, 1)
    page_number = request.GET.get('page', 1)
    page_content = paginator.get_page(page_number)

    return render(request, 'survey/survey.html', {'page_content': page_content})