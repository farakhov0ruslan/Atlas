import json

from django.shortcuts import render

from routes.models import Place


# Create your views here.
def route_page(request):
    places = Place.objects.all()

    context = {
        "title": "Route Page",
        "places": places,
        # "random": random.Random(),
    }

    return render(request, 'routes/route_page.html', context)
