from datetime import date
from typing import Annotated

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

from app.analytics import referral_rate_by_doctor, revenue_by_doctor, summary
from app.config import settings
from app.db import fetch_all
from app.schema_map import detect_schema

app = FastAPI(
    title="Clinic Analytics",
    description="Отчёт по выручке врачей и перенаправляемости",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.cors_origins.split(",") if o.strip()],
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health() -> dict:
    fetch_all("SELECT 1 AS ok")
    return {"status": "ok"}


@app.get("/api/schema")
def schema_info() -> dict:
    s = detect_schema()
    return {
        "doctors_table": s.doctors,
        "patients_table": s.patients,
        "visits_table": s.visits,
        "revenue_table": s.revenue_table,
    }


@app.get("/api/report")
def report(
    start_date: Annotated[date | None, Query()] = None,
    end_date: Annotated[date | None, Query()] = None,
) -> dict:
    schema = detect_schema()
    return {
        "summary": summary(schema, start_date, end_date),
        "revenue_by_doctor": revenue_by_doctor(schema, start_date, end_date),
        "referral_by_doctor": referral_rate_by_doctor(schema, start_date, end_date),
        "schema": {
            "doctors_table": schema.doctors,
            "visits_table": schema.visits,
            "revenue_table": schema.revenue_table,
        },
    }
