# Contract: Raspberry Pi PostgreSQL Database Connection

**Feature**: `002-raspi-postgres-data`
**Created**: 2026-07-02

## Purpose

This contract defines the backend database connection interface for the Raspberry Pi PostgreSQL implementation.

## Environment configuration

The backend must support the following environment variables for PostgreSQL connectivity:

- `PG_HOST`: hostname or IP address of the Raspberry Pi Postgres instance
- `PG_PORT`: TCP port for Postgres (default `5432`)
- `PG_DATABASE`: Postgres database name
- `PG_USER`: database username
- `PG_PASSWORD`: database password
- `PG_SSLMODE`: SSL mode for the Postgres connection (`disable`, `require`, etc.)

The backend may continue to support `DATABASE_PATH` for SQLite fallback, but the primary production mode for this feature is Postgres.

## Runtime behavior

- On startup, the backend must connect to the configured Postgres instance.
- If the database is unreachable, the backend must emit clear diagnostic logs and fail startup or retry gracefully based on configuration.
- The backend must ensure required tables are created before accepting application traffic.
- It must preserve existing application logic for users, profiles, verifications, requests, pitches, and moderation actions.

## Compatibility

- Use standard SQL constructs compatible with PostgreSQL.
- Avoid SQLite-specific SQL syntax in the Postgres path.
- Preserve current table constraints, unique indexes, and foreign keys.

## Verification

This contract is validated by successful backend startup, table creation, and persistence of user-request-pitch data on the Raspberry Pi database.
