import os
import uuid
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Form
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import pandas as pd
from datetime import datetime

from app.database.db import get_db
from app.database.models import Component, Container
from app.routers.constants import CATEGORIES

router = APIRouter(
    prefix="/import",
    tags=["Bulk Import"]
)

UPLOAD_DIR = "uploads/components"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.get("/components/template")
def download_import_template(db: Session = Depends(get_db)):
    """Generate and download Excel template for component import"""
    from io import BytesIO
    from openpyxl import Workbook
    from openpyxl.worksheet.datavalidation import DataValidation
    
    # Get container codes from database
    containers = db.query(Container).order_by(Container.code).all()
    container_codes = [c.code for c in containers] if containers else ['A1', 'B2', 'C3']  # Fallback examples
    
    # Create workbook and worksheet
    wb = Workbook()
    ws = wb.active
    ws.title = "Components"
    
    # Set column headers
    headers = ['name', 'category', 'quantity', 'container_code', 'location_type', 'location_index', 'remarks']
    ws.append(headers)
    
    # Set column widths
    column_widths = {
        'A': 30,  # name
        'B': 30,  # category
        'C': 10,  # quantity
        'D': 15,  # container_code
        'E': 15,  # location_type
        'F': 15,  # location_index
        'G': 35   # remarks
    }
    for col, width in column_widths.items():
        ws.column_dimensions[col].width = width
    
    # Add example data rows
    ws.append(['Example Component 1', 'Microcontrollers', 5, container_codes[0] if container_codes else 'A1', 'BOX', 1, 'Sample remarks'])
    ws.append(['Example Component 2', 'Sensors and tranducers', 10, container_codes[1] if len(container_codes) > 1 else 'B2', 'NONE', '', ''])
    
    # Data validation for category (Column B, starting from row 2)
    category_validation = DataValidation(
        type="list",
        formula1=f'"{",".join(CATEGORIES)}"',
        allow_blank=False
    )
    category_validation.add(f"B2:B1000")  # Apply to rows 2-1000
    ws.add_data_validation(category_validation)
    
    # Data validation for container_code (Column D)
    container_validation = DataValidation(
        type="list",
        formula1=f'"{",".join(container_codes)}"',
        allow_blank=False
    )
    container_validation.add(f"D2:D1000")
    ws.add_data_validation(container_validation)
    
    # Data validation for location_type (Column E)
    location_type_validation = DataValidation(
        type="list",
        formula1='"NONE,BOX,PARTITION"',
        allow_blank=False
    )
    location_type_validation.add(f"E2:E1000")
    ws.add_data_validation(location_type_validation)
    
    # Data validation for location_index (Column F) - numbers 1-15
    location_index_validation = DataValidation(
        type="whole",
        operator="between",
        formula1=1,
        formula2=15,
        allow_blank=True
    )
    location_index_validation.add(f"F2:F1000")
    ws.add_data_validation(location_index_validation)
    
    # Save to BytesIO
    output = BytesIO()
    wb.save(output)
    output.seek(0)
    
    return StreamingResponse(
        output,
        media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        headers={
            'Content-Disposition': 'attachment; filename=component_import_template.xlsx'
        }
    )


@router.post("/components/validate")
def validate_excel_import(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Validate Excel file and return components to be imported (without committing)"""
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

    components_to_import = []
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
                raise ValueError("location_index required when location_type is not NONE")

            components_to_import.append({
                "index": idx,  # Zero-based index for image mapping
                "row_index": idx + 2,  # Excel row number (1-based + header)
                "name": name,
                "category": category,
                "quantity": quantity,
                "container_code": container_code,
                "container_id": container.id,
                "location_type": location_type,
                "location_index": location_index,
                "remarks": remarks
            })

        except Exception as e:
            errors.append({
                "row": idx + 2,
                "error": str(e)
            })

    return {
        "components": components_to_import,
        "errors": errors
    }


@router.post("/components/finalize")
def finalize_component_import(
    components_json: str = Form(...),
    db: Session = Depends(get_db)
):
    """Create components from validated data. Returns component IDs mapped to indices for image upload."""
    import json
    
    try:
        components = json.loads(components_json)
        
        created_components = []
        placeholder_path = os.path.join(UPLOAD_DIR, "placeholder.svg")
        
        for comp_data in components:
            # Create component with placeholder image initially
            component = Component(
                name=comp_data["name"],
                category=comp_data["category"],
                quantity=comp_data["quantity"],
                remarks=comp_data.get("remarks"),
                image_path=placeholder_path,
                container_id=comp_data["container_id"],
                location_type=comp_data["location_type"],
                location_index=comp_data.get("location_index"),
                is_deleted=False
            )
            
            db.add(component)
            db.flush()  # Get the ID without committing
            
            created_components.append({
                "id": component.id,
                "index": comp_data.get("index", len(created_components))  # Map back to original index
            })
        
        db.commit()
        
        return {
            "inserted": len(created_components),
            "components": created_components,
            "message": f"Successfully imported {len(created_components)} components"
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(400, f"Error importing components: {str(e)}")


@router.post("/components/upload-image")
def upload_component_image(
    component_id: int = Form(...),
    image: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload image for a specific component"""
    try:
        component = db.query(Component).filter(Component.id == component_id).first()
        if not component:
            raise HTTPException(404, "Component not found")
        
        # Save image
        filename = f"{uuid.uuid4().hex}_{image.filename}"
        file_path = os.path.join(UPLOAD_DIR, filename)
        with open(file_path, "wb") as f:
            content = image.file.read()
            f.write(content)
        
        # Update component image path
        component.image_path = file_path
        db.commit()
        
        return {"message": "Image uploaded successfully", "image_path": file_path}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(400, f"Error uploading image: {str(e)}")
