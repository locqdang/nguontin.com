# Feature Specification: NguonTin MVP

**Feature Branch**: `001-nguontin-mvp`

**Created**: 2026-07-02

**Status**: Approved planning baseline

**Input**: User description: "Build the NguonTin MVP as a trust-first, Vietnamese-first platform where journalists create source requests, experts browse and pitch through the platform, and admins review verification and moderate trust-sensitive workflows."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Journalist creates and manages a source request (Priority: P1)

A journalist can sign in without a password, create a Vietnamese-language journalist profile, submit or begin verification, create a source request, and manage incoming expert pitches for that request.

**Why this priority**: Without journalist request creation, the marketplace has no supply of opportunities and the product has no core value.

**Independent Test**: Can be fully tested by signing in as a journalist, creating a profile, creating a request, viewing it in the journalist dashboard, and accepting or rejecting an incoming pitch.

**Acceptance Scenarios**:

1. **Given** a journalist with an authenticated account and completed profile, **When** they create a request with the MVP-required fields, **Then** the request is stored and appears in their own dashboard.
2. **Given** an existing open request owned by a journalist, **When** the journalist edits or closes it, **Then** the updated status is reflected in journalist views and expert availability changes accordingly.
3. **Given** an open request with at least one submitted pitch, **When** the journalist reviews a pitch and accepts or rejects it, **Then** the pitch status changes and the decision is visible to the expert.

---

### User Story 2 - Expert discovers requests and submits a pitch (Priority: P2)

An expert can sign in without a password, create a Vietnamese-language expert profile, submit or begin verification, browse open requests available to authenticated experts, and submit a platform-managed pitch.

**Why this priority**: Once journalist requests exist, expert discovery and pitch submission are the minimum marketplace loop needed to validate adoption.

**Independent Test**: Can be fully tested by signing in as an expert, browsing open requests, filtering to a relevant request, submitting one pitch, and observing that the pitch appears as pending for both expert and journalist flows.

**Acceptance Scenarios**:

1. **Given** an authenticated expert, **When** they browse open requests, **Then** they can see only MVP-visible requests that are open and intended for authenticated experts.
2. **Given** an expert viewing a request detail page, **When** they submit a pitch through the platform inbox flow, **Then** exactly one pitch is stored for that expert and request and its initial status is `pending`.
3. **Given** an expert with a submitted pitch, **When** the journalist later accepts, rejects, or the request closes, **Then** the expert can see the updated pitch status in their dashboard.

---

### User Story 3 - Admin reviews verification and moderates trust-sensitive flows (Priority: P3)

An admin can review user verification evidence, approve or reject submissions, and take moderation actions on users, requests, pitches, and verification records.

**Why this priority**: Trust is the core product differentiator; the MVP fails its positioning if verification and moderation do not exist.

**Independent Test**: Can be fully tested by submitting verification evidence as a journalist or expert, reviewing it as an admin, recording a decision, and confirming that only public-safe verification labels appear in profile trust displays.

**Acceptance Scenarios**:

1. **Given** a user has submitted verification evidence, **When** an admin approves or rejects it, **Then** the system records an append-only review decision and updates the user’s aggregate verification status.
2. **Given** a moderated request, pitch, user, or verification record, **When** an admin records a moderation action, **Then** the action is stored for auditability and the affected workflow respects that moderation state.
3. **Given** a verified profile, **When** another authenticated user views its trust indicators, **Then** they see public-safe verification method labels without exposure of sensitive raw evidence.

---

### Edge Cases

- What happens when a user signs in successfully but has not yet chosen or completed a journalist or expert role?
- What happens when one account holds both `journalist` and `expert` roles and needs separate profile flows?
- What happens when a journalist closes a request after pitches were already submitted?
- What happens when an expert tries to submit a second pitch to the same request?
- What happens when verification evidence is a broken link, inaccessible page, or unsupported evidence type?
- What happens when a user is suspended after they already own requests, pitches, or pending verification records?
- What happens when direct contact is allowed as a product concept but the MVP implementation is limited to platform inbox workflows?
- What happens when Google OAuth is configured but the required public Privacy Policy and Terms of Service pages are missing or not reachable?
- How does the system handle abuse controls such as rate limiting or CAPTCHA on passwordless login and pitch submission endpoints?
- How does the system handle Vietnamese-first public UX while internal code, schema names, and payload keys remain English?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST allow users to create and access accounts using passwordless email login and approved SSO providers, with no password-based login in the MVP.
- **FR-002**: The system MUST support at least the roles `journalist`, `expert`, and `admin`, and one account MUST be able to hold more than one role.
- **FR-003**: The system MUST allow journalists to create and maintain a journalist profile in a Vietnamese-language product UI.
- **FR-004**: The system MUST allow experts to create and maintain an expert profile in a Vietnamese-language product UI.
- **FR-005**: The system MUST allow journalists and experts to submit verification evidence with structured evidence records and admin review outcomes.
- **FR-006**: The system MUST store verification reviews as append-only decision records rather than only overwriting a single status field.
- **FR-007**: The system MUST show public-safe verification method labels on profiles without exposing sensitive private evidence details.
- **FR-008**: The system MUST allow journalists to create, edit, close, and list their own source requests.
- **FR-009**: Each source request MUST support the MVP field set: title, description, category, outlet name, deadline, language, region, preferred interview method, and number of experts required.
- **FR-010**: The system MUST restrict MVP request visibility to authenticated experts and admins rather than the public web.
- **FR-011**: The system MUST allow authenticated experts to browse, search, and filter open source requests that are visible to them.
- **FR-012**: The system MUST allow experts to submit a platform-managed pitch to an open source request.
- **FR-013**: The system MUST prevent duplicate MVP pitches from the same expert to the same request unless a later feature explicitly changes that rule.
- **FR-014**: The system MUST support pitch statuses `pending`, `accepted`, `rejected`, `withdrawn`, and `request_closed`.
- **FR-015**: The system MUST allow only the journalist who owns a request, or an admin, to accept or reject pitches for that request.
- **FR-016**: The system MUST provide experts with a way to see the current status of their submitted pitches.
- **FR-017**: The system MUST provide admins with a verification review queue and moderation controls for users, requests, pitches, and verification records.
- **FR-018**: The system MUST record audit events for trust-sensitive and operationally important actions such as authentication, verification decisions, request changes, pitch changes, and moderation actions.
- **FR-019**: The system MUST enforce server-side authorization checks for all protected actions.
- **FR-020**: The system MUST use PostgreSQL as the system of record for users, profiles, verification evidence, verification reviews, requests, pitches, audit events, and moderation actions.
- **FR-021**: The system MUST keep Strapi limited to content and marketing pages, and MUST NOT use Strapi as the system of record for marketplace or trust workflows.
- **FR-022**: All public-facing MVP navigation, labels, validation messages, and workflow copy MUST default to Vietnamese.
- **FR-023**: The system MUST support public Privacy Policy and Terms of Service pages if Google OAuth is included in any externally tested or launched environment.
- **FR-024**: The system MUST block Google OAuth launch readiness until public legal page URLs exist and return successful responses.
- **FR-025**: The system MUST include rate limiting and safe token handling for sensitive authentication and verification flows.
- **FR-026**: The system MUST provide health checks and structured logging sufficient to debug moderation, delivery, and workflow issues.
- **FR-027**: The system MUST support Docker Compose as the standard way to run the MVP stack in local development and deployment.
- **FR-028**: The MVP MUST treat AI as assistive only, limited to functions such as spam detection, duplicate detection, or category suggestion, rather than making AI central to trust decisions.

### Key Entities *(include if feature involves data)*

- **User**: Account identity with email, auth preference, user status, primary language, and timestamps.
- **UserRole**: Join model allowing one user to hold `journalist`, `expert`, and/or `admin` roles.
- **JournalistProfile**: Journalist-facing professional profile with public-safe trust fields and optional sensitive contact fields.
- **ExpertProfile**: Expert-facing professional profile with specialties, organization context, public-safe trust fields, and optional sensitive contact fields.
- **VerificationEvidence**: Structured verification proof record containing type, URL or metadata, notes, and status.
- **VerificationReview**: Append-only admin decision record for submitted verification evidence.
- **SourceRequest**: Journalist-owned request for expert sources with workflow fields, visibility, and status.
- **Pitch**: Expert response to a source request with message, supporting links, and status.
- **AuditEvent**: Append-only event record for sensitive or operationally important actions.
- **ModerationAction**: Admin action record for users, requests, pitches, or verification records.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A journalist can complete the MVP core journey from sign-in to published source request without using a password-based flow.
- **SC-002**: An authenticated expert can independently discover an open request, submit one pitch, and later observe a status update on that pitch.
- **SC-003**: An admin can review submitted verification evidence and record an approval or rejection decision that updates visible trust state without exposing raw sensitive evidence.
- **SC-004**: The product supports the full platform-observable workflow loop of request creation, pitch submission, and pitch decision with auditability for the key state transitions.
- **SC-005**: All core user-facing MVP screens for public and authenticated product workflows launch in Vietnamese.
- **SC-006**: If Google OAuth is enabled for external testing or launch, the deployed product exposes reachable public Privacy Policy and Terms of Service pages that return `200 OK`.
- **SC-007**: Core marketplace and trust data remain in the application backend and PostgreSQL rather than being stored in Strapi.
- **SC-008**: The deployed MVP exposes health checks and enough structured logs to diagnose authentication, moderation, and request or pitch workflow failures.

## Assumptions

- The MVP launch uses a trust-first marketplace model for Vietnamese-speaking journalists and experts.
- Mobile apps are out of scope for MVP one.
- Organizations and newsroom hierarchies are deferred beyond MVP one and are represented by plain-text profile fields for now.
- Public request browsing is out of scope for MVP one; requests are visible only to authenticated experts and admins.
- The first implemented interaction path is the platform inbox workflow, even if direct contact remains a product concept or later extension.
- The first launch may stage SSO provider rollout, but the MVP auth direction remains email login plus approved SSO and no passwords.
- Legal page content can start with founder-reviewed baseline copy, but the routes must exist publicly before Google OAuth launch verification.
- Reputation in MVP is lightweight and limited to signals that can be observed by the platform; broader public scoring can be designed later.
- The exact launch vertical, first journalist cohort, first expert cohort, and monetization path are intentionally not locked in this feature spec.
- Local development and production deployment are both expected to run through Docker Compose, with PostgreSQL hosted separately on the existing Raspberry Pi Docker environment.
