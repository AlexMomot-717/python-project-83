install:
	poetry install
dev:
    poetry run flask --app page_analyzer.app:app run

PORT ?= 8000
start:
	poetry run gunicorn -w 5 -b 0.0.0.0:$(PORT) page_analyzer:app

pre-commit:
	pre-commit run --all-files

lint:
	poetry run flake8

build:
	./build.sh

test:
	poetry run pytest

test-coverage:
	poetry run pytest --cov=page_analyzer --cov-report xml --cov-report=html tests/

start-postgres:
	@docker-compose up -d postgres
	@sleep 2

stop-postgres:
	@docker-compose stop postgres

refresh-postgres-data:
	@docker-compose down --volumes
	@docker-compose build postgres
	@docker-compose up -d postgres
	@sleep 2

build-services:
	@docker-compose build --no-cache

up:
	@docker-compose up -d

down:
	@docker-compose down

start-services:
	@docker-compose start

stop-services:
	@docker-compose stop

restart:
	@docker-compose up --build
