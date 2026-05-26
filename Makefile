.PHONY: up down build test logs download-dump reset-db

up:
	docker compose up --build -d

down:
	docker compose down

build:
	docker compose build

test:
	docker compose run --rm api pytest tests/ -v -m "not integration"

test-integration:
	docker compose run --rm api pytest tests/ -v -m integration

test-local:
	cd backend && pytest tests/ -v -m "not integration"

logs:
	docker compose logs -f

download-dump:
	./scripts/download_dump.sh

reset-db:
	docker compose down -v
	docker compose up --build -d
