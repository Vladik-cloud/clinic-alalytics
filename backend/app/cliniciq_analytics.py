from datetime import date

from app.db import fetch_all


def _date_filter(column: str, start: date | None, end: date | None) -> tuple[str, dict]:
    parts: list[str] = []
    params: dict = {}
    if start:
        parts.append(f"{column} >= :start_date")
        params["start_date"] = start
    if end:
        parts.append(f"{column} < CAST(:end_date AS date) + INTERVAL '1 day'")
        params["end_date"] = end
    if not parts:
        return "", params
    return " AND " + " AND ".join(parts), params


def revenue_by_doctor(start: date | None = None, end: date | None = None) -> list[dict]:
    date_sql, params = _date_filter("s.completed_at", start, end)
    sql = f"""
        SELECT
            u.id AS doctor_id,
            TRIM(CONCAT(u.last_name, ' ', u.first_name)) AS doctor_name,
            COALESCE(SUM(p.frozen_price * p.quantity), 0)::float AS revenue,
            COUNT(p.id) AS service_count
        FROM auth_user u
        INNER JOIN schedules_schedule sch ON sch.doctor_id = u.id
        INNER JOIN appointments_appointment a ON a.schedule_id = sch.id
        INNER JOIN appointments_treatmentplanstage s
            ON s.appointment_id = a.id
           AND NOT s.is_voided
           AND s.status = 'completed'
        INNER JOIN appointments_treatmentplanstageprocedure p
            ON p.stage_id = s.id
           AND p.frozen_price IS NOT NULL
        WHERE u.is_active
          {date_sql}
        GROUP BY u.id, doctor_name
        ORDER BY revenue DESC, doctor_name
    """
    return fetch_all(sql, params)


def referral_rate_by_doctor(start: date | None = None, end: date | None = None) -> list[dict]:
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
                a.patient_id,
                sch.doctor_id,
                a.start_time AS visit_at
            FROM appointments_appointment a
            INNER JOIN schedules_schedule sch ON sch.id = a.schedule_id
            WHERE a.status = 'completed'
              AND a.patient_id IS NOT NULL
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
            u.id AS doctor_id,
            TRIM(CONCAT(u.last_name, ' ', u.first_name)) AS doctor_name,
            COUNT(ff.patient_id) AS patients_first_visit,
            COUNT(r.patient_id) AS patients_referred,
            ROUND(
                100.0 * COUNT(r.patient_id) / NULLIF(COUNT(ff.patient_id), 0),
                1
            ) AS referral_rate_pct
        FROM auth_user u
        JOIN filtered_first ff ON ff.first_doctor_id = u.id
        LEFT JOIN referred r
            ON r.first_doctor_id = ff.first_doctor_id
           AND r.patient_id = ff.patient_id
        GROUP BY u.id, doctor_name
        ORDER BY referral_rate_pct DESC, patients_first_visit DESC
    """
    return fetch_all(sql, params)
