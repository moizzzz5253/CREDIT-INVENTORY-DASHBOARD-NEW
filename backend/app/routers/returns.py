from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.database.models import BorrowItem, BorrowTransaction, ReturnEvent, BorrowStatus
from app.utils.user_resolver import resolve_user

router = APIRouter(prefix="/returns", tags=["Returns"])

@router.post("/")
def return_component(
    transaction_id: int,
    component_id: int,
    quantity: int,
    pic_name: str,
    remarks: str | None = None,
    db: Session = Depends(get_db)
):
    pic_user = resolve_user(db, pic_name)

    borrow_item = (
        db.query(BorrowItem)
        .join(BorrowTransaction)
        .filter(
            BorrowTransaction.id == transaction_id,
            BorrowItem.component_id == component_id,
            BorrowTransaction.status != BorrowStatus.COMPLETED
        )
        .first()
    )

    if not borrow_item:
        raise HTTPException(404, "Borrow record not found")

    remaining = borrow_item.quantity_borrowed - borrow_item.quantity_returned
    if quantity > remaining:
        raise HTTPException(400, "Return exceeds borrowed quantity")

    borrow_item.quantity_returned += quantity
    borrow_item.component.quantity += quantity

    db.add(ReturnEvent(
        borrow_item_id=borrow_item.id,
        quantity_returned=quantity,
        remarks=remarks,
        returned_by_id=pic_user.id
    ))

    # Only mark transaction as COMPLETED when ALL items in the transaction are fully returned
    transaction = borrow_item.transaction
    all_items_returned = all(
        item.quantity_returned >= item.quantity_borrowed
        for item in transaction.items
    )
    
    if all_items_returned:
        transaction.status = BorrowStatus.COMPLETED

    db.commit()

    return {"message": "Return successful"}
