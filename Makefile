up:
	docker-compose up -d
	@echo "Waiting for services to be ready..."
	@sleep 10
	@echo "Services are ready!"

db-up:
	docker-compose up -d db
	@echo "Waiting for database service to be ready..."
	@sleep 10
	@echo "Database service is ready!"

clean:
	docker-compose down -v

rebuild: clean
	docker-compose up -d --build
	@echo "Waiting for services to be ready..."
	@sleep 15
	@echo "Services rebuilt successfully!"

env:
	@if [ ! -f .env.sample ]; then \
		echo "Error: .env.sample file not found!"; \
		exit 1; \
	fi
	@echo "Generating .env file from .env.sample..."
	@cp .env.sample .env
	@echo ".env file created successfully!"
	@echo "Generating .env.docker file from .env.sample..."
	@cp .env.sample .env.docker
	@sed -i.bak 's/POSTGRES_SERVER=localhost/POSTGRES_SERVER=wingz_db/' .env.docker && rm .env.docker.bak
	@echo ".env.docker file created successfully!"
	@echo "Environment files generated successfully!"

# Django management commands
migrate:
	@echo "Running database migrations..."
	cd wingz-api && poetry run python manage.py migrate

migrations:
	@echo "Creating new migrations..."
	cd wingz-api && poetry run python manage.py makemigrations

superuser:
	@echo "Creating superuser..."
	cd wingz-api && poetry run python manage.py createsuperuser

runserver:
	@echo "Starting development server..."
	cd wingz-api && poetry run python manage.py runserver

test:
	@echo "Running tests..."
	cd wingz-api && poetry run python manage.py test

load-dummy-data:
	@echo "Loading dummy data..."
	cd wingz-api && poetry run python load_dummy_data.py

fake: up migrate load-dummy-data
	@echo "Setup completed! Services are up, migrations are applied, and dummy data is loaded."

# Code quality targets
lint:
	@echo "Running flake8 code quality checks..."
	cd wingz-api && poetry run flake8 .

format:
	@echo "Formatting code with black..."
	cd wingz-api && poetry run black .

format-check:
	@echo "Checking code formatting with black..."
	cd wingz-api && poetry run black --check .

quality: format lint
	@echo "Code quality checks completed!"

.PHONY: up db-up clean rebuild env migrate migrations superuser runserver test load-dummy-data fake lint format format-check quality
