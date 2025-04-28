import random
from django import template

register = template.Library()


@register.simple_tag
def random_number(min_value=100, max_value=1000):
    return random.randint(min_value, max_value)


@register.simple_tag
def random_float(min_value=40, max_value=50):
    return random.randint(min_value, max_value)/10

@register.filter
def get_item(dictionary, key):
    return dictionary.get(f"{key} день", None)

@register.filter
def filter_by_category(places, category_name):
    """
    Возвращает список мест из places, у которых в ManyToMany-поле category
    есть объект с именем, совпадающим с category_name (без учета регистра и пробелов).
    """
    filtered = []
    # Приводим искомое имя к нижнему регистру без пробелов по краям
    category_name = category_name.strip().lower()
    for place in places:
        # Итерируемся по всем связанным категориям
        if any(cat.name and cat.name.strip().lower() == category_name for cat in place.category.all()):
            filtered.append(place)
    return filtered

@register.filter
def filter_by_current_place_categories(all_places, current_place):
    """
    Возвращает список мест из all_places, у которых есть хотя бы одна категория,
    совпадающая с любой из категорий текущего места (current_place).
    Текущее место (current_place) исключается из списка.
    """
    if not current_place:
        return []
    # Получаем множество ID категорий текущего места
    current_cat_ids = {cat.id for cat in current_place.category.all()}
    filtered = []
    for place in all_places:
        # Не показываем само текущее место
        if place.id == current_place.id:
            continue
        # Получаем множество ID категорий для candidate
        place_cat_ids = {cat.id for cat in place.category.all()}
        if current_cat_ids.intersection(place_cat_ids):
            filtered.append(place)
    return filtered