"""Maps real ClinicIQ dump tables to analytics queries via env overrides."""

from dataclasses import dataclass
import os

from sqlalchemy import text

from app.db import engine


@dataclass(frozen=True)
class SchemaMap:
    doctors: str
    doctor_id: str
    doctor_name: str
    patients: str
    patient_id: str
    visits: str
    visit_id: str
    visit_patient: str
    visit_doctor: str
    visit_at: str
    visit_status: str | None
    revenue_table: str
    revenue_doctor: str
    revenue_amount: str
    revenue_at: str

    @property
    def uses_services(self) -> bool:
        return self.revenue_table == "services"


DEFAULT = SchemaMap(
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


def _table_exists(name: str) -> bool:
    with engine.connect() as conn:
        row = conn.execute(
            text(
                """
                SELECT 1 FROM information_schema.tables
                WHERE table_schema = 'public' AND table_name = :name
                """
            ),
            {"name": name},
        ).first()
        return row is not None


def _pick(*candidates: str) -> str | None:
    for name in candidates:
        if _table_exists(name):
            return name
    return None


def detect_schema() -> SchemaMap:
    """Auto-detect common ClinicIQ / MIS naming when env vars are not set."""
    if os.getenv("SCHEMA_DOCTORS_TABLE"):
        return SchemaMap(
            doctors=os.environ["SCHEMA_DOCTORS_TABLE"],
            doctor_id=os.getenv("SCHEMA_DOCTOR_ID", "id"),
            doctor_name=os.getenv("SCHEMA_DOCTOR_NAME", "full_name"),
            patients=os.environ.get("SCHEMA_PATIENTS_TABLE", "patients"),
            patient_id=os.getenv("SCHEMA_PATIENT_ID", "id"),
            visits=os.environ["SCHEMA_VISITS_TABLE"],
            visit_id=os.getenv("SCHEMA_VISIT_ID", "id"),
            visit_patient=os.getenv("SCHEMA_VISIT_PATIENT", "patient_id"),
            visit_doctor=os.getenv("SCHEMA_VISIT_DOCTOR", "doctor_id"),
            visit_at=os.getenv("SCHEMA_VISIT_AT", "visit_at"),
            visit_status=os.getenv("SCHEMA_VISIT_STATUS"),
            revenue_table=os.environ.get("SCHEMA_REVENUE_TABLE", "services"),
            revenue_doctor=os.getenv("SCHEMA_REVENUE_DOCTOR", "doctor_id"),
            revenue_amount=os.getenv("SCHEMA_REVENUE_AMOUNT", "amount"),
            revenue_at=os.getenv("SCHEMA_REVENUE_AT", "provided_at"),
        )

    doctors = _pick("doctors", "doctor", "employees", "employee", "medics", "specialists")
    patients = _pick("patients", "patient", "clients", "client")
    visits = _pick("visits", "visit", "appointments", "appointment", "receptions")
    services = _pick("services", "service", "invoice_items", "invoice_item", "bill_items")

    if not (doctors and patients and visits):
        return DEFAULT

    return SchemaMap(
        doctors=doctors,
        doctor_id="id",
        doctor_name=_column_or_default(doctors, ("full_name", "name", "fio", "title"), "full_name"),
        patients=patients,
        patient_id="id",
        visits=visits,
        visit_id="id",
        visit_patient=_column_or_default(visits, ("patient_id", "client_id"), "patient_id"),
        visit_doctor=_column_or_default(visits, ("doctor_id", "employee_id", "medic_id"), "doctor_id"),
        visit_at=_column_or_default(visits, ("visit_at", "started_at", "date_time", "appointment_at"), "visit_at"),
        visit_status=_column_or_default(visits, ("status",), None),
        revenue_table=services or visits,
        revenue_doctor=_column_or_default(services or visits, ("doctor_id", "employee_id"), "doctor_id"),
        revenue_amount=_column_or_default(services or visits, ("amount", "price", "sum", "total"), "amount"),
        revenue_at=_column_or_default(services or visits, ("provided_at", "visit_at", "created_at"), "visit_at"),
    )


def _column_or_default(table: str, candidates: tuple[str, ...], default: str | None) -> str | None:
    with engine.connect() as conn:
        cols = {
            row[0]
            for row in conn.execute(
                text(
                    """
                    SELECT column_name FROM information_schema.columns
                    WHERE table_schema = 'public' AND table_name = :table
                    """
                ),
                {"table": table},
            )
        }
    for col in candidates:
        if col in cols:
            return col
    return default
