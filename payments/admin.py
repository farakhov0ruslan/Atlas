from django.contrib import admin
from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'user', 'yookassa_id', 'status',
        'amount', 'currency', 'paid_at',
        'created_at', 'updated_at'
    )
    list_filter = ('status', 'currency', 'paid_at')
    search_fields = ('payment_id', 'user__email')

    # делаем все поля readonly
    readonly_fields = [field.name for field in Payment._meta.fields]

    # запретим добавление, изменение и удаление
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
