Purpose
-------
This file gives concise, actionable guidance for AI coding agents working in this repository so they can be immediately productive.

Quick Overview
--------------
- Backend: FastAPI app under `backend/app/` (entry: `backend/app/main.py`). Routers live in `backend/app/routers/`, Pydantic schemas in `backend/app/schemas/`, database in `backend/app/database/` (SQLite `inventory.db`).
- Frontend: Vite + React in `frontend2/` (scripts in `frontend2/package.json`). The primary dev commands are `npm run dev` and `npm run build`.

Run & Develop (exact commands)
-----------------------------
- Backend (development):
  - From repository root: `cd backend` then `pip install -r requirements.txt` then `uvicorn app.main:app --reload --port 8000`
  - Or from root (if Python path configured): `uvicorn backend.app.main:app --reload --port 8000`
- Frontend (development):
  - `cd frontend2 && npm install` then `npm run dev`

Architecture & Patterns to Know
-------------------------------
- Router-first API: `backend/app/main.py` imports and `include_router(...)` for each feature area (e.g. `component`, `container`, `borrow`). Modify or add endpoints by creating/updating modules in `backend/app/routers/`.
- Separation of concerns:
  - `schemas/` — Pydantic request/response models (used by routers).
  - `services/` — business logic called by routers (e.g. `container_service.py`).
  - `database/` — SQLAlchemy `engine`, `SessionLocal`, and `Base` definitions (`db.py`). Models live in `database/models.py`.
  - `utils/` — mappers and small helpers (e.g., `borrow_mapper.py`, `component_mapper.py`).
- DB behavior: on app import `Base.metadata.create_all(bind=engine)` (see `backend/app/main.py`), so the SQLite file (`inventory.db`) will be created automatically in development.
- Static assets: `/qr_codes` is mounted via `app.mount("/qr_codes", ...)` (see `backend/app/main.py`), and uploads live in `backend/qr_codes/` and `backend/uploads/components/`.
- Network/config: base URL logic uses `backend/app/core/config.py` which calls `get_local_ip()` in `backend/app/core/network.py` — be careful when hardcoding host addresses in examples.
- CORS: currently `allow_origins=["*"]` in `main.py` — tighten before production.

Conventions & small rules
-------------------------
- Add new API endpoints in `backend/app/routers/` and register them in `main.py` (follow existing router patterns).
- Use Pydantic models from `backend/app/schemas/` for request validation and responses.
- Put DB access inside `services/` or explicitly use the `get_db()` dependency from `backend/app/database/db.py`.
- Use mappers in `utils/` to convert DB models ↔ response schemas.
- Frontend components follow `frontend2/src/` conventions; update imports relative to Vite aliasing or file paths.

Integration Points & External Dependencies
-----------------------------------------
- Backend: FastAPI, Uvicorn, SQLAlchemy, Alembic (migration tooling included in requirements), Pydantic. DB default is SQLite at `sqlite:///./inventory.db` (see `database/db.py`).
- Frontend: Vite with `@vitejs/plugin-react` (see `frontend2/package.json`). API calls go to backend base URL — check `backend/app/core/config.py` for default port `8000`.

When Editing or Adding Files — Examples
--------------------------------------
- To add an endpoint for components: add route functions to `backend/app/routers/component.py`, use Pydantic models from `backend/app/schemas/component.py`, and call business logic from `backend/app/services/*`.
- To change DB schema: update `backend/app/database/models.py` and prefer Alembic for migrations if the project adds migration scripts. For quick dev, the app will `create_all()` but production should use Alembic.

Notes for AI Agents
-------------------
- Always reference concrete files when proposing changes (example: `backend/app/routers/container.py`).
- Prefer minimal, focused patches that follow existing module boundaries.
- Avoid changing global CORS or DB defaults without explicit task context — call out required env changes instead.

Feedback
--------
If any repo-specific workflow is missing (CI, hosting, or special env setup), tell me which area to expand and provide any additional files (CI configs, deployment docs) to include.
