up:
	docker-compose up -d
	@echo "Waiting for services to be ready..."
	@sleep 10
	@echo "Services are ready!"

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

.PHONY: up clean rebuild env lint format format-check quality
