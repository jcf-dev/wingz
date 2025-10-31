from django.contrib import admin
from .models import Ride, RideEvent


@admin.register(Ride)
class RideAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'status',
        'rider',
        'driver',
        'pickup_time',
        'pickup_latitude',
        'pickup_longitude'
    ]
    list_filter = ['status', 'pickup_time']
    search_fields = ['id', 'status']
    ordering = ['-pickup_time']
    raw_id_fields = ['rider', 'driver']


@admin.register(RideEvent)
class RideEventAdmin(admin.ModelAdmin):
    list_display = ['id', 'ride', 'description', 'created_at']
    list_filter = ['created_at']
    search_fields = ['description']
    ordering = ['-created_at']
    raw_id_fields = ['ride']
