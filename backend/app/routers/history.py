from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import date

from app.database.db import get_db
from app.database.models import BorrowTransaction, ReturnEvent, Component, ComponentModificationHistory

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
                    "email": tx.borrower.email,
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


@router.get("/added-components/")
def get_added_components_history(db: Session = Depends(get_db)):
    """Get history of all components that were added (not deleted)"""
    components = (
        db.query(Component)
        .filter(Component.is_deleted == False)
        .order_by(Component.created_at.desc())
        .all()
    )

    result = []
    for c in components:
        # Format date with UTC timezone indicator
        created_at_str = None
        if c.created_at:
            created_at_str = c.created_at.isoformat() + 'Z' if not c.created_at.tzinfo else c.created_at.isoformat()
        
        result.append({
            "component_id": c.id,
            "component_name": c.name,
            "category": c.category,
            "quantity": c.quantity,
            "is_controlled": c.is_controlled,
            "date_added": created_at_str
        })
    
    return result


@router.get("/modified-components/")
def get_modified_components_history(db: Session = Depends(get_db)):
    """Get history of all component modifications grouped by component and modification time"""
    # Get all modification history entries, ordered by modification time
    modifications = (
        db.query(ComponentModificationHistory)
        .join(Component)
        .filter(Component.is_deleted == False)
        .order_by(ComponentModificationHistory.modified_at.desc())
        .all()
    )

    # Group modifications by component_id and modified_at (same timestamp = same update session)
    grouped_modifications = {}
    
    for mod in modifications:
        # Create a key based on component_id and modified_at (rounded to nearest second for grouping)
        # This groups changes made in the same update operation
        key = f"{mod.component_id}_{mod.modified_at.strftime('%Y-%m-%d %H:%M:%S')}"
        
        if key not in grouped_modifications:
            # Get component details
            component = db.query(Component).filter(Component.id == mod.component_id).first()
            if not component:
                continue
            
            # Format modification time with UTC timezone indicator
            modified_at_str = None
            if mod.modified_at:
                modified_at_str = mod.modified_at.isoformat() + 'Z' if not mod.modified_at.tzinfo else mod.modified_at.isoformat()
            
            grouped_modifications[key] = {
                "component_id": mod.component_id,
                "component_name": component.name,
                "modified_at": modified_at_str,
                "changes": []
            }
        
        # Format the change description
        field_display_name = {
            "quantity": "Quantity",
            "category": "Category",
            "is_controlled": "Is Controlled",
            "name": "Name",
            "remarks": "Remarks",
            "location": "Location"
        }.get(mod.field_name, mod.field_name.title())
        
        # Format values for display
        old_val = mod.old_value if mod.old_value != "None" else "N/A"
        new_val = mod.new_value if mod.new_value != "None" else "N/A"
        
        grouped_modifications[key]["changes"].append({
            "field": field_display_name,
            "old_value": old_val,
            "new_value": new_val,
            "display": f"{field_display_name}: {old_val} ➡️ {new_val}"
        })
    
    # Convert to list and sort by modified_at descending
    result = list(grouped_modifications.values())
    result.sort(key=lambda x: x["modified_at"] or "", reverse=True)
    
    return result
