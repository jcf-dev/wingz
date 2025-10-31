"""
Load dummy data into the Wingz database.

This script creates:
- 1 admin user
- 50 users (25 riders, 25 drivers)
- 1000 rides with realistic data
- Multiple ride events per ride
"""

import os
import sys
import django
from datetime import timedelta
from random import randint, choice, uniform

# Setup Django environment
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from django.utils import timezone  # noqa: E402
from faker import Faker  # noqa: E402
from users.models import User  # noqa: E402
from rides.models import Ride, RideEvent  # noqa: E402

fake = Faker()

# Realistic ride statuses and events
RIDE_STATUSES = [
    "requested",
    "accepted",
    "en-route",
    "pickup",
    "in-progress",
    "completed",
    "cancelled",
]

RIDE_EVENTS_BY_STATUS = {
    "requested": ["Ride requested by passenger"],
    "accepted": ["Driver accepted ride", "Driver is on the way"],
    "en-route": ["Driver is 5 minutes away", "Driver is 2 minutes away"],
    "pickup": ["Driver arrived at pickup location", "Passenger is boarding"],
    "in-progress": [
        "Trip started",
        "Halfway to destination",
        "Approaching destination",
    ],
    "completed": ["Passenger dropped off", "Ride completed", "Payment processed"],
    "cancelled": [
        "Ride cancelled by passenger",
        "Ride cancelled by driver",
        "Ride cancelled due to timeout",
    ],
}

# San Francisco Bay Area coordinates for realistic locations
SF_BAY_AREA_BOUNDS = {
    "lat_min": 37.3,
    "lat_max": 37.9,
    "lon_min": -122.5,
    "lon_max": -122.0,
}


def generate_coordinates():
    """Generate random coordinates within San Francisco Bay Area"""
    lat = uniform(SF_BAY_AREA_BOUNDS["lat_min"], SF_BAY_AREA_BOUNDS["lat_max"])
    lon = uniform(SF_BAY_AREA_BOUNDS["lon_min"], SF_BAY_AREA_BOUNDS["lon_max"])
    return round(lat, 6), round(lon, 6)


def create_admin_user():
    """Create admin user"""
    print("Creating admin user...")
    admin, created = User.objects.get_or_create(
        username="admin",
        defaults={
            "email": "admin@wingz.com",
            "first_name": "Admin",
            "last_name": "User",
            "role": "admin",
            "phone_number": "+1234567890",
            "is_staff": True,
            "is_superuser": True,
        },
    )
    if created:
        admin.set_password("admin123")
        admin.save()
        print(f"✓ Created admin user: {admin.username}")
    else:
        print(f"✓ Admin user already exists: {admin.username}")
    return admin


def create_users(num_riders=25, num_drivers=25):
    """Create riders and drivers"""
    print(f"\nCreating {num_riders} riders and {num_drivers} drivers...")

    riders = []
    drivers = []

    # Create riders
    for i in range(num_riders):
        username = fake.user_name()

        # Ensure unique username
        counter = 1
        original_username = username
        while User.objects.filter(username=username).exists():
            username = f"{original_username}{counter}"
            counter += 1

        rider = User.objects.create(
            username=username,
            email=fake.email(),
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            role="rider",
            phone_number=fake.phone_number()[:20],
        )
        riders.append(rider)

        if (i + 1) % 10 == 0:
            print(f"  Created {i + 1}/{num_riders} riders...")

    print(f"✓ Created {num_riders} riders")

    # Create drivers
    for i in range(num_drivers):
        username = fake.user_name()

        # Ensure unique username
        counter = 1
        original_username = username
        while User.objects.filter(username=username).exists():
            username = f"{original_username}{counter}"
            counter += 1

        driver = User.objects.create(
            username=username,
            email=fake.email(),
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            role="driver",
            phone_number=fake.phone_number()[:20],
        )
        drivers.append(driver)

        if (i + 1) % 10 == 0:
            print(f"  Created {i + 1}/{num_drivers} drivers...")

    print(f"✓ Created {num_drivers} drivers")

    return riders, drivers


def create_rides_and_events(riders, drivers, num_rides=1000):
    """Create rides with corresponding events"""
    print(f"\nCreating {num_rides} rides with events...")

    rides_created = 0
    events_created = 0

    # Create rides over the past 30 days
    now = timezone.now()

    for i in range(num_rides):
        # Random pickup time within the last 30 days
        days_ago = randint(0, 30)
        hours_ago = randint(0, 23)
        minutes_ago = randint(0, 59)
        pickup_time = now - timedelta(
            days=days_ago, hours=hours_ago, minutes=minutes_ago
        )

        # Random rider and driver
        rider = choice(riders)
        driver = choice(drivers)

        # Random status (most rides should be completed)
        status = choice(
            [
                "requested",
                "accepted",
                "en-route",
                "pickup",
                "in-progress",
                "completed",
                "cancelled",
            ]
        )

        # Generate pickup and dropoff coordinates
        pickup_lat, pickup_lon = generate_coordinates()
        dropoff_lat, dropoff_lon = generate_coordinates()

        # Create ride
        ride = Ride.objects.create(
            status=status,
            rider=rider,
            driver=driver,
            pickup_latitude=pickup_lat,
            pickup_longitude=pickup_lon,
            dropoff_latitude=dropoff_lat,
            dropoff_longitude=dropoff_lon,
            pickup_time=pickup_time,
        )
        rides_created += 1

        # Create events for this ride
        event_descriptions = RIDE_EVENTS_BY_STATUS.get(status, ["Ride event"])

        # Create 1-4 events per ride
        num_events = randint(1, min(4, len(event_descriptions)))
        event_time = pickup_time

        for j in range(num_events):
            description = event_descriptions[min(j, len(event_descriptions) - 1)]

            # Events happen shortly after each other
            event_time = event_time + timedelta(minutes=randint(1, 10))

            event = RideEvent.objects.create(ride=ride, description=description)
            # Manually set created_at to match the ride timeline
            event.created_at = event_time
            event.save()
            events_created += 1

        if (i + 1) % 100 == 0:
            print(f"  Created {i + 1}/{num_rides} rides with events...")

    print(f"✓ Created {rides_created} rides")
    print(f"✓ Created {events_created} ride events")

    return rides_created, events_created


def main():
    """Main function to load all dummy data"""
    print("=" * 60)
    print("Loading Dummy Data for Wingz Database")
    print("=" * 60)

    try:
        # Create admin user
        create_admin_user()

        # Create riders and drivers
        riders, drivers = create_users(num_riders=25, num_drivers=25)

        # Create rides and events
        rides_count, events_count = create_rides_and_events(
            riders, drivers, num_rides=1000
        )

        # Summary
        print("\n" + "=" * 60)
        print("SUMMARY")
        print("=" * 60)
        print(f"Total Users: {User.objects.count()}")
        print(f"  - Admins: {User.objects.filter(role='admin').count()}")
        print(f"  - Riders: {User.objects.filter(role='rider').count()}")
        print(f"  - Drivers: {User.objects.filter(role='driver').count()}")
        print(f"Total Rides: {Ride.objects.count()}")
        print(f"  - Completed: {Ride.objects.filter(status='completed').count()}")
        print(f"  - In Progress: {Ride.objects.filter(status='in-progress').count()}")
        print(f"  - Cancelled: {Ride.objects.filter(status='cancelled').count()}")
        print(
            f"  - Other: {Ride.objects.exclude(status__in=['completed', 'in-progress', 'cancelled']).count()}"
        )
        print(f"Total Ride Events: {RideEvent.objects.count()}")
        print("=" * 60)
        print("✓ Dummy data loaded successfully!")
        print("\nAdmin credentials:")
        print("  Username: admin")
        print("  Password: admin123")
        print("=" * 60)

    except Exception as e:
        print(f"\n✗ Error loading dummy data: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
