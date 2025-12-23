from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from io import BytesIO
from datetime import datetime

from openpyxl import Workbook

from app.database.db import get_db
from app.database.models import Component, BorrowItem

router = APIRouter(
    prefix="/reports",
    tags=["Reports"]
)


@router.get("/components/export")
def export_components_report(db: Session = Depends(get_db)):
    components = (
        db.query(Component)
        .filter(Component.is_deleted == False)
        .all()
    )

    wb = Workbook()
    ws = wb.active
    ws.title = "Component Report"

    # -------------------------
    # Header row
    # -------------------------
    ws.append([
        "Component Name",
        "Category",
        "Container",
        "Location Type",
        "Location Index",
        "Total Quantity",
        "Borrowed Quantity",
        "Date Added"
    ])

    # -------------------------
    # Data rows
    # -------------------------
    for component in components:
        borrowed_qty = sum(
            (item.quantity_borrowed - item.quantity_returned)
            for item in component.borrow_items
        )

        ws.append([
            component.name,
            component.category,
            component.container.code,
            component.location_type,
            component.location_index,
            component.quantity,
            borrowed_qty,
            component.created_at.strftime("%d/%m/%Y")
        ])

    # -------------------------
    # Stream file
    # -------------------------
    output = BytesIO()
    wb.save(output)
    output.seek(0)

    filename = f"component_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"

    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )
