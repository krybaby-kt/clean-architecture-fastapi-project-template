.PHONY: help install install-dev lint lint-fix format type-check check test clean

help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install production dependencies
	poetry install --no-root --sync

install-dev: ## Install development dependencies
	poetry install --no-root --sync

lint: ## Run linting with ruff
	poetry run ruff check src/{{cookiecutter.project_slug}}/

lint-fix: ## Run linting with ruff and fix auto-fixable issues
	poetry run ruff check --fix src/{{cookiecutter.project_slug}}/

format: ## Format code with ruff
	poetry run ruff format src/{{cookiecutter.project_slug}}/

type-check: ## Run type checking with mypy
	poetry run mypy src/{{cookiecutter.project_slug}}/

check: ## Run all checks (lint + format check + type check)
	poetry run ruff check src/{{cookiecutter.project_slug}}/
	poetry run ruff format --check src/{{cookiecutter.project_slug}}/
	poetry run mypy src/{{cookiecutter.project_slug}}/

test: ## Run tests
	poetry run pytest tests/ -v

test-cov: ## Run tests with coverage
	poetry run pytest tests/ -v --cov=src/{{cookiecutter.project_slug}} --cov-report=html --cov-report=term

clean: ## Clean up cache and temporary files
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .pytest_cache/
	rm -rf .ruff_cache/
	rm -rf htmlcov/
	rm -rf .coverage

dev-setup: install-dev ## Set up development environment
	@echo "Development environment set up successfully!"
	@echo "Run 'make check' to verify everything is working."

# Database migration commands
migration: ## Create a new migration file
	poetry run alembic revision --autogenerate -m "$(msg)"

migrate: ## Apply all pending migrations
	poetry run alembic upgrade head

migrate-downgrade: ## Downgrade to previous migration
	poetry run alembic downgrade -1

migrate-history: ## Show migration history
	poetry run alembic history

migrate-current: ## Show current migration
	poetry run alembic current

migrate-stamp: ## Stamp database with current migration (without applying)
	poetry run alembic stamp head

# Docker commands
docker-build: ## Build Docker image for production
	docker build --target production -t {{cookiecutter.project_slug}}:latest .

docker-build-dev: ## Build Docker image for development
	docker build --target development -t {{cookiecutter.project_slug}}:dev .

docker-build-test: ## Build Docker image for testing
	docker build --target testing -t {{cookiecutter.project_slug}}:test .

docker-up: ## Start all services with docker-compose
	docker compose up -d

docker-up-dev: ## Start development environment
	docker compose --profile dev up -d

COMPOSE_ALL_PROFILES := --profile dev --profile test --profile migrate --profile dev-tools

docker-down: ## Stop all services (across every profile)
	docker compose $(COMPOSE_ALL_PROFILES) down --remove-orphans

docker-down-volumes: ## Stop all services AND remove volumes (destroys DB data)
	docker compose $(COMPOSE_ALL_PROFILES) down -v --remove-orphans

docker-logs: ## Show logs for all services
	docker compose logs -f

docker-logs-app: ## Show logs for application
	docker compose logs -f app

docker-shell: ## Open shell in running app container
	docker compose exec app bash

docker-migrate: ## Run database migrations
	docker compose --profile migrate run --rm migrate

docker-test: ## Run tests in Docker
	docker compose --profile test run --rm test

docker-clean: ## Clean up Docker resources
	docker compose down -v --remove-orphans
	docker system prune -f

docker-rebuild: ## Rebuild and restart services (rebuilds ALL profiles incl. app-dev)
	docker compose $(COMPOSE_ALL_PROFILES) down --remove-orphans
	docker compose $(COMPOSE_ALL_PROFILES) build --no-cache
	docker compose up -d

# Environment setup
setup-env: ## Create .env file from template
	./scripts/setup-env.sh

# Development helpers

dev-setup-docker: setup-env ## Set up development environment with Docker
{% if cookiecutter.use_database == "postgresql" and cookiecutter.use_cache == "redis" %}
	docker compose --profile dev up -d postgres redis
{% elif cookiecutter.use_database == "postgresql" and cookiecutter.use_cache == "keydb" %}
	docker compose --profile dev up -d postgres keydb
{% elif cookiecutter.use_database == "postgresql" and cookiecutter.use_cache == "dragonfly" %}
	docker compose --profile dev up -d postgres dragonfly
{% elif cookiecutter.use_database == "postgresql" and cookiecutter.use_cache == "tarantool" %}
	docker compose --profile dev up -d postgres tarantool
{% elif cookiecutter.use_database == "postgresql" %}
	docker compose --profile dev up -d postgres
{% elif cookiecutter.use_database == "mysql" and cookiecutter.use_cache == "redis" %}
	docker compose --profile dev up -d mysql redis
{% elif cookiecutter.use_database == "mysql" %}
	docker compose --profile dev up -d mysql
{% elif cookiecutter.use_database == "sqlite" %}
	docker compose --profile dev --profile init up -d sqlite-init
{% endif %}
	@echo "Waiting for services to be ready..."
	@sleep 10
{% if cookiecutter.use_database != "none" %}
	$(MAKE) docker-migrate
{% endif %}
	@echo "Development environment is ready!"
	@echo "Run 'make docker-up-dev' to start the application"

ci: check test ## Run CI pipeline (lint + type check + test)
	@echo "CI pipeline completed successfully!"

{% if cookiecutter.use_broker == "kafka" %}
# Kafka commands
docker-kafka-logs: ## Show Kafka logs
	docker compose logs -f kafka

docker-kafka-shell: ## Open shell in Kafka container
	docker compose exec kafka bash

docker-kafka-topics: ## List Kafka topics
	docker compose exec kafka kafka-topics --bootstrap-server localhost:9092 --list

docker-kafka-create-topic: ## Create Kafka topic for artifacts
	docker compose exec kafka kafka-topics --bootstrap-server localhost:9092 --create --topic new_artifacts --partitions 3 --replication-factor 1

docker-kafka-consume: ## Consume messages from Kafka topic
	docker compose exec kafka kafka-console-consumer --bootstrap-server localhost:9092 --topic new_artifacts --from-beginning
{% endif %}
{% if cookiecutter.use_broker == "rabbitmq" %}
# RabbitMQ commands
docker-rabbitmq-logs: ## Show RabbitMQ logs
	docker compose logs -f rabbitmq

docker-rabbitmq-shell: ## Open shell in RabbitMQ container
	docker compose exec rabbitmq bash
{% endif %}
{% if cookiecutter.use_broker == "nats" %}
# NATS commands
docker-nats-logs: ## Show NATS logs
	docker compose logs -f nats
{% endif %}
