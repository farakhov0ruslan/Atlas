from django.core.paginator import Paginator
from django.shortcuts import render
from django.templatetags.static import static

def survey_index(request):
    return render(request, 'survey/survey.html')


def survey_second(request):
    return render(request, 'survey/survey_second.html')

def survey_view(request):
    # Данные для отображения на страницах
    pages_content = [
        {'title': 'Выберите наиболее интересные категории мест или активностей, которые вы хотите включить в план поездкии', 'type': 'buttons', 'data': [
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

    # Используем пагинатор для постраничного вывода
    paginator = Paginator(pages_content, 1)  # 1 страница на "страницу"

    page_number = request.GET.get('page', 1)  # Номер текущей страницы
    page_content = paginator.get_page(page_number)

    return render(request, 'survey/survey.html', {'page_content': page_content})
