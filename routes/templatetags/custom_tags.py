import random
from django import template

register = template.Library()


@register.simple_tag
def random_number(min_value=100, max_value=1000):
    return random.randint(min_value, max_value)


@register.simple_tag
def random_float(min_value=40, max_value=50):
    return random.randint(min_value, max_value)/10


