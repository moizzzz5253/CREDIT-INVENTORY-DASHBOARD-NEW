from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date

from app.database.db import get_db
from app.database.models import BorrowTransaction, BorrowItem, Borrower, Component, BorrowStatus
from app.schemas.borrow import BorrowCreate, BorrowTransactionRead
from app.utils.user_resolver import resolve_user
from app.utils.borrow_mapper import borrow_transaction_to_read

router = APIRouter(prefix="/borrow", tags=["Borrow"])

@router.post("/", response_model=BorrowTransactionRead)
def create_borrow(data: BorrowCreate, db: Session = Depends(get_db)):
    pic_user = resolve_user(db, data.pic_name)

    borrower = Borrower(
        name=data.borrower.name.upper(),
        tp_id=data.borrower.tp_id.upper(),
        phone=data.borrower.phone
    )

    db.add(borrower)
    db.commit()
    db.refresh(borrower)

    tx = BorrowTransaction(
        borrower_id=borrower.id,
        borrowed_by_id=pic_user.id,
        reason=data.reason,
        expected_return_date=data.expected_return_date,
        status=BorrowStatus.ACTIVE
    )

    db.add(tx)
    db.commit()
    db.refresh(tx)

    for item in data.items:
        component = db.query(Component).filter(
            Component.id == item.component_id,
            Component.is_deleted == False
        ).first()

        if not component or component.quantity < item.quantity:
            raise HTTPException(400, "Invalid component or quantity")
        
        if data.expected_return_date < date.today():
            raise HTTPException(
                status_code=400,
                detail="Expected return date cannot be earlier than borrowed date"
    )
        component.quantity -= item.quantity

        db.add(BorrowItem(
            transaction_id=tx.id,
            component_id=component.id,
            quantity_borrowed=item.quantity
        ))

    db.commit()
    return borrow_transaction_to_read(tx)

@router.get("/active", tags=["Borrow"])
def get_active_borrows(db: Session = Depends(get_db)):
    today = date.today()

    transactions = (
        db.query(BorrowTransaction)
        .filter(BorrowTransaction.status != BorrowStatus.COMPLETED)
        .all()
    )

    results = []

    for tx in transactions:
        status = (
            "OVERDUE"
            if today > tx.expected_return_date
            else "ACTIVE"
        )

        for item in tx.items:
            remaining = item.quantity_borrowed - item.quantity_returned
            if remaining <= 0:
                continue

            results.append({
                "borrower_name": tx.borrower.name,
                "tp_id": tx.borrower.tp_id,
                "phone": tx.borrower.phone,
                "component_name": item.component.name,
                "remaining_quantity": remaining,
                "expected_return_date": tx.expected_return_date,
                "borrowed_by_pic": tx.borrowed_by.name,
                "status": status
            })

    return results

