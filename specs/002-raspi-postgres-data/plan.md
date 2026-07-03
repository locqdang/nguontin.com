# Implementation Plan: Raspberry Pi PostgreSQL Data Platform

**Branch**: `002-raspi-postgres-data` | **Date**: 2026-07-02 | **Spec**: `specs/002-raspi-postgres-data/spec.md`

**Input**: Feature specification from `/specs/002-raspi-postgres-data/spec.md`

The goal of this plan is to migrate the NguonTin backend from its current SQLite data layer to a self-hosted PostgreSQL instance running on the Raspberry Pi, while preserving the existing FastAPI application shell and user workflow. Deliver a configurable Postgres connection model, validate persistence across Raspberry Pi reboots, and document the required Raspberry Pi database settings for local development and deployment.

## Summary

Replace the backend's SQLite engine with PostgreSQL support and point the application at the self-hosted Raspberry Pi database. Add environment-driven connection settings, ensure the Raspberry Pi Postgres instance is the primary data store, and validate that data survives Pi restarts and network interruptions. Keep the frontend and existing product behavior unchanged, while moving core app persistence to the intended Raspi Postgres platform.

## Technical Context

**Language/Version**: Python 3.12

**Primary Dependencies**: FastAPI, python-dotenv, sqlite3 (existing), `psycopg[binary]` for PostgreSQL support, Docker Compose for local/deployment orchestration

**Storage**: PostgreSQL on the self-hosted Raspberry Pi host

**Testing**: pytest for backend integration and database connectivity tests

**Target Platform**: Linux server environment with Docker Compose; PostgreSQL service hosted on a Raspberry Pi reachable from the backend runtime

**Project Type**: Web backend infrastructure migration / data platform integration

**Performance Goals**: Stable database connectivity for MVP workloads; support reliable request and pitch persistence with no data loss across Raspberry Pi restarts

**Constraints**: Must use the self-hosted Raspberry Pi Postgres instance; cloud-managed SQL services are prohibited for this feature. Connection settings must be configurable by environment variables. The backend must handle intermittent network availability gracefully.

**Scale/Scope**: Small MVP deployment for a limited trust-first journalist/expert marketplace. The focus is on correct persistence and recovery, not high throughput.

## Constitution Check

*The repository constitution file is authored and active as `.specify/memory/constitution.md`; this plan follows the project's governance principles and should be aligned with those rules.*

- Planning before code: **PASS**. The feature spec and plan artifacts are created under `specs/002-raspi-postgres-data/`.
- Architecture boundaries: **PASS**. This feature targets backend database integration only, without affecting frontend workflows.
- Verification before claiming completion: **PASS**. The plan includes concrete validation steps in `quickstart.md`.
- Security-sensitive workflows: **PASS**. The change is limited to backend storage configuration and connection handling.

No constitution violations are identified that require complexity tracking.

## Project Structure

### Documentation (this feature)

```text
specs/002-raspi-postgres-data/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── database-connection.md
└── spec.md
```

### Source Code (repository root)

```text
backend/
├── app/
│   ├── api/
│   ├── core/
│   │   ├── config.py
│   │   ├── db.py
│   │   └── __init__.py
│   ├── models/
│   ├── schemas/
│   ├── services/
│   └── main.py
├── Dockerfile
├── pyproject.toml
└── tests/

frontend/
# frontend is unaffected by this feature

docker-compose.yml
.env.example
```

**Structure Decision**: Focus this plan on the backend database layer in `backend/app/core/db.py` and `backend/app/core/config.py`, with deployment config in `docker-compose.yml` and environment variables in `.env`.

## Phase 0: Research and design conclusions

### Key decisions

- Keep the existing FastAPI backend and minimal SQLite-backed application model, but add a clean Postgres adapter layer to support the Raspberry Pi host.
- Use environment-driven database settings rather than hard-coded file paths, enabling host, port, database, user, password, and sslmode configuration.
- Use `psycopg[binary]` for direct PostgreSQL connectivity, keeping the DB layer simple and compatible with the current raw SQL approach.

### Risks and mitigation

- Raspberry Pi network reachability is the primary operational risk. Mitigate by documenting expected host discovery and by surfacing clear connection failure diagnostics.
- PostgreSQL version compatibility with the Pi host may differ from desktop/local expectations. Mitigate by avoiding Postgres-specific SQL extensions and using standard SQL types.
- Migration from SQLite to Postgres is non-trivial. Mitigate by keeping the current SQLite schema shape and building a one-time schema migration path or initial table creation script for Postgres.

## Phase 1: Design detail

### Data model summary

The existing application schema is small and already defined in `backend/app/core/db.py` for SQLite. This feature does not introduce new domain entities; it translates the existing schema to PostgreSQL-compatible types and connection handling. Key tables remain:

- `users`
- `email_login_challenges`
- `profiles`
- `verification_submissions`
- `requests`
- `pitches`
- `moderation_actions`

PostgreSQL schema design should preserve the existing fields and constraints while using PostgreSQL serial or identity columns, timestamp types, and appropriate text types.

### API surface summary

There are no planned changes to user-facing application APIs for this feature. The backend routes remain the same and continue to use the existing FastAPI routers. This feature changes only the backend storage driver and connection configuration.

### Deployment and runtime summary

- Add environment variables for PostgreSQL connection: `PG_HOST`, `PG_PORT`, `PG_DATABASE`, `PG_USER`, `PG_PASSWORD`, `PG_SSLMODE`.
- In Docker Compose or local `.env`, configure the backend to connect to the Raspberry Pi Postgres host rather than using `DATABASE_PATH`.
- Keep the SQLite path option for backward compatibility and local testing, but the primary path for this feature is the Raspi Postgres instance.
- Confirm `docker-compose` can start the backend and connect successfully to the remote Pi database.

## Phase 2: Implementation strategy

### Workstreams

1. Add Postgres connection configuration to `backend/app/core/config.py`.
2. Extend or replace the current `backend/app/core/db.py` abstraction to support both SQLite and PostgreSQL connections.
3. Add `psycopg[binary]` to backend dependencies in `backend/pyproject.toml`.
4. Update environment examples and documentation in `.env.example` and `specs/002-raspi-postgres-data/quickstart.md`.
5. Implement table creation and schema compatibility checks for Postgres in the backend startup flow.
6. Add backend tests that verify a Postgres database connection and persistence across a simulated restart.
7. Document the Raspberry Pi Postgres connection contract in `specs/002-raspi-postgres-data/contracts/database-connection.md`.

### Delivery order

1. Connection configuration and environment setup
2. Postgres adapter and schema setup
3. Runtime validation and error handling
4. Persistence verification and recovery tests
5. Documentation and quickstart validation

### Why this order

This order isolates infrastructure changes from the rest of the application. The backend will first gain the ability to talk to Postgres, then verify that schema creation and persistence work, and finally confirm the end-to-end behavior with the Raspberry Pi host.

## Verification Strategy

### Build and test layers

- pytest backend tests for database configuration parsing and connection handling
- integration tests for schema creation on Postgres and basic CRUD flows
- runtime validation during backend startup for connection failures

### Minimum end-to-end flows before completion

1. Backend starts with Raspberry Pi Postgres settings and creates required tables.
2. Backend writes a `users` record and later reads it back from the Raspberry Pi database.
3. Raspberry Pi restarts and the same data remains available after backend reconnects.
4. The backend reports clear, actionable errors when the Raspberry Pi Postgres host is unreachable.

