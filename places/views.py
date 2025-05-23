from django.shortcuts import render, get_object_or_404
from routes.models import Place, Category

def place_list(request, category_slug=None):
    categories = Category.objects.all()  # Получаем все категории
    current_city = request.session.get('city', '')
    places = Place.objects.filter(city=current_city)

    if category_slug:  # Если есть категория в URL
        category = get_object_or_404(Category, slug=category_slug)
        places = places.filter(category=category)

    return render(request, 'places/place_page.html', {
        'categories': categories,
        'places': places,
        'selected_category': category_slug
    })
