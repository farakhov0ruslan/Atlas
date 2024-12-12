from django.contrib import admin
from .models import Category, Place, WorkingHours, Route, Day, RouteCell, CustomUser

admin.site.register(Category)
admin.site.register(Place)
admin.site.register(WorkingHours)
admin.site.register(Route)
admin.site.register(Day)
admin.site.register(RouteCell)
admin.site.register(CustomUser)