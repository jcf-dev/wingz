from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import User
from .serializers import UserSerializer


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing User CRUD operations.

    Provides:
    - list: Get all users
    - create: Create a new user
    - retrieve: Get a specific user
    - update: Update a user
    - partial_update: Partially update a user
    - destroy: Delete a user
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["role", "email", "username"]
    search_fields = ["username", "first_name", "last_name", "email", "phone_number"]
    ordering_fields = ["id", "username", "first_name", "last_name", "email"]
    ordering = ["id"]

    @action(detail=False, methods=["get"])
    def riders(self, request):
        """Get all users with rider role"""
        riders = self.queryset.filter(role="rider")
        serializer = self.get_serializer(riders, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def drivers(self, request):
        """Get all users with driver role"""
        drivers = self.queryset.filter(role="driver")
        serializer = self.get_serializer(drivers, many=True)
        return Response(serializer.data)
