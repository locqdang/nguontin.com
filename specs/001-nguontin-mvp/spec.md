# Feature Specification: NguonTin MVP

**Feature Branch**: `001-nguontin-mvp`

**Created**: 2026-07-02

**Status**: Approved planning baseline

**Input**: User description: "Build the NguonTin MVP as a trust-first, Vietnamese-first platform where journalists create source requests, experts browse and pitch through the platform, and users manage trust-sensitive workflows."


## Clarifications

### Session 2026-07-02

- Q: Should journalists require both business email and LinkedIn verification before creating source requests? → A: Require both business email and LinkedIn verification before a journalist can create source requests.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Journalist creates and manages a source request (Priority: P1)

A journalist can sign in without a password via email login or LinkedIn SSO (with automatic verification), create a Vietnamese-language journalist profile, complete business email verification, create a source request, and manage incoming expert pitches for that request.

**Why this priority**: Without journalist request creation, the marketplace has no supply of opportunities and the product has no core value.

**Independent Test**: Can be fully tested by signing in as a journalist via email or LinkedIn, creating a profile, completing business email verification, creating a request, viewing it in the journalist dashboard, and accepting or rejecting an incoming pitch.

**Acceptance Scenarios**:

1. **Given** a journalist with an authenticated account, completed profile, and business email verification, **When** they create a request with the MVP-required fields, **Then** the request is stored and appears in their own dashboard.
2. **Given** an existing open request owned by a journalist, **When** the journalist edits or closes it, **Then** the updated status is reflected in journalist views and expert availability changes accordingly.
3. **Given** an open request with at least one submitted pitch, **When** the journalist reviews a pitch and accepts or rejects it, **Then** the pitch status changes and the decision is visible to the expert.

---

### User Story 2 - Expert discovers requests and submits a pitch (Priority: P2)

An expert can sign in without a password via email login or LinkedIn SSO (with automatic verification), create a Vietnamese-language expert profile, optionally link additional verification methods, browse open requests available to authenticated experts, and submit a platform-managed pitch.

**Why this priority**: Once journalist requests exist, expert discovery and pitch submission are the minimum marketplace loop needed to validate adoption.

**Independent Test**: Can be fully tested by signing in as an expert via email or LinkedIn, creating a profile, optionally linking additional verification, browsing open requests, filtering to a relevant request, submitting one pitch, and observing that the pitch appears as pending for both expert and journalist flows.

**Acceptance Scenarios**:

1. **Given** an authenticated expert, **When** they browse open requests, **Then** they can see only MVP-visible requests that are open and intended for authenticated experts.
2. **Given** an expert viewing a request detail page, **When** they submit a pitch through the platform inbox flow, **Then** exactly one pitch is stored for that expert and request and its initial status is `pending`.
3. **Given** an expert with a submitted pitch, **When** the journalist later accepts, rejects, or the request closes, **Then** the expert can see the updated pitch status in their dashboard.

---

### Edge Cases

- What happens when a user signs in successfully but has not yet chosen or completed a journalist or expert role?
- What happens when one account holds both `journalist` and `expert` roles and needs separate profile flows?
- What happens when a journalist closes a request after pitches were already submitted?
- What happens when an expert tries to submit a second pitch to the same request?
- What happens when a user is suspended after they already own requests, pitches, or pending verification records?
- What happens when direct contact is allowed as a product concept but the MVP implementation is limited to platform inbox workflows?
- What happens when Google OAuth is configured but the required public Privacy Policy and Terms of Service pages are missing or not reachable?
- How does the system handle abuse controls such as rate limiting or CAPTCHA on passwordless login and pitch submission endpoints?
- How does the system handle Vietnamese-first public UX while internal code, schema names, and payload keys remain English?
- What happens when a LinkedIn profile becomes private or is deleted after initial verification?
- What happens when a LinkedIn URL validation check fails (LinkedIn API down, rate limits, etc.)?
- What happens when a user changes their business email domain after verification?
- What happens when a business email domain verification fails or the domain expires?
- When a user signs in via LinkedIn and later adds business email verification from a different email address, the system consolidates the accounts, keeps the LinkedIn identity as primary, and updates the account email to the business email.
- What if a user tries to consolidate accounts but the LinkedIn and business email profiles belong to detectably different people?
- What happens if one verification method expires while the user has both LinkedIn and business email verified?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST allow users to create and access accounts using passwordless email login and approved SSO providers, with no password-based login in the MVP.
- **FR-002**: The system MUST support at least the roles `journalist`, `expert`, and `admin`, and one account MUST be able to hold more than one role.
- **FR-003**: The system MUST allow journalists to create and maintain a journalist profile in a Vietnamese-language product UI.
- **FR-004**: The system MUST allow experts to create and maintain an expert profile in a Vietnamese-language product UI.
- **FR-005**: When a user signs in via LinkedIn SSO, the system MUST automatically create a verification record with type `linkedin-verified`, capture the LinkedIn profile URL, and make it visible to all authenticated users on the profile.
- **FR-006**: When a user signs in via business email or email login with a business domain, the system MUST automatically create or update a verification record with type `business-email-verified`, validate the domain, and make it visible to all authenticated users on the profile.
- **FR-006a**: After initial sign-in and automatic verification, users MUST be able to manually initiate the alternative verification method from their profile settings. When a user links the alternative verification method, the system MUST check if the underlying identity matches an existing verified account; if it does, the system MUST initiate account consolidation.
- **FR-006b**: During account consolidation via verification linking, the system MUST keep the LinkedIn identity as the primary account identifier and atomically update the user's account email to the business email domain. The system MUST create an audit record for the consolidation event and ensure both verification records are linked to the consolidated account.
- **FR-006c**: The system MUST prevent account consolidation if the LinkedIn and business email verifications belong to detectably different people (e.g., significantly different names in the profiles, unrelated profile histories). In such cases, the system MUST notify the user and prevent the linking.
- **FR-007**: The system MUST show public-safe verification method labels (`linkedin-verified`, `business-email-verified`) on profiles with associated LinkedIn URLs or business domain names visible to authenticated users, without exposing sensitive private evidence.
- **FR-008**: The system MUST allow journalists to create, edit, close, and list their own source requests only if their account is verified via both business email and linkedin.
- **FR-009**: Each source request MUST support the MVP field set: title, description, category, outlet name, deadline, language, region, preferred interview method, and number of experts required.
- **FR-010**: The system MUST restrict MVP request visibility to authenticated experts rather than the public web.
- **FR-011**: The system MUST allow authenticated experts to browse, search, and filter open source requests that are visible to them.
- **FR-012**: The system MUST allow experts to submit a platform-managed pitch to an open source request.
- **FR-013**: The system MUST prevent duplicate MVP pitches from the same expert to the same request unless a later feature explicitly changes that rule.
- **FR-014**: The system MUST support pitch statuses `pending`, `accepted`, `rejected`, `withdrawn`, and `request_closed`.
- **FR-015**: The system MUST allow only the journalist who owns a request to accept or reject pitches for that request.
- **FR-016**: The system MUST provide experts with a way to see the current status of their submitted pitches.
- **FR-017**: The system MUST provide system-driven verification controls to revoke or suspend invalid verification records without disrupting other linked verifications or account access.
- **FR-018**: The system MUST automatically validate LinkedIn profile URLs and business email domains on a scheduled basis; if validation fails, the system MUST flag the verification record as `expired` or `inaccessible` and notify the account owner to take action. The system MUST NOT break account access or linked verifications if one verification method expires.
- **FR-019**: The system MUST record audit events for trust-sensitive and operationally important actions such as authentication, verification creation or revocation, verification linking, account consolidation, request changes, and pitch changes.
- **FR-020**: The system MUST enforce server-side authorization checks for all protected actions.
- **FR-021**: The system MUST use PostgreSQL as the system of record for users, profiles, verification evidence, requests, pitches, audit events, and moderation actions.
- **FR-022**: The system MUST keep Strapi limited to content and marketing pages, and MUST NOT use Strapi as the system of record for marketplace or trust workflows.
- **FR-023**: All public-facing MVP navigation, labels, validation messages, and workflow copy MUST default to Vietnamese.
- **FR-024**: The system MUST support public Privacy Policy and Terms of Service pages if Google OAuth is included in any externally tested or launched environment.
- **FR-025**: The system MUST block Google OAuth launch readiness until public legal page URLs exist and return successful responses.
- **FR-026**: The system MUST include rate limiting and safe token handling for sensitive authentication and verification flows.
- **FR-027**: The system MUST provide health checks and structured logging sufficient to debug verification, delivery, and workflow issues.
- **FR-028**: The system MUST support Docker Compose as the standard way to run the MVP stack in local development and deployment.
- **FR-029**: The MVP MUST treat AI as assistive only, limited to functions such as spam detection, duplicate detection, or category suggestion, rather than making AI central to trust decisions.

### Key Entities *(include if feature involves data)*

- **User**: Account identity with email, auth preference (primary sign-in method), user status, primary language, and timestamps. One user can hold multiple verifications and roles.
- **UserRole**: Join model allowing one user to hold `journalist`, `expert`, and/or `admin` roles.
- **JournalistProfile**: Journalist-facing professional profile with public-safe trust fields and optional sensitive contact fields.
- **ExpertProfile**: Expert-facing professional profile with specialties, organization context, public-safe trust fields, and optional sensitive contact fields.
- **VerificationEvidence**: Verification proof record containing provider (`linkedin` or `business_email`), provider_url (LinkedIn profile URL or business domain), status (`valid`, `expired`, `inaccessible`), created_at, last_validated_at, and is_primary (indicating if this is the verification method used for initial account creation).
- **SourceRequest**: Journalist-owned request for expert sources with workflow fields, visibility, and status.
- **Pitch**: Expert response to a source request with message, supporting links, and status.
- **AuditEvent**: Append-only event record for sensitive or operationally important actions, including account consolidation events.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A journalist can complete the MVP core journey from sign-in (via email or LinkedIn) to published source request without using a password-based flow, with automatic verification on sign-in and business email verification required for request creation.
- **SC-002**: An authenticated expert can independently discover an open request, submit one pitch, and later observe a status update on that pitch.
- **SC-003**: A verified profile displays `linkedin-verified` and/or `business-email-verified` badges with associated LinkedIn URLs or business domains visible to all authenticated users.
- **SC-004**: The product supports the full platform-observable workflow loop of request creation, pitch submission, and pitch decision with auditability for the key state transitions.
- **SC-005**: All core user-facing MVP screens for public and authenticated product workflows launch in Vietnamese.
- **SC-006**: If Google OAuth is enabled for external testing or launch, the deployed product exposes reachable public Privacy Policy and Terms of Service pages that return `200 OK`.
- **SC-007**: Core marketplace and trust data remain in the application backend and PostgreSQL rather than being stored in Strapi.
- **SC-008**: The deployed MVP exposes health checks and enough structured logs to diagnose authentication, verification, and request or pitch workflow failures.
- **SC-009**: LinkedIn profile URLs and business email domains are validated on a schedule; expired or inaccessible verifications are flagged as `expired` or `inaccessible` for owner action without disrupting user access or linked verifications.
- **SC-010**: Users can manually link a second verification method (LinkedIn or business email) from their profile settings; if the identity matches an existing account, account consolidation succeeds with the LinkedIn identity as primary and the business email as the account email.

## Assumptions

- The MVP launch uses a trust-first marketplace model for Vietnamese-speaking journalists and experts.
- Mobile apps are out of scope for MVP one.
- Organizations and newsroom hierarchies are deferred beyond MVP one and are represented by plain-text profile fields for now.
- Public request browsing is out of scope for MVP one; requests are visible only to authenticated experts.
- The first implemented interaction path is the platform inbox workflow, even if direct contact remains a product concept or later extension.
- Verification is automatic and optional: users gain a verification badge when they sign in via LinkedIn SSO or provide a business email, but unverified users can still access the platform and submit pitches.
- Only users verified through both business email and LinkedIn can create source requests.
- Users can manually link a second verification method (LinkedIn or business email) after initial sign-in; if the underlying identities match, the accounts consolidate with LinkedIn as the primary identity and the business email as the account email.
- Account consolidation via verification linking prioritizes LinkedIn identity as the primary account identifier; the business email becomes the account's primary email address.
- When accounts are consolidated, the user has one unified account with both verifications linked, and audit trails capture the consolidation event.
- Legal page content can start with founder-reviewed baseline copy, but the routes must exist publicly before Google OAuth launch verification.
- Reputation in MVP is lightweight and limited to signals that can be observed by the platform; broader public scoring can be designed later.
- The exact launch vertical, first journalist cohort, first expert cohort, and monetization path are intentionally not locked in this feature spec.
- Local development and production deployment are both expected to run through Docker Compose, with PostgreSQL hosted separately on the existing Raspberry Pi Docker environment.