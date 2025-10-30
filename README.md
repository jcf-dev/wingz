# Wingz - Django REST API

A Django REST Framework application for managing rides, users (riders and drivers), and ride events.

## Quick Start

### 1. Install Dependencies
```bash
poetry install
```

### 2. Run Migrations (Already Done)
The database is already set up, but if you need to reset:
```bash
cd src
python manage.py migrate
```

### 3. Create a Superuser (Optional)
```bash
cd src
python manage.py createsuperuser
```

### 4. Start the Development Server
```bash
cd src
python manage.py runserver
```

### 5. Test the API
```bash
# In a new terminal
python test_api.py
```

## Documentation

- **[API Documentation](docs/API_DOCUMENTATION.md)** - Complete endpoint reference

## API Endpoints

### Base URL: `http://localhost:8000/api/`

- **Users**: `/api/users/`
- **Rides**: `/api/rides/`
- **Ride Events**: `/api/ride-events/`
- **Admin Panel**: `http://localhost:8000/admin/`
- **Browsable API**: `http://localhost:8000/api/`

## Features

**Models**
- User (riders, drivers, admins)
- Ride (with pickup/dropoff locations)
- RideEvent (event tracking)

**REST API**
- Full CRUD operations via ViewSets
- JSON serialization/deserialization
- Nested relationships
- Data validation

**Advanced Features**
- Filtering (by status, role, etc.)
- Search (full-text search)
- Ordering (sort by any field)
- Pagination (10 items per page)
- Custom actions (add_event, filter by status, etc.)

**Admin Interface**
- Web-based data management
- Custom list displays
- Search and filters

## Tech Stack

- **Django 5.2.7**
- **Django REST Framework 3.16.1**
- **Django Filter 25.2**
- **Python 3.14**
- **Poetry** (dependency management)

## Example Usage

### Create a Rider
```bash
curl -X POST http://localhost:8000/api/users/ \
  -H "Content-Type: application/json" \
  -d '{
    "role": "rider",
    "first_name": "John",
    "last_name": "Doe",
    "email": "john@example.com",
    "phone_number": "+1234567890"
  }'
```

### Create a Ride
```bash
curl -X POST http://localhost:8000/api/rides/ \
  -H "Content-Type: application/json" \
  -d '{
    "status": "en-route",
    "id_rider": 1,
    "id_driver": 2,
    "pickup_latitude": 37.7749,
    "pickup_longitude": -122.4194,
    "dropoff_latitude": 37.7849,
    "dropoff_longitude": -122.4094,
    "pickup_time": "2025-10-30T10:00:00Z"
  }'
```

### List Rides with Filters
```bash
curl http://localhost:8000/api/rides/?status=en-route&ordering=-pickup_time
```

## Project Structure

```
wingz/
├── src/
│   ├── manage.py
│   ├── core/                 # Django project settings
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   └── rides/                # Main application
│       ├── models.py         # User, Ride, RideEvent models
│       ├── serializers.py    # DRF serializers
│       ├── views.py          # ViewSets for API endpoints
│       ├── urls.py           # API routing
│       ├── admin.py          # Admin configuration
│       └── migrations/       # Database migrations
├── docs/
│   └── API_DOCUMENTATION.md  # Complete API reference
├── test_api.py               # API test script
└── README.md                 # This file
```

## Requirements Met

- Django REST Framework utilized  
- Models created for Ride, User, and RideEvent  
- Serializers implemented for JSON serialization/deserialization  
- ViewSets for managing CRUD operations  

## License

MIT

## Author

Joween Flores <hello@joween.dev>
Simple Ride API written in Python
