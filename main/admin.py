from django.contrib import admin
from .models import Subscription, SubscriptionPlan


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'plan',
        'purchase_date',
        'end_date',
        'is_active',
    )
    list_filter = (
        'plan',
        'purchase_date',
        'end_date',
    )
    search_fields = (
        'user__email',
        'user__username',
    )
    readonly_fields = ('purchase_date',)

    def is_active(self, obj):
        return obj.is_active()

    is_active.boolean = True
    is_active.short_description = 'Активна?'


@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ('key', 'name', 'routes', 'duration', 'price', 'currency')
    search_fields = ('key', 'name')
    list_filter = ('currency',)