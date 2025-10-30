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
