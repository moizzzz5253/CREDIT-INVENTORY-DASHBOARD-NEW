from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date

from app.database.db import get_db
from app.database.models import (
    Borrower,
    BorrowTransaction,
    BorrowItem,
    BorrowStatus,
    Component
)
from app.schemas.borrow import BorrowCreate, BorrowTransactionRead

router = APIRouter(prefix="/borrow", tags=["Borrow"])

@router.post("/", response_model=BorrowTransactionRead)
def create_borrow(data: BorrowCreate, db: Session = Depends(get_db)):

    # Normalize borrower data
    name = data.borrower.name.strip().upper()
    tp_id = data.borrower.tp_id.strip().upper()
    phone = data.borrower.phone.strip()

    borrower = (
        db.query(Borrower)
        .filter(
            Borrower.name == name,
            Borrower.tp_id == tp_id,
            Borrower.phone == phone
        )
        .first()
    )

    if not borrower:
        borrower = Borrower(
            name=name,
            tp_id=tp_id,
            phone=phone
        )
        db.add(borrower)
        db.commit()
        db.refresh(borrower)

    transaction = BorrowTransaction(
        borrower_id=borrower.id,
        reason=data.reason,
        expected_return_date=data.expected_return_date
    )
    db.add(transaction)
    db.commit()
    db.refresh(transaction)

    for item in data.items:
        component = db.query(Component).filter(
            Component.id == item.component_id
        ).first()

        if not component:
            raise HTTPException(404, "Component not found")

        if component.quantity < item.quantity:
            raise HTTPException(
                400,
                f"Not enough quantity for {component.name}"
            )

        component.quantity -= item.quantity

        borrow_item = BorrowItem(
            transaction_id=transaction.id,
            component_id=component.id,
            quantity_borrowed=item.quantity
        )

        db.add(borrow_item)

    db.commit()
    db.refresh(transaction)

    return transaction

@router.get("/active")
def get_active_borrowers(db: Session = Depends(get_db)):
    today = date.today()

    transactions = (
        db.query(BorrowTransaction)
        .filter(BorrowTransaction.status != BorrowStatus.COMPLETED)
        .all()
    )

    results = []

    for t in transactions:
        derived_status = (
            BorrowStatus.OVERDUE
            if today > t.expected_return_date
            else BorrowStatus.ACTIVE
        )

        for item in t.items:
            remaining = item.quantity_borrowed - item.quantity_returned
            if remaining > 0:
                results.append({
                    "borrower_name": t.borrower.name,
                    "tp_id": t.borrower.tp_id,
                    "phone": t.borrower.phone,
                    "component": item.component.name,
                    "quantity": remaining,
                    "expected_return_date": t.expected_return_date,
                    "status": derived_status
                })

    return results

