# Wingz API Documentation

This Django REST Framework API provides endpoints for managing Users, Rides, and Ride Events.

## Setup

1. Install dependencies:
```bash
poetry install
```

2. Run migrations:
```bash
cd src
python manage.py makemigrations
python manage.py migrate
```

3. Create a superuser (optional):
```bash
python manage.py createsuperuser
```

4. Run the development server:
```bash
python manage.py runserver
```

## API Endpoints

Base URL: `http://localhost:8000/api/`

### Users

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/users/` | List all users |
| POST | `/api/users/` | Create a new user |
| GET | `/api/users/{id}/` | Get a specific user |
| PUT | `/api/users/{id}/` | Update a user |
| PATCH | `/api/users/{id}/` | Partially update a user |
| DELETE | `/api/users/{id}/` | Delete a user |
| GET | `/api/users/riders/` | Get all riders |
| GET | `/api/users/drivers/` | Get all drivers |

**User Fields:**
- `id_user` (read-only)
- `role` (string)
- `first_name` (string)
- `last_name` (string)
- `email` (email, unique)
- `phone_number` (string)

**Example POST Request:**
```json
{
  "role": "rider",
  "first_name": "John",
  "last_name": "Doe",
  "email": "john.doe@example.com",
  "phone_number": "+1234567890"
}
```

### Rides

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/rides/` | List all rides |
| POST | `/api/rides/` | Create a new ride |
| GET | `/api/rides/{id}/` | Get a specific ride (with events) |
| PUT | `/api/rides/{id}/` | Update a ride |
| PATCH | `/api/rides/{id}/` | Partially update a ride |
| DELETE | `/api/rides/{id}/` | Delete a ride |
| POST | `/api/rides/{id}/add_event/` | Add an event to a ride |
| GET | `/api/rides/by_status/?status=en-route` | Get rides by status |
| GET | `/api/rides/rider_rides/?rider_id=1` | Get rides for a specific rider |
| GET | `/api/rides/driver_rides/?driver_id=2` | Get rides for a specific driver |

**Ride Fields:**
- `id_ride` (read-only)
- `status` (string: 'en-route', 'pickup', 'dropoff')
- `id_rider` (integer, foreign key to User)
- `id_driver` (integer, foreign key to User)
- `pickup_latitude` (float, -90 to 90)
- `pickup_longitude` (float, -180 to 180)
- `dropoff_latitude` (float, -90 to 90)
- `dropoff_longitude` (float, -180 to 180)
- `pickup_time` (datetime)
- `events` (read-only, nested)
- `rider_details` (read-only, nested)
- `driver_details` (read-only, nested)

**Example POST Request:**
```json
{
  "status": "en-route",
  "id_rider": 1,
  "id_driver": 2,
  "pickup_latitude": 37.7749,
  "pickup_longitude": -122.4194,
  "dropoff_latitude": 37.7849,
  "dropoff_longitude": -122.4094,
  "pickup_time": "2025-10-30T10:00:00Z"
}
```

### Ride Events

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/ride-events/` | List all ride events |
| POST | `/api/ride-events/` | Create a new ride event |
| GET | `/api/ride-events/{id}/` | Get a specific ride event |
| PUT | `/api/ride-events/{id}/` | Update a ride event |
| PATCH | `/api/ride-events/{id}/` | Partially update a ride event |
| DELETE | `/api/ride-events/{id}/` | Delete a ride event |

**RideEvent Fields:**
- `id_ride_event` (read-only)
- `id_ride` (integer, foreign key to Ride)
- `description` (string)
- `created_at` (read-only, auto-generated)

**Example POST Request:**
```json
{
  "id_ride": 1,
  "description": "Driver arrived at pickup location"
}
```

## Filtering, Searching, and Ordering

All list endpoints support filtering, searching, and ordering:

### Users
- **Filter by:** `role`, `email`
- **Search in:** `first_name`, `last_name`, `email`, `phone_number`
- **Order by:** `id_user`, `first_name`, `last_name`, `email`

Example: `/api/users/?role=rider&search=john&ordering=first_name`

### Rides
- **Filter by:** `status`, `id_rider`, `id_driver`
- **Search in:** `status`
- **Order by:** `id_ride`, `pickup_time`, `status`

Example: `/api/rides/?status=en-route&ordering=-pickup_time`

### Ride Events
- **Filter by:** `id_ride`
- **Search in:** `description`
- **Order by:** `id_ride_event`, `created_at`

Example: `/api/ride-events/?id_ride=1&ordering=-created_at`

## Pagination

All list endpoints are paginated with 10 items per page by default.

Use `?page=2` to get the next page.

## Browsable API

Visit `http://localhost:8000/api/` in your browser to use the Django REST Framework browsable API interface.

## Admin Panel

Access the Django admin panel at `http://localhost:8000/admin/` to manage data through the web interface.

