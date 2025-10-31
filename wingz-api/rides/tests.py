from django.test import TestCase
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from .models import Ride, RideEvent
from users.models import User


class RideModelTest(TestCase):
    """Test cases for Ride model"""

    def setUp(self):
        """Set up test data"""
        self.rider = User.objects.create(
            role='rider',
            first_name='John',
            last_name='Doe',
            email='rider@example.com',
            phone_number='+1234567890'
        )
        self.driver = User.objects.create(
            role='driver',
            first_name='Jane',
            last_name='Smith',
            email='driver@example.com',
            phone_number='+1234567891'
        )
        self.ride = Ride.objects.create(
            status='en-route',
            driver=self.driver,
            pickup_latitude=37.7749,
            pickup_longitude=-122.4194,
            dropoff_latitude=37.7849,
            dropoff_longitude=-122.4094,
            pickup_time=timezone.now()
        )

    def test_ride_creation(self):
        """Test that a ride can be created"""
        self.assertEqual(self.ride.status, 'en-route')
        self.assertEqual(self.ride.rider, self.rider)
        self.assertEqual(self.ride.driver, self.driver)
        self.assertEqual(self.ride.pickup_latitude, 37.7749)
        self.assertEqual(self.ride.pickup_longitude, -122.4194)

    def test_ride_str_method(self):
        """Test the string representation of ride"""
        expected_str = f"Ride {self.ride.ride} - {self.ride.status}"
        self.assertEqual(str(self.ride), expected_str)

    def test_ride_relationships(self):
        """Test ride relationships with users"""
        self.assertEqual(self.ride.rider.first_name, 'John')
        self.assertEqual(self.ride.driver.first_name, 'Jane')


class RideEventModelTest(TestCase):
    """Test cases for RideEvent model"""

    def setUp(self):
        """Set up test data"""
        self.rider = User.objects.create(
            role='rider',
            first_name='John',
            last_name='Doe',
            email='rider@example.com',
            phone_number='+1234567890'
        )
        self.driver = User.objects.create(
            role='driver',
            first_name='Jane',
            last_name='Smith',
            email='driver@example.com',
            phone_number='+1234567891'
        )
        self.ride = Ride.objects.create(
            status='en-route',
            rider=self.rider,
            driver=self.driver,
            pickup_latitude=37.7749,
            pickup_longitude=-122.4194,
            dropoff_latitude=37.7849,
            dropoff_longitude=-122.4094,
            pickup_time=timezone.now()
        )
        self.event = RideEvent.objects.create(
            ride=self.ride,
            description='Driver arrived at pickup location'
        )

    def test_ride_event_creation(self):
        """Test that a ride event can be created"""
        self.assertEqual(self.event.description, 'Driver arrived at pickup location')
        self.assertEqual(self.event.ride, self.ride)
        self.assertIsNotNone(self.event.created_at)

    def test_ride_event_str_method(self):
        """Test the string representation of ride event"""
        expected_str = f"Event {self.event.id} - {self.event.description}"
        self.assertEqual(str(self.event), expected_str)

    def test_ride_event_auto_timestamp(self):
        """Test that created_at is automatically set"""
        self.assertIsNotNone(self.event.created_at)
        self.assertLessEqual(self.event.created_at, timezone.now())


class RideAPITest(APITestCase):
    """Test cases for Ride API endpoints"""

    def setUp(self):
        """Set up test client and data"""
        from users.models import User as CustomUser

        self.client = APIClient()

        # Create admin user using custom User model
        self.admin_user = CustomUser.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='admin123',
            first_name='Admin',
            last_name='User',
            phone_number='+1234567890'
        )

        # Authenticate the client
        self.client.force_authenticate(user=self.admin_user)

        self.rider = User.objects.create(
            role='rider',
            first_name='John',
            last_name='Doe',
            email='rider@example.com',
            phone_number='+1234567890'
        )
        self.driver = User.objects.create(
            role='driver',
            first_name='Jane',
            last_name='Smith',
            email='driver@example.com',
            phone_number='+1234567891'
        )
        self.ride_data = {
            'status': 'en-route',
            'rider': self.rider.id,
            'driver': self.driver.id,
            'pickup_latitude': 37.7749,
            'pickup_longitude': -122.4194,
            'dropoff_latitude': 37.7849,
            'dropoff_longitude': -122.4094,
            'pickup_time': timezone.now().isoformat()
        }
        self.ride = Ride.objects.create(
            status='en-route',
            rider=self.rider,
            driver=self.driver,
            pickup_latitude=37.7749,
            pickup_longitude=-122.4194,
            dropoff_latitude=37.7849,
            dropoff_longitude=-122.4094,
            pickup_time=timezone.now()
        )
        self.list_url = reverse('ride-list')
        self.detail_url = reverse('ride-detail', kwargs={'pk': self.ride.ride})

    def test_get_ride_list(self):
        """Test retrieving list of rides"""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)

    def test_create_ride(self):
        """Test creating a new ride"""
        new_ride_data = {
            'status': 'pickup',
            'rider': self.rider.id,
            'driver': self.driver.id,
            'pickup_latitude': 37.8000,
            'pickup_longitude': -122.4500,
            'dropoff_latitude': 37.8100,
            'dropoff_longitude': -122.4400,
            'pickup_time': (timezone.now() + timedelta(hours=1)).isoformat()
        }
        response = self.client.post(self.list_url, new_ride_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Ride.objects.count(), 2)

    def test_get_ride_detail(self):
        """Test retrieving a specific ride with nested data"""
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'en-route')
        self.assertIn('rider_details', response.data)
        self.assertIn('driver_details', response.data)
        self.assertIn('events', response.data)

    def test_update_ride(self):
        """Test updating a ride with PUT"""
        updated_data = self.ride_data.copy()
        updated_data['status'] = 'pickup'
        response = self.client.put(self.detail_url, updated_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.ride.refresh_from_db()
        self.assertEqual(self.ride.status, 'pickup')

    def test_partial_update_ride(self):
        """Test partially updating a ride with PATCH"""
        response = self.client.patch(
            self.detail_url,
            {'status': 'dropoff'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.ride.refresh_from_db()
        self.assertEqual(self.ride.status, 'dropoff')

    def test_delete_ride(self):
        """Test deleting a ride"""
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Ride.objects.count(), 0)

    def test_create_ride_invalid_latitude(self):
        """Test that creating a ride with invalid latitude fails"""
        invalid_data = self.ride_data.copy()
        invalid_data['pickup_latitude'] = 100  # Invalid latitude
        response = self.client.post(self.list_url, invalid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_ride_invalid_longitude(self):
        """Test that creating a ride with invalid longitude fails"""
        invalid_data = self.ride_data.copy()
        invalid_data['pickup_longitude'] = 200  # Invalid longitude
        response = self.client.post(self.list_url, invalid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_ride_same_rider_and_driver(self):
        """Test that rider and driver must be different"""
        invalid_data = self.ride_data.copy()
        invalid_data['rider'] = self.driver.id
        invalid_data['driver'] = self.driver.id
        response = self.client.post(self.list_url, invalid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_filter_rides_by_status(self):
        """Test filtering rides by status"""
        Ride.objects.create(
            status='pickup',
            rider=self.rider,
            driver=self.driver,
            pickup_latitude=37.8000,
            pickup_longitude=-122.4500,
            dropoff_latitude=37.8100,
            dropoff_longitude=-122.4400,
            pickup_time=timezone.now()
        )

        response = self.client.get(self.list_url, {'status': 'en-route'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)

    def test_filter_ride_events_by_ride(self):
        """Test filtering ride events by ride"""
        response = self.client.get(self.list_url, {'ride': self.ride.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data['results']), 1)

    def test_add_event_to_ride(self):
        """Test adding an event to a ride"""
        add_event_url = reverse('ride-add-event', kwargs={'pk': self.ride.id})
        event_data = {'description': 'Passenger picked up'}
        response = self.client.post(add_event_url, event_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(RideEvent.objects.filter(ride=self.ride).count(), 1)

    def test_by_status_action(self):
        """Test custom by_status action"""
        by_status_url = reverse('ride-by-status')
        response = self.client.get(by_status_url, {'status': 'en-route'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_by_status_action_missing_parameter(self):
        """Test by_status action without status parameter"""
        by_status_url = reverse('ride-by-status')
        response = self.client.get(by_status_url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_rider_rides_action(self):
        """Test custom rider_rides action"""
        rider_rides_url = reverse('ride-rider-rides')
        response = self.client.get(rider_rides_url, {'rider_id': self.rider.id})
            self.list_url,

    def test_driver_rides_action(self):
        """Test custom driver_rides action"""
        driver_rides_url = reverse('ride-driver-rides')
        response = self.client.get(driver_rides_url, {'driver_id': self.driver.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class RideEventAPITest(APITestCase):
    """Test cases for RideEvent API endpoints"""

    def setUp(self):
        """Set up test client and data"""
        from users.models import User as CustomUser

        self.client = APIClient()

        # Create admin user using custom User model

            username='admin_event',
            email='admin_event@example.com',
            password='admin123',
            first_name='Admin',
            last_name='Event',
            phone_number='+1234567890'
        )

        # Authenticate the client
        self.client.force_authenticate(user=self.admin_user)

        self.rider = User.objects.create(
            role='rider',
            first_name='John',
            last_name='Doe',
            email='rider@example.com',
            phone_number='+1234567890'
        )
        self.driver = User.objects.create(
            role='driver',
            first_name='Jane',
            last_name='Smith',
            email='driver@example.com',
            phone_number='+1234567891'
        )
        self.ride = Ride.objects.create(
            status='en-route',
            rider=self.rider,
            driver=self.driver,
            pickup_latitude=37.7749,
            pickup_longitude=-122.4194,
            dropoff_latitude=37.7849,
            dropoff_longitude=-122.4094,
            pickup_time=timezone.now()
        )
        self.event = RideEvent.objects.create(
            ride=self.ride,
            description='Driver arrived at pickup location'
        )
        self.list_url = reverse('rideevent-list')
        self.detail_url = reverse('rideevent-detail', kwargs={'pk': self.event.id})

    def test_get_ride_event_list(self):
        """Test retrieving list of ride events"""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)

    def test_create_ride_event(self):
        """Test creating a new ride event"""
        event_data = {
            'ride': self.ride.ride,
            'description': 'Passenger picked up'
        }
        response = self.client.post(self.list_url, event_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(RideEvent.objects.count(), 2)

    def test_get_ride_event_detail(self):
        """Test retrieving a specific ride event"""
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['description'], 'Driver arrived at pickup location')

    def test_update_ride_event(self):
        """Test updating a ride event with PUT"""
        updated_data = {
            'ride': self.ride.ride,
            'description': 'Updated description'
        }
        response = self.client.put(self.detail_url, updated_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.event.refresh_from_db()
        self.assertEqual(self.event.description, 'Updated description')

    def test_partial_update_ride_event(self):
        """Test partially updating a ride event with PATCH"""
        response = self.client.patch(
            self.detail_url,
            {'description': 'Partially updated'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.event.refresh_from_db()
        self.assertEqual(self.event.description, 'Partially updated')

    def test_delete_ride_event(self):
        """Test deleting a ride event"""
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(RideEvent.objects.count(), 0)

    def test_filter_ride_events_by_ride(self):
        """Test filtering ride events by ride"""
        # Create another ride and event
        other_ride = Ride.objects.create(
            status='pickup',
            rider=self.rider,
            driver=self.driver,
            pickup_latitude=37.8000,
            pickup_longitude=-122.4500,
            dropoff_latitude=37.8100,
            dropoff_longitude=-122.4400,
            pickup_time=timezone.now()
        )
        RideEvent.objects.create(
            ride=other_ride,
            description='Other ride event'
        )

        response = self.client.get(self.list_url, {'ride': self.ride.ride})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)

    def test_search_ride_events(self):
        """Test searching ride events by description"""
        response = self.client.get(self.list_url, {'search': 'arrived'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(response.data['count'], 1)

    def test_ordering_ride_events(self):
        """Test ordering ride events"""
        RideEvent.objects.create(
            ride=self.ride,
            description='Second event'
        )

        response = self.client.get(self.list_url, {'ordering': '-created_at'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data['results']
        self.assertEqual(results[0]['description'], 'Second event')
