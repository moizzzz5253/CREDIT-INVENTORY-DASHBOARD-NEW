from pydantic import BaseModel, EmailStr

class BorrowerCreate(BaseModel):
    name: str
    tp_id: str
    phone: str
    email: EmailStr


class BorrowerRead(BorrowerCreate):
    id: int

    class Config:
        from_attributes = True
