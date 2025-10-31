# Wingz - Django REST API

A Django REST Framework application for managing rides, users (riders and drivers), and ride events.

## Quick Start

### 1. Generate Environment Files
Generate `.env` and `.env.docker` files from the `.env.sample` template:
```bash
make env
```

This will create:
- `.env` - For local development (uses `localhost` for database connection)
- `.env.docker` - For Docker environment (uses `wingz_db` service name)

### 2. Install Dependencies
```bash
poetry install --with dev
```

This installs all dependencies including development tools (flake8, black).

### 3. Run Migrations (Already Done)
The database is already set up, but if you need to reset:
```bash
make migrate
```

### 4. Create an Admin User (Required for API Access)
```bash
make createsuperuser
```

**Note:** Only admin users can access the API endpoints.

### 5. Start the Development Server
```bash
make runserver
```

### 6. Run Tests
```bash
make test
```

## Documentation

- **[API Documentation](docs/API_DOCUMENTATION.md)** - Complete endpoint reference

## API Endpoints

### Base URL: `http://localhost:8000/api/`

**Authentication Required:** All API endpoints require JWT authentication with admin privileges.

### Authentication
- **Login**: `POST /api/auth/login/`
- **Token Refresh**: `POST /api/auth/token/refresh/`
- **Token Verify**: `POST /api/auth/token/verify/`
- **Logout**: `POST /api/auth/logout/`

### Protected Endpoints
- **Users**: `/api/users/`
- **Rides**: `/api/rides/`
- **Ride Events**: `/api/ride-events/`

### Other
- **Admin Panel**: `http://localhost:8000/admin/`
- **Browsable API**: `http://localhost:8000/api/`

## Features

**Separate Apps Architecture**
- Users app - Dedicated user management (riders, drivers, admins)
- Rides app - Ride and event management

**Models**
- User (in users app)
- Ride (with pickup/dropoff locations)
- RideEvent (event tracking)

**REST API**
- Full CRUD operations via ViewSets
- JSON serialization/deserialization
- Nested relationships
- Data validation

**Authentication & Security**
- JWT (JSON Web Token) authentication
- Simple JWT implementation
- Token refresh mechanism
- Admin-only API access
- Secure endpoints

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

**Testing**
- Comprehensive unit tests (47 tests)
- Model and API tests
- Test coverage for all endpoints

**Code Quality**
- Black for consistent code formatting (line length: 88)
- Flake8 for style checking and linting (max complexity: 10)
- Automated formatting and linting via Makefile commands
- Excludes migrations and build directories from checks

## Tech Stack

- **Django 5.2.7**
- **Django REST Framework 3.16.1**
- **Django REST Framework Simple JWT** - JWT authentication
- **dj-rest-auth** - Authentication endpoints
- **Django Filter 25.2**
- **Python Decouple 3.8** - Environment variable management
- **Python 3.14**
- **Poetry** (dependency management)

### Development Tools
- **Black 24.x** - Code formatter
- **Flake8 7.x** - Code linter and style checker

## Makefile Commands

The project includes several Makefile targets for common tasks:

### Environment Management

#### `make env`
Generates environment files from the `.env.sample` template:
- Creates `.env` for local development (uses `localhost` for database)
- Creates `.env.docker` for Docker environment (uses `wingz_db` service name)

```bash
make env
```

### Django Management

#### `make migrate`
Runs database migrations:

```bash
make migrate
```

#### `make makemigrations`
Creates new migration files based on model changes:

```bash
make makemigrations
```

#### `make createsuperuser`
Creates an admin superuser for API access:

```bash
make createsuperuser
```

#### `make runserver`
Starts the Django development server:

```bash
make runserver
```

#### `make test`
Runs all test suites:

```bash
make test
```

### Docker Management

#### `make up`
Starts the Docker containers in detached mode and waits for services to be ready:

```bash
make up
```

#### `make clean`
Stops and removes all Docker containers and volumes:

```bash
make clean
```

#### `make rebuild`
Cleans the environment and rebuilds all Docker containers from scratch:

```bash
make rebuild
```

### Code Quality

#### `make lint`
Runs flake8 to check code quality and style:

```bash
make lint
```

#### `make format`
Formats all Python code using black:

```bash
make format
```

#### `make format-check`
Checks if code formatting is needed without modifying files:

```bash
make format-check
```

#### `make quality`
Runs both format and lint checks (recommended before commits):

```bash
make quality
```

## Code Quality

The project uses industry-standard tools to maintain code quality and consistency:

### Configuration

- **Black**: Configured in `pyproject.toml` with 88-character line length
- **Flake8**: Configured in `.flake8` with black-compatible settings

### Workflow

Before committing code, run:

```bash
make quality
```

This will:
1. Auto-format all Python files with black
2. Check code quality with flake8

### Manual Usage

You can also run the tools individually:

```bash
# Format code
make format

# Check code style
make lint

# Check formatting without modifying files
make format-check
```

### Best Practices

- Run `make quality` before committing changes
- All code follows PEP 8 style guidelines
- Maximum line length: 88 characters
- Maximum cyclomatic complexity: 10
- Migrations are excluded from checks

## Authentication

The API uses **JWT (JSON Web Token)** authentication with a **custom User model**. Only users with `role='admin'` can access the API endpoints.

### Custom User Model

- **Username-based authentication** (with required email)
- **Role field** determines access ('admin', 'rider', 'driver')
- Only users with `role='admin'` can access API

### Quick Start

1. **Create an admin user:**
   ```bash
   make createsuperuser
   ```
   This creates a user with `role='admin'` automatically.

2. **Get JWT token:**
   ```bash
   curl -X POST http://localhost:8000/api/auth/login/ \
     -H "Content-Type: application/json" \
     -d '{"username": "admin", "password": "your_password"}'
   ```

3. **Use token in requests:**
   ```bash
   curl http://localhost:8000/api/users/ \
     -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
   ```

See [API Documentation](docs/API_DOCUMENTATION.md) for detailed authentication information.

## Example Usage

### Step 1: Login and Get JWT Token
```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "your_password"
  }'
```


Response:
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### Step 2: Use Access Token for API Requests

#### Create a Rider
```bash
curl -X POST http://localhost:8000/api/users/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "username": "johndoe",
    "email": "john@example.com",
    "role": "rider",
    "first_name": "John",
    "last_name": "Doe",
    "phone_number": "+1234567890"
  }'
```

#### Create a Ride
```bash
curl -X POST http://localhost:8000/api/rides/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
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

#### List Rides with Filters
```bash
curl http://localhost:8000/api/rides/?status=en-route&ordering=-pickup_time \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Step 3: Refresh Token When Expired
```bash
curl -X POST http://localhost:8000/api/auth/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{
    "refresh": "YOUR_REFRESH_TOKEN"
  }'
```

## Project Structure

```
wingz/
├── wingz-api/                # Main application directory
│   ├── manage.py
│   ├── load_dummy_data.py    # Dummy data generator script
│   ├── core/                 # Django project settings
│   │   ├── settings.py
│   │   ├── urls.py
│   │   ├── permissions.py    # Custom permissions
│   │   └── wsgi.py
│   ├── users/                # Users application
│   │   ├── models.py         # User model
│   │   ├── serializers.py    # User serializer
│   │   ├── views.py          # User ViewSet
│   │   ├── urls.py           # User API routing
│   │   ├── admin.py          # User admin configuration
│   │   ├── tests.py          # User tests
│   │   └── migrations/       # User migrations
│   └── rides/                # Rides application
│       ├── models.py         # Ride, RideEvent models
│       ├── serializers.py    # Ride serializers
│       ├── views.py          # Ride ViewSets
│       ├── urls.py           # Ride API routing
│       ├── admin.py          # Ride admin configuration
│       ├── tests.py          # Ride tests
│       └── migrations/       # Ride migrations
├── docs/
│   └── API_DOCUMENTATION.md  # Complete API reference
├── pyproject.toml            # Poetry dependencies & black config
├── .flake8                   # Flake8 configuration
├── Makefile                  # Project automation commands
├── docker-compose.yml        # Docker configuration
├── Dockerfile                # Docker image definition
└── README.md                 # This file
```
