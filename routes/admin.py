from django.contrib import admin
from django import forms
from django.db.models.signals import post_save
from django.dispatch import receiver
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

    def clean_location(self):
        location = self.cleaned_data.get("location")
        if location:
            if "latitude" not in location or "longitude" not in location:
                raise forms.ValidationError("Поле location должно содержать latitude и longitude.")
        return location

    def clean_contacts(self):
        contacts = self.cleaned_data.get("contacts")
        if contacts:
            if any(x not in contacts for x in ['telegram', 'instagram', 'phone', 'vk']):
                raise forms.ValidationError(
                    "Поле contacts должно содержать telegram и instagram, phone, vk.")
        return contacts

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


class WorkingHoursInline(admin.TabularInline):
    model = WorkingHours
    extra = 7  # Показываем 7 строк для каждого дня недели



@admin.register(Place)
class PlaceAdmin(admin.ModelAdmin):
    form = PlaceForm
    prepopulated_fields = {"slug": ("name",)}
    inlines = [WorkingHoursInline]


# @receiver(post_save, sender=Place)
# def create_working_hours(sender, instance, created, **kwargs):
#     if created:
#         # Создаем рабочие часы для каждого дня недели
#         for day in range(7):
#             WorkingHours.objects.create(
#                 place=instance,
#                 day_of_week=day,
#                 open_time="09:00",  # Значение по умолчанию
#                 close_time="18:00"  # Значение по умолчанию
#             )
