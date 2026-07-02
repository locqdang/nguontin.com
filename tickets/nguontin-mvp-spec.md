# NguonTin MVP Specification

**Project:** NguonTin
**Status:** Draft approved for planning
**Version:** 1.1
**Last updated:** 2026-07-01

## 1. Product summary

NguonTin is a trust-first platform that helps Vietnamese-speaking journalists find and work with credible expert sources.

The MVP should validate whether journalists and experts will use a more structured, verified workflow than informal channels such as Facebook groups, email chains, or chat groups.

NguonTin should differentiate itself through:
- transparent verification, not just a generic verified badge
- better organization of source requests and expert pitches
- optional platform-managed inbox workflows that create trackable trust and reputation signals
- support for familiar direct-contact workflows during early adoption

## 2. Product vision

NguonTin aims to become the default platform in Vietnam for finding credible media sources.

The long-term product should help journalists:
- find relevant, trustworthy experts faster
- manage requests and responses in one place
- build a professional network of reliable sources

The long-term product should help experts:
- discover relevant media opportunities
- present credible professional profiles
- build reputation through successful journalist interactions

## 3. Product principles

The MVP and later versions should follow these principles:
- Trust before growth
- Verification should be transparent
- Encourage better workflows, do not force them prematurely
- AI should assist humans, not replace judgment
- Reputation should be earned through verified interactions
- Core application data should stay in the app backend, not the CMS

## 3.1 Front-facing language rule

For the MVP:
- the public site should be in Vietnamese
- public URLs and front-facing navigation should follow Vietnamese product positioning
- all front-facing user features should be written in Vietnamese
- user-visible product copy should default to Vietnamese across the site and app

This includes at minimum:
- homepage and marketing pages
- authentication screens
- dashboards
- request creation and management screens
- pitch submission and review screens
- verification flows
- admin screens that are part of the product UI

Internal code, schema names, and implementation details do not need to be written in Vietnamese.

## 4. Primary user roles

### 4.1 Journalist
A journalist can:
- create an account and sign in through passwordless email login or approved SSO
- create a journalist profile
- complete identity verification
- create and manage source requests
- receive expert responses
- accept or reject pitches
- build a professional reputation over time

### 4.2 Expert
An expert can:
- create an account and sign in through passwordless email login or approved SSO
- create an expert profile
- complete identity verification
- browse open journalist requests
- submit pitches to relevant requests
- track pitch status
- build a media reputation over time

### 4.3 Administrator
An administrator can:
- review and verify users
- moderate requests, pitches, and profiles
- handle abuse and spam
- manage trust and safety actions
- review core operational analytics

## 5. MVP goals

The MVP should prove the following:
- journalists are willing to post source requests on the platform
- experts are willing to browse requests and submit pitches
- verification increases trust and platform credibility
- a platform inbox workflow provides enough value to justify adoption
- the product can support both direct contact and platform-managed responses without confusing users

## 6. Non-goals for MVP

The MVP does not need to fully solve:
- advanced AI matching and ranking
- complex company or newsroom account hierarchies
- mobile apps
- public API access
- deep CRM workflows
- full quote tracking and interview scheduling automation
- sophisticated monetization systems

These can be revisited after MVP validation.

## 7. Core MVP workflows

### 7.1 Journalist request workflow
A journalist should be able to:
1. create an account, then authenticate through passwordless email login or approved SSO
2. create a profile
3. complete or begin verification
4. create a source request
5. edit or close the request
6. review incoming pitches
7. accept or reject pitches

### 7.2 Expert response workflow
An expert should be able to:
1. create an account, then authenticate through passwordless email login or approved SSO
2. create a profile
3. complete or begin verification
4. browse and filter open requests
5. open a request detail page
6. submit a pitch
7. track whether the pitch is pending, accepted, rejected, or closed

### 7.3 Admin moderation workflow
An administrator should be able to:
1. review pending verification submissions
2. approve or reject verification evidence
3. review reports or abuse flags
4. moderate low-quality or suspicious requests and pitches
5. view basic operational and trust metrics

## 8. Request model, journalist side

Each source request should include at minimum:
- title
- description
- category
- publication or outlet name
- deadline
- language
- region
- preferred interview method
- number of experts required

Optional future fields can be added later if needed, but the MVP should keep request creation focused and easy to complete.

## 9. Pitch delivery modes

NguonTin should support two response modes.

### 9.1 Direct contact mode
Experts contact the journalist directly using the journalist's chosen contact path.

Advantages:
- familiar workflow
- low friction for early adoption

Limitations:
- the platform cannot reliably track response quality or outcomes
- reputation signals are weaker
- analytics are limited

### 9.2 NguonTin inbox mode
Experts submit pitches through the platform.

Benefits:
- better pitch organization
- future AI ranking and summarization support
- measurable workflow analytics
- stronger reputation signals
- cleaner moderation and trust controls
- future expert CRM and shortlist features

### 9.3 Product rule
Journalists should not be forced into the platform inbox during MVP.

However, only platform-managed interactions should contribute to verified workflow metrics and trust signals.

## 10. Verification model

Verification is a core product differentiator.

NguonTin should not only show whether a user is verified. It should also show how that verification was established, without exposing sensitive private information.

### 10.1 Journalist verification evidence
Possible journalist verification evidence includes:
- organization email
- LinkedIn profile
- Facebook profile
- published articles
- manual review

### 10.2 Expert verification evidence
Possible expert verification evidence includes at least one of:
- business email
- LinkedIn profile
- Facebook Professional profile
- company website
- government profile
- university profile
- personal website

### 10.3 Verification transparency
Profiles should display a human-readable list of verification methods, for example:
- Business Email
- LinkedIn Verified
- Company Website
- Facebook Professional

Sensitive details must not be exposed directly.

## 11. Reputation and trust

The product should support a lightweight MVP trust model.

### 11.1 Journalist trust signals
Potential signals include:
- number of requests published
- verified workflow history
- responsiveness
- completion behavior

### 11.2 Expert trust signals
Potential signals include:
- accepted pitches
- response timeliness
- successful media appearances or quotes, when verifiable
- journalist feedback, if introduced later

### 11.3 MVP rule
Only platform-observable interactions should count toward reputation and verified workflow metrics.

Direct email interactions may be allowed, but they should not create strong trust claims unless later verified through another process.

## 12. AI in MVP

AI should be assistive, not central, in the first version.

### 12.1 MVP AI features
The MVP may include:
- spam detection
- duplicate detection
- category suggestion

### 12.2 Future AI features
Later versions may include:
- expert matching
- pitch ranking
- inbox summaries
- writing assistance
- quality scoring

## 13. Authentication and account access

The product should support these authentication methods:
- passwordless email login, for example magic links or one-time codes sent to the user's email
- Google OAuth
- LinkedIn OAuth
- other approved SSO providers added later if launch needs justify them

The exact provider rollout can be staged during implementation, but the MVP direction is clear: no password login, email login plus SSO only.

### 13.1 Google OAuth verification requirement
Because Google OAuth verification requires clear public legal disclosures, the MVP public site must include:
- a public Privacy Policy page
- a public Terms of Service page
- stable footer or equivalent public navigation links to both pages
- production URLs that can be submitted in the Google Auth consent-screen verification flow

These pages are not optional if Google OAuth is part of the launch auth set.

The legal pages should at minimum explain:
- what user data is collected
- how sign-in data and profile data are used
- how verification evidence is handled
- whether the product sends platform emails or notifications
- how users can contact the operator about privacy or account concerns

The implementation can start with founder-reviewed baseline legal copy, but the routes must exist publicly before Google OAuth launch verification is attempted.

## 14. MVP feature scope

All user-facing MVP features should be presented in Vietnamese in site copy, navigation, labels, helper text, validation messages, and workflow content.

### 14.1 Journalist features
Must-have MVP features:
- account sign-up and sign-in through passwordless email login or approved SSO
- journalist profile creation
- journalist verification submission
- create request
- edit request
- close request
- dashboard for own requests
- browse or search requests where appropriate
- review pitches for owned requests
- accept or reject pitches

### 14.2 Expert features
Must-have MVP features:
- account sign-up and sign-in through passwordless email login or approved SSO
- expert profile creation
- expert verification submission
- browse requests
- search requests
- filter requests
- submit pitch
- track pitch status

### 14.3 Administrator features
Must-have MVP features:
- verification review queue
- user moderation controls
- request and pitch moderation controls
- abuse handling tools
- basic analytics dashboard

## 15. Content management boundary

Strapi should be used only for content and marketing pages such as:
- blog
- FAQ
- privacy policy
- terms of service
- landing pages
- documentation
- SEO pages

Core application data must remain in the FastAPI and PostgreSQL application backend.

Strapi must not become the system of record for:
- users
- expert profiles used for workflow logic
- journalist profiles used for workflow logic
- requests
- pitches
- verification states
- reputation metrics

Any CMS-managed public content for the MVP should also be published in Vietnamese by default.

## 16. Technical direction

The current planned stack is:

### Frontend
- Next.js
- TypeScript
- Tailwind CSS
- Vitest for unit and integration tests
- Playwright for end-to-end browser tests

### Frontend product presentation
- the public site URL structure should support a Vietnamese-first product experience
- front-facing routes, page content, and user-visible product copy should launch in Vietnamese
- if multilingual support is added later, Vietnamese remains the MVP default and first priority

### Backend
- FastAPI

### Data and background processing
- PostgreSQL for application data
- Redis for cache and queue support
- Celery for background jobs

### Authentication and security
- passwordless email login, for example magic links or one-time codes
- SSO providers, starting with the approved launch set
- JWT-based session or API auth after successful email or SSO authentication
- rate limiting
- CAPTCHA
- audit logs

### CMS
- Strapi for content only

## 17. Infrastructure direction

Planned infrastructure direction:
- Cloudflare
- Cloudflare Tunnel
- Nginx reverse proxy
- Docker Compose as the standard deployment model for the full stack
- Docker Compose managed services for frontend, API, worker, Redis, Strapi, Nginx, and related components
- PostgreSQL hosted separately on the existing Raspberry Pi Docker environment

The MVP should be designed so both local development and production deployment run through Docker Compose, using shared base services plus environment-specific overrides where needed.

This direction is acceptable for planning, but exact Compose file layout, service definitions, volumes, networks, and environment handling can be refined later.

## 18. Environment and repository expectations

The repository should eventually include:
- `.env.example` committed with safe example values
- `.env.local` ignored for local development
- Docker Compose files for shared, development, and production deployment
- dockerized local development and deployment setup aligned with the Compose deployment model

## 19. Security requirements

The MVP must include:
- HTTPS in deployed environments
- safe passwordless login token handling and expiry controls
- safe SSO token validation and provider-side callback handling
- rate limiting on sensitive endpoints
- CAPTCHA or equivalent abuse reduction where needed
- audit logs for sensitive admin and verification actions
- careful handling of uploaded or linked verification evidence
- server-side authorization checks for all protected actions

## 19.1 Public legal and consent-screen readiness requirements

If Google OAuth is enabled in any environment intended for external testing or launch, the deployed product must also include:
- a reachable public Privacy Policy URL
- a reachable public Terms of Service URL
- consent-screen app information that matches the deployed product name and domain
- a documented owner contact method shown on the public site or legal pages

Google Auth launch readiness should be blocked until those public URLs exist and return `200 OK`.

## 20. Observability and operations

The product should be designed with:
- health checks
- structured logging
- enough metrics and diagnostics to debug moderation, delivery, and workflow issues

Prometheus and Grafana are reasonable future or early-production choices, but detailed observability implementation can be planned later.

## 21. Risks and product questions to resolve later

These questions do not block this spec from being recorded, but they should be answered before implementation planning is complete:
- what launch category or vertical should go first
- who the first journalist and expert cohorts are
- which verification steps are manual versus automated
- whether request visibility is public, gated, or role-limited
- how much of the inbox workflow is required in MVP one
- what the first reputation model should expose to users
- whether concierge-assisted matching is needed for launch
- what monetization path will be tested first, if any

## 22. Success criteria

NguonTin should be considered successful if journalists prefer it over informal alternatives because it provides:
- more credible experts
- better request organization
- better source search and filtering
- better workflow management
- better trust signals
- better long-term reputation building for both journalists and experts

## 23. Planning handoff

This document is a product specification baseline.

The next planning stage should produce:
- an implementation plan
- a proposed domain and database model
- bite-sized engineering tasks
- MVP acceptance criteria by workflow

Those artifacts are intentionally deferred until after this spec is recorded and reviewed.
