from pydantic import BaseModel
from datetime import datetime, date
from typing import Optional


class HistoryRecord(BaseModel):
    borrower_name: str
    tp_id: str
    phone: str

    component_name: str

    borrowed_quantity: int
    returned_quantity: int

    borrow_reason: str

    borrowed_at: datetime
    expected_return_date: date

    returned_at: Optional[datetime]
    returned_by: Optional[str]
    return_remarks: Optional[str]

    status: str   # ACTIVE | OVERDUE | RETURNED
