# NguonTin MVP Domain Model and DB Schema Plan

**Project:** NguonTin  
**Status:** Phase B complete draft for implementation  
**Version:** 1.0  
**Last updated:** 2026-07-01

## 1. Purpose

This document locks the core MVP application data model before backend scaffolding starts.

It is intended to remove ambiguity for:
- backend table and model creation
- API ownership and authorization rules
- request, pitch, verification, and moderation workflows
- Vietnamese-facing product copy boundaries versus internal implementation names

This document covers PostgreSQL application data only. Strapi remains content-only and must not store core marketplace, trust, or moderation records.

## 2. Scope and design rules

### 2.1 MVP storage boundary
PostgreSQL is the system of record for:
- users and auth-adjacent profile data
- journalist and expert profiles
- verification evidence and review decisions
- source requests
- pitches
- audit and moderation records

Redis and Celery may support async work later, but they are not the source of truth for these entities.

### 2.2 Naming rule
- Internal code, DB tables, enums, and API payload keys should use English identifiers.
- User-facing labels, screen copy, navigation, validation messages, and public trust labels should default to Vietnamese.
- Stored free-text content may be Vietnamese or English depending on what the user enters, but field names remain English.

### 2.3 Auditability rule
Sensitive workflow decisions should be append-only where practical.

For MVP this means:
- verification reviews are stored as separate records, not only as overwritten status text
- moderation actions are stored as separate records
- important state transitions should also emit audit events

### 2.4 MVP simplification rule
To keep backend implementation straightforward:
- one user account may hold one or more roles
- one user may have at most one journalist profile and at most one expert profile
- organizations are deferred beyond MVP one, except plain-text organization or outlet name fields
- the first implemented interaction path should be platform inbox workflow, even if direct contact remains a product concept

## 3. Locked MVP decisions

### 3.1 Request visibility
**Decision:** MVP source requests are visible only to authenticated experts and admins, not to the public web.

**Why:**
- reduces scraping and spam risk early
- keeps the trust model focused on registered participants
- avoids exposing journalist needs publicly before moderation patterns are understood

**Implementation effect:**
- `SourceRequest.visibility` exists but MVP allowed value is only `authenticated_experts`
- public browsing is out of scope for MVP one
- future expansion may add `public` or `invite_only`

### 3.2 Verification evidence format
**Decision:** Verification evidence is submitted as structured evidence records with optional link fields and optional file metadata, but MVP does not require full binary file storage in the first backend slice.

**MVP accepted evidence shape:**
- evidence type enum
- label or short description
- URL, when evidence is link-based
- optional notes from the user
- optional file reference metadata for later upload support

**Why:**
- supports LinkedIn, websites, published articles, and professional profiles immediately
- allows later file uploads without redesigning the table
- avoids blocking Phase C and Phase I on storage infrastructure decisions

### 3.3 Organizations in MVP
**Decision:** dedicated `Organization` table is deferred to later.

**MVP substitute:**
- journalist profile stores `outlet_name`
- expert profile stores `organization_name` and `job_title`
- verification evidence may reference an organization domain or website

**Why:**
- newsroom and company hierarchy is explicitly out of MVP scope
- text fields are enough to validate early workflow demand

### 3.4 Role model shape
**Decision:** use multi-role support with a join table from day one.

**Implementation:**
- canonical roles are stored as enum values
- `users` does not contain a single `role` column as the only source of truth
- `user_roles` allows one user to hold `journalist`, `expert`, and/or `admin`

**Why:**
- supports users who act as both journalist and expert
- avoids schema churn if an admin is also a normal account
- keeps authorization explicit

### 3.5 Status enums
**Decision:** lock the following MVP enums now.

- `user_status`: `active`, `suspended`, `deactivated`
- `verification_status`: `not_started`, `pending`, `approved`, `rejected`
- `verification_review_decision`: `approved`, `rejected`, `needs_more_info`
- `request_status`: `draft`, `open`, `closed`, `archived`
- `request_visibility`: `authenticated_experts`
- `pitch_status`: `pending`, `accepted`, `rejected`, `withdrawn`, `request_closed`
- `moderation_target_type`: `user`, `request`, `pitch`, `verification`
- `moderation_action_type`: `approve`, `reject`, `flag`, `suspend`, `hide`, `restore`
- `evidence_type`: `organization_email`, `business_email`, `linkedin_profile`, `facebook_profile`, `facebook_professional_profile`, `published_article`, `company_website`, `government_profile`, `university_profile`, `personal_website`, `manual_review_note`, `other`
- `contact_method`: `email`, `phone`, `zalo`, `facebook`, `linkedin`, `other`
- `response_mode`: `platform_inbox`, `direct_contact`

## 4. Core entities overview

The required MVP entities are:
- User
- JournalistProfile
- ExpertProfile
- VerificationEvidence
- VerificationReview
- SourceRequest
- Pitch
- AuditEvent
- ModerationAction

Supporting implementation entities recommended now:
- UserRole

Deferred entity:
- Organization

## 5. Entity definitions

## 5.1 User
**Purpose:** authentication identity and top-level account state.

**Suggested table:** `users`

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| id | uuid | yes | primary key |
| email | citext or varchar | yes | unique, normalized lowercase |
| display_name | varchar | yes | human name for the account |
| auth_preference | enum | yes | `email_login`, `google_sso`, `linkedin_sso`, or another approved provider key |
| user_status | enum | yes | `active`, `suspended`, `deactivated` |
| primary_language | varchar | yes | default `vi` for MVP unless user chooses otherwise later |
| last_login_at | timestamptz | no | operational field |
| email_verified_at | timestamptz | no | set after successful email login verification or trusted provider confirmation |
| created_at | timestamptz | yes | |
| updated_at | timestamptz | yes | |

**Ownership rules:**
- owned by the account holder
- readable by the user and admins
- mutable by the user for allowed profile-adjacent fields, by admins for moderation state
- email login secrets, one-time codes, magic-link tokens, and provider refresh tokens must never be returned to frontend clients

**Relationships:**
- one-to-many with `user_roles`
- one-to-one with `journalist_profiles` by user id, optional
- one-to-one with `expert_profiles` by user id, optional
- one-to-many with `verification_evidence`
- one-to-many with `source_requests` as journalist owner
- one-to-many with `pitches` as expert owner
- one-to-many with `audit_events`
- one-to-many with `moderation_actions` as target user when applicable

## 5.2 UserRole
**Purpose:** explicit role assignment for authorization.

**Suggested table:** `user_roles`

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| id | uuid | yes | primary key |
| user_id | uuid | yes | FK to users |
| role | enum | yes | `journalist`, `expert`, `admin` |
| created_at | timestamptz | yes | |
| created_by_user_id | uuid | no | admin actor for admin grants, nullable for self-selected roles |

**Constraints:**
- unique `(user_id, role)`

**Ownership rules:**
- account holder can read their roles
- only admins can grant or revoke `admin`
- MVP can allow self-selection of journalist and expert during onboarding

## 5.3 JournalistProfile
**Purpose:** journalist-facing professional profile used for trust and request creation.

**Suggested table:** `journalist_profiles`

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| id | uuid | yes | primary key |
| user_id | uuid | yes | unique FK to users |
| full_name | varchar | yes | public-facing professional name |
| outlet_name | varchar | no | plain-text organization field for MVP |
| beat | varchar | no | e.g. politics, health, business |
| bio | text | no | short background |
| region | varchar | no | geography served |
| preferred_language | varchar | yes | default `vi` |
| preferred_contact_method | enum | no | how experts should respond when direct contact is allowed later |
| contact_email | varchar | no | optional, sensitive |
| contact_phone | varchar | no | optional, sensitive |
| zalo_handle | varchar | no | optional, sensitive |
| linkedin_url | text | no | optional |
| facebook_url | text | no | optional |
| verification_status | enum | yes | cached aggregate status |
| verification_summary_public | jsonb | no | public-safe method labels only |
| is_profile_public_to_experts | boolean | yes | default true |
| created_at | timestamptz | yes | |
| updated_at | timestamptz | yes | |

**Ownership rules:**
- editable only by the owning user and admins
- visible to admins and the owner
- selectively visible to authenticated experts for fields intended for matching
- sensitive contact fields should not be public by default

**Relationships:**
- belongs to one user
- journalist user owns many source requests

## 5.4 ExpertProfile
**Purpose:** expert-facing professional profile used for discovery and trust.

**Suggested table:** `expert_profiles`

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| id | uuid | yes | primary key |
| user_id | uuid | yes | unique FK to users |
| full_name | varchar | yes | professional display name |
| headline | varchar | no | concise expertise summary |
| bio | text | no | expertise overview |
| specialties | jsonb | no | array of topic strings for MVP |
| organization_name | varchar | no | plain-text employer or affiliation |
| job_title | varchar | no | role/title |
| region | varchar | no | location or coverage area |
| preferred_language | varchar | yes | default `vi` |
| contact_email | varchar | no | sensitive |
| contact_phone | varchar | no | sensitive |
| zalo_handle | varchar | no | sensitive |
| linkedin_url | text | no | optional |
| facebook_url | text | no | optional |
| website_url | text | no | optional |
| availability_notes | text | no | optional |
| verification_status | enum | yes | cached aggregate status |
| verification_summary_public | jsonb | no | public-safe verification labels |
| is_listed_to_journalists | boolean | yes | default true |
| created_at | timestamptz | yes | |
| updated_at | timestamptz | yes | |

**Ownership rules:**
- editable only by the owning user and admins
- visible to the owner, admins, and relevant journalist flows
- sensitive contact fields should remain private unless explicit direct-contact features are enabled later

**Relationships:**
- belongs to one user
- expert user owns many pitches

## 5.5 VerificationEvidence
**Purpose:** stores each submitted verification proof item.

**Suggested table:** `verification_evidence`

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| id | uuid | yes | primary key |
| user_id | uuid | yes | FK to users |
| profile_type | varchar | yes | `journalist` or `expert` for routing; could become enum |
| evidence_type | enum | yes | see locked enum |
| label | varchar | no | short human description |
| evidence_url | text | no | for LinkedIn, website, article, public profile |
| file_storage_key | varchar | no | reserved for future uploaded files |
| file_original_name | varchar | no | reserved metadata |
| notes_private | text | no | user explanation for reviewers |
| status | enum | yes | `pending`, `approved`, `rejected`; derived from latest review for convenience |
| submitted_at | timestamptz | yes | |
| created_at | timestamptz | yes | |
| updated_at | timestamptz | yes | |

**Ownership rules:**
- creatable by the owning user
- readable by the owning user and admins
- raw URLs and file references are never shown publicly as proof details by default

**Relationships:**
- belongs to one user
- has many verification reviews

**Implementation note:**
- when `evidence_type` is email-based, the actual address may be stored as a protected field or handled through a verification workflow later; do not expose it publicly just because the verification label becomes public

## 5.6 VerificationReview
**Purpose:** append-only review decisions on submitted evidence.

**Suggested table:** `verification_reviews`

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| id | uuid | yes | primary key |
| verification_evidence_id | uuid | yes | FK to verification_evidence |
| reviewed_user_id | uuid | yes | denormalized target user |
| reviewer_user_id | uuid | yes | admin reviewer |
| decision | enum | yes | `approved`, `rejected`, `needs_more_info` |
| public_method_label_vi | varchar | no | e.g. `Đã xác minh qua LinkedIn` |
| public_method_label_en | varchar | no | optional internal/admin helper |
| reviewer_notes_private | text | no | internal only |
| reviewed_at | timestamptz | yes | |
| created_at | timestamptz | yes | |

**Ownership rules:**
- only admins create reviews
- only admins and the owning user can read the decision outcome
- reviewer notes stay admin-only
- only public-safe labels may flow into public profile trust display

**Relationships:**
- belongs to one verification evidence record
- belongs to one admin reviewer

## 5.7 SourceRequest
**Purpose:** journalist request for expert sources.

**Suggested table:** `source_requests`

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| id | uuid | yes | primary key |
| journalist_user_id | uuid | yes | FK to users |
| journalist_profile_id | uuid | yes | FK to journalist_profiles |
| title | varchar | yes | MVP required |
| description | text | yes | MVP required |
| category | varchar | yes | MVP required |
| outlet_name | varchar | no | copied from profile or overridden per request |
| deadline_at | timestamptz | no | |
| language | varchar | yes | default `vi` |
| region | varchar | no | |
| preferred_interview_method | enum | no | use `contact_method` values initially |
| experts_needed_count | integer | yes | default 1 |
| response_mode | enum | yes | `platform_inbox` for MVP implementation path |
| visibility | enum | yes | locked to `authenticated_experts` |
| status | enum | yes | `draft`, `open`, `closed`, `archived` |
| moderation_status | varchar | no | optional lightweight field, or infer from latest moderation action |
| closed_at | timestamptz | no | |
| created_at | timestamptz | yes | |
| updated_at | timestamptz | yes | |

**Ownership rules:**
- only the owning journalist and admins can create, update, close, or archive
- authenticated experts can browse only requests in `open` status
- non-authenticated public users cannot browse MVP requests

**Relationships:**
- belongs to one journalist user
- belongs to one journalist profile
- has many pitches
- has many audit events and possible moderation actions

## 5.8 Pitch
**Purpose:** expert response to a source request.

**Suggested table:** `pitches`

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| id | uuid | yes | primary key |
| source_request_id | uuid | yes | FK to source_requests |
| expert_user_id | uuid | yes | FK to users |
| expert_profile_id | uuid | yes | FK to expert_profiles |
| message | text | yes | core pitch body |
| supporting_links | jsonb | no | array of URLs |
| contact_method | enum | no | preferred follow-up path |
| status | enum | yes | `pending`, `accepted`, `rejected`, `withdrawn`, `request_closed` |
| submitted_at | timestamptz | yes | |
| decided_at | timestamptz | no | set when accepted or rejected |
| withdrawn_at | timestamptz | no | |
| created_at | timestamptz | yes | |
| updated_at | timestamptz | yes | |

**Constraints:**
- unique `(source_request_id, expert_user_id)` for MVP, unless later allowing multiple revisions

**Ownership rules:**
- only the expert owner may create or withdraw their pitch
- only the journalist who owns the related request may accept or reject
- admins may review for moderation purposes

**Relationships:**
- belongs to one source request
- belongs to one expert user
- belongs to one expert profile
- has many audit events and possible moderation actions

## 5.9 AuditEvent
**Purpose:** general append-only event log for workflow and trust-sensitive changes.

**Suggested table:** `audit_events`

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| id | uuid | yes | primary key |
| actor_user_id | uuid | no | nullable for system events |
| event_type | varchar | yes | e.g. `user_registered`, `email_login_started`, `email_login_verified`, `request_created`, `pitch_accepted` |
| target_type | varchar | yes | e.g. `user`, `request`, `pitch`, `verification` |
| target_id | uuid | no | related record id |
| request_context_id | varchar | no | trace or request id |
| metadata | jsonb | no | small structured payload, no secrets |
| created_at | timestamptz | yes | |

**Ownership rules:**
- app writes events, not end users directly
- admin-readable in operations tools
- user-facing exposure should be highly selective, if any

**Logging rule:**
- never store passwords, raw uploaded documents, raw tokens, or unnecessary private contact data in metadata

## 5.10 ModerationAction
**Purpose:** explicit record of trust and safety actions taken by admins.

**Suggested table:** `moderation_actions`

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| id | uuid | yes | primary key |
| moderator_user_id | uuid | yes | admin actor |
| target_type | enum | yes | `user`, `request`, `pitch`, `verification` |
| target_id | uuid | yes | id of moderated record |
| action_type | enum | yes | `approve`, `reject`, `flag`, `suspend`, `hide`, `restore` |
| reason_code | varchar | no | short structured code |
| notes_private | text | no | internal notes |
| created_at | timestamptz | yes | |

**Ownership rules:**
- only admins create moderation actions
- admins read all moderation records
- only downstream public-safe consequences may be visible to end users

**Relationships:**
- belongs to one admin moderator
- targets users, requests, pitches, or verification records polymorphically

## 6. Relationships summary

- `users` 1-to-many `user_roles`
- `users` 1-to-1 `journalist_profiles` (optional)
- `users` 1-to-1 `expert_profiles` (optional)
- `users` 1-to-many `verification_evidence`
- `verification_evidence` 1-to-many `verification_reviews`
- `users` 1-to-many `source_requests` as journalist owner
- `source_requests` 1-to-many `pitches`
- `users` 1-to-many `pitches` as expert owner
- `users` 1-to-many `audit_events` as actor
- `users` 1-to-many `moderation_actions` as moderator
- `users`, `source_requests`, `pitches`, and `verification_evidence` may each be moderation targets

## 7. Ownership and authorization rules

### 7.1 Self-owned records
A normal user may manage only their own:
- account basics where allowed
- journalist profile
- expert profile
- verification evidence submissions
- pitches they created
- requests they created, if they have the journalist role

### 7.2 Journalist permissions
A journalist may:
- create and edit their own source requests
- close their own source requests
- read pitches attached to their own requests
- accept or reject pitches on their own requests

A journalist may not:
- review other journalists' private request management data
- moderate users or pitches globally unless they are also admin

### 7.3 Expert permissions
An expert may:
- browse open MVP requests when authenticated
- submit one pitch per request in MVP
- view the status of their own pitches

An expert may not:
- edit request records they do not own
- view private journalist-only workflow notes
- review another expert's pitch record

### 7.4 Admin permissions
An admin may:
- review verification evidence and create verification reviews
- create moderation actions
- view audit records needed for trust and safety operations
- suspend users or hide problematic content within MVP moderation scope

## 8. Vietnamese-facing boundaries versus internal English identifiers

### 8.1 Internal English identifiers
Use English for:
- table names
- enum values
- API field names
- backend module names
- internal event types

Examples:
- `source_requests`
- `verification_status = pending`
- `pitch_status = accepted`

### 8.2 Vietnamese-facing product copy
Use Vietnamese for:
- route labels and navigation text
- form labels and helper copy
- empty states and validation errors
- public trust labels displayed on profiles
- moderation and verification status text shown in the UI

Examples:
- internal enum: `approved`
- user-facing label: `Đã xác minh`

- internal enum: `request_closed`
- user-facing label: `Yêu cầu đã đóng`

### 8.3 Public verification display rule
The profile UI should display only public-safe verification method labels, not raw evidence.

Allowed public examples:
- `Đã xác minh qua email công việc`
- `Đã xác minh qua LinkedIn`
- `Đã xác minh qua website tổ chức`

Not allowed for public display by default:
- full email address used for verification
- raw LinkedIn or Facebook evidence URL if it exposes unnecessary private info
- uploaded documents or screenshots
- admin reviewer notes

## 9. Recommended initial PostgreSQL table order

To reduce migration friction, create tables in this order:
1. `users`
2. `user_roles`
3. `journalist_profiles`
4. `expert_profiles`
5. `verification_evidence`
6. `verification_reviews`
7. `source_requests`
8. `pitches`
9. `audit_events`
10. `moderation_actions`

## 10. Recommended implementation notes for Phase C and Phase E

- Use UUID primary keys across all core tables.
- Normalize email to lowercase before uniqueness checks.
- Cache aggregate `verification_status` on profile tables for easy rendering, but keep `verification_reviews` as the review source of truth.
- Prefer JSONB only for genuinely variable lists such as `specialties`, `supporting_links`, or public verification summaries, not for the whole record.
- Add DB indexes early on:
  - `users(email)` unique
  - `user_roles(user_id, role)` unique
  - `verification_evidence(user_id, status)`
  - `source_requests(status, visibility, deadline_at)`
  - `pitches(source_request_id, expert_user_id)` unique
  - `moderation_actions(target_type, target_id)`
  - `audit_events(target_type, target_id, created_at)`

## 11. Deferred items, explicitly not in MVP one schema

These are intentionally deferred so backend scaffolding can stay focused:
- dedicated `organizations` table and account hierarchy
- team or newsroom memberships
- multilingual schema complexity beyond storing Vietnamese-facing copy in the UI layer
- public reputation scoring model
- automated trust scoring
- binary file storage pipeline as a Phase B blocker
- multiple pitch revisions per expert per request
- public request marketplace browsing

## 12. Phase B verification checklist

This document explicitly covers all required core entities:
- User
- JournalistProfile
- ExpertProfile
- VerificationEvidence
- VerificationReview
- SourceRequest
- Pitch
- AuditEvent
- ModerationAction

This document also locks all blocking MVP decisions:
- request visibility: authenticated experts only
- verification evidence format: structured records with link-first support and optional file metadata
- organizations: deferred beyond MVP one
- role model shape: multi-role via join table
- status enums: locked in section 3.5

## 13. Session exit conclusion

Backend scaffolding can now start without guessing:
- which tables exist
- who owns each record
- which statuses and roles are legal
- what stays Vietnamese in the UI versus English in code
- what is in MVP now versus deferred
