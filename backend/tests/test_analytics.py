import os
from datetime import date

import pytest
from sqlalchemy import create_engine, text

from app.analytics import referral_rate_by_doctor, revenue_by_doctor, summary
from app.schema_map import SchemaMap

DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql://cliniciq_readonly:cliniciq_readonly@localhost:5432/cliniciq",
)


def _db_available() -> bool:
    try:
        engine = create_engine(DATABASE_URL)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False


@pytest.fixture
def live_db(monkeypatch):
    if not _db_available():
        pytest.skip("PostgreSQL is not available")
    import app.db as db_module

    db_module.engine = create_engine(
        DATABASE_URL,
        connect_args={"options": "-c default_transaction_read_only=on"},
    )


@pytest.mark.integration
def test_revenue_returns_doctors(live_db):
    rows = revenue_by_doctor()
    assert len(rows) >= 1
    assert "revenue" in rows[0]
    assert "doctor_name" in rows[0]


@pytest.mark.integration
def test_referral_rate_in_valid_range(live_db):
    rows = referral_rate_by_doctor()
    for row in rows:
        rate = float(row["referral_rate_pct"])
        assert 0 <= rate <= 100


@pytest.mark.integration
def test_summary_with_date_filter(live_db):
    result = summary(start=date(2025, 1, 1), end=date(2025, 12, 31))
    assert "total_revenue" in result
    assert result["period"]["start"] == "2025-01-01"


@pytest.mark.integration
def test_referral_query_runs_with_default_schema(live_db):
    rows = referral_rate_by_doctor()
    assert isinstance(rows, list)


def test_schema_map_dataclass():
    schema = SchemaMap(
        doctors="doctors",
        doctor_id="id",
        doctor_name="full_name",
        patients="patients",
        patient_id="id",
        visits="visits",
        visit_id="id",
        visit_patient="patient_id",
        visit_doctor="doctor_id",
        visit_at="visit_at",
        visit_status="status",
        revenue_table="services",
        revenue_doctor="doctor_id",
        revenue_amount="amount",
        revenue_at="provided_at",
    )
    assert schema.uses_services is True
