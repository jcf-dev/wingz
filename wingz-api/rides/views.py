from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Prefetch, F, ExpressionWrapper, FloatField
from django.db.models.functions import ACos, Cos, Sin, Radians
from django.db import transaction
from django.utils import timezone
from datetime import timedelta
from .models import Ride, RideEvent
from .serializers import RideDetailSerializer, RideListSerializer, RideEventSerializer


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
    filterset_fields = ["status"]
    ordering_fields = ["pickup_time"]
    ordering = ["-pickup_time"]

    def get_serializer_class(self):
        """Use different serializers for list vs detail views"""
        if self.action == "list":
            return RideListSerializer
        return RideDetailSerializer

    def filter_queryset(self, queryset):
        """
        Custom filtering to handle distance sorting.
        Only applies distance sorting when valid coordinates are provided.
        """
        ordering_param = self.request.query_params.get("ordering", None)

        if ordering_param in [
            "distance",
            "-distance",
            "distance_to_pickup",
            "-distance_to_pickup",
        ]:
            for backend in [DjangoFilterBackend]:
                queryset = backend().filter_queryset(self.request, queryset, self)
            return queryset

        return super().filter_queryset(queryset)

    def get_queryset(self):
        """
        Optimize queryset with select_related and prefetch_related.
        Only fetch today's ride events (last 24 hours) for performance.
        Supports filtering by rider email and sorting by distance.
        """
        queryset = Ride.objects.select_related("rider", "driver")

        if self.action == "list":
            twenty_four_hours_ago = timezone.now() - timedelta(hours=24)

            todays_events = Prefetch(
                "events",
                queryset=RideEvent.objects.filter(
                    created_at__gte=twenty_four_hours_ago
                ).order_by("-created_at"),
                to_attr="todays_events",
            )
            queryset = queryset.prefetch_related(todays_events)

            rider_email = self.request.query_params.get("rider_email", None)
            if rider_email:
                queryset = queryset.filter(rider__email=rider_email)

            lat = self.request.query_params.get("latitude", None)
            lon = self.request.query_params.get("longitude", None)

            if lat and lon:
                try:
                    lat = float(lat)
                    lon = float(lon)

                    queryset = queryset.annotate(
                        distance_to_pickup=ExpressionWrapper(
                            6371
                            * ACos(
                                Cos(Radians(lat))
                                * Cos(Radians(F("pickup_latitude")))
                                * Cos(Radians(F("pickup_longitude")) - Radians(lon))
                                + Sin(Radians(lat)) * Sin(Radians(F("pickup_latitude")))
                            ),
                            output_field=FloatField(),
                        )
                    )

                    ordering = self.request.query_params.get("ordering", None)
                    if ordering == "distance" or ordering == "distance_to_pickup":
                        queryset = queryset.order_by("distance_to_pickup")
                    elif ordering == "-distance" or ordering == "-distance_to_pickup":
                        queryset = queryset.order_by("-distance_to_pickup")

                except (ValueError, TypeError):
                    pass

        elif self.action == "retrieve":
            queryset = queryset.prefetch_related("events")

        return queryset

    def list(self, request, *args, **kwargs):
        """
        List rides with optimized querying.
        Total queries: 2-3 (1 for rides with users, 1 for today's events, 1 optional for count)
        """
        return super().list(request, *args, **kwargs)

    @action(detail=True, methods=["post"])
    @transaction.atomic
    def add_event(self, request, pk=None):
        """Add an event to a specific ride with transaction protection"""
        ride = Ride.objects.select_for_update().get(pk=pk)

        MAX_EVENTS_PER_RIDE = 1000
        event_count = ride.events.count()
        if event_count >= MAX_EVENTS_PER_RIDE:
            return Response(
                {
                    "error": f"Maximum number of events ({MAX_EVENTS_PER_RIDE}) reached for this ride."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = RideEventSerializer(
            data={"ride": ride.id, "description": request.data.get("description")}
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RideEventViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing RideEvent CRUD operations.

    Provides:
    - create: Create a new ride event
    - retrieve: Get all ride events for a specific ride (accepts ride_id)
    - update: Update a ride event
    - partial_update: Partially update a ride event
    - destroy: Delete a ride event

    Note: List action is disabled for performance reasons. Use the retrieve
    endpoint with a ride ID to get all events for a specific ride.
    """

    queryset = RideEvent.objects.select_related("ride").all()
    serializer_class = RideEventSerializer
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["ride"]
    search_fields = ["description"]
    ordering_fields = ["id", "created_at"]
    ordering = ["-created_at"]

    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve all ride events for a specific ride.
        Accepts ride_id as the URL parameter.
        """
        ride_id = kwargs.get("pk")

        try:
            Ride.objects.get(pk=ride_id)
        except Ride.DoesNotExist:
            return Response(
                {"error": f"Ride with id {ride_id} does not exist."},
                status=status.HTTP_404_NOT_FOUND,
            )

        events = RideEvent.objects.filter(ride_id=ride_id).order_by("-created_at")
        serializer = self.get_serializer(events, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def list(self, request, *args, **kwargs):
        """
        Disable listing all ride events for performance reasons.
        Use the retrieve endpoint with a ride ID instead.
        """
        return Response(
            {
                "error": "Listing all ride events is not supported for performance reasons. "
                "Please use /api/ride-events/{ride_id}/ to get all events for a specific ride."
            },
            status=status.HTTP_400_BAD_REQUEST,
        )
