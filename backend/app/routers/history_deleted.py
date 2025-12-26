from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.database.models import Component

router = APIRouter(
    prefix="/history/deleted-components",
    tags=["History"]
)

@router.get("/")
def deleted_components_history(db: Session = Depends(get_db)):
    deleted = (
        db.query(Component)
        .filter(Component.is_deleted == True)
        .order_by(Component.deleted_at.desc())
        .all()
    )

    result = []
    for c in deleted:
        # Build container string with location if available
        container_str = c.container.code if c.container else "Unknown"
        if c.location_type and c.location_type != "NONE":
            if c.location_index is not None:
                container_str += f" - {c.location_type} {c.location_index}"
            else:
                container_str += f" - {c.location_type}"
        
        # Format dates with UTC timezone indicator
        added_at_str = None
        if c.created_at:
            added_at_str = c.created_at.isoformat() + 'Z' if not c.created_at.tzinfo else c.created_at.isoformat()
        
        deleted_at_str = None
        if c.deleted_at:
            deleted_at_str = c.deleted_at.isoformat() + 'Z' if not c.deleted_at.tzinfo else c.deleted_at.isoformat()
        
        result.append({
            "component_id": c.id,
            "component_name": c.name,
            "category": c.category,
            "quantity": c.quantity,
            "container": container_str,
            "added_at": added_at_str,
            "deleted_at": deleted_at_str,
            "reason": c.deleted_reason
        })
    
    return result
