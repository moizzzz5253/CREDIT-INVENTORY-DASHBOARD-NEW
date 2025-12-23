from pydantic import BaseModel, Field
from typing import Optional, Literal

class ComponentLocation(BaseModel):
    type: str = Field("NONE", description="NONE | BOX | PARTITION")
    index: Optional[int] = Field(None, ge=1, le=15)
    label: str

class ComponentLocationRead(BaseModel):
    type: str
    index: int | None
    label: str

class ComponentBase(BaseModel):
    name: str
    category: str
    quantity: int
    remarks: Optional[str] = None
    container_id: int
    
    location_type: Optional[str] = "NONE"
    location_index: Optional[int] = None


class ComponentCreate(ComponentBase):
    name: str
    category: str
    quantity: int
    container_id: int
    remarks: Optional[str]
    location: Optional[ComponentLocation] = None

class ComponentContainerInfo(BaseModel):
    id: int
    code: str

    class Config:
        from_attributes = True

class ComponentRead(BaseModel):
    id: int
    name: str
    category: str
    quantity: int
    remarks: str | None
    image_path: str
    container: ComponentContainerInfo
    borrowed_quantity: int
    available_quantity: int
    location: ComponentLocation
    class Config:
        from_attributes = True



class ComponentDelete(BaseModel):
    reason: str

class ComponentUpdate(BaseModel):
    name: Optional[str] = Field(
        None,
        min_length=1,
        max_length=150
    )

    category: Optional[str] = None

    quantity: Optional[int] = Field(
        None,
        ge=0
    )

    remarks: Optional[str] = Field(
        None,
        max_length=500
    )

    container_id: Optional[int] = None

    # 🔽 NEW (THIS FIXES YOUR ERROR)
    location_type: Optional[Literal["NONE", "BOX", "PARTITION"]] = None
    location_index: Optional[int] = Field(
        None,
        ge=1,
        le=15
    )
