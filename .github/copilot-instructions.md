Purpose
-------
Concise guidance for AI agents to be immediately productive in this inventory management system.

Quick Overview
--------------
**Backend**: FastAPI app in `backend/app/` (entry: `main.py`). Routers in `routers/`, schemas in `schemas/`, SQLAlchemy models in `database/models.py`, business logic in `services/`.
**Frontend**: React + Vite in `frontend2/` using Tailwind CSS, axios for API calls, react-router for navigation.
**Deployment**: Docker Compose setup supports both local dev and containerized deployment with Cloudflare Tunnel support.
**Database**: SQLite at `backend/data/inventory.db` (containerized) or `backend/app/database/inventory.db` (local dev).

Development Commands
--------------------
- **Backend local**: `cd backend && pip install -r requirements.txt && uvicorn app.main:app --reload --port 8000`
- **Frontend local**: `cd frontend2 && npm install && npm run dev` (Vite dev server on `:5173`)
- **Docker**: `docker-compose up --build` (runs both, backend on `:8000`, frontend on `:80`)
- **Database**: Automatically created via SQLAlchemy `Base.metadata.create_all()` on app startup

Architecture & Key Data Flow
-----------------------------
1. **API Design**: Routers register in `main.py` via `include_router(...)`. Each domain has a router file (e.g., `borrow.py`, `component.py`, `container.py`, `location.py`, `reports.py`, `returns.py`, `history.py`).
2. **Request → Response**: Frontend (axios) → FastAPI endpoint (router) → Service layer (business logic) → SQLAlchemy DB models → Response schema (Pydantic) → Frontend.
3. **Database Relationships**: Admin/User → BorrowTransaction/ReturnEvent; Container → Component; Location (hierarchical: zone → cabinet → shelf → position).
4. **Special Features**:
   - **QR Codes**: Generated for containers/components via `qrcode` library, served at `/qr_codes/` (static mount), used in borrow workflow.
   - **Email**: SMTP service with overdue reminder scheduler (runs in background via lifespan events, emails in Kuala Lumpur time).
   - **Arduino Integration**: Optional serial communication for buzzer alerts (gracefully degrades if no Arduino/pyserial).

File Organization
-----------------
```
backend/app/
  routers/        → One .py per feature area; each registers endpoints
  services/       → Business logic (borrow_service, container_service, email_service, arduino_service, overdue_email_scheduler)
  schemas/        → Pydantic models (requests/responses per domain, e.g., component.py, container.py, borrow.py)
  database/
    models.py     → SQLAlchemy ORM models (Admin, User, Container, Component, BorrowTransaction, ReturnEvent, Location, etc.)
    db.py         → Engine, SessionLocal, Base, get_db() dependency
  core/
    config.py     → API_PORT, FRONTEND_PORT, get_base_url(), get_frontend_url() (network detection for QR codes)
    network.py    → get_local_ip() helper (detects LAN IP for multi-device QR scanning)
  utils/          → Mappers and validators (component_mapper.py, borrow_mapper.py, etc.)
frontend2/src/
  components/     → Reusable React components
  pages/          → Page-level components (routes)
  api/            → Axios API client with base config
  layouts/        → Layout wrappers
  router/         → React Router configuration
```

Conventions & Patterns
---------------------
- **New Endpoints**: Create function in `backend/app/routers/{domain}.py`, use Pydantic schema from `schemas/{domain}.py`, call service from `services/{domain}_service.py`. Register route in `main.py` if not already included.
- **Database Access**: Always inject `db: Session = Depends(get_db)` in router functions. Access via `db.query(Model).filter(...)`. Services call `db` passed from router.
- **Response Mapping**: Use mapper functions (e.g., `component_mapper.py`) to convert DB models to response schemas. Keeps API decoupled from DB.
- **Async Patterns**: Routers are async, services are sync (database operations are sync-only with SQLAlchemy core). Background tasks use APScheduler (see `overdue_email_scheduler.py`).
- **Environment**: Load from `.env` file (see `env.example`). Key vars: `API_PORT`, `FRONTEND_PORT`, `DATABASE_PATH` (Docker), `API_HOST`, `FRONTEND_URL`, email settings (`SMTP_SERVER`, `SMTP_PORT`, `SENDER_EMAIL`, `SENDER_PASSWORD`).

Critical Implementation Details
-------------------------------
- **Database Path in Docker**: Set via `DATABASE_PATH=/app/data/inventory.db` env var (see `docker-compose.yml`), ensures persistence across restarts.
- **Network Detection**: `config.py:get_base_url()` detects local IP for multi-device QR scanning. In containers, override via `API_HOST` env var.
- **CORS**: Currently `allow_origins=["*"]` — tighten to `["http://localhost:3000", "http://frontend:80"]` for production.
- **Static File Mounts**: `/qr_codes` and `/uploads` mounted in `main.py`; volumes in Docker map to `backend/qr_codes/` and `backend/uploads/components/`.
- **Lifespan Events**: Background scheduler (email) and Arduino service start on app startup, stop on shutdown (see `lifespan` context manager in `main.py`).

Adding Features (Examples)
--------------------------
- **New domain (e.g., "rental")**: Create `routers/rental.py`, `schemas/rental.py`, `services/rental_service.py`, add models to `database/models.py`, then `include_router(rental, prefix="/rentals")` in `main.py`.
- **New endpoint in existing domain**: Add function to `routers/{domain}.py` with `@app.get/post/put/delete(...)` and Pydantic schema; service handles DB logic.
- **Database migration**: Modify `database/models.py`, then either run `Base.metadata.create_all()` (dev) or use Alembic (production).

Testing & Debugging
-------------------
- **Backend debug**: Run with `--reload` flag; use `logger` from `loguru` (logs go to console and file if configured).
- **Frontend debug**: Vite dev server has HMR; check browser console for axios errors and network requests in DevTools.
- **Arduino testing**: Run `python test_arduino.py` from backend root (test buzzer connectivity without full app).
- **Docker logs**: `docker-compose logs -f backend` or `docker-compose logs -f frontend`.

Notes for AI Agents
-------------------
- Reference concrete files when proposing changes (e.g., `backend/app/routers/component.py`).
- Preserve module boundaries; avoid mixing router, service, and schema logic.
- Check `.env` and environment variables before hardcoding config; Docker and local dev may differ.
- Email/Arduino features are optional; handle gracefully if SMTP config or pyserial are missing.
- Frontend uses Tailwind CSS (no custom CSS framework); check `frontend2/package.json` for installed dependencies.
