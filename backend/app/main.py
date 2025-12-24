from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.database.db import Base, engine
from app.routers import (
    component,
    container,
    borrow,
    returns,
    history,
    history_deleted,
    reports,
    import_component
)
from app.routers import constants_router

# -----------------------------
# Database initialization
# -----------------------------
Base.metadata.create_all(bind=engine)

# -----------------------------
# App initialization
# -----------------------------
app = FastAPI(
    title="CREDIT Inventory Management System",
    version="1.0.0"
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
app.include_router(constants_router.router)


# -----------------------------app.include_router(reports.router)
# Health check
# -----------------------------


@app.get("/")
def root():
    return {"status": "CREDIT backend running"}
