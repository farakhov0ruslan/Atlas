import json
from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from django.templatetags.static import static


def survey_view(request):
    if request.method == "POST":
        for field in ['city', 'person_count', 'budget', 'departure_date', 'return_date']:
            if field in request.POST:
                request.session[field] = request.POST[field]

        # Если пришёл POST с первой страницы (кнопки)
        selected_categories = request.POST.get('selected_categories')
        if selected_categories:
            request.session['selected_categories'] = json.loads(selected_categories)
        # Если пришёл POST со второй страницы (изображения)
        selected_images = request.POST.get('selected_images')
        if selected_images:
            request.session['selected_images'] = json.loads(selected_images)

        preferences = request.POST.get('preferences')

        print(request.POST)
        if preferences:
            print(111)
            request.session['preferences'] = preferences

        r = request.session
        r["route"] = ""
        print(r.items())

    pages_content = [
        {
            'title': 'Выберите наиболее интересные категории мест или активностей, которые вы хотите включить в план поездки',
            'type': 'buttons',
            'data': [
                'Бары', 'Музыка', 'Шоппинг', 'Экстрим', 'Достопримечательности',
                'Искусство', 'Музеи', 'Прогулка', 'Инстаграмные места', 'Экскурсии', 'Выставки', 'Вкусно поесть'
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
