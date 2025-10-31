# Wingz API Documentation

This Django REST Framework API provides endpoints for managing Users, Rides, and Ride Events.

## Setup

1. Setup environment variables:
```bash
cp .env.sample .env
```
Edit the `.env` file with your configuration. The application uses `python-decouple` for environment variable management.

2. Install dependencies:
```bash
poetry install
```

3. Run migrations:
```bash
cd wingz-api
python manage.py makemigrations
python manage.py migrate
```

4. Create a superuser (optional):
```bash
cd wingz-api
python manage.py createsuperuser
```

5. Run the development server:
```bash
cd wingz-api
python manage.py runserver
```

## Environment Variables

The application uses `python-decouple` to manage environment variables. Configure the following variables in your `.env` file:

| Variable | Description | Default Value |
|----------|-------------|---------------|
| `SECRET_KEY` | Django secret key for cryptographic signing | `django-insecure-change-this-in-production` |
| `DEBUG` | Enable/disable debug mode (1 for True, 0 for False) | `True` |
| `DJANGO_ALLOWED_HOSTS` | Comma-separated list of allowed hosts | `localhost,127.0.0.1` |
| `POSTGRES_DB` | PostgreSQL database name | `wbsm_db` |
| `POSTGRES_USER` | PostgreSQL username | `admin` |
| `POSTGRES_PASSWORD` | PostgreSQL password | `admin` |
| `POSTGRES_SERVER` | PostgreSQL server host | `db` |
| `POSTGRES_PORT` | PostgreSQL server port | `5432` |

**Note:** For production, always use strong, unique values for `SECRET_KEY` and database credentials.

## Authentication

The API uses JWT (JSON Web Token) authentication with a custom User model. Only users with `role='admin'` can access the API endpoints.

### Custom User Model

The application uses a custom User model with the following fields:
- `username` - Used for authentication (unique)
- `email` - User email address (unique, required)
- `role` - User role: 'admin', 'rider', or 'driver'
- `first_name`, `last_name`, `phone_number` - User information
- `password` - Hashed password

**Important:** Only users with `role='admin'` can access the API endpoints.

### Authentication Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/login/` | Login and obtain JWT tokens |
| POST | `/api/auth/token/refresh/` | Refresh access token |
| POST | `/api/auth/token/verify/` | Verify token validity |
| POST | `/api/auth/logout/` | Logout (invalidate tokens) |

### Obtaining JWT Tokens

**Login Request:**
```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "your_password"
  }'
```


**Response:**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### Using JWT Tokens

Include the access token in the Authorization header for all API requests:

```bash
curl -X GET http://localhost:8000/api/users/ \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..."
```

### Token Lifetime

- **Access Token**: 1 hour
- **Refresh Token**: 1 day

### Refreshing Tokens

When the access token expires, use the refresh token to obtain a new access token:

```bash
curl -X POST http://localhost:8000/api/auth/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
  }'
```

### Creating Admin User

To create an admin user who can access the API:

```bash
python manage.py createsuperuser
```

This will prompt for:
- Username (used for authentication)
- Email (required)
- First name
- Last name
- Password

The user will automatically be created with `role='admin'`.

## API Endpoints

Base URL: `http://localhost:8000/api/`

**Note:** All endpoints below require authentication with admin privileges.

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
- `username` (string, unique)
- `email` (email, unique, required)
- `role` (string)
- `first_name` (string)
- `last_name` (string)
- `phone_number` (string)

**Example POST Request:**
```bash
curl -X POST http://localhost:8000/api/users/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "username": "johndoe",
    "email": "john.doe@example.com",
    "role": "rider",
    "first_name": "John",
    "last_name": "Doe",
    "phone_number": "+1234567890"
  }'
```

**Example Response:**
```json
{
  "id_user": 1,
  "username": "johndoe",
  "email": "john.doe@example.com",
  "role": "rider",
  "first_name": "John",
  "last_name": "Doe",
  "phone_number": "+1234567890"
}
```

### Rides

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/rides/` | List all rides (optimized, returns today's events only) |
| POST | `/api/rides/` | Create a new ride |
| GET | `/api/rides/{id}/` | Get a specific ride (with all events) |
| PUT | `/api/rides/{id}/` | Update a ride |
| PATCH | `/api/rides/{id}/` | Partially update a ride |
| DELETE | `/api/rides/{id}/` | Delete a ride |
| POST | `/api/rides/{id}/add_event/` | Add an event to a ride |

#### Ride List API - Performance Optimized

The ride list API (`GET /api/rides/`) is highly optimized for performance with the following features:

**Query Optimization:**
- Uses `select_related` for rider and driver (1 query)
- Uses `prefetch_related` for today's ride events only (1 query)
- Total: **2-3 database queries** (including pagination count)
- Never retrieves full list of RideEvents for performance

**Filtering:**
- `status` - Filter by ride status (e.g., `?status=en-route`)
- `rider_email` - Filter by rider's email address (e.g., `?rider_email=john@example.com`)

**Sorting:**
- `pickup_time` - Sort by pickup time (e.g., `?ordering=pickup_time` or `?ordering=-pickup_time`)
- `distance` - Sort by distance to pickup location (requires GPS coordinates)

**Distance-Based Sorting:**

To sort rides by distance to a GPS position, provide `latitude`, `longitude`, and `ordering=distance`:

```bash
GET /api/rides/?latitude=37.7749&longitude=-122.4194&ordering=distance
```

This uses the **[Haversine formula](https://en.wikipedia.org/wiki/Haversine_formula)** in the database for efficient distance calculation, with support for:
- Ascending order: `?ordering=distance`
- Descending order: `?ordering=-distance`
- Works with pagination
- Uses database indexes on pickup coordinates for optimal performance

**Ride List Fields:**
- `id_ride` (read-only)
- `status` (string: 'en-route', 'pickup', 'dropoff')
- `id_rider` (integer, foreign key to User)
- `id_driver` (integer, foreign key to User)
- `pickup_latitude` (float, -90 to 90)
- `pickup_longitude` (float, -180 to 180)
- `dropoff_latitude` (float, -90 to 90)
- `dropoff_longitude` (float, -180 to 180)
- `pickup_time` (datetime)
- `rider_details` (object, nested User data)
- `driver_details` (object, nested User data)
- `todays_ride_events` (array, only events from last 24 hours)
- `distance_to_pickup` (float, in km, only present when GPS coords provided)

**Ride Detail Fields (GET /api/rides/{id}/):**
- All fields from list, plus:
- `events` (array, all ride events)

**Example Requests:**

List all rides:
```bash
GET /api/rides/
```

Filter by status:
```bash
GET /api/rides/?status=en-route
```

Filter by rider email:
```bash
GET /api/rides/?rider_email=john@example.com
```

Sort by pickup time (descending):
```bash
GET /api/rides/?ordering=-pickup_time
```

Sort by distance to pickup location:
```bash
GET /api/rides/?latitude=37.7749&longitude=-122.4194&ordering=distance
```

Combined filtering and sorting:
```bash
GET /api/rides/?status=en-route&rider_email=john@example.com&ordering=pickup_time&page=1
```

**Example Response:**
```json
{
  "count": 100,
  "next": "http://localhost:8000/api/rides/?page=2",
  "previous": null,
  "results": [
    {
      "id_ride": 1,
      "status": "en-route",
      "id_rider": 1,
      "id_driver": 2,
      "pickup_latitude": 37.7749,
      "pickup_longitude": -122.4194,
      "dropoff_latitude": 37.7849,
      "dropoff_longitude": -122.4094,
      "pickup_time": "2025-10-30T10:00:00Z",
      "rider_details": {
        "id_user": 1,
        "username": "johndoe",
        "email": "john@example.com",
        "role": "rider",
        "first_name": "John",
        "last_name": "Doe",
        "phone_number": "+1234567890"
      },
      "driver_details": {
        "id_user": 2,
        "username": "janedoe",
        "email": "jane@example.com",
        "role": "driver",
        "first_name": "Jane",
        "last_name": "Doe",
        "phone_number": "+0987654321"
      },
      "todays_ride_events": [
        {
          "id_ride_event": 1,
          "id_ride": 1,
          "description": "Driver arrived at pickup",
          "created_at": "2025-10-31T09:30:00Z"
        }
      ],
      "distance_to_pickup": 2.5
    }
  ]
}
```

**Example POST Request (Create Ride):**
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
- **Filter by:** `role`, `email`, `username`
- **Search in:** `username`, `first_name`, `last_name`, `email`, `phone_number`
- **Order by:** `id_user`, `username`, `first_name`, `last_name`, `email`

Example: `/api/users/?role=rider&search=john&ordering=username`

### Rides (Optimized)
- **Filter by:** 
  - `status` - Ride status (indexed for performance)
  - `rider_email` - Rider's email address (uses indexed email field)
- **Order by:** 
  - `pickup_time` - Sort by pickup time (indexed for performance)
  - `distance` - Sort by distance to pickup (requires `latitude` and `longitude` params)
  - Use `-` prefix for descending order (e.g., `-pickup_time`)

**Performance Notes:**
- All filtering and sorting uses database indexes for optimal performance
- Distance sorting uses Haversine formula calculated in the database
- Pagination is fully supported with all sorting options

Example: `/api/rides/?status=en-route&rider_email=john@example.com&ordering=-pickup_time`

Example with distance: `/api/rides/?latitude=37.7749&longitude=-122.4194&ordering=distance&page=1`

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

