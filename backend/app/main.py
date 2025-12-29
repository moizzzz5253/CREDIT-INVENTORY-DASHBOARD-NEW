from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv

# Load environment variables from .env file
# Specify explicit path to ensure .env is found
backend_dir = Path(__file__).parent.parent
env_path = backend_dir / ".env"
load_dotenv(dotenv_path=env_path, override=True)

from app.database.db import Base, engine
from app.routers import (
    component,
    container,
    borrow,
    returns,
    history,
    history_deleted,
    reports,
    import_component,
    database_manager
)
from app.routers import constants_router
from app.routers import email_admin
from app.services.overdue_email_scheduler import overdue_scheduler

# -----------------------------
# Database initialization
# -----------------------------
Base.metadata.create_all(bind=engine)

# -----------------------------
# Lifespan events
# -----------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    overdue_scheduler.start()
    yield
    # Shutdown
    overdue_scheduler.stop()

# -----------------------------
# App initialization
# -----------------------------
app = FastAPI(
    title="CREDIT Inventory Management System",
    version="1.0.0",
    lifespan=lifespan
)
app.mount("/qr_codes", StaticFiles(directory="qr_codes"), name="qr_codes")
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
# -----------------------------
# CORS (frontend support)
# -----------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------
# Routers
# -----------------------------
app.include_router(component.router)
app.include_router(container.router)
app.include_router(borrow.router)
app.include_router(returns.router)
app.include_router(history.router)
app.include_router(history_deleted.router)
app.include_router(import_component.router)
app.include_router(reports.router)
app.include_router(database_manager.router)
app.include_router(constants_router.router)
app.include_router(email_admin.router)


# -----------------------------app.include_router(reports.router)
# Health check
# -----------------------------


@app.get("/")
def root():
    return {"status": "CREDIT backend running"}
