from pydantic import BaseModel
from typing import Optional

class ComponentBase(BaseModel):
    name: str
    category: str
    quantity: int
    remarks: Optional[str] = None
    container_id: int


class ComponentCreate(ComponentBase):
    pass


class ComponentRead(ComponentBase):
    id: int
    image_path: str

    class Config:
        from_attributes = True
