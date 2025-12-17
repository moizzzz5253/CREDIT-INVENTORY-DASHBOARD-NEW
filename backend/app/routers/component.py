import os
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.database.models import Component, Container
from app.schemas.component import ComponentRead
from app.routers.constants import CATEGORIES

router = APIRouter(
    prefix="/components",
    tags=["Components"]
)

UPLOAD_DIR = "uploads/components"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/", response_model=ComponentRead)
def create_component(
    name: str = Form(...),
    category: str = Form(...),
    quantity: int = Form(...),
    container_id: int = Form(...),
    remarks: str | None = Form(None),
    image: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    # Validate category
    if category not in CATEGORIES:
        raise HTTPException(status_code=400, detail="Invalid category")

    # Validate container
    container = db.query(Container).filter(Container.id == container_id).first()
    if not container:
        raise HTTPException(status_code=404, detail="Container not found")

    # Save image
    filename = f"{name.replace(' ', '_')}_{image.filename}"
    file_path = os.path.join(UPLOAD_DIR, filename)

    with open(file_path, "wb") as f:
        f.write(image.file.read())

    component = Component(
        name=name,
        category=category,
        quantity=quantity,
        remarks=remarks,
        image_path=file_path,
        container_id=container_id
    )

    db.add(component)
    db.commit()
    db.refresh(component)

    return component

@router.get("/", response_model=list[ComponentRead])
def list_components(db: Session = Depends(get_db)):
    return db.query(Component).all()

