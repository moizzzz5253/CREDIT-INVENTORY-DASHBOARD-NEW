import os
import uuid
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
from app.utils.component_mapper import component_to_read

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

    location_type: str = Form("NONE"),   # NONE | BOX | PARTITION
    location_index: int | None = Form(None),

    remarks: str | None = Form(None),
    image: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    # ---------------------------
    # Validate category
    # ---------------------------
    if category not in CATEGORIES:
        raise HTTPException(400, "Invalid category")

    # ---------------------------
    # Validate container
    # ---------------------------
    container = db.query(Container).filter(Container.id == container_id).first()
    if not container:
        raise HTTPException(404, "Container not found")

    # ---------------------------
    # Validate location
    # ---------------------------
    if location_type not in ["NONE", "BOX", "PARTITION"]:
        raise HTTPException(400, "Invalid location type")

    if location_type == "NONE":
        resolved_location_type = "NONE"
        resolved_location_index = None
    else:
        if location_index is None or not (1 <= location_index <= 15):
            raise HTTPException(400, "Location index must be between 1 and 15")
        resolved_location_type = location_type
        resolved_location_index = location_index
    
    # ---------------------------
    # Save image
    # ---------------------------
    filename = f"{name.replace(' ', '_')}_{image.filename}"
    file_path = os.path.join(UPLOAD_DIR, filename)

    with open(file_path, "wb") as f:
        f.write(image.file.read())

    # ---------------------------
    # Create component
    # ---------------------------
    component = Component(
        name=name,
        category=category,
        quantity=quantity,
        remarks=remarks,
        image_path=file_path,
        container_id=container_id,
        location_type=resolved_location_type,
        location_index=resolved_location_index,
        is_deleted=False,
    )
    

    db.add(component)
    db.commit()
    db.refresh(component)
    db.refresh(component, attribute_names=["container"])
    added_date = component.created_at

    return {**component_to_read(component), "message": f"component added on {added_date}"}


# ---------------------------------------------------
# LIST COMPONENTS (HIDE DELETED)
# ---------------------------------------------------
@router.get("/", response_model=list[ComponentRead])
def list_components(db: Session = Depends(get_db)):
    components = (
        db.query(Component)
        .filter(Component.is_deleted == False)
        .all()
    )

    return [component_to_read(c) for c in components]


# ---------------------------------------------------
# UPDATE COMPONENT
# ---------------------------------------------------
UPLOAD_DIR = "uploads/components"

@router.put("/{component_id}", response_model=ComponentRead)
def update_component(
    component_id: int,

    name: str | None = Form(None),
    category: str | None = Form(None),
    quantity: int | None = Form(None),
    remarks: str | None = Form(None),

    container_id: int | None = Form(None),
    location_type: str | None = Form(None),
    location_index: int | None = Form(None),

    image: UploadFile | None = File(None),

    db: Session = Depends(get_db),
):
    # -------------------------------------------------
    # Fetch existing component (NO CREATION)
    # -------------------------------------------------
    component = (
        db.query(Component)
        .filter(
            Component.id == component_id,
            Component.is_deleted == False
        )
        .first()
    )

    if not component:
        raise HTTPException(404, "Component not found")

    # -------------------------------------------------
    # Borrow safety
    # -------------------------------------------------
    borrowed_qty = sum(
        b.quantity_borrowed - b.quantity_returned
        for b in component.borrow_items
    )

    # -------------------------------------------------
    # Quantity rule
    # -------------------------------------------------
    if quantity is not None and quantity < borrowed_qty:
        raise HTTPException(
            400,
            "Quantity cannot be less than borrowed quantity"
        )

    # -------------------------------------------------
    # Container / location safety
    # -------------------------------------------------
    container_change = (
        container_id is not None and
        container_id != component.container_id
    )

    location_change = (
        location_type is not None or
        location_index is not None
    )

    if borrowed_qty > 0 and (container_change or location_change):
        raise HTTPException(
            400,
            "Cannot change container or location while component is borrowed"
        )

    # -------------------------------------------------
    # Apply container
    # -------------------------------------------------
    if container_id is not None:
        target_container = (
            db.query(Container)
            .filter(Container.id == container_id)
            .first()
        )
        if not target_container:
            raise HTTPException(404, "Target container not found")
        component.container_id = container_id

    # -------------------------------------------------
    # Apply location
    # -------------------------------------------------
    if location_type is not None:
        if location_type not in ["NONE", "BOX", "PARTITION"]:
            raise HTTPException(400, "Invalid location type")

        if location_type == "NONE":
            component.location_type = "NONE"
            component.location_index = None
        else:
            if location_index is None or not (1 <= location_index <= 15):
                raise HTTPException(
                    400,
                    "Location index must be between 1 and 15"
                )
            component.location_type = location_type
            component.location_index = location_index

    # -------------------------------------------------
    # Apply basic fields
    # -------------------------------------------------
    if name is not None:
        component.name = name

    if category is not None:
        if category not in CATEGORIES:
            raise HTTPException(400, "Invalid category")
        component.category = category

    if quantity is not None:
        component.quantity = quantity

    if remarks is not None:
        component.remarks = remarks

    # -------------------------------------------------
    # IMAGE OVERWRITE (CRITICAL FIX)
    # -------------------------------------------------
    if image is not None:
        os.makedirs(UPLOAD_DIR, exist_ok=True)

        # Remove old image
        if component.image_path and os.path.exists(component.image_path):
            try:
                os.remove(component.image_path)
            except Exception:
                pass

        filename = f"{uuid.uuid4().hex}_{image.filename}"
        file_path = os.path.join(UPLOAD_DIR, filename)

        with open(file_path, "wb") as f:
            f.write(image.file.read())

        component.image_path = file_path

    # -------------------------------------------------
    # Timestamp
    # -------------------------------------------------
    component.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(component)
    db.refresh(component, attribute_names=["container"])

    return component_to_read(component)


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
        raise HTTPException(404, "Component not found")

    if component.is_deleted:
        raise HTTPException(400, "Component already deleted")

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
            400,
            "Component is currently borrowed"
        )

    component.is_deleted = True
    component.deleted_reason = payload.reason
    component.updated_at =  datetime.utcnow()
    component.deleted_at =  datetime.utcnow()

    db.commit()

    return {
        "message": "Component deleted successfully",
        "component_id": component.id,
        "deleted_at": component.deleted_at,
        "reason": component.deleted_reason
    }