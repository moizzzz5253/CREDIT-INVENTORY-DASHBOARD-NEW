from pydantic import BaseModel

class ContainerRead(BaseModel):
    id: int
    code: str
    cabinet_number: int
    shelf_number: int | None = None
    qr_path: str

    class Config:
        from_attributes = True
