from django.shortcuts import render

def place_page(request):
    return render(request, 'places/place_page.html')