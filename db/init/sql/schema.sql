CREATE TABLE IF NOT EXISTS doctors (
    id          SERIAL PRIMARY KEY,
    full_name   TEXT NOT NULL,
    specialty   TEXT,
    is_active   BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS patients (
    id          SERIAL PRIMARY KEY,
    full_name   TEXT NOT NULL,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS visits (
    id          SERIAL PRIMARY KEY,
    patient_id  INTEGER NOT NULL REFERENCES patients(id),
    doctor_id   INTEGER NOT NULL REFERENCES doctors(id),
    visit_at    TIMESTAMPTZ NOT NULL,
    status      TEXT NOT NULL DEFAULT 'completed'
        CHECK (status IN ('scheduled', 'completed', 'cancelled', 'no_show'))
);

CREATE INDEX IF NOT EXISTS idx_visits_patient_at ON visits (patient_id, visit_at);
CREATE INDEX IF NOT EXISTS idx_visits_doctor_at ON visits (doctor_id, visit_at);
CREATE INDEX IF NOT EXISTS idx_visits_at ON visits (visit_at);

CREATE TABLE IF NOT EXISTS services (
    id          SERIAL PRIMARY KEY,
    visit_id    INTEGER NOT NULL REFERENCES visits(id),
    doctor_id   INTEGER NOT NULL REFERENCES doctors(id),
    name        TEXT NOT NULL,
    amount      NUMERIC(12, 2) NOT NULL CHECK (amount >= 0),
    provided_at TIMESTAMPTZ NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_services_doctor_at ON services (doctor_id, provided_at);
