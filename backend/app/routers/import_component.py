from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
import pandas as pd

from app.database.db import get_db
from app.database.models import Component, Container
from app.routers.constants import CATEGORIES

router = APIRouter(
    prefix="/import",
    tags=["Bulk Import"]
)


@router.post("/components")
def import_components_from_excel(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    if not file.filename.endswith(".xlsx"):
        raise HTTPException(400, "Only .xlsx files are supported")

    try:
        df = pd.read_excel(file.file)
    except Exception:
        raise HTTPException(400, "Invalid Excel file")

    required_columns = {"name", "category", "quantity", "container_code"}
    if not required_columns.issubset(df.columns):
        raise HTTPException(
            400,
            f"Missing required columns: {required_columns}"
        )

    inserted = 0
    errors = []

    for idx, row in df.iterrows():
        try:
            name = str(row["name"]).strip()
            category = str(row["category"]).strip()
            quantity = int(row["quantity"])
            container_code = str(row["container_code"]).strip()

            remarks = (
                str(row["remarks"]).strip()
                if "remarks" in df.columns and not pd.isna(row["remarks"])
                else None
            )

            location_type = (
                str(row["location_type"]).strip().upper()
                if "location_type" in df.columns and not pd.isna(row["location_type"])
                else "NONE"
            )

            location_index = (
                int(row["location_index"])
                if "location_index" in df.columns and not pd.isna(row["location_index"])
                else None
            )

            if category not in CATEGORIES:
                raise ValueError(f"Invalid category: {category}")

            container = (
                db.query(Container)
                .filter(Container.code == container_code)
                .first()
            )

            if not container:
                raise ValueError(f"Container {container_code} not found")

            if location_type not in ["NONE", "BOX", "PARTITION"]:
                raise ValueError("Invalid location_type")

            if location_type != "NONE" and not location_index:
                raise ValueError("location_index required")

            component = Component(
                name=name,
                category=category,
                quantity=quantity,
                remarks=remarks,
                image_path="uploads/components/placeholder.png",
                container_id=container.id,
                location_type=location_type,
                location_index=location_index,
                is_deleted=False
            )

            db.add(component)
            inserted += 1

        except Exception as e:
            errors.append({
                "row": idx + 2,
                "error": str(e)
            })

    db.commit()

    return {
        "inserted": inserted,
        "errors": errors
    }
