from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Ride, RideEvent
from .serializers import (
    RideSerializer,
    RideListSerializer,
    RideEventSerializer
)



class RideViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Ride CRUD operations.

    Provides:
    - list: Get all rides (uses lightweight serializer)
    - create: Create a new ride
    - retrieve: Get a specific ride (includes nested events and user details)
    - update: Update a ride
    - partial_update: Partially update a ride
    - destroy: Delete a ride
    """
    queryset = Ride.objects.select_related('id_rider', 'id_driver').prefetch_related('events')
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'id_rider', 'id_driver']
    search_fields = ['status']
    ordering_fields = ['id_ride', 'pickup_time', 'status']
    ordering = ['-pickup_time']

    def get_serializer_class(self):
        """Use different serializers for list vs detail views"""
        if self.action == 'list':
            return RideListSerializer
        return RideSerializer

    @action(detail=True, methods=['post'])
    def add_event(self, request, pk=None):
        """Add an event to a specific ride"""
        ride = self.get_object()
        serializer = RideEventSerializer(data={
            'id_ride': ride.id_ride,
            'description': request.data.get('description')
        })

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def by_status(self, request):
        """Get rides filtered by status"""
        status_param = request.query_params.get('status', None)
        if status_param:
            rides = self.queryset.filter(status=status_param)
            serializer = self.get_serializer(rides, many=True)
            return Response(serializer.data)
        return Response(
            {"error": "Status parameter is required"},
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(detail=False, methods=['get'])
    def rider_rides(self, request):
        """Get all rides for a specific rider"""
        rider_id = request.query_params.get('rider_id', None)
        if rider_id:
            rides = self.queryset.filter(id_rider=rider_id)
            serializer = self.get_serializer(rides, many=True)
            return Response(serializer.data)
        return Response(
            {"error": "rider_id parameter is required"},
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(detail=False, methods=['get'])
    def driver_rides(self, request):
        """Get all rides for a specific driver"""
        driver_id = request.query_params.get('driver_id', None)
        if driver_id:
            rides = self.queryset.filter(id_driver=driver_id)
            serializer = self.get_serializer(rides, many=True)
            return Response(serializer.data)
        return Response(
            {"error": "driver_id parameter is required"},
            status=status.HTTP_400_BAD_REQUEST
        )


class RideEventViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing RideEvent CRUD operations.

    Provides:
    - list: Get all ride events
    - create: Create a new ride event
    - retrieve: Get a specific ride event
    - update: Update a ride event
    - partial_update: Partially update a ride event
    - destroy: Delete a ride event
    """
    queryset = RideEvent.objects.select_related('id_ride').all()
    serializer_class = RideEventSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['id_ride']
    search_fields = ['description']
    ordering_fields = ['id_ride_event', 'created_at']
    ordering = ['-created_at']
