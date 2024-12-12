from django.contrib import admin
from django import forms
from routes.models import Category, Place, WorkingHours, Route, Day, RouteCell, CustomUser

admin.site.register(WorkingHours)
admin.site.register(Route)
admin.site.register(Day)
admin.site.register(RouteCell)
admin.site.register(CustomUser)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}


class PlaceForm(forms.ModelForm):
    class Meta:
        model = Place
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Установка начальных значений для JSON-полей
        self.fields['location'].initial = {
            "latitude": None,
            "longitude": None
        }
        self.fields['contacts'].initial = {
            "telegram": None,
            "instagram": None,
            "phone": "+7",
            "vk": None
        }


@admin.register(Place)
class PlaceAdmin(admin.ModelAdmin):
    form = PlaceForm
    prepopulated_fields = {"slug": ("name",)}

