from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import date

from app.database.db import get_db
from app.database.models import BorrowTransaction

router = APIRouter(prefix="/history", tags=["History"])

@router.get("/")
def get_history(db: Session = Depends(get_db)):
    today = date.today()
    history = []

    transactions = (
        db.query(BorrowTransaction)
        .order_by(BorrowTransaction.borrowed_at.desc())
        .all()
    )

    for tx in transactions:
        for item in tx.items:
            for r in item.return_events:
                history.append({
                    "borrower": tx.borrower.name,
                    "component": item.component.name,
                    "borrowed_qty": item.quantity_borrowed,
                    "returned_qty": r.quantity_returned,
                    "returned_by": r.returned_by.name,
                    "remarks": r.remarks,
                    "borrowed_at": tx.borrowed_at,
                    "expected_return_date": tx.expected_return_date,
                    "returned_at": r.returned_at,
                    "status": "RETURNED" if tx.status == "COMPLETED" else "ACTIVE"
                })

    return history
