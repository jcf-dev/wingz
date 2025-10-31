from rest_framework import serializers
from .models import Ride, RideEvent
from users.serializers import UserSerializer


class RideEventSerializer(serializers.ModelSerializer):
    """Serializer for RideEvent model"""

    class Meta:
        model = RideEvent
        fields = [
            'id_ride_event',
            'id_ride',
            'description',
            'created_at'
        ]
        read_only_fields = ['id_ride_event', 'created_at']


class RideSerializer(serializers.ModelSerializer):
    """Serializer for Ride model"""
    # Nested serializers for detailed view
    events = RideEventSerializer(many=True, read_only=True)
    rider_details = UserSerializer(source='id_rider', read_only=True)
    driver_details = UserSerializer(source='id_driver', read_only=True)

    class Meta:
        model = Ride
        fields = [
            'id_ride',
            'status',
            'id_rider',
            'id_driver',
            'pickup_latitude',
            'pickup_longitude',
            'dropoff_latitude',
            'dropoff_longitude',
            'pickup_time',
            'events',
            'rider_details',
            'driver_details'
        ]
        read_only_fields = ['id_ride']

    def validate(self, data):
        """Validate ride data"""
        # Validate latitude values
        for lat_field in ['pickup_latitude', 'dropoff_latitude']:
            if lat_field in data:
                if not -90 <= data[lat_field] <= 90:
                    raise serializers.ValidationError(
                        f"{lat_field} must be between -90 and 90 degrees."
                    )

        # Validate longitude values
        for lon_field in ['pickup_longitude', 'dropoff_longitude']:
            if lon_field in data:
                if not -180 <= data[lon_field] <= 180:
                    raise serializers.ValidationError(
                        f"{lon_field} must be between -180 and 180 degrees."
                    )

        # Validate that rider and driver are different users
        if 'id_rider' in data and 'id_driver' in data:
            if data['id_rider'].id_user == data['id_driver'].id_user:
                raise serializers.ValidationError(
                    "Rider and driver must be different users."
                )

        return data


class RideListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing rides without nested data"""

    class Meta:
        model = Ride
        fields = [
            'id_ride',
            'status',
            'id_rider',
            'id_driver',
            'pickup_latitude',
            'pickup_longitude',
            'dropoff_latitude',
            'dropoff_longitude',
            'pickup_time'
        ]
        read_only_fields = ['id_ride']

