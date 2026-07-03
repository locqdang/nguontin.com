<!--
Sync Impact Report
Version change: 1.0.0 -> 1.1.0
Modified principles:
- I. Spec-First Decision Making
- II. Trust-First Data Ownership
- III. Vietnamese-First User Experience
- IV. Minimal MVP with Safety Controls
- VI. Readable, Intentful Code
- V. Observable, Recoverable Operations
Added sections:
- Project Constraints
- Development Workflow
Removed sections:
- none
Templates reviewed:
- .specify/templates/plan-template.md ✅ reviewed
- .specify/templates/spec-template.md ✅ reviewed
- .specify/templates/tasks-template.md ✅ reviewed
- .specify/templates/constitution-template.md ✅ replaced
Follow-up TODOs:
- none
-->
# NguonTin Constitution

## Core Principles

### I. Spec-First Decision Making
Every feature begins with a written specification, independent acceptance criteria, explicit edge cases, and test-driven validation before implementation begins. This ensures the team moves quickly without sacrificing clarity or introducing hidden scope.

### II. Trust-First Data Ownership
Core marketplace, verification, and audit data must remain in application-owned storage. External systems may support marketing or content presentation only; they must never become the system of record for trust-sensitive workflows. The project should maximize self-hosted services for core infrastructure and avoid cloud-managed services for trust-sensitive operations whenever possible.

### III. Vietnamese-First User Experience
Public-facing navigation, labels, validation messages, and workflows must default to Vietnamese. Internal code, schemas, data models, and APIs should remain English to preserve engineering clarity.

### IV. Minimal MVP with Safety Controls
The initial product must deliver the smallest viable trust marketplace loop while enforcing server-side authorization, verification controls, and audit trails. Safety and correctness take priority over feature breadth.

### V. Observable, Recoverable Operations
Every release must include observability and recoverability: health checks, structured diagnostics, deployment guidance, and clear failure behavior are required before shipping.

### VI. Readable, Intentful Code
Code must remain easy to read, with intent comments that explain design choices and safety guards. Complexity should be justified, and the implementation should favor clarity over cleverness.

## Project Constraints
The project is scoped as a trust-first Vietnamese marketplace prototype with backend-owned persistence and Docker Compose-based local deployment. PostgreSQL or equivalent application storage is the primary data store for core workflows; Strapi is limited to marketing content only. The project should maximize self-hosted services for core infrastructure and avoid cloud-managed data services for trust-sensitive workflows unless added through an explicit governance amendment.

## Development Workflow
Feature work follows the `specs/<feature>/` structure, with explicit `spec.md`, `plan.md`, `data-model.md`, and `tasks.md` artifacts. Changes require documented acceptance criteria, edge cases, operational notes, and test-driven implementation. Code should be easy to read, with intent comments for non-obvious decisions. All PRs must reference the relevant feature spec and demonstrate that they preserve the Vietnamese-first public experience and the project’s trust-oriented architecture.

## Governance
This constitution defines the guiding rules for the NguonTin project. It supersedes informal practices and must be consulted before making architectural or product decisions affecting trust, data ownership, localization, or operational readiness.

- Amendments require a written rationale, a version increment, and review by the maintainers.
- Major governance changes require a new principle or the removal of an existing one.
- Minor clarifications require a patch version update and a note in the constitution file.
- All PRs should include a brief constitution compliance statement linking to this document.

**Version**: 1.1.0 | **Ratified**: 2026-07-02 | **Last Amended**: 2026-07-02
