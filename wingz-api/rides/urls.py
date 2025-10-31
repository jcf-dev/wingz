from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RideViewSet, RideEventViewSet

# Create a router and register our viewsets
router = DefaultRouter()
router.register(r'rides', RideViewSet, basename='ride')
router.register(r'ride-events', RideEventViewSet, basename='rideevent')

# The API URLs are determined automatically by the router
urlpatterns = [
    path('', include(router.urls)),
]

