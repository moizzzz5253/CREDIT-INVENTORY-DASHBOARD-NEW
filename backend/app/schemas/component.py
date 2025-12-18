from pydantic import BaseModel, Field
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

class ComponentDelete(BaseModel):
    reason: str

class ComponentUpdate(BaseModel):
    name: Optional[str] = Field(
        None,
        min_length=1,
        max_length=150,
        description="Updated component name"
    )

    category: Optional[str] = Field(
        None,
        description="Updated category (must match predefined categories)"
    )

    quantity: Optional[int] = Field(
        None,
        ge=0,
        description="Updated quantity (must be >= borrowed quantity)"
    )

    remarks: Optional[str] = Field(
        None,
        max_length=500,
        description="Optional remarks"
    )

    class Config:
        from_attributes = True