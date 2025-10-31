from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager


class UserManager(BaseUserManager):
    """Custom manager for User model"""

    def create_user(self, username, email, password=None, **extra_fields):
        """Create and save a regular user"""
        if not username:
            raise ValueError('The Username field must be set')
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        extra_fields.setdefault('role', 'rider')
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        """Create and save a superuser with admin role"""
        extra_fields.setdefault('role', 'admin')
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('role') != 'admin':
            raise ValueError('Superuser must have role="admin"')

        return self.create_user(username, email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """Custom User model representing riders, drivers, and admins"""
    id_user = models.AutoField(primary_key=True)
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(max_length=255, unique=True)
    role = models.CharField(
        max_length=50,
        default='rider',
        help_text="User role (e.g., 'admin', 'rider', 'driver')"
    )
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20)

    # Required for Django admin
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'first_name', 'last_name']

    class Meta:
        db_table = 'user'

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.role})"

    @property
    def is_admin(self):
        """Check if user has admin role"""
        return self.role == 'admin'
