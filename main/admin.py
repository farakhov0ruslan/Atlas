from django.contrib import admin
from routes.models import Category, Place, Working_Hours, Route, Day, Route_Cell

admin.site.register(Category)
admin.site.register(Place)
admin.site.register(Working_Hours)
admin.site.register(Route)
admin.site.register(Day)
admin.site.register(Route_Cell)