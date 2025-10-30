from django.contrib import admin
from .models import User, Ride, RideEvent


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['id_user', 'first_name', 'last_name', 'email', 'role', 'phone_number']
    list_filter = ['role']
    search_fields = ['first_name', 'last_name', 'email', 'phone_number']
    ordering = ['id_user']


@admin.register(Ride)
class RideAdmin(admin.ModelAdmin):
    list_display = [
        'id_ride',
        'status',
        'id_rider',
        'id_driver',
        'pickup_time',
        'pickup_latitude',
        'pickup_longitude'
    ]
    list_filter = ['status', 'pickup_time']
    search_fields = ['id_ride', 'status']
    ordering = ['-pickup_time']
    raw_id_fields = ['id_rider', 'id_driver']


@admin.register(RideEvent)
class RideEventAdmin(admin.ModelAdmin):
    list_display = ['id_ride_event', 'id_ride', 'description', 'created_at']
    list_filter = ['created_at']
    search_fields = ['description']
    ordering = ['-created_at']
    raw_id_fields = ['id_ride']
