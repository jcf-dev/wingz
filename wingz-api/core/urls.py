from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
from users.views import UserViewSet
from rides.views import RideViewSet, RideEventViewSet

router = DefaultRouter()
router.register(r"users", UserViewSet, basename="user")
router.register(r"rides", RideViewSet, basename="ride")
router.register(r"ride-events", RideEventViewSet, basename="rideevent")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(router.urls)),
    # JWT Authentication endpoints
    path("api/auth/login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/auth/token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    # dj-rest-auth endpoints
    path("api/auth/", include("dj_rest_auth.urls")),
]
