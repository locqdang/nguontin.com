# Tasks: Raspberry Pi PostgreSQL Data Platform

**Input**: Design documents from `/specs/002-raspi-postgres-data/`

**Prerequisites**: `spec.md`, `plan.md`, `research.md`, `data-model.md`, `contracts/`

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Prepare backend dependencies, environment configuration, and Docker Compose deployment for the Raspberry Pi Postgres data platform.

- [ ] T001 [P] Update `backend/pyproject.toml` to add `psycopg[binary]` as a backend dependency for PostgreSQL support.
- [ ] T002 [P] Add Raspberry Pi Postgres environment variables to `.env.example`: `PG_HOST`, `PG_PORT`, `PG_DATABASE`, `PG_USER`, `PG_PASSWORD`, `PG_SSLMODE`.
- [ ] T003 [P] Verify `docker-compose.yml` passes the Postgres environment variables into the `backend` service and document the required self-hosted deployment setup.
- [ ] T004 [P] Create or update `specs/002-raspi-postgres-data/contracts/database-connection.md` to define the runtime Postgres connection contract.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Implement the core backend storage configuration, connection selection, and schema initialization logic before any user story can be validated.

- [ ] T005 Implement Postgres connection configuration in `backend/app/core/config.py`, including environment-driven fallback logic for SQLite if Postgres settings are absent.
- [ ] T006 Extend `backend/app/core/db.py` to support both SQLite and PostgreSQL connections and to select the correct adapter at runtime.
- [ ] T007 Implement Postgres schema creation and compatibility checks in `backend/app/core/db.py` for the Raspberry Pi database on backend startup.
- [ ] T008 Add clear diagnostic logging and failure messages for unreachable Raspberry Pi Postgres connections in `backend/app/core/db.py` and `backend/app/main.py` startup flow.
- [ ] T009 Add unit tests in `backend/tests/` for Postgres config parsing, adapter selection, and connection failure diagnostics.
- [ ] T010 Update `specs/002-raspi-postgres-data/quickstart.md` with the new Postgres deployment prerequisites and local development guidance.

---

## Phase 3: User Story 1 - Connect application to a self-hosted Raspberry Pi database (Priority: P1)

**Goal**: Enable the backend to connect to the self-hosted Raspberry Pi PostgreSQL instance and persist application data.

**Independent Test**: Start the backend with the Raspberry Pi Postgres settings, write data through the app, and verify the same data is stored in the Raspberry Pi database.

### Implementation

- [ ] T011 [US1] Implement runtime Postgres connectivity in `backend/app/core/db.py` and ensure the backend can open a PostgreSQL session using Raspberry Pi settings.
- [ ] T012 [US1] Update `backend/app/main.py` to initialize the database via the Postgres adapter during startup.
- [ ] T013 [US1] Add an integration test in `backend/tests/test_db_postgres.py` that connects to a Postgres instance, creates a table, inserts a row, and reads it back.
- [ ] T014 [US1] Verify the backend can use the Raspberry Pi database without changing frontend behavior by running `docker compose up --build backend` and validating `/health`.
- [ ] T015 [US1] Document the Postgres connection setup in `README.md` or `specs/002-raspi-postgres-data/quickstart.md` as the primary data path for local and deployed environments.

---

## Phase 4: User Story 2 - Recover application data after Raspberry Pi reboot (Priority: P2)

**Goal**: Ensure the self-hosted Raspberry Pi Postgres data persists across Pi restarts and the backend recovers cleanly.

**Independent Test**: Write data, reboot or restart the Raspberry Pi Postgres instance, reconnect the backend, and verify the data remains available.

- [ ] T016 [US2] Implement backend behavior for connection retries, clear error reporting, and recovery after temporary Postgres outages in `backend/app/core/db.py`.
- [ ] T017 [US2] Add an integration test that simulates Postgres unavailability and verifies the backend reports an actionable failure and recovers when the database becomes reachable again.
- [ ] T018 [US2] Document the recovery and reboot procedure in `specs/002-raspi-postgres-data/quickstart.md`.
- [ ] T019 [US2] Ensure the Postgres adapter does not corrupt partially committed data during intermittent network failures.

---

## Phase 5: User Story 3 - Enable local development against the Raspberry Pi Postgres instance (Priority: P3)

**Goal**: Make the self-hosted Raspberry Pi Postgres instance usable for local development without additional cloud services.

**Independent Test**: Start the app locally against the Raspberry Pi Postgres host and verify that data written by the app is stored on the self-hosted instance.

- [ ] T020 [US3] Add local development guidance to `.env.local` usage in `README.md` and `specs/002-raspi-postgres-data/quickstart.md` so developers can connect to the Pi host.
- [ ] T021 [US3] Add a dev-mode integration test that validates local environment variable overrides can target the Raspberry Pi Postgres instance.
- [ ] T022 [US3] Verify Docker Compose deployment and local development both use the same connection model for Raspberry Pi Postgres.
- [ ] T023 [US3] Confirm `backend/pyproject.toml` and `backend/requirements` reflect the Postgres driver dependency for local and deployed environments.

---

## Phase N: Polish & Cross-Cutting Concerns

**Purpose**: Clean up code readability, ensure test-driven implementation, and validate operational documentation.

- [ ] T024 [P] [Polish] Review `backend/app/core/config.py` and `backend/app/core/db.py` for readability and add intent comments where non-obvious decisions were made.
- [ ] T025 [P] [Polish] Run `pytest` for backend integration tests and ensure all Postgres-related test cases pass.
- [ ] T026 [P] [Polish] Validate `specs/002-raspi-postgres-data/quickstart.md` end-to-end by following the documented Raspberry Pi Postgres setup steps.
- [ ] T027 [P] [Polish] Update `README.md` to include Docker Compose guidance for connecting to a self-hosted Raspberry Pi PostgreSQL instance.
- [ ] T028 [P] [Polish] Ensure the feature contract in `specs/002-raspi-postgres-data/contracts/database-connection.md` remains consistent with implementation and docs.

---

## Dependencies & Execution Order

- **Phase 1**: Setup tasks can start immediately and run in parallel.
- **Phase 2**: Foundational tasks block all user stories and must complete before Phase 3.
- **Phase 3+**: User stories can proceed after foundational work is complete.
- **Polish**: Final cleanup and documentation validation should occur after all user stories are implemented.
