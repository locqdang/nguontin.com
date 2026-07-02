# Tasks: NguonTin MVP

**Input**: Design documents from `/specs/001-nguontin-mvp/`

**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`

**Tests**: Include focused backend, frontend, and E2E verification for each implemented slice because the spec explicitly requires independently testable user journeys.

**Organization**: Tasks are grouped by shared setup, shared foundations, and then by user story so each story can be implemented and validated as its own increment.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel, different files and no direct dependency
- **[Story]**: `SETUP`, `FOUND`, `US1`, `US2`, `US3`, or `POLISH`
- Every task includes exact file paths where practical

## Path Conventions

- **Frontend**: `frontend/`
- **Backend**: `backend/`
- **Infrastructure**: `infra/` or root Compose files if the repo still uses them
- **Planning docs**: `specs/001-nguontin-mvp/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Establish the repo structure, documentation paths, and runnable local baseline for the MVP.

- [ ] T001 [SETUP] Confirm canonical planning files exist under `specs/001-nguontin-mvp/`: `spec.md`, `plan.md`, `data-model.md`, `tasks.md`, `quickstart.md`, `research.md`
- [ ] T002 [SETUP] Align repository documentation in `README.md` so `specs/001-nguontin-mvp/` is the canonical planning location
- [ ] T003 [P] [SETUP] Review `.gitignore`, `.dockerignore`, and env-file handling so generated files, caches, and local secrets are not tracked
- [ ] T004 [SETUP] Standardize the repo layout for `frontend/`, `backend/`, and Docker Compose entry points based on the approved plan
- [ ] T005 [P] [SETUP] Verify the current homepage and Compose baseline still build or configure cleanly with `npm run build` in `frontend/` and `docker compose config` from repo root

**Checkpoint**: The repo has a stable documented starting point and the planning artifacts are canonical.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Create the shared platform pieces that every user story depends on.

**⚠️ CRITICAL**: No user story work should start until these foundations are in place.

- [ ] T006 [FOUND] Finalize `specs/001-nguontin-mvp/data-model.md` as the locked source for entities, enums, ownership rules, and visibility rules
- [ ] T007 [P] [FOUND] Scaffold backend application structure under `backend/app/` and backend tests under `backend/tests/`
- [ ] T008 [P] [FOUND] Scaffold or confirm frontend app structure for authenticated app routes and shared UI under `frontend/app/`
- [ ] T009 [FOUND] Add base environment documentation in `.env.example` for frontend, backend, auth, database, Redis, and SSO settings
- [ ] T010 [FOUND] Add Docker Compose service definitions for frontend, backend, PostgreSQL, Redis, and worker in the chosen Compose files
- [ ] T011 [P] [FOUND] Add backend health endpoint and startup validation in `backend/app/main.py`
- [ ] T012 [P] [FOUND] Establish backend testing baseline, for example `pytest` config and a first smoke test in `backend/tests/`
- [ ] T013 [P] [FOUND] Establish frontend verification baseline, including build and any existing smoke or route tests in `frontend/`
- [ ] T014 [FOUND] Add shared auth and authorization primitives in backend code, including user identity, role mapping, and current-user resolution
- [ ] T015 [FOUND] Add shared logging and request-correlation baseline in backend code without leaking secrets or private evidence

**Checkpoint**: Frontend and backend foundations exist, compose wiring is valid, and the app is ready for independent user-story implementation.

---

## Phase 3: User Story 1 - Journalist creates and manages a source request (Priority: P1) 🎯 MVP

**Goal**: Let a journalist sign in, create a profile, create a request, and manage pitches on owned requests.

**Independent Test**: Sign in as a journalist, create a journalist profile, create a request, view it in the journalist dashboard, and accept or reject a pitch tied to that owned request.

### Tests for User Story 1

- [ ] T016 [P] [US1] Add backend auth and ownership tests for journalist-only request management in `backend/tests/`
- [ ] T017 [P] [US1] Add backend API tests for journalist profile and request routes in `backend/tests/`
- [ ] T018 [P] [US1] Add frontend route or component coverage for journalist profile and request creation screens in `frontend/`

### Implementation for User Story 1

- [ ] T019 [P] [US1] Implement journalist profile persistence using `JournalistProfile` model, schema, and service files under `backend/app/models/`, `backend/app/schemas/`, and `backend/app/services/`
- [ ] T020 [US1] Implement journalist profile API routes under `backend/app/api/`
- [ ] T021 [P] [US1] Implement `SourceRequest` model, schema, and service files under `backend/app/models/`, `backend/app/schemas/`, and `backend/app/services/`
- [ ] T022 [US1] Implement journalist request CRUD and close routes under `backend/app/api/`
- [ ] T023 [US1] Add journalist dashboard query or service support for owned requests in backend code
- [ ] T024 [US1] Build Vietnamese journalist profile UI under `frontend/app/`
- [ ] T025 [US1] Build Vietnamese request creation, request detail, and journalist dashboard UI under `frontend/app/`
- [ ] T026 [US1] Enforce journalist request ownership server-side and reflect forbidden states clearly in UI
- [ ] T027 [US1] Add audit logging for journalist request creation, update, and close actions in backend code

**Checkpoint**: A journalist can independently use the platform to create and manage requests.

---

## Phase 4: User Story 2 - Expert discovers requests and submits a pitch (Priority: P2)

**Goal**: Let an expert sign in, create a profile, browse relevant open requests, submit one platform-managed pitch, and track that pitch’s status.

**Independent Test**: Sign in as an expert, create an expert profile, browse open requests, submit one pitch to a request, and verify the pending status is visible.

### Tests for User Story 2

- [ ] T028 [P] [US2] Add backend tests for expert profile ownership, request visibility, and duplicate-pitch prevention in `backend/tests/`
- [ ] T029 [P] [US2] Add backend API tests for open-request browsing and pitch submission in `backend/tests/`
- [ ] T030 [P] [US2] Add frontend route or integration coverage for expert browse and pitch flows in `frontend/`

### Implementation for User Story 2

- [ ] T031 [P] [US2] Implement expert profile persistence using `ExpertProfile` model, schema, and service files under `backend/app/models/`, `backend/app/schemas/`, and `backend/app/services/`
- [ ] T032 [US2] Implement expert profile API routes under `backend/app/api/`
- [ ] T033 [US2] Implement authenticated-expert request browse, search, and filter routes under `backend/app/api/`
- [ ] T034 [P] [US2] Implement `Pitch` model, schema, service, and status rules under `backend/app/models/`, `backend/app/schemas/`, and `backend/app/services/`
- [ ] T035 [US2] Implement pitch submission and expert pitch-list routes under `backend/app/api/`
- [ ] T036 [US2] Build Vietnamese expert profile UI under `frontend/app/`
- [ ] T037 [US2] Build Vietnamese expert request browse, request detail, and pitch submission UI under `frontend/app/`
- [ ] T038 [US2] Build expert pitch status UI under `frontend/app/`
- [ ] T039 [US2] Add audit logging for pitch submission, withdrawal, and status-view-critical transitions in backend code

**Checkpoint**: The expert can independently discover requests and create a pitch, which gives the product its first marketplace response loop.

---

## Phase 5: User Story 3 - Admin reviews verification and moderates trust-sensitive flows (Priority: P3)

**Goal**: Let users submit verification evidence and let admins review it, record append-only decisions, and moderate trust-sensitive records.

**Independent Test**: Submit verification evidence as a normal user, review it as an admin, approve or reject it, confirm a public-safe verification label appears, and record at least one moderation action.

### Tests for User Story 3

- [ ] T040 [P] [US3] Add backend tests for verification evidence intake, admin-only review actions, and moderation permissions in `backend/tests/`
- [ ] T041 [P] [US3] Add backend API tests for verification queues, approve or reject actions, and moderation endpoints in `backend/tests/`
- [ ] T042 [P] [US3] Add frontend route or integration coverage for verification submission and admin review flows in `frontend/`

### Implementation for User Story 3

- [ ] T043 [P] [US3] Implement `VerificationEvidence` model, schema, and service files under `backend/app/models/`, `backend/app/schemas/`, and `backend/app/services/`
- [ ] T044 [P] [US3] Implement append-only `VerificationReview` model, schema, and service files under `backend/app/models/`, `backend/app/schemas/`, and `backend/app/services/`
- [ ] T045 [P] [US3] Implement `ModerationAction` model, schema, and service files under `backend/app/models/`, `backend/app/schemas/`, and `backend/app/services/`
- [ ] T046 [US3] Implement user verification submission routes under `backend/app/api/`
- [ ] T047 [US3] Implement admin verification queue, approve, and reject routes under `backend/app/api/`
- [ ] T048 [US3] Implement moderation endpoints for users, requests, pitches, and verification records under `backend/app/api/`
- [ ] T049 [US3] Build Vietnamese verification submission UI for journalist and expert flows under `frontend/app/`
- [ ] T050 [US3] Build admin verification and moderation UI under `frontend/app/`
- [ ] T051 [US3] Render public-safe verification labels in relevant frontend profile or trust surfaces
- [ ] T052 [US3] Add audit logging for verification decisions and moderation actions in backend code

**Checkpoint**: Trust and moderation workflows are operational, which makes the MVP’s differentiation real rather than aspirational.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Complete the operational, legal, and launch-readiness work that touches multiple stories.

- [ ] T053 [POLISH] Add or finalize legal routes and Vietnamese public content for Privacy Policy and Terms of Service in `frontend/app/` or the agreed content system
- [ ] T054 [POLISH] Add stable sitewide links to legal pages and any launch-critical public content
- [ ] T055 [POLISH] Verify Google OAuth launch prerequisites, if Google is in the enabled launch set
- [ ] T056 [POLISH] Add auth and trust-sensitive endpoint rate limiting in backend code
- [ ] T057 [POLISH] Add or refine structured logging and health checks across frontend, backend, and Compose services
- [ ] T058 [POLISH] Add worker or async job wiring only for MVP-critical notifications or reminders
- [ ] T059 [POLISH] Add or refine Playwright E2E coverage for the main journalist, expert, and admin workflows
- [ ] T060 [POLISH] Update `specs/001-nguontin-mvp/quickstart.md`, `README.md`, and launch or smoke-test instructions to reflect the final runnable MVP path

**Checkpoint**: The MVP has a credible public surface, launch-required legal pages, and enough observability to operate safely.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies
- **Foundational (Phase 2)**: Depends on setup, blocks all user stories
- **User Story 1 (Phase 3)**: Depends on foundational work
- **User Story 2 (Phase 4)**: Depends on foundational work, benefits from US1 request creation being available
- **User Story 3 (Phase 5)**: Depends on foundational work, and should be integrated before any real launch
- **Polish (Phase 6)**: Depends on whichever user stories are intended for the first release

### User Story Dependencies

- **US1** creates the first independently valuable workflow and should land first
- **US2** depends on request entities and open-request visibility rules established by US1
- **US3** can begin after foundations, but verification and moderation should be wired before broad testing or launch

### Within Each User Story

- Tests first where practical
- Models and schemas before services
- Services before API routes
- Backend behavior before frontend integration
- Verification before claiming a story complete

### Parallel Opportunities

- Setup hygiene tasks marked `[P]`
- Foundational backend or frontend scaffolding tasks that do not touch the same files
- Test-writing tasks within a user story
- Model or schema tasks inside the same story when they target separate files

---

## Parallel Example: Early Story Work

```text
T016 Backend auth and ownership tests for journalist request management
T017 Backend API tests for journalist profile and request routes
T018 Frontend route or component coverage for journalist flows

T019 Journalist profile persistence implementation
T021 SourceRequest model and service implementation
```

---

## Implementation Strategy

### MVP First

1. Complete Setup
2. Complete Foundational work
3. Complete User Story 1
4. Stop and validate the journalist-only workflow end to end

### Incremental Delivery

1. Setup + Foundational
2. User Story 1, journalist request loop
3. User Story 2, expert browse and pitch loop
4. User Story 3, admin trust and moderation loop
5. Polish only after the core loop is real

### What should not be bundled into one session

- Full auth backend, frontend auth UI, profiles, verification, and moderation all at once
- Full request workflow plus expert browse plus admin tools in one unverified jump
- Strapi launch prep plus backend auth plus infra hardening in the same slice
- Redis or Celery overbuild before the synchronous marketplace loop works end to end

---

## Notes

- Keep user-facing product copy in Vietnamese, keep planning and code artifacts in English
- Keep Strapi content-only
- Keep direct-contact support as a product direction, not the first implementation path
- Preserve auditability for verification, moderation, and pitch-state transitions
- Prefer small slices that can be built, tested, and reviewed in one session
