from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import date

from app.database.db import get_db
from app.database.models import BorrowTransaction, ReturnEvent

router = APIRouter(prefix="/history", tags=["History"])

@router.get("/")
def get_history(db: Session = Depends(get_db)):
    history = []

    transactions = (
        db.query(BorrowTransaction)
        .all()
    )

    for tx in transactions:
        for item in tx.items:
            # Skip items with deleted/missing components
            if not item.component:
                continue
                
            for r in item.return_events:
                # Format dates with UTC timezone indicator
                borrowed_at_str = None
                if tx.borrowed_at:
                    borrowed_at_str = tx.borrowed_at.isoformat() + 'Z' if not tx.borrowed_at.tzinfo else tx.borrowed_at.isoformat()
                
                returned_at_str = None
                if r.returned_at:
                    returned_at_str = r.returned_at.isoformat() + 'Z' if not r.returned_at.tzinfo else r.returned_at.isoformat()
                
                history.append({
                    "borrower_name": tx.borrower.name,
                    "tp_id": tx.borrower.tp_id,
                    "phone": tx.borrower.phone,
                    "component_name": item.component.name,
                    "component_category": item.component.category,
                    "borrowed_qty": item.quantity_borrowed,
                    "returned_qty": r.quantity_returned,
                    "returned_by": r.returned_by.name,
                    "borrowed_by_pic": tx.borrowed_by.name,
                    "remarks": r.remarks,
                    "borrow_reason": tx.reason,
                    "borrowed_at": borrowed_at_str,
                    "expected_return_date": tx.expected_return_date.isoformat() if isinstance(tx.expected_return_date, date) else tx.expected_return_date,
                    "returned_at": returned_at_str,
                    "status": "RETURNED" if tx.status == "COMPLETED" else "ACTIVE"
                })

    # Sort by returned_at descending (newest first)
    history.sort(key=lambda x: x["returned_at"] or "", reverse=True)
    
    return history
