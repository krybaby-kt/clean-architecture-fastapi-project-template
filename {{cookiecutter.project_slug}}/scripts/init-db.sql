-- Database initialization script for {{ cookiecutter.project_name }}.
-- The postgres docker image already creates the user/database from
-- POSTGRES_USER / POSTGRES_DB env vars, so this script only adds
-- extensions and adjusts privileges idempotently.

\c {{ cookiecutter.database_name }};

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

SET timezone = 'UTC';

GRANT ALL ON SCHEMA public TO {{ cookiecutter.database_user }};
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO {{ cookiecutter.database_user }};
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO {{ cookiecutter.database_user }};
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO {{ cookiecutter.database_user }};
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO {{ cookiecutter.database_user }};
