# Implementation Plan: NguonTin MVP

**Branch**: `001-nguontin-mvp` | **Date**: 2026-07-02 | **Spec**: `specs/001-nguontin-mvp/spec.md`

**Input**: Feature specification from `/specs/001-nguontin-mvp/spec.md`

**Note**: Normalized from the migrated planning doc so this feature now follows Spec Kit structure while preserving the actual MVP decisions already made.

## Summary

Build the first working NguonTin MVP as a Vietnamese-first web application where journalists create source requests, experts browse and pitch through the platform, and admins review verification and moderate trust-sensitive workflows. Use a split architecture with a Next.js frontend, FastAPI backend, PostgreSQL as the system of record, Redis plus Celery for background work, and Strapi limited to marketing and content pages. Deliver the MVP in vertical slices, starting with shared foundations, then the journalist loop, then the expert response loop, then admin trust operations.

## Technical Context

**Language/Version**: TypeScript for the frontend, Python 3.12 for the backend

**Primary Dependencies**: Next.js, Tailwind CSS, FastAPI, PostgreSQL, Redis, Celery, JWT auth, passwordless email login, Google and LinkedIn SSO candidates, Docker Compose, Strapi

**Storage**: PostgreSQL for application data, Redis for queue or cache support, Strapi content storage for marketing pages only

**Testing**: Vitest and Playwright for frontend verification, pytest for backend and API verification

**Target Platform**: Linux server deployment via Docker Compose, browser-based web application

**Project Type**: Web application with separated frontend, backend, worker, and CMS concerns

**Performance Goals**: Support the MVP marketplace loop with responsive authenticated workflows and enough operational visibility to debug auth, moderation, and workflow issues

**Constraints**: Vietnamese-first user-facing product copy, no password login in MVP, server-side authorization for all protected actions, Strapi must not own core marketplace data, Google OAuth launch readiness requires public legal pages

**Scale/Scope**: MVP for a small initial cohort of journalists and experts, not a public-at-scale marketplace yet

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- Planning before code: **PASS**. Spec, plan, data model, and task docs exist under `specs/001-nguontin-mvp/`.
- Clear architecture boundaries: **PASS**. Frontend, backend, database, worker, and CMS roles are separated.
- Verification before claiming completion: **PASS**. Each planned slice includes concrete verification commands or independently testable outcomes.
- Vietnamese product copy, English internal artifacts: **PASS**. User-facing product is Vietnamese-first; planning and implementation artifacts remain English.
- Security-sensitive workflows handled server-side: **PASS**. Auth, verification, moderation, and ownership rules are explicitly backend-owned.

No constitution violations currently need a complexity waiver.

## Project Structure

### Documentation (this feature)

```text
specs/001-nguontin-mvp/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── spec.md
└── tasks.md
```

### Source Code (repository root)

```text
frontend/
├── app/
├── public/
├── tests/
├── e2e/
└── package.json

backend/
├── app/
│   ├── api/
│   ├── core/
│   ├── db/
│   ├── models/
│   ├── schemas/
│   ├── services/
│   ├── tasks/
│   └── main.py
└── tests/

infra/
├── docker/
├── nginx/
└── scripts/

cms/
└── strapi/ or deployment wiring only
```

**Structure Decision**: Use the repo as a web application with explicit `frontend/` and `backend/` boundaries. Keep operational files under `infra/`. Keep Strapi isolated to content concerns. Keep feature planning under `specs/001-nguontin-mvp/` as the canonical Spec Kit home for this MVP.

## Phase 0: Research and design conclusions

### Product and scope conclusions

- The MVP is trust-first, not growth-first.
- Requests are visible to authenticated experts and admins, not the public web.
- The first implemented interaction path should be `platform_inbox`, even if direct contact remains part of the broader product direction.
- Verification should expose public-safe method labels, not raw evidence.
- AI is assistive only in MVP, for example spam detection, duplicate detection, or category suggestion.

### Architecture conclusions

- Next.js owns pages, forms, and user-facing app workflows.
- FastAPI owns auth, authorization, profiles, verification, requests, pitches, moderation, and audit logic.
- PostgreSQL is the system of record for users, profiles, requests, pitches, verification, moderation, and audit records.
- Redis and Celery exist for async support only where it materially helps the MVP.
- Strapi must not store marketplace or trust workflow records.

## Phase 1: Design detail

### Data model summary

The MVP depends on these core entities:

- `User`
- `UserRole`
- `JournalistProfile`
- `ExpertProfile`
- `VerificationEvidence`
- `VerificationReview`
- `SourceRequest`
- `Pitch`
- `AuditEvent`
- `ModerationAction`

Key locked enums already recorded in `data-model.md` include:

- `user_status`
- `verification_status`
- `verification_review_decision`
- `request_status`
- `request_visibility`
- `pitch_status`
- `moderation_target_type`
- `moderation_action_type`
- `evidence_type`
- `contact_method`
- `response_mode`

### API surface summary

Planned workflow-first backend route groups:

- Auth: `/auth/email/start`, `/auth/email/verify`, `/auth/sso/{provider}/start`, `/auth/sso/{provider}/callback`, `/me`
- Profiles: `/profiles/me`, `/profiles/journalist`, `/profiles/expert`, `/profiles/verification-evidence`
- Requests: `/requests`, `/requests/{request_id}`, `/requests/{request_id}/close`, `/journalists/me/requests`
- Pitches: `/requests/{request_id}/pitches`, `/experts/me/pitches`, `/pitches/{pitch_id}/accept`, `/pitches/{pitch_id}/reject`, `/pitches/{pitch_id}/withdraw`
- Admin: `/admin/verifications`, `/admin/verifications/{verification_id}/approve`, `/admin/verifications/{verification_id}/reject`, `/admin/moderation/actions`, `/admin/metrics/overview`

### Frontend route summary

Planned user-facing route groups:

- Public: `/`, `/about`, `/faq`, `/login`, `/register`, legal routes, and content routes such as `/blog`
- Journalist app: dashboard, requests, profile, verification
- Expert app: dashboard, requests, pitches, profile, verification
- Admin app: dashboard, verifications, moderation, users, requests, pitches

## Implementation Strategy

### Delivery order

1. Establish and verify shared project foundations
2. Build the journalist-owned request flow
3. Build the expert discovery and pitch flow
4. Build the admin verification and moderation flow
5. Harden operations, legal readiness, and launch support

### Why this order

This sequence keeps the product vertically testable. The journalist workflow creates supply, the expert workflow closes the core marketplace loop, and the admin workflow validates the trust proposition that differentiates the product.

## Story-to-Architecture Mapping

### User Story 1, Journalist request flow

Backend:
- auth and role checks
- journalist profile persistence
- request CRUD
- request ownership enforcement
- request dashboard queries

Frontend:
- registration or login screens
- journalist profile form
- journalist request creation and management screens
- Vietnamese validation and workflow copy

Data:
- `users`
- `user_roles`
- `journalist_profiles`
- `source_requests`
- relevant `audit_events`

### User Story 2, Expert browse and pitch flow

Backend:
- expert profile persistence
- open-request browse or filter queries
- pitch submission
- pitch state tracking
- duplicate-pitch protection

Frontend:
- expert profile form
- browse page
- request detail page
- pitch submission UI
- expert pitch list or status view

Data:
- `expert_profiles`
- `source_requests`
- `pitches`
- relevant `audit_events`

### User Story 3, Admin verification and moderation flow

Backend:
- verification evidence intake
- append-only verification review decisions
- moderation action recording
- admin-only route protection
- overview metrics or queue summaries

Frontend:
- verification submission UI for normal users
- admin verification queue UI
- admin moderation views
- public-safe trust label rendering

Data:
- `verification_evidence`
- `verification_reviews`
- `moderation_actions`
- `audit_events`

## Verification Strategy

### Build and test layers

Backend verification should include:
- pytest unit tests for auth, permission, and workflow helpers
- API tests for auth, profiles, requests, pitches, and admin routes
- DB-backed integration tests for status transitions and ownership rules

Frontend verification should include:
- `npm run build`
- route-level UI checks for login, register, profile, request, and moderation paths
- Playwright coverage for the main user journeys once the basic app shell exists

### Minimum end-to-end flows before MVP release

1. Journalist signs in, creates a profile, and creates a request
2. Expert signs in, finds a request, and submits a pitch
3. Journalist accepts or rejects a pitch on an owned request
4. Admin reviews verification evidence and records a moderation-safe decision

## Security and Observability Plan

### Security requirements carried into implementation

- Signed, expiring email-login tokens or one-time codes
- Strict SSO state and callback validation
- Server-side ownership and role enforcement
- Input validation on all write endpoints
- File type and size constraints for any verification uploads
- Rate limiting on auth and trust-sensitive endpoints
- Auditability for admin and verification decisions

### Logging and observability baseline

At minimum log:
- auth failures and suspicious auth activity
- request creation, edits, and closure
- pitch submissions and status changes
- verification submissions and review decisions
- moderation actions
- background job failures

Never log:
- raw tokens
- raw verification documents
- sensitive private contact data beyond operational need
- secrets or credential values

## Open Decisions and Assumptions

These are treated as current assumptions unless later revised:

- Google and LinkedIn are the leading SSO candidates, but the exact launch set may still be staged.
- The auth transport model may be bearer tokens or another backend-owned pattern, but it must remain secure and compatible with the split frontend and backend architecture.
- Full organization accounts are deferred unless a launch partner requires them.
- The first launch cohort and niche are not yet locked in this plan.
- Strapi may be introduced in the first launch-prep pass or slightly later, depending on when public content becomes necessary.

## Exit Condition for Coding Readiness

Implementation can proceed cleanly when all of the following are present:

- approved `spec.md`
- approved `plan.md`
- approved `data-model.md`
- approved `tasks.md`
- locked request visibility rule
- locked verification evidence format
- chosen auth delivery approach for frontend-backend integration

## Complexity Tracking

No exceptional complexity currently needs formal justification.
