# nguontin.com

NguonTin is an early Vietnamese-first homepage prototype for a journalist-to-expert matching product.

## Current Phase A baseline

- Frontend: Next.js app in `frontend/`
- Docker Compose service: `frontend`
- Host port: `3007`
- Container port: `3000`
- Current homepage language: Vietnamese
- Test baseline: Vitest and Playwright smoke coverage for the homepage

## Run locally with Docker Compose

From the repo root:

```bash
docker compose up --build
```

Then open:

```text
http://127.0.0.1:3007
```

Validate the Compose file:

```bash
docker compose config
```

## Run the frontend directly

```bash
cd frontend
npm install
npm run dev
```

The direct dev server runs on port `3000` by default.

## Verification commands for the current baseline

```bash
cd frontend && npm test
cd frontend && npm run test:e2e
cd frontend && npm run build
curl -I http://127.0.0.1:3007
```

## Logo note

The repo did not contain `logo.png` or `nguontinlogo.png`, so the current homepage uses a lightweight placeholder SVG wordmark at `frontend/public/nguontin-logo.svg`. Replace that file with the official logo asset when it is ready.
