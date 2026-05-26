from datetime import date

from app import cliniciq_analytics
from app.db import fetch_all
from app.schema_map import SchemaMap, detect_schema


def _status_sql(schema: SchemaMap, alias: str = "v") -> str:
    if not schema.visit_status:
        return ""
    return f" AND ({alias}.{schema.visit_status} IS NULL OR {alias}.{schema.visit_status} = 'completed')"


def revenue_by_doctor(
    schema: SchemaMap | None = None,
    start: date | None = None,
    end: date | None = None,
) -> list[dict]:
    s = schema or detect_schema()
    if s.mode == "cliniciq":
        return cliniciq_analytics.revenue_by_doctor(start, end)
    date_parts = []
    if start:
        date_parts.append(f"r.{s.revenue_at} >= :start_date")
    if end:
        date_parts.append(f"r.{s.revenue_at} < CAST(:end_date AS date) + INTERVAL '1 day'")
    date_sql = (" AND " + " AND ".join(date_parts)) if date_parts else ""

    sql = f"""
        SELECT
            d.{s.doctor_id} AS doctor_id,
            d.{s.doctor_name} AS doctor_name,
            COALESCE(SUM(r.{s.revenue_amount}), 0)::float AS revenue,
            COUNT(r.{s.revenue_amount}) AS service_count
        FROM {s.doctors} d
        LEFT JOIN {s.revenue_table} r
            ON r.{s.revenue_doctor} = d.{s.doctor_id}
            {date_sql}
        GROUP BY d.{s.doctor_id}, d.{s.doctor_name}
        ORDER BY revenue DESC, doctor_name
    """
    return fetch_all(sql, params)


def referral_rate_by_doctor(
    schema: SchemaMap | None = None,
    start: date | None = None,
    end: date | None = None,
) -> list[dict]:
    s = schema or detect_schema()
    if s.mode == "cliniciq":
        return cliniciq_analytics.referral_rate_by_doctor(start, end)
    params: dict = {}
    fv_filters: list[str] = []
    if start:
        fv_filters.append("fv.first_visit_at >= :start_date")
        params["start_date"] = start
    if end:
        fv_filters.append("fv.first_visit_at < CAST(:end_date AS date) + INTERVAL '1 day'")
        params["end_date"] = end
    fv_where = ("WHERE " + " AND ".join(fv_filters)) if fv_filters else ""

    sql = f"""
        WITH completed_visits AS (
            SELECT
                v.{s.visit_patient} AS patient_id,
                v.{s.visit_doctor} AS doctor_id,
                v.{s.visit_at} AS visit_at
            FROM {s.visits} v
            WHERE 1=1 {_status_sql(s)}
        ),
        first_visits AS (
            SELECT DISTINCT ON (patient_id)
                patient_id,
                doctor_id AS first_doctor_id,
                visit_at AS first_visit_at
            FROM completed_visits
            ORDER BY patient_id, visit_at ASC, doctor_id ASC
        ),
        filtered_first AS (
            SELECT * FROM first_visits fv
            {fv_where}
        ),
        referred AS (
            SELECT DISTINCT ff.patient_id, ff.first_doctor_id
            FROM filtered_first ff
            JOIN completed_visits cv
                ON cv.patient_id = ff.patient_id
               AND cv.visit_at > ff.first_visit_at
               AND cv.doctor_id <> ff.first_doctor_id
        )
        SELECT
            d.{s.doctor_id} AS doctor_id,
            d.{s.doctor_name} AS doctor_name,
            COUNT(ff.patient_id) AS patients_first_visit,
            COUNT(r.patient_id) AS patients_referred,
            ROUND(
                100.0 * COUNT(r.patient_id) / NULLIF(COUNT(ff.patient_id), 0),
                1
            ) AS referral_rate_pct
        FROM {s.doctors} d
        JOIN filtered_first ff ON ff.first_doctor_id = d.{s.doctor_id}
        LEFT JOIN referred r
            ON r.first_doctor_id = ff.first_doctor_id
           AND r.patient_id = ff.patient_id
        GROUP BY d.{s.doctor_id}, d.{s.doctor_name}
        ORDER BY referral_rate_pct DESC, patients_first_visit DESC
    """
    return fetch_all(sql, params)


def summary(
    schema: SchemaMap | None = None,
    start: date | None = None,
    end: date | None = None,
) -> dict:
    rev = revenue_by_doctor(schema, start, end)
    ref = referral_rate_by_doctor(schema, start, end)
    total_revenue = sum(float(r.get("revenue") or 0) for r in rev)
    return {
        "total_revenue": total_revenue,
        "doctors_count": len(rev),
        "avg_referral_rate_pct": (
            round(sum(float(r["referral_rate_pct"] or 0) for r in ref) / len(ref), 1)
            if ref
            else 0
        ),
        "period": {
            "start": start.isoformat() if start else None,
            "end": end.isoformat() if end else None,
        },
    }
