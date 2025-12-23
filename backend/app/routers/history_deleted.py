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

    return [
        {
            "component": {
                "id": c.id,
                "name": c.name,
                "category": c.category,
            },
            "added_at": c.created_at,
            "deleted_at": c.deleted_at,
            "reason": c.deleted_reason
        }
        for c in deleted
    ]
