from django.contrib import admin

from .models import Payment, User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ["email", "phone_number", "city"]
    list_filter = ["city"]
    search_fields = ["email", "phone_number"]


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ["user", "payment_date", "amount", "payment_method"]
    list_filter = ["payment_method", "payment_date"]
    search_fields = ["user__email"]
