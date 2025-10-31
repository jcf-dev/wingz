from rest_framework import serializers
from .models import Ride, RideEvent
from users.serializers import UserSerializer


class RideEventSerializer(serializers.ModelSerializer):
    """Serializer for RideEvent model"""

    class Meta:
        model = RideEvent
        fields = [
            'id',
            'ride',
            'description',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class RideListSerializer(serializers.ModelSerializer):
    """
    Optimized serializer for listing rides with related data.
    Includes rider, driver, and today's ride events (last 24 hours only).
    """
    rider_details = UserSerializer(source='rider', read_only=True)
    driver_details = UserSerializer(source='driver', read_only=True)
    todays_ride_events = serializers.SerializerMethodField()
    distance_to_pickup = serializers.FloatField(read_only=True, required=False)

    class Meta:
        model = Ride
        fields = [
            'id',
            'status',
            'rider',
            'driver',
            'pickup_latitude',
            'pickup_longitude',
            'dropoff_latitude',
            'dropoff_longitude',
            'pickup_time',
            'rider_details',
            'driver_details',
            'todays_ride_events',
            'distance_to_pickup',
        ]
        read_only_fields = ['id']

    def get_todays_ride_events(self, obj):
        """
        Get only today's ride events (last 24 hours).
        This uses the prefetched 'todays_events' to avoid N+1 queries.
        """
        if hasattr(obj, 'todays_events'):
            return RideEventSerializer(obj.todays_events, many=True).data
        return []


class RideDetailSerializer(serializers.ModelSerializer):
    """Serializer for detailed Ride view with all events"""
    events = RideEventSerializer(many=True, read_only=True)
    rider_details = UserSerializer(source='rider', read_only=True)
    driver_details = UserSerializer(source='driver', read_only=True)

    class Meta:
        model = Ride
        fields = [
            'id',
            'status',
            'rider',
            'driver',
            'pickup_latitude',
            'pickup_longitude',
            'dropoff_latitude',
            'dropoff_longitude',
            'pickup_time',
            'events',
            'rider_details',
            'driver_details'
        ]
        read_only_fields = ['id']

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
        if 'rider' in data and 'driver' in data:
            if data['rider'].id == data['driver'].id:
                raise serializers.ValidationError(
                    "Rider and driver must be different users."
                )

        return data


