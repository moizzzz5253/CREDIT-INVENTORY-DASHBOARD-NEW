from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import string

from app.database.db import get_db
from app.database.models import Container
from app.schemas.container import ContainerRead
from app.services.container_service import generate_qr

from app.database.models import Component
from app.schemas.component import ComponentRead

router = APIRouter(
    prefix="/containers",
    tags=["Containers"]
)


@router.post("/init", response_model=dict)
def initialize_containers(db: Session = Depends(get_db)):
    existing = db.query(Container).first()
    if existing:
        raise HTTPException(
            status_code=400,
            detail="Containers already initialized"
        )

    container_codes = list(string.ascii_uppercase[:20])  # A–T

    created = 0
    for cabinet in range(1, 4):  # 3 cabinets
        for code in container_codes:
            container_code = f"{code}{cabinet}"
            qr_path = generate_qr(container_code)

            db_container = Container(
                code=container_code,
                cabinet_number=cabinet,
                qr_path=qr_path
            )
            db.add(db_container)
            created += 1

    db.commit()

    return {
        "message": "Containers initialized successfully",
        "total_containers": created
    }
@router.post("/regenerate-qr", response_model=dict)
def regenerate_qr_codes(db: Session = Depends(get_db)):
    containers = db.query(Container).all()

    if not containers:
        raise HTTPException(
            status_code=400,
            detail="No containers found to regenerate"
        )

    for container in containers:
        new_qr_path = generate_qr(
            container.code,
            overwrite=True
        )
        container.qr_path = new_qr_path

    db.commit()

    return {
        "message": "QR codes regenerated successfully",
        "total": len(containers)
    }


@router.get("/", response_model=list[ContainerRead])
def list_containers(db: Session = Depends(get_db)):
    return db.query(Container).order_by(Container.code).all()

@router.get("/{container_code}/components", response_model=list[ComponentRead])
def get_components_in_container(
    container_code: str,
    db: Session = Depends(get_db)
):
    container = db.query(Container).filter(
        Container.code == container_code
    ).first()

    if not container:
        raise HTTPException(
            status_code=404,
            detail="Container not found"
        )

    return (
        db.query(Component)
        .filter(Component.container_id == container.id)
        .all()
    )