# NguonTin MVP Implementation Plan

> **For Hermes:** Use subagent-driven-development skill to implement this plan task-by-task.

**Goal:** Build a first working NguonTin MVP that allows journalists to create source requests, experts to browse and pitch through the platform, and admins to review verification and moderate trust-sensitive workflows.

**Architecture:** Use a separated app architecture: Next.js for the user-facing web app, FastAPI for application APIs and workflow logic, PostgreSQL as the source of truth for all app data, Redis plus Celery for background jobs, and Strapi only for marketing and content pages. Deploy the full stack with Docker Compose, using environment-specific Compose files or overrides for local development and production. Build the MVP in vertical slices, starting with the core data model and auth, then profile and verification, then requests and pitches, then admin moderation and operational hardening.

**Tech Stack:** Next.js, TypeScript, Tailwind CSS, FastAPI, PostgreSQL, Redis, Celery, JWT auth, Argon2, Docker Compose, Strapi

---

## 1. Purpose of this plan

This document translates the approved MVP spec into an implementation sequence.

It is intentionally focused on:
- delivery order
- architectural boundaries
- module and service responsibilities
- verification and test expectations
- rollout dependencies
- what to build now versus later

It is not yet the bite-sized task list. That should be created after this plan is reviewed.

## 2. MVP implementation strategy

Build the MVP in this order:

1. establish repo structure and local development workflow
2. define the domain model and database schema first
3. implement authentication and role-aware access control
4. implement user profiles and verification evidence submission
5. implement journalist request creation and management
6. implement expert browsing and platform inbox pitch submission
7. implement journalist pitch review actions
8. implement admin verification and moderation tools
9. add operational basics: audit logging, health checks, rate limits, async jobs
10. add content system and final Docker Compose deployment wiring needed for MVP launch

This order reduces wasted UI work and keeps trust-sensitive workflows grounded in a stable backend model.

## 3. Proposed repository structure

The repo is almost empty now, so the MVP should standardize structure early.

```text
nguontin.com/
├─ tickets/
│  ├─ nguontin-mvp-spec.md
│  ├─ nguontin-mvp-implementation-plan.md
│  ├─ nguontin-mvp-domain-model.md
│  └─ nguontin-mvp-tasks.md
├─ frontend/
│  ├─ src/
│  ├─ public/
│  ├─ tests/
│  └─ package.json
├─ backend/
│  ├─ app/
│  │  ├─ api/
│  │  ├─ core/
│  │  ├─ db/
│  │  ├─ models/
│  │  ├─ schemas/
│  │  ├─ services/
│  │  ├─ tasks/
│  │  └─ main.py
│  ├─ tests/
│  └─ pyproject.toml
├─ cms/
│  └─ strapi/ or docker wiring only
├─ infra/
│  ├─ docker/
│  ├─ nginx/
│  └─ scripts/
├─ .env.example
├─ .gitignore
└─ README.md
```

This keeps app code and content concerns separate from day one.

## 4. Architecture boundaries

### 4.1 Frontend responsibilities
The Next.js app should handle:
- landing and marketing pages, unless served separately via Strapi-driven content routes
- auth screens and authenticated app shell
- journalist dashboard screens
- expert browsing and pitch screens
- admin interface screens, if not split into a separate admin app
- client-side form handling and validation
- server calls to the FastAPI backend

The frontend should not own core business rules. It should not decide verification status, permissions, reputation calculations, or moderation outcomes.

### 4.2 Backend responsibilities
The FastAPI backend should handle:
- authentication and token issuance
- role-aware authorization
- profile storage and verification workflows
- request CRUD and workflow rules
- pitch submission and status transitions
- audit logging and moderation actions
- async job orchestration triggers
- reputation-event recording, if the MVP starts storing those events

### 4.3 Database responsibility
PostgreSQL should be the system of record for:
- users
- roles
- journalist profiles
- expert profiles
- organizations, if included in MVP one
- verification evidence and verification decisions
- requests
- pitches
- moderation actions
- workflow and audit events

### 4.4 Redis and Celery responsibility
Use Redis and Celery only for async work that actually helps the MVP, such as:
- verification notification emails
- request deadline reminders
- moderation queue notifications
- spam-check jobs
- future digest jobs

Do not overbuild job types before the first workflow works end to end.

### 4.5 Strapi responsibility
Strapi should be limited to:
- blog
- FAQ
- landing pages
- docs
- SEO content

Do not put requests, pitches, user verification, or reputation into Strapi.

## 5. MVP scope decisions for implementation

To keep MVP one shippable, the implementation should make these practical scope decisions.

### 5.1 Authentication scope
Implement first:
- email and password auth
- JWT-based authenticated sessions or API access
- role support for journalist, expert, and admin

Defer until later unless clearly needed before launch:
- Google OAuth
- Facebook OAuth
- LinkedIn OAuth

Reason: these providers add setup and edge cases, but do not prove the core marketplace workflow.

### 5.2 Verification scope
Implement first:
- verification submission workflow
- ability to attach verification methods and evidence links or files
- admin review queue
- approve and reject decisions
- public display of verification method labels only

Do not implement first:
- deep automated third-party verification integrations
- complicated weighted trust scoring
- full public trust analytics

### 5.3 Request workflow scope
Implement first:
- create request
- edit request
- close request
- list own requests for journalists
- request detail page
- request browse/search/filter for experts

Keep request fields limited to the approved MVP set.

### 5.4 Pitch workflow scope
Implement first:
- expert submits pitch through NguonTin inbox workflow
- pitch status values: pending, accepted, rejected, withdrawn, request_closed
- journalist can review pitches on owned requests
- journalist can accept or reject pitches
- expert can track pitch status on their dashboard

Defer direct email automation for MVP one. The product can describe direct-contact support as an allowed workflow direction, but the first implemented version should focus on platform inbox flow because that is where the trust and operational value lives.

### 5.5 Admin scope
Implement first:
- pending verification queue
- simple user moderation actions
- request moderation actions
- pitch moderation actions
- basic operational dashboard counts

Defer advanced analytics, BI, and moderation automation.

## 6. Proposed domain model planning work

Before coding the app, create `tickets/nguontin-mvp-domain-model.md`.

That domain-model document should finalize these entities.

### 6.1 Core entities
- User
- UserRole or role mapping
- JournalistProfile
- ExpertProfile
- Organization, only if needed in MVP one
- VerificationEvidence
- VerificationReview
- SourceRequest
- Pitch
- AuditEvent
- ModerationAction
- ReputationEvent, optional but recommended as an event table even if public scoring is minimal

### 6.2 Recommended early enum sets
- user_role: journalist, expert, admin
- verification_status: not_started, pending, approved, rejected
- request_status: draft, open, closed, archived
- pitch_status: pending, accepted, rejected, withdrawn, request_closed
- moderation_target_type: user, request, pitch, verification
- moderation_action_type: approve, reject, flag, suspend, hide, restore

### 6.3 Recommended design rule
Prefer append-only event records for auditability on sensitive workflows such as:
- verification decisions
- pitch status changes
- moderation actions

This will help later trust, analytics, and dispute resolution.

## 7. API design plan

The backend should be built around workflow-first API groups.

### 7.1 Auth APIs
Examples:
- `POST /auth/register`
- `POST /auth/login`
- `POST /auth/refresh` if refresh tokens are used
- `POST /auth/logout`
- `GET /me`

### 7.2 Profile APIs
Examples:
- `GET /profiles/me`
- `PATCH /profiles/journalist`
- `PATCH /profiles/expert`
- `POST /profiles/verification-evidence`
- `GET /profiles/verification-status`

### 7.3 Request APIs
Examples:
- `POST /requests`
- `GET /requests`
- `GET /requests/{request_id}`
- `PATCH /requests/{request_id}`
- `POST /requests/{request_id}/close`
- `GET /journalists/me/requests`

### 7.4 Pitch APIs
Examples:
- `POST /requests/{request_id}/pitches`
- `GET /experts/me/pitches`
- `GET /journalists/me/requests/{request_id}/pitches`
- `POST /pitches/{pitch_id}/accept`
- `POST /pitches/{pitch_id}/reject`
- `POST /pitches/{pitch_id}/withdraw`

### 7.5 Admin APIs
Examples:
- `GET /admin/verifications`
- `POST /admin/verifications/{verification_id}/approve`
- `POST /admin/verifications/{verification_id}/reject`
- `GET /admin/moderation/requests`
- `GET /admin/moderation/pitches`
- `POST /admin/moderation/actions`
- `GET /admin/metrics/overview`

These are examples, not final locked routes. The route style should be standardized before implementation starts.

## 8. Frontend route plan

The frontend should be organized by user workflow, not by raw entity names alone.

### 8.1 Public routes
- `/`
- `/about`
- `/faq`
- `/blog`
- `/login`
- `/register`

### 8.2 Journalist app routes
- `/app/journalist/dashboard`
- `/app/journalist/requests`
- `/app/journalist/requests/new`
- `/app/journalist/requests/[id]`
- `/app/journalist/pitches` or pitch list under each request
- `/app/journalist/profile`
- `/app/journalist/verification`

### 8.3 Expert app routes
- `/app/expert/dashboard`
- `/app/expert/requests`
- `/app/expert/requests/[id]`
- `/app/expert/pitches`
- `/app/expert/profile`
- `/app/expert/verification`

### 8.4 Admin routes
- `/app/admin/dashboard`
- `/app/admin/verifications`
- `/app/admin/requests`
- `/app/admin/pitches`
- `/app/admin/users`
- `/app/admin/moderation`

## 9. Logging and observability plan

The MVP should include structured logging from the beginning, especially because trust workflows and moderation decisions matter.

### 9.1 Log categories
At minimum log:
- auth failures and suspicious auth activity
- request creation, edits, and closure
- pitch submissions and status transitions
- verification submissions and decisions
- admin moderation actions
- background job failures
- API validation failures where useful

### 9.2 Never log
Do not log:
- passwords
- raw verification documents
- raw JWTs
- sensitive uploaded file contents
- personal contact details beyond what is operationally necessary

### 9.3 Operational baseline
The MVP should include:
- API health endpoint
- frontend readiness check if deployed behind reverse proxy
- structured logs in app containers
- basic error correlation strategy, even if simple request IDs only

## 10. Security implementation plan

Security is part of MVP, not polish.

### 10.1 Must-have controls
- Argon2 password hashing
- server-side role and ownership checks
- input validation on all write endpoints
- file type and size validation for verification uploads
- rate limiting on auth and sensitive submission endpoints
- audit records for admin and verification decisions
- safe CORS and cookie or token handling based on final auth design

### 10.2 Security-sensitive workflows to test explicitly
- one user cannot edit another user's profile
- one journalist cannot manage another journalist's requests
- one expert cannot see private admin data
- only request owners can accept or reject pitches on that request
- only admins can approve or reject verification evidence

## 11. Testing strategy plan

Testing should be layered.

### 11.1 Backend tests
Include:
- unit tests for workflow helpers and permission logic
- API tests for auth, profiles, requests, pitches, and admin routes
- DB-backed integration tests for state transitions

### 11.2 Frontend tests
Include:
- component tests for high-risk forms if chosen
- route-level or integration tests for key user flows
- end-to-end tests for core journeys after the basic app exists

### 11.3 Minimum end-to-end flows to verify before MVP release
1. journalist registers, creates profile, submits verification, creates request
2. expert registers, creates profile, submits verification, browses requests, submits pitch
3. journalist reviews pitch and accepts or rejects it
4. admin reviews verification and performs a moderation action

## 12. Infrastructure and local development plan

### 12.1 Deployment model
Use Docker Compose as the standard orchestration and deployment model for the full MVP stack.

That means:
- local development should run through Docker Compose
- production deployment should run through Docker Compose
- services should be defined once, then adapted with environment-specific Compose files, overrides, env files, and secrets handling

The core stack should include at least:
- frontend
- backend
- postgres
- redis
- worker

Optional but expected for launch-ready deployment:
- nginx
- strapi
- cloudflared, if it remains part of the chosen deployment path

Strapi may be added in the first infra pass or later, depending on whether content pages matter before core workflow validation.

### 12.2 Recommended infra files
- `infra/docker/docker-compose.yml`
- `infra/docker/docker-compose.dev.yml`
- `infra/docker/docker-compose.prod.yml`
- `infra/nginx/`
- `infra/scripts/`
- project root `.env.example`

### 12.3 Compose design priority
The first Compose setup should optimize for fast local iteration while preserving a clear path to production deployment.

Recommended approach:
- keep one shared base Compose file for common services
- use a development override for hot reload, local ports, and relaxed dev settings
- use a production override for stable images, restart policies, reverse proxy integration, health checks, and persistent volumes
- avoid maintaining completely separate stack definitions unless the environments truly diverge

## 13. Delivery phases

### Phase 0: Planning completion
Deliverables:
- MVP spec approved
- MVP implementation plan approved
- MVP domain model doc created
- MVP task breakdown doc created

Exit criteria:
- the first build slice is clear enough that coding can begin without major architecture guessing

### Phase 1: Project bootstrap
Deliverables:
- repo structure created
- frontend and backend apps scaffolded
- Docker Compose base, dev, and production stack files created
- environment example file added
- CI baseline chosen, even if minimal

Exit criteria:
- one command path exists to run the local stack
- one command path exists to run the production-shaped stack on a target host
- frontend and backend health checks are reachable

### Phase 2: Auth and access control
Deliverables:
- registration and login
- password hashing
- JWT issuance and auth middleware
- role-aware route guards
- current-user endpoint

Exit criteria:
- users can sign up and sign in
- role checks are enforced server-side

### Phase 3: Profiles and verification
Deliverables:
- journalist profile workflow
- expert profile workflow
- verification evidence submission
- verification status display
- admin verification review flow

Exit criteria:
- a user can submit verification evidence
- an admin can approve or reject it
- the public-facing profile layer can show approved verification methods safely

### Phase 4: Requests
Deliverables:
- create request
- edit request
- close request
- own-requests dashboard
- expert browse, search, and filter

Exit criteria:
- journalists can manage requests
- experts can find open requests cleanly

### Phase 5: Pitches
Deliverables:
- submit pitch
- expert pitch tracking
- journalist review interface
- accept or reject actions
- pitch status transition rules

Exit criteria:
- the core marketplace loop works end to end inside the platform

### Phase 6: Admin moderation and trust operations
Deliverables:
- request moderation tools
- pitch moderation tools
- user moderation tools
- basic admin overview metrics
- audit-event visibility where needed

Exit criteria:
- trust and safety operations are viable for a small real launch

### Phase 7: Operational hardening
Deliverables:
- rate limiting
- structured logging
- health checks
- async notifications or reminders where needed
- backup and restore basics for the app DB

Exit criteria:
- the MVP can be debugged and operated without blind spots

### Phase 8: Content and launch prep
Deliverables:
- content pages via Strapi or another agreed path
- SEO baseline
- final Docker Compose deployment config
- launch checklist

Exit criteria:
- the product can be shown publicly with both app and content surfaces

## 14. Suggested implementation order inside each phase

Within each phase, prefer this order:
- schema and backend contracts first
- backend tests second
- backend implementation third
- frontend integration fourth
- end-to-end verification fifth
- docs and cleanup sixth

This reduces frontend churn and keeps permission logic centralized.

## 15. Open decisions to settle before coding starts

These should be settled in the domain-model or task docs before implementation begins.

### 15.1 Request visibility
Choose one:
- public to anyone
- public to logged-in users only
- visible only to approved or verified experts

This affects SEO, growth, trust, and moderation burden.

### 15.2 Verification submission shape
Choose whether MVP evidence is:
- link-based only
- upload-based only
- mixed links and uploads

This affects storage and moderation implementation.

### 15.3 Auth delivery mode
Choose whether frontend uses:
- secure cookies
- bearer tokens
- short-lived access plus refresh flow

This affects API and frontend integration patterns.

### 15.4 First launch niche
Pick the first journalist and expert vertical before marketing or content buildout grows too broad.

### 15.5 Organization support
Decide whether organizations are first-class MVP entities now, or deferred until after individual workflows are proven.

My recommendation: defer full organization accounts unless a launch partner requires them.

## 16. Recommended next planning artifacts

After reviewing this plan, create these files next:
- `tickets/nguontin-mvp-domain-model.md`
- `tickets/nguontin-mvp-tasks.md`

### 16.1 Domain-model document should include
- entities
- fields
- relationships
- status enums
- ownership rules
- moderation rules
- audit-event strategy

### 16.2 Task document should include
- bite-sized tasks in execution order
- exact file paths to create or modify
- commands to run
- verification steps
- suggested commit boundaries

## 17. Practical recommendation

If the goal is to validate the product quickly, bias the first implementation toward the platform inbox workflow rather than trying to fully implement both direct email and inbox workflows at once.

Reason:
- the inbox workflow is the source of measurable trust signals
- it produces cleaner product learning
- it reduces ambiguity in the first build
- it avoids spending time on partial email-tracking logic that will still not provide strong verified metrics

The spec can still preserve the broader product direction, but the MVP build should focus on one clean operational loop.

## 18. Exit condition for moving from planning to coding

Do not start implementation until all of the following exist:
- approved MVP spec
- approved MVP implementation plan
- approved MVP domain model
- approved MVP task breakdown
- decision on request visibility
- decision on verification evidence format
- decision on first auth delivery approach

Once those are in place, coding can begin with much less thrash.
