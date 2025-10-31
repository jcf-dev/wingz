from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Prefetch, F, ExpressionWrapper, FloatField
from django.db.models.functions import ACos, Cos, Sin, Radians
from django.utils import timezone
from datetime import timedelta
from .models import Ride, RideEvent
from .serializers import (
    RideDetailSerializer,
    RideListSerializer,
    RideEventSerializer
)


class RideViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Ride CRUD operations with optimized querying.

    Features:
    - Efficient querying with select_related and prefetch_related (2-3 queries total)
    - Filtering by status and rider email
    - Sorting by pickup_time and distance to pickup (with GPS coordinates)
    - Only retrieves today's ride events (last 24 hours) for performance
    - Pagination support
    """
    queryset = Ride.objects.all()
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status']
    ordering_fields = ['pickup_time']
    ordering = ['-pickup_time']

    def get_serializer_class(self):
        """Use different serializers for list vs detail views"""
        if self.action == 'list':
            return RideListSerializer
        return RideDetailSerializer

    def get_queryset(self):
        """
        Optimize queryset with select_related and prefetch_related.
        Only fetch today's ride events (last 24 hours) for performance.
        Supports filtering by rider email and sorting by distance.
        """
        queryset = Ride.objects.select_related('rider', 'driver')

        # Only for list action, add today's events prefetch
        if self.action == 'list':
            # Calculate 24 hours ago
            twenty_four_hours_ago = timezone.now() - timedelta(hours=24)

            # Prefetch only today's ride events
            todays_events = Prefetch(
                'events',
                queryset=RideEvent.objects.filter(
                    created_at__gte=twenty_four_hours_ago
                ).order_by('-created_at'),
                to_attr='todays_events'
            )
            queryset = queryset.prefetch_related(todays_events)

            # Filter by rider email if provided
            rider_email = self.request.query_params.get('rider_email', None)
            if rider_email:
                queryset = queryset.filter(rider__email=rider_email)

            # Handle distance-based sorting
            lat = self.request.query_params.get('latitude', None)
            lon = self.request.query_params.get('longitude', None)

            if lat and lon:
                try:
                    lat = float(lat)
                    lon = float(lon)

                    # Use Haversine formula for distance calculation in database
                    # Distance in kilometers
                    # Formula: 6371 * acos(cos(radians(lat1)) * cos(radians(lat2)) * cos(radians(lon2) - radians(lon1)) + sin(radians(lat1)) * sin(radians(lat2)))
                    queryset = queryset.annotate(
                        distance_to_pickup=ExpressionWrapper(
                            6371 * ACos(
                                Cos(Radians(lat)) * Cos(Radians(F('pickup_latitude'))) *
                                Cos(Radians(F('pickup_longitude')) - Radians(lon)) +
                                Sin(Radians(lat)) * Sin(Radians(F('pickup_latitude')))
                            ),
                            output_field=FloatField()
                        )
                    )

                    # Check if sorting by distance is requested
                    ordering = self.request.query_params.get('ordering', None)
                    if ordering == 'distance' or ordering == 'distance_to_pickup':
                        queryset = queryset.order_by('distance_to_pickup')
                    elif ordering == '-distance' or ordering == '-distance_to_pickup':
                        queryset = queryset.order_by('-distance_to_pickup')

                except (ValueError, TypeError):
                    pass  # Invalid lat/lon, ignore distance calculation

        elif self.action == 'retrieve':
            # For detail view, prefetch all events
            queryset = queryset.prefetch_related('events')

        return queryset

    def list(self, request, *args, **kwargs):
        """
        List rides with optimized querying.
        Total queries: 2-3 (1 for rides with users, 1 for today's events, 1 optional for count)
        """
        return super().list(request, *args, **kwargs)

    @action(detail=True, methods=['post'])
    def add_event(self, request, pk=None):
        """Add an event to a specific ride"""
        ride = self.get_object()
        serializer = RideEventSerializer(data={
            'ride': ride.id,
            'description': request.data.get('description')
        })

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class RideEventViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing RideEvent CRUD operations.

    Provides:
    - create: Create a new ride event
    - retrieve: Get a specific ride event
    - update: Update a ride event
    - partial_update: Partially update a ride event
    - destroy: Delete a ride event

    Note: List action is disabled for performance reasons. Use ride-specific
    queries through the Ride detail endpoint or filter by ride ID.
    """
    queryset = RideEvent.objects.select_related('ride').all()
    serializer_class = RideEventSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['ride']
    search_fields = ['description']
    ordering_fields = ['id', 'created_at']
    ordering = ['-created_at']

    def list(self, request, *args, **kwargs):
        """
        Disable listing all ride events for performance reasons.
        Clients must filter by specific ride ID.
        """
        ride_filter = request.query_params.get('ride', None)
        if not ride_filter:
            return Response(
                {
                    'error': 'Listing all ride events is not supported for performance reasons. '
                             'Please filter by ride ID using ?ride=<ride_id>'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().list(request, *args, **kwargs)
