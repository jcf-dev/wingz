from rest_framework import serializers
from django.utils import timezone
from datetime import timedelta
import math
from .models import Ride, RideEvent
from users.serializers import UserSerializer


class RideEventSerializer(serializers.ModelSerializer):
    """Serializer for RideEvent model"""

    class Meta:
        model = RideEvent
        fields = ["id", "ride", "description", "created_at"]
        read_only_fields = ["id", "created_at"]
        extra_kwargs = {
            "description": {
                "required": True,
                "allow_blank": False,
                "max_length": 255,
                "trim_whitespace": True,
            }
        }

    def validate_description(self, value):
        """Validate description is not empty after trimming"""
        if not value or not value.strip():
            raise serializers.ValidationError(
                "Description cannot be empty or only whitespace."
            )
        return value.strip()


class RideListSerializer(serializers.ModelSerializer):
    """
    Optimized serializer for listing rides with related data.
    Includes rider, driver, and today's ride events (last 24 hours only).
    """

    rider_details = UserSerializer(source="rider", read_only=True)
    driver_details = UserSerializer(source="driver", read_only=True)
    todays_ride_events = serializers.SerializerMethodField()
    distance_to_pickup = serializers.FloatField(read_only=True, required=False)

    class Meta:
        model = Ride
        fields = [
            "id",
            "status",
            "rider",
            "driver",
            "pickup_latitude",
            "pickup_longitude",
            "dropoff_latitude",
            "dropoff_longitude",
            "pickup_time",
            "rider_details",
            "driver_details",
            "todays_ride_events",
            "distance_to_pickup",
        ]
        read_only_fields = ["id"]

    def get_todays_ride_events(self, obj):
        """
        Get only today's ride events (last 24 hours).
        This uses the prefetched 'todays_events' to avoid N+1 queries.
        """
        if hasattr(obj, "todays_events"):
            return RideEventSerializer(obj.todays_events, many=True).data
        return []


class RideDetailSerializer(serializers.ModelSerializer):
    """Serializer for detailed Ride view with all events"""

    events = RideEventSerializer(many=True, read_only=True)
    rider_details = UserSerializer(source="rider", read_only=True)
    driver_details = UserSerializer(source="driver", read_only=True)

    class Meta:
        model = Ride
        fields = [
            "id",
            "status",
            "rider",
            "driver",
            "pickup_latitude",
            "pickup_longitude",
            "dropoff_latitude",
            "dropoff_longitude",
            "pickup_time",
            "events",
            "rider_details",
            "driver_details",
        ]
        read_only_fields = ["id"]

    def _validate_coordinate(self, field_name, value, min_val, max_val):
        """Helper to validate coordinate values"""
        if math.isnan(value) or math.isinf(value):
            raise serializers.ValidationError(
                {field_name: "Invalid value. Cannot be NaN or infinity."}
            )
        if not min_val <= value <= max_val:
            raise serializers.ValidationError(
                {field_name: f"Must be between {min_val} and {max_val} degrees."}
            )

    def _validate_coordinates(self, data):
        """Validate all coordinate fields"""
        for lat_field in ["pickup_latitude", "dropoff_latitude"]:
            if lat_field in data:
                self._validate_coordinate(lat_field, data[lat_field], -90, 90)

        for lon_field in ["pickup_longitude", "dropoff_longitude"]:
            if lon_field in data:
                self._validate_coordinate(lon_field, data[lon_field], -180, 180)

    def _validate_location_difference(
        self, pickup_lat, pickup_lon, dropoff_lat, dropoff_lon
    ):
        """Validate pickup and dropoff are not the same location"""
        if all([pickup_lat, pickup_lon, dropoff_lat, dropoff_lon]):
            lat_diff = abs(pickup_lat - dropoff_lat)
            lon_diff = abs(pickup_lon - dropoff_lon)
            if lat_diff < 0.00001 and lon_diff < 0.00001:
                raise serializers.ValidationError(
                    "Pickup and dropoff locations cannot be the same."
                )

    def _validate_user_roles(self, rider, driver):
        """Validate user roles and that rider and driver are different"""
        if rider and driver and rider.id == driver.id:
            raise serializers.ValidationError(
                "Rider and driver must be different users."
            )

        if rider and rider.role != "rider":
            raise serializers.ValidationError(
                {"rider": f'User must have role "rider", not "{rider.role}".'}
            )

        if driver and driver.role != "driver":
            raise serializers.ValidationError(
                {"driver": f'User must have role "driver", not "{driver.role}".'}
            )

    def validate(self, data):
        """Validate ride data with comprehensive business logic checks"""
        rider = data.get("rider", getattr(self.instance, "rider", None))
        driver = data.get("driver", getattr(self.instance, "driver", None))
        pickup_lat = data.get(
            "pickup_latitude", getattr(self.instance, "pickup_latitude", None)
        )
        pickup_lon = data.get(
            "pickup_longitude", getattr(self.instance, "pickup_longitude", None)
        )
        dropoff_lat = data.get(
            "dropoff_latitude", getattr(self.instance, "dropoff_latitude", None)
        )
        dropoff_lon = data.get(
            "dropoff_longitude", getattr(self.instance, "dropoff_longitude", None)
        )
        pickup_time = data.get(
            "pickup_time", getattr(self.instance, "pickup_time", None)
        )

        self._validate_coordinates(data)
        self._validate_location_difference(
            pickup_lat, pickup_lon, dropoff_lat, dropoff_lon
        )
        self._validate_user_roles(rider, driver)

        if pickup_time:
            buffer_time = timezone.now() - timedelta(minutes=5)
            if pickup_time < buffer_time:
                raise serializers.ValidationError(
                    {"pickup_time": "Pickup time cannot be in the past."}
                )

        return data
