from django.db import models
from users.models import User


class Ride(models.Model):
    """Ride model representing ride requests and their details"""
    id = models.AutoField(primary_key=True)
    status = models.CharField(
        max_length=50,
        help_text="Ride status (e.g., 'en-route', 'pickup', 'dropoff')"
    )
    rider = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='rides_as_rider',
        db_column='rider_id'
    )
    driver = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='rides_as_driver',
        db_column='driver_id'
    )
    pickup_latitude = models.FloatField()
    pickup_longitude = models.FloatField()
    dropoff_latitude = models.FloatField()
    dropoff_longitude = models.FloatField()
    pickup_time = models.DateTimeField()

    class Meta:
        db_table = 'ride'
        indexes = [
            models.Index(fields=['pickup_time'], name='ride_pickup_time_idx'),
            models.Index(fields=['status'], name='ride_status_idx'),
            models.Index(fields=['pickup_latitude', 'pickup_longitude'], name='ride_pickup_coords_idx'),
        ]

    def __str__(self):
        return f"Ride {self.id} - {self.status}"


class RideEvent(models.Model):
    """Ride Event model for tracking ride events"""
    id = models.AutoField(primary_key=True)
    ride = models.ForeignKey(
        Ride,
        on_delete=models.CASCADE,
        related_name='events',
        db_column='ride_id'
    )
    description = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'ride_event'
        indexes = [
            models.Index(fields=['ride', 'created_at'], name='ride_event_ride_created_idx'),
            models.Index(fields=['created_at'], name='ride_event_created_idx'),
        ]

    def __str__(self):
        return f"Event {self.id} - {self.description}"
