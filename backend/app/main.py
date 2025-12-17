#FastAPI
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

#database
from app.database.db import engine
from app.database import models

#CORS
from fastapi.middleware.cors import CORSMiddleware

#Routers
from app.routers import container
from app.routers import component
from app.routers import borrow, returns


# Create DB tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Lab Inventory Dashboard API",
    version="1.0.0"
)
# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://10.101.117.186:5173"
       
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Routers

app.mount(
    "/uploads",
    StaticFiles(directory="uploads"),
    name="uploads"
)

app.mount(
    "/qr_codes",
    StaticFiles(directory="qr_codes"),
    name="qr_codes"
)

#Routers Include
app.include_router(container.router)
app.include_router(component.router)
app.include_router(borrow.router)
app.include_router(returns.router)


