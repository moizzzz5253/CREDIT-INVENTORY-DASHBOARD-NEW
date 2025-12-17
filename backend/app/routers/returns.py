from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.database.models import BorrowItem, BorrowStatus

router = APIRouter(prefix="/return", tags=["Return"])

@router.post("/")
def return_component(
    borrow_item_id: int,
    quantity_returned: int,
    db: Session = Depends(get_db)
):

    item = db.query(BorrowItem).filter(
        BorrowItem.id == borrow_item_id
    ).first()

    if not item:
        raise HTTPException(404, "Borrow item not found")

    remaining = item.quantity_borrowed - item.quantity_returned

    if quantity_returned > remaining:
        raise HTTPException(400, "Return quantity exceeds borrowed amount")

    item.quantity_returned += quantity_returned
    item.component.quantity += quantity_returned

    transaction = item.transaction

    # Check if transaction is completed
    all_returned = all(
        i.quantity_borrowed == i.quantity_returned
        for i in transaction.items
    )

    if all_returned:
        transaction.status = BorrowStatus.COMPLETED

    db.commit()

    return {"message": "Return processed successfully"}
