.PHONY: up down build test logs download-dump reset-db deploy-prod publish-vps

up:
	docker compose up --build -d

down:
	docker compose down

build:
	docker compose build

test:
	docker compose run --rm --build api pytest tests/ -v -m "not integration"

test-integration:
	docker compose run --rm --build api pytest tests/ -v -m integration

test-local:
	cd backend && test -x .venv/bin/pytest || (python3 -m venv .venv && .venv/bin/pip install -q -r requirements.txt)
	cd backend && .venv/bin/pytest tests/ -v -m "not integration"

logs:
	docker compose logs -f

download-dump:
	./scripts/download_dump.sh

reset-db:
	docker compose down -v
	docker compose up --build -d

deploy-prod:
	docker compose -f docker-compose.vps.yml up --build -d

publish-vps:
	chmod +x scripts/publish-to-vps.sh scripts/deploy-on-server.sh scripts/fix-vps.sh
	./scripts/publish-to-vps.sh
