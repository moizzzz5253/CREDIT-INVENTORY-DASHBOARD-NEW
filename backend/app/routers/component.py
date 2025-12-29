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


def validate_storage_location(
    storage_type: str,
    cabinet_number: int | None = None,
    shelf_number: int | None = None,
    container_id: int | None = None,
    drawer_index: int | None = None,
    storage_box_index: int | None = None,
    location_type: str | None = None,
    location_index: int | None = None,
    db: Session | None = None
):
    """Validate storage location parameters based on storage type"""
    errors = []
    
    if storage_type == "CABINET":
        if cabinet_number is None:
            errors.append("cabinet_number is required for CABINET storage")
        elif not (1 <= cabinet_number <= 10):
            errors.append("cabinet_number must be between 1 and 10")
        
        if shelf_number is None:
            errors.append("shelf_number is required for CABINET storage")
        elif not (0 <= shelf_number <= 5):
            errors.append("shelf_number must be between 0 and 5")
        
        # If shelf > 0, container is optional but if provided must be valid
        if container_id is not None:
            if db:
                container = db.query(Container).filter(Container.id == container_id).first()
                if not container:
                    errors.append(f"Container {container_id} not found")
                elif container.cabinet_number != cabinet_number:
                    errors.append(f"Container {container.code} does not belong to cabinet {cabinet_number}")
        
        # Drawer and storage_box must be None
        if drawer_index is not None:
            errors.append("drawer_index must be None for CABINET storage")
        if storage_box_index is not None:
            errors.append("storage_box_index must be None for CABINET storage")
    
    elif storage_type == "DRAWER":
        if drawer_index is None:
            errors.append("drawer_index is required for DRAWER storage")
        elif drawer_index < 1:
            errors.append("drawer_index must be >= 1")
        
        # Cabinet fields must be None
        if cabinet_number is not None:
            errors.append("cabinet_number must be None for DRAWER storage")
        if shelf_number is not None:
            errors.append("shelf_number must be None for DRAWER storage")
        if container_id is not None:
            errors.append("container_id must be None for DRAWER storage")
        if storage_box_index is not None:
            errors.append("storage_box_index must be None for DRAWER storage")
    
    elif storage_type == "STORAGE_BOX":
        if storage_box_index is None:
            errors.append("storage_box_index is required for STORAGE_BOX storage")
        elif storage_box_index < 1:
            errors.append("storage_box_index must be >= 1")
        
        # All other fields must be None
        if cabinet_number is not None:
            errors.append("cabinet_number must be None for STORAGE_BOX storage")
        if shelf_number is not None:
            errors.append("shelf_number must be None for STORAGE_BOX storage")
        if container_id is not None:
            errors.append("container_id must be None for STORAGE_BOX storage")
        if drawer_index is not None:
            errors.append("drawer_index must be None for STORAGE_BOX storage")
        
        # Storage boxes cannot have boxes/partitions
        if location_type and location_type != "NONE":
            errors.append("STORAGE_BOX cannot have BOX or PARTITION location_type")
    else:
        errors.append(f"Invalid storage_type: {storage_type}. Must be CABINET, DRAWER, or STORAGE_BOX")
    
    # Validate location_type and location_index (for boxes/partitions)
    if location_type:
        if location_type not in ["NONE", "BOX", "PARTITION"]:
            errors.append("location_type must be NONE, BOX, or PARTITION")
        elif location_type != "NONE":
            if location_index is None:
                errors.append("location_index is required when location_type is BOX or PARTITION")
            elif not (1 <= location_index <= 15):
                errors.append("location_index must be between 1 and 15")
    
    if errors:
        raise HTTPException(400, "; ".join(errors))


# ---------------------------------------------------
# CREATE COMPONENT
# ---------------------------------------------------
@router.post("/", response_model=ComponentRead)
def create_component(
    name: str = Form(...),
    category: str = Form(...),
    quantity: int = Form(...),
    
    # Storage type and location fields
    storage_type: str = Form("CABINET"),  # CABINET | DRAWER | STORAGE_BOX
    cabinet_number: int | None = Form(None),
    shelf_number: int | None = Form(None),
    container_id: int | None = Form(None),
    drawer_index: int | None = Form(None),
    storage_box_index: int | None = Form(None),
    location_type: str = Form("NONE"),   # NONE | BOX | PARTITION
    location_index: int | None = Form(None),

    remarks: str | None = Form(None),
    image: UploadFile | None = File(None),
    db: Session = Depends(get_db),
):
    # ---------------------------
    # Validate category
    # ---------------------------
    if category not in CATEGORIES:
        raise HTTPException(400, "Invalid category")

    # ---------------------------
    # Validate storage location
    # ---------------------------
    validate_storage_location(
        storage_type=storage_type,
        cabinet_number=cabinet_number,
        shelf_number=shelf_number,
        container_id=container_id,
        drawer_index=drawer_index,
        storage_box_index=storage_box_index,
        location_type=location_type,
        location_index=location_index,
        db=db
    )
    
    # ---------------------------
    # Save image (optional)
    # ---------------------------
    if image is None:
        # Use placeholder image path (ensure this file exists at uploads/components/placeholder.svg)
        file_path = os.path.join(UPLOAD_DIR, "placeholder.svg")
    else:
        filename = f"{name.replace(' ', '_')}_{image.filename}"
        file_path = os.path.join(UPLOAD_DIR, filename)

        with open(file_path, "wb") as f:
            f.write(image.file.read())

    # ---------------------------
    # Resolve location_type and location_index
    # ---------------------------
    resolved_location_type = location_type if location_type else "NONE"
    resolved_location_index = location_index if resolved_location_type != "NONE" else None

    # ---------------------------
    # Create component
    # ---------------------------
    component = Component(
        name=name,
        category=category,
        quantity=quantity,
        remarks=remarks,
        image_path=file_path,
        storage_type=storage_type,
        cabinet_number=cabinet_number,
        shelf_number=shelf_number,
        container_id=container_id,
        drawer_index=drawer_index,
        storage_box_index=storage_box_index,
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

    # Storage type and location fields
    storage_type: str | None = Form(None),
    cabinet_number: int | None = Form(None),
    shelf_number: int | None = Form(None),
    container_id: int | None = Form(None),
    drawer_index: int | None = Form(None),
    storage_box_index: int | None = Form(None),
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
    # Storage location change detection
    # -------------------------------------------------
    storage_changed = (
        storage_type is not None and storage_type != component.storage_type
    ) or (
        cabinet_number is not None and cabinet_number != component.cabinet_number
    ) or (
        shelf_number is not None and shelf_number != component.shelf_number
    ) or (
        container_id is not None and container_id != component.container_id
    ) or (
        drawer_index is not None and drawer_index != component.drawer_index
    ) or (
        storage_box_index is not None and storage_box_index != component.storage_box_index
    ) or (
        location_type is not None and location_type != component.location_type
    ) or (
        location_index is not None and location_index != component.location_index
    )

    if borrowed_qty > 0 and storage_changed:
        raise HTTPException(
            400,
            "Cannot change storage location while component is borrowed"
        )

    # -------------------------------------------------
    # Determine storage_type to use for validation
    # -------------------------------------------------
    effective_storage_type = storage_type if storage_type is not None else component.storage_type
    
    # Get effective values for validation
    # IMPORTANT: When storage_type changes, incompatible fields should be None
    # If storage_type changed, clear incompatible fields before validation
    effective_cabinet = cabinet_number
    effective_shelf = shelf_number
    effective_container = container_id
    effective_drawer = drawer_index
    effective_storage_box = storage_box_index
    
    # Only use existing values if storage_type hasn't changed
    if storage_type is None or storage_type == component.storage_type:
        # Storage type unchanged, use provided or existing values
        effective_cabinet = cabinet_number if cabinet_number is not None else component.cabinet_number
        effective_shelf = shelf_number if shelf_number is not None else component.shelf_number
        effective_container = container_id if container_id is not None else component.container_id
        effective_drawer = drawer_index if drawer_index is not None else component.drawer_index
        effective_storage_box = storage_box_index if storage_box_index is not None else component.storage_box_index
    else:
        # Storage type changed - clear incompatible fields
        if effective_storage_type == "DRAWER":
            effective_cabinet = None
            effective_shelf = None
            effective_container = None
            effective_storage_box = None
        elif effective_storage_type == "STORAGE_BOX":
            effective_cabinet = None
            effective_shelf = None
            effective_container = None
            effective_drawer = None
        elif effective_storage_type == "CABINET":
            effective_drawer = None
            effective_storage_box = None
    
    effective_location_type = location_type if location_type is not None else component.location_type
    effective_location_index = location_index if location_index is not None else component.location_index

    # -------------------------------------------------
    # Validate storage location if any storage field changed
    # -------------------------------------------------
    if storage_changed:
        validate_storage_location(
            storage_type=effective_storage_type,
            cabinet_number=effective_cabinet,
            shelf_number=effective_shelf,
            container_id=effective_container,
            drawer_index=effective_drawer,
            storage_box_index=effective_storage_box,
            location_type=effective_location_type,
            location_index=effective_location_index,
            db=db
        )

    # -------------------------------------------------
    # Apply storage fields
    # -------------------------------------------------
    new_storage_type = storage_type if storage_type is not None else component.storage_type
    
    if storage_type is not None:
        component.storage_type = storage_type
    
    # Apply cabinet_number
    if cabinet_number is not None:
        component.cabinet_number = cabinet_number
    elif new_storage_type != "CABINET":
        component.cabinet_number = None
    
    # Apply shelf_number
    if shelf_number is not None:
        component.shelf_number = shelf_number
    elif new_storage_type != "CABINET":
        component.shelf_number = None
    
    # Apply container_id
    if container_id is not None:
        component.container_id = container_id
    elif new_storage_type != "CABINET":
        component.container_id = None
    
    # Apply drawer_index
    if drawer_index is not None:
        component.drawer_index = drawer_index
    elif new_storage_type != "DRAWER":
        component.drawer_index = None
    
    # Apply storage_box_index
    if storage_box_index is not None:
        component.storage_box_index = storage_box_index
    elif new_storage_type != "STORAGE_BOX":
        component.storage_box_index = None

    # -------------------------------------------------
    # Apply location (box/partition)
    # -------------------------------------------------
    if location_type is not None:
        component.location_type = location_type
        if location_type == "NONE":
            component.location_index = None
        else:
            component.location_index = location_index
    elif location_index is not None:
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
        # Calculate current borrowed quantity
        borrowed_qty = sum(
            b.quantity_borrowed - b.quantity_returned
            for b in component.borrow_items
        )
        # Ensure new total quantity is not less than borrowed quantity
        if quantity < borrowed_qty:
            raise HTTPException(
                400,
                f"Cannot set quantity to {quantity}. There are {borrowed_qty} items currently borrowed. "
                f"Minimum quantity must be at least {borrowed_qty}."
            )
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