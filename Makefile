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
