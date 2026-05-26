DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'cliniciq_readonly') THEN
        CREATE ROLE cliniciq_readonly LOGIN PASSWORD 'cliniciq_readonly';
    END IF;
END
$$;

GRANT CONNECT ON DATABASE cliniciq TO cliniciq_readonly;
GRANT USAGE ON SCHEMA public TO cliniciq_readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO cliniciq_readonly;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO cliniciq_readonly;
