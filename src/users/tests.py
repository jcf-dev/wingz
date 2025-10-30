from django.test import TestCase
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse
from .models import User


class UserModelTest(TestCase):
    """Test cases for User model"""

    def setUp(self):
        """Set up test data"""
        self.user_data = {
            'role': 'rider',
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john.doe@example.com',
            'phone_number': '+1234567890'
        }
        self.user = User.objects.create(**self.user_data)

    def test_user_creation(self):
        """Test that a user can be created"""
        self.assertEqual(self.user.first_name, 'John')
        self.assertEqual(self.user.last_name, 'Doe')
        self.assertEqual(self.user.email, 'john.doe@example.com')
        self.assertEqual(self.user.role, 'rider')
        self.assertEqual(self.user.phone_number, '+1234567890')

    def test_user_str_method(self):
        """Test the string representation of user"""
        expected_str = f"{self.user.first_name} {self.user.last_name} ({self.user.role})"
        self.assertEqual(str(self.user), expected_str)

    def test_email_uniqueness(self):
        """Test that email must be unique"""
        duplicate_data = self.user_data.copy()
        duplicate_data['email'] = 'john.doe@example.com'
        with self.assertRaises(Exception):
            User.objects.create(**duplicate_data)

    def test_user_primary_key(self):
        """Test that id_user is the primary key"""
        self.assertIsNotNone(self.user.id_user)
        self.assertEqual(self.user.pk, self.user.id_user)


class UserAPITest(APITestCase):
    """Test cases for User API endpoints"""

    def setUp(self):
        """Set up test client and data"""
        self.client = APIClient()
        self.user_data = {
            'role': 'rider',
            'first_name': 'Jane',
            'last_name': 'Smith',
            'email': 'jane.smith@example.com',
            'phone_number': '+1234567891'
        }
        self.user = User.objects.create(**self.user_data)
        self.list_url = reverse('user-list')
        self.detail_url = reverse('user-detail', kwargs={'pk': self.user.id_user})

    def test_get_user_list(self):
        """Test retrieving list of users"""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)

    def test_create_user(self):
        """Test creating a new user"""
        new_user_data = {
            'role': 'driver',
            'first_name': 'Bob',
            'last_name': 'Johnson',
            'email': 'bob.johnson@example.com',
            'phone_number': '+1234567892'
        }
        response = self.client.post(self.list_url, new_user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 2)
        self.assertEqual(response.data['first_name'], 'Bob')
        self.assertEqual(response.data['email'], 'bob.johnson@example.com')

    def test_get_user_detail(self):
        """Test retrieving a specific user"""
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['first_name'], 'Jane')
        self.assertEqual(response.data['email'], 'jane.smith@example.com')

    def test_update_user(self):
        """Test updating a user with PUT"""
        updated_data = self.user_data.copy()
        updated_data['first_name'] = 'Janet'
        response = self.client.put(self.detail_url, updated_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Janet')

    def test_partial_update_user(self):
        """Test partially updating a user with PATCH"""
        response = self.client.patch(
            self.detail_url,
            {'phone_number': '+9876543210'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.phone_number, '+9876543210')

    def test_delete_user(self):
        """Test deleting a user"""
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(User.objects.count(), 0)

    def test_create_user_duplicate_email(self):
        """Test that creating a user with duplicate email fails"""
        duplicate_data = {
            'role': 'rider',
            'first_name': 'Duplicate',
            'last_name': 'User',
            'email': 'jane.smith@example.com',  # Same as existing user
            'phone_number': '+1111111111'
        }
        response = self.client.post(self.list_url, duplicate_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_filter_users_by_role(self):
        """Test filtering users by role"""
        # Create additional users
        User.objects.create(
            role='driver',
            first_name='Driver',
            last_name='One',
            email='driver1@example.com',
            phone_number='+1111111111'
        )
        User.objects.create(
            role='rider',
            first_name='Rider',
            last_name='Two',
            email='rider2@example.com',
            phone_number='+2222222222'
        )

        response = self.client.get(self.list_url, {'role': 'rider'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)

    def test_search_users(self):
        """Test searching users by name or email"""
        response = self.client.get(self.list_url, {'search': 'Jane'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(response.data['count'], 1)

    def test_get_riders_action(self):
        """Test custom action to get all riders"""
        # Create additional users
        User.objects.create(
            role='driver',
            first_name='Driver',
            last_name='One',
            email='driver1@example.com',
            phone_number='+1111111111'
        )

        riders_url = reverse('user-riders')
        response = self.client.get(riders_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['role'], 'rider')

    def test_get_drivers_action(self):
        """Test custom action to get all drivers"""
        # Create driver
        User.objects.create(
            role='driver',
            first_name='Driver',
            last_name='One',
            email='driver1@example.com',
            phone_number='+1111111111'
        )

        drivers_url = reverse('user-drivers')
        response = self.client.get(drivers_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['role'], 'driver')

    def test_ordering_users(self):
        """Test ordering users"""
        # Create additional user
        User.objects.create(
            role='driver',
            first_name='Adam',
            last_name='Apple',
            email='adam@example.com',
            phone_number='+1111111111'
        )

        response = self.client.get(self.list_url, {'ordering': 'first_name'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data['results']
        self.assertEqual(results[0]['first_name'], 'Adam')
