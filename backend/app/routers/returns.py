from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from loguru import logger

from app.database.db import get_db
from app.database.models import BorrowItem, BorrowTransaction, ReturnEvent, BorrowStatus
from app.utils.user_resolver import resolve_user
from app.services.email_service import email_service
from app.schemas.return_event import BatchReturnCreate
from app.utils.admin_emails import get_admin_email_list

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
    # Don't modify component.quantity - it represents total quantity
    # Available quantity is calculated dynamically: total - borrowed

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
    db.refresh(borrow_item)  # Refresh to get return_events
    
    # Send email notification to borrower
    try:
        borrower = transaction.borrower
        if borrower.email and borrow_item.component:
            # Get the most recent return event
            return_event = borrow_item.return_events[-1] if borrow_item.return_events else None
            
            if return_event:
                returned_items = [{
                    'component_name': borrow_item.component.name,
                    'category': borrow_item.component.category,
                    'quantity': return_event.quantity_returned
                }]
                
                email_service.send_return_notification(
                    borrower_email=borrower.email,
                    borrower_name=borrower.name,
                    returned_items=returned_items,
                    returned_at=return_event.returned_at,
                    returned_by=return_event.returned_by.name,
                    remarks=return_event.remarks
                )
                
                # Send admin email notifications
                admin_emails = get_admin_email_list(db)
                if admin_emails:
                    email_service.send_return_notification_to_admin(
                        borrower_name=borrower.name,
                        borrower_email=borrower.email,
                        borrower_tp_id=borrower.tp_id,
                        borrower_phone=borrower.phone,
                        returned_items=returned_items,
                        returned_at=return_event.returned_at,
                        returned_by=return_event.returned_by.name,
                        remarks=return_event.remarks,
                        admin_emails=admin_emails
                    )
    except Exception as e:
        # Log error but don't fail the transaction
        from loguru import logger
        logger.error(f"Failed to send return notification email: {e}")

    return {"message": "Return successful"}


@router.post("/batch")
def return_components_batch(
    data: BatchReturnCreate,
    db: Session = Depends(get_db)
):
    """
    Batch return endpoint - return multiple items at once with same PIC.
    Groups items by borrower and sends one email per borrower.
    """
    if not data.items:
        raise HTTPException(400, "No items provided for return")
    
    pic_user = resolve_user(db, data.pic_name)
    returned_at = datetime.utcnow()
    
    # Process each return item
    processed_returns = []  # List of (borrow_item, return_event, borrower) tuples
    completed_transactions = set()
    
    for item_data in data.items:
        borrow_item = (
            db.query(BorrowItem)
            .join(BorrowTransaction)
            .filter(
                BorrowTransaction.id == item_data.transaction_id,
                BorrowItem.component_id == item_data.component_id,
                BorrowTransaction.status != BorrowStatus.COMPLETED
            )
            .first()
        )
        
        if not borrow_item:
            raise HTTPException(404, f"Borrow record not found for transaction {item_data.transaction_id}, component {item_data.component_id}")
        
        remaining = borrow_item.quantity_borrowed - borrow_item.quantity_returned
        if item_data.quantity > remaining:
            raise HTTPException(
                400, 
                f"Return quantity ({item_data.quantity}) exceeds remaining borrowed quantity ({remaining}) "
                f"for component {borrow_item.component.name if borrow_item.component else 'Unknown'}"
            )
        
        # Update quantities
        borrow_item.quantity_returned += item_data.quantity
        
        # Create return event
        return_event = ReturnEvent(
            borrow_item_id=borrow_item.id,
            quantity_returned=item_data.quantity,
            remarks=item_data.remarks,
            returned_by_id=pic_user.id,
            returned_at=returned_at
        )
        db.add(return_event)
        
        # Check if transaction is now completed
        transaction = borrow_item.transaction
        all_items_returned = all(
            item.quantity_returned >= item.quantity_borrowed
            for item in transaction.items
        )
        
        if all_items_returned:
            transaction.status = BorrowStatus.COMPLETED
            completed_transactions.add(transaction.id)
        
        processed_returns.append((borrow_item, return_event, transaction.borrower))
    
    db.commit()
    
    # Refresh to get relationships
    for borrow_item, return_event, borrower in processed_returns:
        db.refresh(borrow_item)
        db.refresh(return_event)
    
    # Group returns by borrower email for email sending
    borrower_groups = {}
    
    for borrow_item, return_event, borrower in processed_returns:
        if not borrower.email or not borrow_item.component:
            continue
        
        borrower_email = borrower.email.lower()
        
        if borrower_email not in borrower_groups:
            borrower_groups[borrower_email] = {
                'borrower_name': borrower.name,
                'borrower_email': borrower_email,
                'borrower_tp_id': borrower.tp_id,
                'borrower_phone': borrower.phone,
                'returned_items': [],
                'returned_at': returned_at,
                'returned_by': pic_user.name
            }
        
        borrower_groups[borrower_email]['returned_items'].append({
            'component_name': borrow_item.component.name,
            'category': borrow_item.component.category,
            'quantity': return_event.quantity_returned,
            'remarks': return_event.remarks
        })
    
    # Send one email per borrower
    emails_sent = 0
    admin_emails = get_admin_email_list(db)
    
    for borrower_email, group_data in borrower_groups.items():
        try:
            success = email_service.send_return_notification(
                borrower_email=group_data['borrower_email'],
                borrower_name=group_data['borrower_name'],
                returned_items=group_data['returned_items'],
                returned_at=group_data['returned_at'],
                returned_by=group_data['returned_by'],
                remarks=None  # Individual remarks are in items
            )
            
            if success:
                emails_sent += 1
                logger.info(
                    f"Sent batch return email to {borrower_email} "
                    f"({len(group_data['returned_items'])} item(s))"
                )
            else:
                logger.warning(f"Failed to send batch return email to {borrower_email}")
        except Exception as e:
            logger.error(f"Error sending batch return email to {borrower_email}: {e}")
        
        # Send admin email notifications for this borrower group
        try:
            if admin_emails:
                email_service.send_return_notification_to_admin(
                    borrower_name=group_data['borrower_name'],
                    borrower_email=group_data['borrower_email'],
                    borrower_tp_id=group_data['borrower_tp_id'],
                    borrower_phone=group_data['borrower_phone'],
                    returned_items=group_data['returned_items'],
                    returned_at=group_data['returned_at'],
                    returned_by=group_data['returned_by'],
                    remarks=None,  # Individual remarks are in items
                    admin_emails=admin_emails
                )
        except Exception as e:
            logger.error(f"Error sending admin return notification email: {e}")
    
    return {
        "message": f"Batch return successful - {len(processed_returns)} item(s) returned",
        "items_returned": len(processed_returns),
        "emails_sent": emails_sent,
        "completed_transactions": list(completed_transactions)
    }
