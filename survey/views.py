from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from django.templatetags.static import static

def survey_view(request):
    # Сохраняем данные из сессии
    if request.method == "POST":
        request.session['city'] = request.POST.get('city', 'Не указано')
        request.session['person_count'] = request.POST.get('person_count', 'Не указано')
        request.session['budget'] = request.POST.get('budget', 'Не указано')
        request.session['departure_date'] = request.POST.get('departure_date', 'Не указано')
        request.session['return_date'] = request.POST.get('return_date', 'Не указано')

    # Пример данных для страниц опроса
    pages_content = [
        {
            'title': 'Выберите наиболее интересные категории мест или активностей, которые вы хотите включить в план поездкии',
            'type': 'buttons', 'data': [
            'Бары', 'Музыка', 'Шоппинг', 'Экстрим', 'Достопримечательности',
            'Искусство', 'Музеи', 'Гулять', 'Инстаграмные места', 'Экскурсии', 'Вкусно поесть'
        ]},
        {'title': 'Как вы видите вашу поездку? (выберите картинки)', 'type': 'images', 'data': [
            {'src': static('deps/images/survey/бары опросник.jpg'), 'alt': 'Бары'},
            {'src': static('deps/images/survey/музеи опросник.jpg'), 'alt': 'Вкусно поесть'},
            {'src': static('deps/images/survey/достопримечательности опросник.jpg'), 'alt': 'Достопримечательности'},
            {'src': static('deps/images/survey/музеи опросник.jpg'), 'alt': 'Музеи'},
            {'src': static('deps/images/survey/музыка опросник.jpeg'), 'alt': 'Музыка'},
            {'src': static('deps/images/survey/экстрим опросник.jpg'), 'alt': 'Экстрим'}
        ]}
    ]

    # Пагинация
    paginator = Paginator(pages_content, 1)
    page_number = request.GET.get('page', 1)
    page_content = paginator.get_page(page_number)

    return render(request, 'survey/survey.html', {'page_content': page_content})