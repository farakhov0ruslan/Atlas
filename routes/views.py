from django.shortcuts import render

# Create your views here.
def route_page(request):
    return render(request, 'routes/route_page.html')