from pydantic import BaseModel

class BorrowerCreate(BaseModel):
    name: str
    tp_id: str
    phone: str


class BorrowerRead(BorrowerCreate):
    id: int

    class Config:
        from_attributes = True
