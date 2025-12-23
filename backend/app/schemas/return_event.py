from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ReturnCreate(BaseModel):
    transaction_id: int
    component_id: int
    quantity: int
    remarks: Optional[str]
    pic_name: str


class ReturnEventRead(BaseModel):
    quantity_returned: int
    remarks: Optional[str]
    returned_at: datetime
    returned_by: str
