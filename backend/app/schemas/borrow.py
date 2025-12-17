from pydantic import BaseModel
from typing import List
from datetime import date


class BorrowerSchema(BaseModel):
    name: str
    tp_id: str
    phone: str


class BorrowItemCreate(BaseModel):
    component_id: int
    quantity: int


class BorrowCreate(BaseModel):
    borrower: BorrowerSchema
    reason: str
    expected_return_date: date
    items: List[BorrowItemCreate]


class BorrowItemRead(BaseModel):
    id: int
    component_id: int
    quantity_borrowed: int
    quantity_returned: int

    class Config:
        from_attributes = True


class BorrowTransactionRead(BaseModel):
    id: int
    borrower_id: int
    reason: str
    expected_return_date: date
    status: str
    items: List[BorrowItemRead]

    class Config:
        from_attributes = True
