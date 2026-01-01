import os
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.database.models import Component, Container, BorrowItem, Admin, ComponentModificationHistory
from app.schemas.component import (
    ComponentRead,
    ComponentUpdate,
    ComponentDelete,
)
from app.routers.constants import CATEGORIES
from app.utils.component_mapper import component_to_read, generate_location_label
from app.core.security import verify_password, DEFAULT_ADMIN_PASSWORD
from app.services.email_service import email_service
from app.utils.admin_emails import get_admin_email_list

router = APIRouter(
    prefix="/components",
    tags=["Components"]
)

UPLOAD_DIR = "uploads/components"
os.makedirs(UPLOAD_DIR, exist_ok=True)


def track_component_change(
    db: Session,
    component_id: int,
    field_name: str,
    old_value: any,
    new_value: any
):
    """Helper function to track component field changes"""
    if old_value != new_value:
        # Convert values to strings for storage
        old_str = str(old_value) if old_value is not None else "None"
        new_str = str(new_value) if new_value is not None else "None"
        
        history_entry = ComponentModificationHistory(
            component_id=component_id,
            field_name=field_name,
            old_value=old_str,
            new_value=new_str,
            modified_at=datetime.utcnow()
        )
        db.add(history_entry)


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
    is_controlled: bool = Form(False),
    admin_password: str | None = Form(None),
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
    # Validate admin password if controlled
    # ---------------------------
    if is_controlled:
        if not admin_password:
            raise HTTPException(400, "Admin password is required for controlled components")
        
        # Get admin record
        admin = db.query(Admin).first()
        if admin is None:
            # No admin record exists, use default password
            if admin_password != DEFAULT_ADMIN_PASSWORD:
                raise HTTPException(400, "Invalid admin password")
        else:
            # Verify password
            is_valid = verify_password(admin_password, admin.password_hash)
            if not is_valid:
                raise HTTPException(400, "Invalid admin password")

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
        is_controlled=is_controlled,
    )
    

    db.add(component)
    db.commit()
    db.refresh(component)
    db.refresh(component, attribute_names=["container"])
    added_date = component.created_at
    
    # Send email notification if component is controlled
    if is_controlled:
        try:
            admin_emails = get_admin_email_list(db)
            if admin_emails:
                email_service.send_component_added_notification(
                    component_name=component.name,
                    category=component.category,
                    quantity=component.quantity,
                    date_added=component.created_at,
                    remarks=component.remarks,
                    admin_emails=admin_emails
                )
        except Exception as e:
            from loguru import logger
            logger.error(f"Failed to send component added notification email: {e}")

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
    is_controlled: bool | None = Form(None),
    admin_password: str | None = Form(None),

    db: Session = Depends(get_db),
):
    # Normalize sentinel values (0) to None for optional foreign keys
    if container_id == 0:
        container_id = None
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
    # Check if password is required for modifications
    # Password is required if:
    # 1. Component is currently controlled AND any field is being modified
    # 2. Component is becoming controlled (is_controlled changing from False to True)
    # 3. Component is becoming uncontrolled (is_controlled changing from True to False) - existing logic
    # -------------------------------------------------
    is_becoming_controlled = (
        is_controlled is not None and 
        is_controlled == True and 
        component.is_controlled == False
    )
    is_becoming_uncontrolled = (
        is_controlled is not None and 
        is_controlled == False and 
        component.is_controlled == True
    )
    is_currently_controlled = component.is_controlled == True
    has_any_modification = any([
        name is not None,
        category is not None,
        quantity is not None,
        remarks is not None,
        storage_type is not None,
        cabinet_number is not None,
        shelf_number is not None,
        container_id is not None,
        drawer_index is not None,
        storage_box_index is not None,
        location_type is not None,
        location_index is not None,
        image is not None,
        is_controlled is not None  # Include is_controlled in modification check
    ])
    
    password_required = (
        (is_currently_controlled and has_any_modification) or
        is_becoming_controlled or
        is_becoming_uncontrolled
    )
    
    if password_required:
        if not admin_password:
            raise HTTPException(
                400, 
                "Admin password is required to modify controlled components or change controlled status"
            )
        
        # Verify password
        admin = db.query(Admin).first()
        if admin is None:
            # No admin record exists, use default password
            if admin_password != DEFAULT_ADMIN_PASSWORD:
                raise HTTPException(400, "Invalid admin password")
        else:
            # Verify password
            is_valid = verify_password(admin_password, admin.password_hash)
            if not is_valid:
                raise HTTPException(400, "Invalid admin password")

    # -------------------------------------------------
    # Collect changes for email notification (before applying changes)
    # -------------------------------------------------
    changes_for_email = []
    component_name_for_email = component.name
    component_category_for_email = component.category

    # -------------------------------------------------
    # Get old location label before any changes (for tracking)
    # -------------------------------------------------
    old_location_label = generate_location_label(component)

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
    # Track location change (after all storage fields applied)
    # -------------------------------------------------
    if storage_changed or location_type is not None or location_index is not None:
        # Refresh component to get updated container relationship if container_id changed
        # We need to flush first to ensure container_id is saved, then refresh
        db.flush()
        # Refresh container relationship if container_id was modified
        if container_id is not None or storage_type is not None:
            db.refresh(component, attribute_names=["container"])
        
        new_location_label = generate_location_label(component)
        if old_location_label != new_location_label:
            # Track location change for email
            changes_for_email.append({
                'field_name': 'location',
                'old_value': old_location_label,
                'new_value': new_location_label
            })
            # Track location change in history
            track_component_change(db, component_id, "location", old_location_label, new_location_label)

    # -------------------------------------------------
    # Handle controlled status change
    # -------------------------------------------------
    if is_controlled is not None:
        # Check if controlled status is being changed
        if is_controlled != component.is_controlled:
            # Track controlled status change for email
            changes_for_email.append({
                'field_name': 'is_controlled',
                'old_value': "Yes" if component.is_controlled else "No",
                'new_value': "Yes" if is_controlled else "No"
            })
            
            # Track controlled status change in history
            track_component_change(
                db, 
                component_id, 
                "is_controlled", 
                "Yes" if component.is_controlled else "No",
                "Yes" if is_controlled else "No"
            )
            # Update controlled status
            component.is_controlled = is_controlled

    # -------------------------------------------------
    # Track changes and apply basic fields
    # -------------------------------------------------
    if name is not None and name != component.name:
        # Track name change for email
        changes_for_email.append({
            'field_name': 'name',
            'old_value': component.name,
            'new_value': name
        })
        # Track name change in history
        track_component_change(db, component_id, "name", component.name, name)
        component.name = name

    if category is not None:
        if category not in CATEGORIES:
            raise HTTPException(400, "Invalid category")
        if category != component.category:
            # Track category change for email
            changes_for_email.append({
                'field_name': 'category',
                'old_value': component.category,
                'new_value': category
            })
        # Track category change in history
        track_component_change(db, component_id, "category", component.category, category)
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
        if quantity != component.quantity:
            # Track quantity change for email
            changes_for_email.append({
                'field_name': 'quantity',
                'old_value': component.quantity,
                'new_value': quantity
            })
        # Track quantity change in history
        track_component_change(db, component_id, "quantity", component.quantity, quantity)
        component.quantity = quantity

    if remarks is not None:
        old_remarks = component.remarks if component.remarks else "None"
        new_remarks = remarks if remarks else "None"
        if old_remarks != new_remarks:
            # Track remarks change for email
            changes_for_email.append({
                'field_name': 'remarks',
                'old_value': old_remarks,
                'new_value': new_remarks
            })
        # Track remarks change in history
        track_component_change(db, component_id, "remarks", old_remarks, new_remarks)
        component.remarks = remarks

    # -------------------------------------------------
    # IMAGE OVERWRITE (CRITICAL FIX)
    # -------------------------------------------------
    if image is not None:
        # Track image change for email
        old_image = component.image_path if component.image_path else "None"
        changes_for_email.append({
            'field_name': 'image',
            'old_value': old_image,
            'new_value': image.filename if image.filename else "Updated"
        })
        
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
    modified_at = component.updated_at

    db.commit()
    db.refresh(component)
    db.refresh(component, attribute_names=["container"])

    # -------------------------------------------------
    # Send email notification if component is controlled and has changes
    # -------------------------------------------------
    if component.is_controlled and changes_for_email:
        try:
            admin_emails = get_admin_email_list(db)
            if admin_emails:
                email_service.send_controlled_component_modified_notification(
                    component_name=component_name_for_email,
                    category=component_category_for_email,
                    changes=changes_for_email,
                    modified_at=modified_at,
                    admin_emails=admin_emails
                )
        except Exception as e:
            # Log error but don't fail the update
            from loguru import logger
            logger.error(f"Failed to send controlled component modified notification email: {e}")

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

    # Check if component is controlled and verify password if needed
    if component.is_controlled:
        if not payload.admin_password:
            raise HTTPException(
                400,
                "Admin password is required to delete controlled components"
            )
        
        # Verify password
        admin = db.query(Admin).first()
        if admin is None:
            # No admin record exists, use default password
            if payload.admin_password != DEFAULT_ADMIN_PASSWORD:
                raise HTTPException(400, "Invalid admin password")
        else:
            # Verify password
            is_valid = verify_password(payload.admin_password, admin.password_hash)
            if not is_valid:
                raise HTTPException(400, "Invalid admin password")

    # Capture component details before deletion for email notification
    component_name = component.name
    component_category = component.category
    component_quantity = component.quantity
    
    component.is_deleted = True
    component.deleted_reason = payload.reason
    component.updated_at =  datetime.utcnow()
    component.deleted_at =  datetime.utcnow()

    db.commit()
    
    # Send email notification for component deletion
    try:
        admin_emails = get_admin_email_list(db)
        if admin_emails:
            email_service.send_component_deleted_notification(
                component_name=component_name,
                category=component_category,
                quantity=component_quantity,
                deletion_reason=payload.reason,
                deleted_at=component.deleted_at,
                admin_emails=admin_emails
            )
    except Exception as e:
        from loguru import logger
        logger.error(f"Failed to send component deleted notification email: {e}")

    return {
        "message": "Component deleted successfully",
        "component_id": component.id,
        "deleted_at": component.deleted_at,
        "reason": component.deleted_reason
    }