from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import string

from app.database.db import get_db
from app.database.models import Container, Component
from app.schemas.container import ContainerRead
from app.schemas.component import ComponentRead
from app.services.container_service import generate_qr
from app.utils.component_mapper import component_to_read

router = APIRouter(
    prefix="/containers",
    tags=["Containers"]
)

# --------------------------------------------------
# INIT CONTAINERS
# --------------------------------------------------
@router.post("/init")
def initialize_containers(db: Session = Depends(get_db)):
    existing = db.query(Container).first()
    if existing:
        raise HTTPException(400, "Containers already initialized")

    container_codes = list(string.ascii_uppercase[:20])  # A–T
    created = 0

    for cabinet in range(1, 4):  # Cabinets 1–3
        for code in container_codes:
            container_code = f"{code}{cabinet}"
            qr_path = generate_qr(container_code)

            db.add(Container(
                code=container_code,
                cabinet_number=cabinet,
                qr_path=qr_path
            ))
            created += 1

    db.commit()
    return {
        "message": "Containers initialized",
        "total": created
    }


# --------------------------------------------------
# LIST CONTAINERS
# --------------------------------------------------
@router.get("/", response_model=list[ContainerRead])
def list_containers(
    cabinet_number: int | None = None,
    db: Session = Depends(get_db)
):
    query = db.query(Container)
    if cabinet_number is not None:
        query = query.filter(Container.cabinet_number == cabinet_number)
    return query.order_by(Container.code).all()


# --------------------------------------------------
# GET SINGLE CONTAINER
# --------------------------------------------------
@router.get("/{container_code}", response_model=ContainerRead)
def get_container(container_code: str, db: Session = Depends(get_db)):
    container = db.query(Container).filter(Container.code == container_code).first()
    if not container:
        raise HTTPException(404, "Container not found")
    return container


# --------------------------------------------------
# COMPONENTS IN CONTAINER
# --------------------------------------------------
@router.get("/{container_code}/components", response_model=dict)
def get_components_in_container(
    container_code: str,
    box: int | None = None,
    partition: int | None = None,
    db: Session = Depends(get_db)
):
    """Get components in container, with optional box/partition selection for deep linking"""
    container = db.query(Container).filter(Container.code == container_code).first()
    if not container:
        raise HTTPException(404, "Container not found")

    components = (
        db.query(Component)
        .filter(
            Component.container_id == container.id,
            Component.is_deleted == False
        )
        .all()
    )

    components_read = [component_to_read(c) for c in components]
    
    return {
        "components": components_read,
        "container_code": container_code,
        "selected_box": box,
        "selected_partition": partition
    }

# ---------------------------------------------------
# REGENERATE QR
# ---------------------------------------------------
@router.post("/regenerate-qr", response_model=dict)
def regenerate_qr_codes(db: Session = Depends(get_db)):
    containers = db.query(Container).all()

    if not containers:
        raise HTTPException(400, "No containers found")

    for container in containers:
        container.qr_path = generate_qr(
            container.code,
            overwrite=True
        )

    db.commit()

    return {
        "message": "QR codes regenerated successfully",
        "total": len(containers)
    }
