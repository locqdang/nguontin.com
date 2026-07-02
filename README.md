# nguontin.com

NguonTin is an early Vietnamese-first homepage prototype for a journalist-to-expert matching product.

## Current baseline

- Frontend: Next.js app in `frontend/`
- Backend: FastAPI app in `backend/`
- Docker Compose services: `frontend`, `backend`
- Frontend host port: `3007`
- Frontend container port: `3000`
- Backend host port: `8008`
- Backend container port: `8000`
- Current homepage language: Vietnamese
- Backend health endpoint: `http://127.0.0.1:8008/health`
- Test baseline: Vitest and Playwright smoke coverage for the homepage

## Run locally with Docker Compose

From the repo root:

```bash
cp .env.example .env
docker compose up --build
```

Then open:

```text
Frontend: http://127.0.0.1:3007
Backend health: http://127.0.0.1:8008/health
```

The homepage now includes a backend API status block. Inside Compose, the frontend reaches the backend through the stable service name `backend` via `INTERNAL_API_BASE_URL=http://backend:8000`.

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

## Run the backend directly

If you run the backend outside Docker, the backend now loads the repo-root `.env` first and then `.env.local` as an override. That lets local debug use local callback and frontend URLs without changing production-like defaults in `.env`.

### Terminal

```bash
cd /home/loc/projects/nguontin.com
set -a
. ./.env
set +a
uv run --directory backend uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Note: shell sourcing only works reliably when `.env` values with spaces are quoted, for example `APP_NAME="NguonTin API"`.

### VS Code debug

Use the checked-in launch config:

```text
.vscode/launch.json → NguonTin Backend (debug)
```

That debug profile points at `.env.local`, and the backend itself loads `.env` first plus `.env.local` overrides for local debugging values such as `FRONTEND_BASE_URL` and `GOOGLE_OAUTH_REDIRECT_URI`.

Install backend dependencies in a local virtual environment first if you want to run it outside Docker.

## Verification commands for the current baseline

```bash
python3 -m py_compile backend/app/main.py
cd frontend && npm test
cd frontend && npm run test:e2e
cd frontend && npm run build
docker compose up -d --build
curl http://127.0.0.1:8008/health
curl -I http://127.0.0.1:3007
```

## Logo note

The repo did not contain `logo.png` or `nguontinlogo.png`, so the current homepage uses a lightweight placeholder SVG wordmark at `frontend/public/nguontin-logo.svg`. Replace that file with the official logo asset when it is ready.
