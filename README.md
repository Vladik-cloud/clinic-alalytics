# Clinic Analytics

Веб-сервис аналитики для стоматологической клиники (ClinicIQ): один отчёт с инфографикой по **выручке врачей** и **перенаправляемости** пациентов.

## Быстрый старт

```bash
make up
# или
docker compose up --build -d
```

Откройте отчёт: **http://localhost:3000**

API: **http://localhost:8000/api/report**

## Что внутри

| Сервис | Порт | Описание |
|--------|------|----------|
| `web`  | 3000 | React + Recharts, фильтр по периоду |
| `api`  | 8000 | FastAPI, только SELECT (read-only роль) |
| `db`   | 5433 (host) | PostgreSQL 16 — 5433, т.к. 5432 часто занят локальным Postgres |


### Дамп ClinicIQ

```bash
cp ~/Downloads/demo_server_20260507.dump data/dump.dump
make reset-db
```

Формат `.dump` (pg_restore). Также: `data/dump.sql.gz`, `data/*.dump`. Без дампа — демо-seed.

Даты приёмов в дампе: примерно **2017-05-03** — **2026-04-30** (фильтр «completed»).

## Метрики

**Выручка** — сумма `amount` по услугам врача за период.

**Перенаправляемость** — среди пациентов, у которых *первый* завершённый приём был у врача X, какая доля позже посетила *другого* врача.

## Тесты

Unit-тесты (без БД, в Docker):

```bash
make test
```

Integration-тесты (нужен `make up`):

```bash
make test-integration
```

Локально (создаёт `backend/.venv` при первом запуске):

```bash
make test-local
```

## Деплой на VPS

**Новичок?** Пошаговая инструкция с нуля: **[DEPLOY_GUIDE.md](./DEPLOY_GUIDE.md)** (где взять VPS, что в каком порядке).

**Что отправить проверяющему** — [SUBMISSION.md](./SUBMISSION.md).

### Вариант A: с Mac одной командой (после настройки VPS)

На сервере один раз: Docker + git + clone (см. ниже). Потом с Mac:

```bash
export VPS_HOST=ВАШ_IP VPS_USER=ubuntu DOMAIN=ваш-домен.ru
make publish-vps
```

Скрипт зальёт `data/dump.dump` и перезапустит prod-стек.

### Вариант B: вручную на сервере

**1. Сервер (Ubuntu 22.04+)**

```bash
sudo apt update && sudo apt install -y git docker.io docker-compose-plugin
sudo usermod -aG docker $USER
# exit и зайти по SSH снова
```

**2. Код, `.env`, дамп**

```bash
git clone https://github.com/Vladik-cloud/clinic-alalytics.git
cd clinic-alalytics
cp .env.example .env
nano .env   # POSTGRES_PASSWORD, CORS_ORIGINS=https://ваш-домен.ru
```

Дамп с Mac:

```bash
scp data/dump.dump ubuntu@ВАШ_IP:~/clinic-alalytics/data/dump.dump
```

**3. Запуск**

```bash
chmod +x scripts/deploy-on-server.sh
./scripts/deploy-on-server.sh
# логи импорта: docker-compose -f docker-compose.vps.yml logs -f db
# Caddy (HTTP): bash scripts/fix-vps.sh
```

**4. Caddy (HTTP, см. deploy/Caddyfile.example)**

```bash
sudo apt install -y debian-keyring debian-archive-keyring apt-transport-https curl
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | sudo gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | sudo tee /etc/apt/sources.list.d/caddy-stable.list
sudo apt update && sudo apt install -y caddy
sudo cp deploy/Caddyfile.example /etc/caddy/Caddyfile
sudo nano /etc/caddy/Caddyfile   # замените DOMAIN
sudo systemctl reload caddy
```

**5. Firewall**

```bash
sudo ufw allow 22 && sudo ufw allow 80 && sudo ufw allow 443 && sudo ufw enable
```

Проверка: `curl -s http://ваш-домен.sslip.io/api/health`

## Документация

См. [ARCHITECTURE.md](./ARCHITECTURE.md) — архитектурные решения и что бы улучшил при большем времени.
