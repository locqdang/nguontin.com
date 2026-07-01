# NguonTin MVP Task Breakdown

> **For Hermes:** Use subagent-driven-development skill to implement this plan task-by-task.

**Goal:** Break the MVP into small, verifiable phases and tasks that can reasonably be completed within a single chat session.

**Architecture:** Keep the same high-level architecture from the MVP implementation plan: Next.js frontend, FastAPI backend, PostgreSQL, Redis, Celery, Docker Compose, Strapi for content only. Execute in short vertical slices with visible deliverables and real verification after each slice.

**Tech Stack:** Next.js, TypeScript, Tailwind CSS, FastAPI, PostgreSQL, Redis, Celery, Docker Compose, Strapi

---

## 1. How to use this document

This file is not the same as the broad implementation plan.

This file answers a more practical question:
- what can be finished in one chat session
- what should be verified before moving on
- what should be deferred to a later session

### Session-sized rule
Each phase below should be small enough to complete in one focused chat session, including:
- code changes
- local verification
- a short review of changed files

If a phase grows beyond that boundary, split it before implementation.

### Verification rule
A phase is only complete when:
- the requested artifact exists
- the relevant command was actually run
- the output matched the expected result closely enough to trust the slice

---

## 2. Phase overview

1. Phase A: stabilize the current homepage and Compose baseline
2. Phase B: define the domain model and DB schema plan
3. Phase C: scaffold the backend app and health endpoints
4. Phase D: connect frontend and backend in Compose
5. Phase E: add auth data model and password utilities
6. Phase F: implement registration and login API
7. Phase G: build Vietnamese auth screens
8. Phase H: add role-aware profiles
9. Phase I: add verification submission flow
10. Phase J: add admin verification review flow
11. Phase K: add request creation and journalist dashboard
12. Phase L: add expert request browsing and filtering
13. Phase M: add pitch submission and tracking
14. Phase N: add journalist pitch review actions
15. Phase O: add admin moderation basics
16. Phase P: add logging, rate limits, and health hardening
17. Phase Q: add public content plumbing and launch readiness

These phases are ordered. Do not skip ahead unless a later phase is intentionally being used as a spike.

---

## 3. Phase A: stabilize the current homepage and Compose baseline

**Objective:** Turn the current homepage prototype into a clean baseline that can be safely built on.

**Current known state:**
- homepage exists and serves on port `3007`
- frontend is in Next.js
- root `docker-compose.yml` exists
- homepage content is in Vietnamese

**Tasks:**

### Task A1: Clean the current app file set
**Deliverable:** homepage files are intentional and basic project ignores are correct.

**Files:**
- Review: `frontend/app/page.tsx`
- Review: `frontend/app/layout.tsx`
- Review: `frontend/app/globals.css`
- Review: `.gitignore`
- Review: `.dockerignore`

**Verify:**
```bash
git status --short
```
Expected:
- build artifacts and dependencies should not be newly tracked by mistake

### Task A2: Add the logo to the homepage
**Deliverable:** one logo appears cleanly on the homepage.

**Files:**
- Use existing: `logo.png` or `nguontinlogo.png`
- Modify: `frontend/app/page.tsx`
- Possibly create: `frontend/public/...`

**Verify:**
```bash
npm run build
curl -I http://127.0.0.1:3007
```
Expected:
- build passes
- homepage still returns `200 OK`

### Task A3: Make Compose configuration explicit
**Deliverable:** current port and service purpose are documented in config or README.

**Files:**
- Modify: `docker-compose.yml`
- Create or modify: `README.md`

**Verify:**
```bash
docker compose config
```
Expected:
- valid Compose output

**Session exit criteria:**
- homepage is visually acceptable as a placeholder
- Compose setup is valid
- startup instructions are documented

---

## 4. Phase B: define the domain model and DB schema plan

**Objective:** Lock the data model before backend implementation starts.

**Tasks:**

### Task B1: Create the domain model document
**Deliverable:** `tickets/nguontin-mvp-domain-model.md`

**Must define:**
- entities
- fields
- required enums
- relationships
- ownership rules
- Vietnamese-facing content boundaries versus internal English identifiers

**Verify:**
- read back the file and confirm all core entities are covered:
  - User
  - JournalistProfile
  - ExpertProfile
  - VerificationEvidence
  - VerificationReview
  - SourceRequest
  - Pitch
  - AuditEvent
  - ModerationAction

### Task B2: Settle open MVP data decisions
**Deliverable:** explicit decisions recorded in the domain-model doc.

**Decisions to lock:**
- request visibility
- verification evidence format
- whether organizations are MVP or later
- role model shape
- status enums

**Verify:**
- no key data-model decision is left ambiguous if it blocks coding

**Session exit criteria:**
- backend scaffolding can start without guessing table purpose

---

## 5. Phase C: scaffold the backend app and health endpoints

**Objective:** Create a minimal FastAPI backend that runs in Docker Compose.

**Tasks:**

### Task C1: Scaffold backend app structure
**Deliverable:** minimal backend app structure exists.

**Files:**
- Create: `backend/app/main.py`
- Create: `backend/pyproject.toml`
- Create: `backend/app/api/`
- Create: `backend/app/core/`

**Verify:**
```bash
python3 -m py_compile backend/app/main.py
```
Expected:
- no syntax error

### Task C2: Add API health endpoint
**Deliverable:** backend serves a basic health route.

**Verify:**
```bash
curl http://127.0.0.1:<backend-port>/health
```
Expected:
- JSON health response

### Task C3: Add backend service to Compose
**Deliverable:** frontend and backend can be started together.

**Files:**
- Modify: `docker-compose.yml`
- Add backend Dockerfile if needed

**Verify:**
```bash
docker compose up -d --build
docker compose ps
```
Expected:
- frontend up
- backend up

**Session exit criteria:**
- backend container exists and answers `/health`

---

## 6. Phase D: connect frontend and backend in Compose

**Objective:** Prove the frontend can talk to the backend.

**Tasks:**

### Task D1: Add a frontend-visible API status check
**Deliverable:** homepage or a temporary debug block can show backend health.

**Files:**
- Modify: `frontend/app/page.tsx` or a small helper module

**Verify:**
```bash
curl http://127.0.0.1:3007
```
Expected:
- page renders
- backend status is visible or confirmed through server logs

### Task D2: Lock service names and env-file pattern
**Deliverable:** Compose networking convention is fixed early.

**Files:**
- Modify: `docker-compose.yml`
- Create: `.env.example`

**Verify:**
```bash
docker compose config
```
Expected:
- service references resolve correctly

**Session exit criteria:**
- frontend-backend connectivity is proven

---

## 7. Phase E: add auth data model and password utilities

**Objective:** Create the smallest secure auth foundation in the backend.

**Tasks:**

### Task E1: Add user and role schema
**Deliverable:** backend model definitions or migration plan for users and roles.

**Verify:**
- model file exists
- role enum is explicit

### Task E2: Add password hashing utility
**Deliverable:** Argon2 hashing and verification helper.

**Verify:**
```bash
pytest backend/tests -q
```
Expected:
- hashing tests pass

### Task E3: Add auth settings and validation
**Deliverable:** env-driven auth config placeholders exist.

**Verify:**
- app can start with env defaults or documented placeholders

**Session exit criteria:**
- user credentials can be stored securely

---

## 8. Phase F: implement registration and login API

**Objective:** Ship the first usable auth API.

**Tasks:**

### Task F1: Registration endpoint
**Deliverable:** `POST /auth/register`

**Verify:**
```bash
curl -X POST http://127.0.0.1:<backend-port>/auth/register ...
```
Expected:
- success response for valid input

### Task F2: Login endpoint
**Deliverable:** `POST /auth/login`

**Verify:**
```bash
curl -X POST http://127.0.0.1:<backend-port>/auth/login ...
```
Expected:
- token or session response

### Task F3: Current-user endpoint
**Deliverable:** authenticated `GET /me`

**Verify:**
```bash
curl http://127.0.0.1:<backend-port>/me -H 'Authorization: Bearer ...'
```
Expected:
- current user payload

**Session exit criteria:**
- sign-up and sign-in work locally

---

## 9. Phase G: build Vietnamese auth screens

**Objective:** Add Vietnamese UI for registration and login.

**Tasks:**

### Task G1: Registration page
**Deliverable:** Vietnamese sign-up form in frontend.

### Task G2: Login page
**Deliverable:** Vietnamese sign-in form in frontend.

### Task G3: API wiring and error states
**Deliverable:** form submits to backend and shows Vietnamese validation or failure copy.

**Verify:**
```bash
npm run build
curl -I http://127.0.0.1:3007/login
curl -I http://127.0.0.1:3007/register
```
Expected:
- routes build and return `200 OK`

**Session exit criteria:**
- a user can register and log in from the UI in Vietnamese

---

## 10. Phase H: add role-aware profiles

**Objective:** Let users create journalist or expert profiles.

**Tasks:**

### Task H1: Journalist profile backend shape
### Task H2: Expert profile backend shape
### Task H3: Vietnamese profile forms in frontend
### Task H4: Ownership checks for self-edit only

**Verify:**
- API tests pass for self-update and forbidden cross-user update
- UI forms load and submit

**Session exit criteria:**
- each role can create and edit its own profile

---

## 11. Phase I: add verification submission flow

**Objective:** Let users submit verification evidence.

**Tasks:**

### Task I1: Verification evidence model and endpoint
### Task I2: Vietnamese verification submission UI
### Task I3: Verification status display in profile/dashboard

**Verify:**
- a user can submit verification evidence
- pending status is visible in UI

**Session exit criteria:**
- verification submission works end to end

---

## 12. Phase J: add admin verification review flow

**Objective:** Let admins review and decide verification submissions.

**Tasks:**

### Task J1: Admin verification list API
### Task J2: Approve and reject actions
### Task J3: Vietnamese admin review page
### Task J4: Public-safe verification method display

**Verify:**
- admin can approve or reject
- approved method labels show without leaking sensitive evidence

**Session exit criteria:**
- trust workflow for verification is operational

---

## 13. Phase K: add request creation and journalist dashboard

**Objective:** Let journalists create and manage source requests.

**Tasks:**

### Task K1: Source request model and migration
### Task K2: Create request API
### Task K3: Journalist dashboard list API
### Task K4: Vietnamese request creation form
### Task K5: Request detail and close action

**Verify:**
- journalist can create request
- journalist sees own request list
- request can be closed

**Session exit criteria:**
- journalist workflow is useful on its own

---

## 14. Phase L: add expert request browsing and filtering

**Objective:** Let experts discover open requests.

**Tasks:**

### Task L1: Open request listing API
### Task L2: Basic search and filter support
### Task L3: Vietnamese expert browse page
### Task L4: Request detail page for experts

**Verify:**
- expert can view only appropriate open requests
- search and filter behavior works on sample data

**Session exit criteria:**
- experts can find opportunities without admin help

---

## 15. Phase M: add pitch submission and tracking

**Objective:** Let experts submit and track pitches through the platform inbox flow.

**Tasks:**

### Task M1: Pitch model and status enum
### Task M2: Submit pitch API
### Task M3: Expert pitch list API
### Task M4: Vietnamese pitch submission UI

**Verify:**
- expert submits a pitch
- expert sees pitch status as pending

**Session exit criteria:**
- platform inbox loop begins to function

---

## 16. Phase N: add journalist pitch review actions

**Objective:** Let journalists review, accept, and reject pitches.

**Tasks:**

### Task N1: Request-owner pitch list API
### Task N2: Accept pitch action
### Task N3: Reject pitch action
### Task N4: Vietnamese pitch review UI

**Verify:**
- journalist can accept or reject only pitches on owned requests
- expert sees updated status

**Session exit criteria:**
- core journalist-expert loop works end to end

---

## 17. Phase O: add admin moderation basics

**Objective:** Give admins enough controls for a small real launch.

**Tasks:**

### Task O1: Moderation action model
### Task O2: Moderate user/request/pitch endpoints
### Task O3: Basic admin overview counts
### Task O4: Vietnamese admin moderation screens

**Verify:**
- moderation actions are recorded
- hidden or flagged content behaves as expected

**Session exit criteria:**
- admins can handle obvious abuse and low-quality content

---

## 18. Phase P: add logging, rate limits, and health hardening

**Objective:** Add the minimum operational guardrails for real usage.

**Tasks:**

### Task P1: Structured backend logging
### Task P2: Auth and submission rate limiting
### Task P3: Audit logging for verification and moderation
### Task P4: Compose health checks

**Verify:**
- rate-limited endpoints reject abuse attempts correctly
- health endpoints still pass
- important actions generate logs without leaking secrets

**Session exit criteria:**
- the app is debuggable and safer under real use

---

## 19. Phase Q: add public content plumbing and launch readiness

**Objective:** Prepare the site for a public MVP launch without bloating the app.

**Tasks:**

### Task Q1: Decide whether Strapi is needed before launch
### Task Q2: Add FAQ/about pages or placeholder content routes in Vietnamese
### Task Q3: Add production-shaped Compose overrides
### Task Q4: Add launch checklist and smoke-test commands

**Verify:**
```bash
docker compose config
npm run build
curl -I http://127.0.0.1:3007
```
Expected:
- production-shaped config is valid
- site still builds and serves

**Session exit criteria:**
- MVP has a credible public surface and deploy path

---

## 20. Recommended first implementation order from today

Given the current repo state, the best next sessions are:

1. **Phase A**: stabilize homepage baseline
2. **Phase B**: create the domain model document
3. **Phase C**: scaffold backend and health endpoint
4. **Phase D**: connect frontend and backend in Compose
5. **Phase E** and **Phase F**: auth foundation and API

That order gives a visible product plus a real backend foundation without overcommitting to too many features at once.

---

## 21. What should not be attempted in one session

Avoid combining these into one chat session:
- full auth backend plus frontend auth screens plus profile flows
- full request workflow plus pitch workflow plus admin moderation
- Strapi setup plus backend auth plus deployment hardening
- Redis/Celery integration before the basic synchronous workflow exists

Those are multi-session chunks and should stay split.

---

## 22. Definition of done for each session

Before ending a session, check all of these:
- the session goal is visible in code or docs
- the relevant command was actually run
- the output was checked, not assumed
- the changed files are listed for review
- the next session starts from a cleaner state than before

---

## 23. Next planning artifacts after this file

After this breakdown exists, the next best planning artifact is:
- `tickets/nguontin-mvp-domain-model.md`

Then implementation can start with Phase A or Phase B, depending on whether you want to polish the public surface first or lock the data model first.
