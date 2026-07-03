# Quickstart: Raspberry Pi PostgreSQL Data Platform

**Feature**: `002-raspi-postgres-data`
**Created**: 2026-07-02

## Prerequisites

- A Raspberry Pi host with PostgreSQL installed and reachable from the backend runtime.
- PostgreSQL database and user created for NguonTin.
- Network access from the backend container or local development machine to the Raspberry Pi host.
- Environment variables configured for Postgres connection.

## Setup

1. Configure the Raspberry Pi Postgres connection in `.env` or `.env.local`:

```env
PG_HOST=raspberrypi.local
PG_PORT=5432
PG_DATABASE=nguontin
PG_USER=nguontin_user
PG_PASSWORD=secure_password
PG_SSLMODE=disable
```

2. Ensure the backend does not use the SQLite `DATABASE_PATH` for the primary production path. If needed, keep `DATABASE_PATH` only for local fallback testing.

## Run the backend

Use Docker Compose or a local Python launch:

```bash
docker compose up --build backend
```

or locally:

```bash
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Expected outcomes

- The backend starts without SQLite-only errors.
- The backend creates required tables in the Raspberry Pi Postgres instance.
- The `/health` endpoint returns a successful response.
- Data written through the backend is visible in the Postgres database.

## Validation commands

1. Create a user or profile through the existing app flow.
2. Query the Raspberry Pi Postgres instance directly to verify the record exists.
3. Reboot the Raspberry Pi, restart the backend, and confirm the same record is still available.

## Notes

- If the backend cannot connect, check host reachability, credentials, and network configuration.
- Use `PG_SSLMODE=disable` for local network setups unless the Pi is configured to accept SSL.
