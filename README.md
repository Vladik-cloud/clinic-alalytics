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

## Дамп из ТЗ

Ссылка из задания — presigned URL с ограниченным сроком. Когда получите свежую ссылку:

```bash
DUMP_URL="https://storage.yandexcloud.net/..." make download-dump
make reset-db
```

Либо положите `data/dump.sql.gz` вручную и пересоздайте volume: `make reset-db`.

Если дамп недоступен, поднимается **демо-схема** (`doctors`, `patients`, `visits`, `services`) с тестовыми данными.

### Маппинг таблиц реального дампа

После импорта сервис пытается автоматически найти таблицы (`doctors`/`employees`, `visits`/`appointments`, …).  
При необходимости задайте переменные окружения для `api` в `docker-compose.yml`:

```yaml
SCHEMA_DOCTORS_TABLE: employees
SCHEMA_VISITS_TABLE: appointments
SCHEMA_REVENUE_TABLE: invoice_items
# и т.д. — см. backend/app/schema_map.py
```

## Метрики

**Выручка** — сумма `amount` по услугам врача за период.

**Перенаправляемость** — среди пациентов, у которых *первый* завершённый приём был у врача X, какая доля позже посетила *другого* врача.

## Тесты

```bash
make test
```

Локально (нужен запущенный Postgres):

```bash
make test-local
```

## Деплой на VPS

1. Установите Docker на сервер.
2. Склонируйте репозиторий, положите дамп в `data/`.
3. `docker compose up --build -d`
4. Настройте reverse proxy (Caddy/Nginx) на порт `3000`.

## Документация

См. [ARCHITECTURE.md](./ARCHITECTURE.md) — архитектурные решения и что бы улучшил при большем времени.
