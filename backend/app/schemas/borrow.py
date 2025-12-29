from pydantic import BaseModel
from typing import List
from datetime import date
from app.schemas.borrower import BorrowerCreate


class BorrowItemCreate(BaseModel):
    component_id: int
    quantity: int


class BorrowCreate(BaseModel):
    borrower: BorrowerCreate
    items: List[BorrowItemCreate]

    reason: str
    expected_return_date: date

    pic_name: str   # 👈 PIC entered manually (no login)


class BorrowItemRead(BaseModel):
    component_id: int
    quantity_borrowed: int
    quantity_returned: int


class BorrowTransactionRead(BaseModel):
    id: int
    status: str
    borrowed_at: str
    expected_return_date: date

    borrower: dict        # name, tp_id, phone, email
    borrowed_by: dict     # PIC name

    items: List[BorrowItemRead]

    class Config:
        from_attributes = True
