from django.db import models


class User(models.Model):
    """User model representing riders, drivers, and admins"""
    id_user = models.AutoField(primary_key=True)
    role = models.CharField(max_length=50, help_text="User role (e.g., 'admin', 'rider', 'driver')")
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(max_length=255, unique=True)
    phone_number = models.CharField(max_length=20)

    class Meta:
        db_table = 'user'

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.role})"


class Ride(models.Model):
    """Ride model representing ride requests and their details"""
    id_ride = models.AutoField(primary_key=True)
    status = models.CharField(
        max_length=50,
        help_text="Ride status (e.g., 'en-route', 'pickup', 'dropoff')"
    )
    id_rider = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='rides_as_rider',
        db_column='id_rider'
    )
    id_driver = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='rides_as_driver',
        db_column='id_driver'
    )
    pickup_latitude = models.FloatField()
    pickup_longitude = models.FloatField()
    dropoff_latitude = models.FloatField()
    dropoff_longitude = models.FloatField()
    pickup_time = models.DateTimeField()

    class Meta:
        db_table = 'ride'

    def __str__(self):
        return f"Ride {self.id_ride} - {self.status}"


class RideEvent(models.Model):
    """Ride Event model for tracking ride events"""
    id_ride_event = models.AutoField(primary_key=True)
    id_ride = models.ForeignKey(
        Ride,
        on_delete=models.CASCADE,
        related_name='events',
        db_column='id_ride'
    )
    description = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'ride_event'

    def __str__(self):
        return f"Event {self.id_ride_event} - {self.description}"
