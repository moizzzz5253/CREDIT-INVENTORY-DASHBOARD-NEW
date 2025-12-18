import os
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.database.models import Component, Container, BorrowItem 
from app.schemas.component import (
    ComponentRead,
    ComponentUpdate,
    ComponentDelete,
)
from app.routers.constants import CATEGORIES

router = APIRouter(
    prefix="/components",
    tags=["Components"]
)

UPLOAD_DIR = "uploads/components"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# ---------------------------------------------------
# CREATE COMPONENT
# ---------------------------------------------------
@router.post("/", response_model=ComponentRead)
def create_component(
    name: str = Form(...),
    category: str = Form(...),
    quantity: int = Form(...),
    container_id: int = Form(...),
    remarks: str | None = Form(None),
    image: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    if category not in CATEGORIES:
        raise HTTPException(status_code=400, detail="Invalid category")

    container = db.query(Container).filter(Container.id == container_id).first()
    if not container:
        raise HTTPException(status_code=404, detail="Container not found")

    filename = f"{name.replace(' ', '_')}_{image.filename}"
    file_path = os.path.join(UPLOAD_DIR, filename)

    with open(file_path, "wb") as f:
        f.write(image.file.read())

    component = Component(
        name=name,
        category=category,
        quantity=quantity,
        remarks=remarks,
        image_path=file_path,
        container_id=container_id,
        is_deleted=False
    )

    db.add(component)
    db.commit()
    db.refresh(component)

    return component


# ---------------------------------------------------
# LIST COMPONENTS (HIDE DELETED)
# ---------------------------------------------------
@router.get("/", response_model=list[ComponentRead])
def list_components(db: Session = Depends(get_db)):
    return (
        db.query(Component)
        .filter(Component.is_deleted == False)
        .all()
    )


# ---------------------------------------------------
# UPDATE COMPONENT
# ---------------------------------------------------
@router.put("/{component_id}", response_model=ComponentRead)
def update_component(
    component_id: int,
    payload: ComponentUpdate,
    db: Session = Depends(get_db),
):
    component = db.query(Component).filter(Component.id == component_id).first()

    if not component:
        raise HTTPException(status_code=404, detail="Component not found")

    if component.is_deleted:
        raise HTTPException(status_code=400, detail="Component is deleted")

    if payload.category and payload.category not in CATEGORIES:
        raise HTTPException(status_code=400, detail="Invalid category")

    # Check active borrow quantity
    active_borrowed = (
        db.query(BorrowItem)
        .filter(
            BorrowItem.component_id == component_id,
            BorrowItem.quantity_borrowed > BorrowItem.quantity_returned
        )
        .with_entities(
            BorrowItem.quantity_borrowed,
            BorrowItem.quantity_returned
        )
        .all()
    )

    borrowed_qty = sum(
        b.quantity_borrowed - b.quantity_returned for b in active_borrowed
    )

    if payload.quantity is not None and payload.quantity < borrowed_qty:
        raise HTTPException(
            status_code=400,
            detail="Quantity less than borrowed amount"
        )

    for field, value in payload.dict(exclude_unset=True).items():
        setattr(component, field, value)

    component.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(component)

    return component


# ---------------------------------------------------
# DELETE COMPONENT (SOFT DELETE)
# ---------------------------------------------------
@router.post("/{component_id}/delete")
def delete_component(
    component_id: int,
    payload: ComponentDelete,
    db: Session = Depends(get_db),
):
    component = db.query(Component).filter(Component.id == component_id).first()

    if not component:
        raise HTTPException(status_code=404, detail="Component not found")

    if component.is_deleted:
        raise HTTPException(status_code=400, detail="Component already deleted")

    active_borrow = (
    db.query(BorrowItem)
    .filter(
        BorrowItem.component_id == component_id,
        BorrowItem.quantity_borrowed > BorrowItem.quantity_returned
    )
    .first()
)

    if active_borrow:
        raise HTTPException(
            status_code=400,
            detail="Component is currently borrowed"
        )

    component.is_deleted = True
    component.deleted_reason = payload.reason
    component.deleted_at = datetime.utcnow()

    db.commit()

    return {"message": "Component deleted successfully"}
