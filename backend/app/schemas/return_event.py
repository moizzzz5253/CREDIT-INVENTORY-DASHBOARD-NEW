from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class ReturnCreate(BaseModel):
    transaction_id: int
    component_id: int
    quantity: int
    remarks: Optional[str]
    pic_name: str


class ReturnItemCreate(BaseModel):
    """Single item in a batch return."""
    transaction_id: int
    component_id: int
    quantity: int
    remarks: Optional[str] = None


class BatchReturnCreate(BaseModel):
    """Batch return request - multiple items with same PIC."""
    pic_name: str
    items: List[ReturnItemCreate]


class ReturnEventRead(BaseModel):
    quantity_returned: int
    remarks: Optional[str]
    returned_at: datetime
    returned_by: str
