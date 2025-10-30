from django.contrib import admin
from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['id_user', 'first_name', 'last_name', 'email', 'role', 'phone_number']
    list_filter = ['role']
    search_fields = ['first_name', 'last_name', 'email', 'phone_number']
    ordering = ['id_user']
