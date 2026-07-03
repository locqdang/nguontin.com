# Research: Raspberry Pi PostgreSQL Data Platform

**Feature**: `002-raspi-postgres-data`
**Created**: 2026-07-02

## Decision: Postgres adapter with environment-driven configuration

The backend currently uses a lightweight SQLite layer with raw `sqlite3` access. For Raspberry Pi PostgreSQL support, the simplest and most maintainable path is to add a separate connection adapter that can open either a SQLite database file or a PostgreSQL connection based on environment settings.

### Chosen approach

- Keep the FastAPI backend structure intact.
- Add `psycopg[binary]` for PostgreSQL support.
- Use `PG_HOST`, `PG_PORT`, `PG_DATABASE`, `PG_USER`, `PG_PASSWORD`, and `PG_SSLMODE` environment variables.
- Preserve the existing SQL schema and constraints as closely as possible.
- Use explicit table creation statements on startup to bootstrap Postgres.

### Alternatives considered

- Using SQLAlchemy or another ORM: rejected because the project currently uses raw SQL and the feature scope is limited to database connectivity rather than a full data layer redesign.
- Using `asyncpg`: rejected because the backend is synchronous and the current DB layer is built around blocking calls.
- Forcing a cloud-managed SQL service: rejected by the feature requirement.

### Rationale

This approach minimizes disruption to the existing backend while satisfying the feature requirement to use the Raspberry Pi Postgres instance as the primary data store. It also keeps the migration scope manageable and the runtime behavior explicit.

## Operational considerations

- Raspberry Pi host discovery may require a stable hostname or IP address in `.env`.
- The backend should handle repeated connection failures gracefully and log clear diagnostics.
- Postgres schema creation must be idempotent and compatible with the existing SQLite schema shape.

