def borrow_transaction_to_read(tx):
    return {
        "id": tx.id,
        "borrower": {
            "name": tx.borrower.name,
            "tp_id": tx.borrower.tp_id,
            "phone": tx.borrower.phone,
        },
        "borrowed_by": {
            "id": tx.borrowed_by.id,
            "name": tx.borrowed_by.name,
        },
        "reason": tx.reason,
        "borrowed_at": tx.borrowed_at.isoformat(),  # 🔑 FIX
        "expected_return_date": tx.expected_return_date,
        "status": tx.status,
        "items": [
            {
                "component_id": item.component_id,
                "quantity_borrowed": item.quantity_borrowed,
                "quantity_returned": item.quantity_returned,
            }
            for item in tx.items
        ],
    }
