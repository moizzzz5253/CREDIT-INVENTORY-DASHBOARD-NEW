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
from app.services.email_service import email_service
from app.utils.admin_emails import get_admin_email_list
from loguru import logger

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
    from app.routers.constants import CATEGORIES
    wb = Workbook()
    ws = wb.active
    ws.title = "Components"
    
    # Set column headers
    headers = ['name', 'category', 'quantity', 'storage_type', 'cabinet_number', 'shelf_number', 
               'container_code', 'drawer_index', 'storage_box_index', 'location_type', 'location_index', 'remarks', 'is_controlled']
    ws.append(headers)
    
    # Set column widths
    column_widths = {
        'A': 30,  # name
        'B': 30,  # category
        'C': 10,  # quantity
        'D': 15,  # storage_type
        'E': 15,  # cabinet_number
        'F': 15,  # shelf_number
        'G': 15,  # container_code
        'H': 15,  # drawer_index
        'I': 15,  # storage_box_index
        'J': 15,  # location_type
        'K': 15,  # location_index
        'L': 35   # remarks
    }
    for col, width in column_widths.items():
        ws.column_dimensions[col].width = width
    
    # Add example data rows
    ws.append(['Example Component 1', 'Microcontrollers', 5, 'CABINET', 1, 2, 
               container_codes[0] if container_codes else 'A1', '', '', 'BOX', 1, 'Sample remarks', 'No'])
    ws.append(['Example Component 2', 'Sensors and tranducers', 10, 'CABINET', 1, 0, 
               '', '', '', 'NONE', '', 'Bare on shelf', 'No'])
    ws.append(['Example Component 3', 'Hardware accessories', 2, 'DRAWER', '', '', 
               '', 1, '', 'BOX', 2, 'In drawer box', 'No'])
    ws.append(['Example Component 4', 'Tools', 5, 'STORAGE_BOX', '', '', 
               '', '', 1, 'NONE', '', 'In storage box', 'Yes'])
    
    # Data validation for category (Column B, starting from row 2)
    category_validation = DataValidation(
        type="list",
        formula1=f'"{",".join(CATEGORIES)}"',
        allow_blank=False
    )
    category_validation.add(f"B2:B1000")
    ws.add_data_validation(category_validation)
    
    # Data validation for storage_type (Column D)
    storage_type_validation = DataValidation(
        type="list",
        formula1='"CABINET,DRAWER,STORAGE_BOX"',
        allow_blank=False
    )
    storage_type_validation.add(f"D2:D1000")
    ws.add_data_validation(storage_type_validation)
    
    # Data validation for cabinet_number (Column E) - numbers 1-10
    cabinet_validation = DataValidation(
        type="whole",
        operator="between",
        formula1=1,
        formula2=10,
        allow_blank=True
    )
    cabinet_validation.add(f"E2:E1000")
    ws.add_data_validation(cabinet_validation)
    
    # Data validation for shelf_number (Column F) - numbers 0-5
    shelf_validation = DataValidation(
        type="whole",
        operator="between",
        formula1=0,
        formula2=5,
        allow_blank=True
    )
    shelf_validation.add(f"F2:F1000")
    ws.add_data_validation(shelf_validation)
    
    # Data validation for container_code (Column G)
    container_validation = DataValidation(
        type="list",
        formula1=f'"{",".join(container_codes)}"',
        allow_blank=True
    )
    container_validation.add(f"G2:G1000")
    ws.add_data_validation(container_validation)
    
    # Data validation for drawer_index (Column H) - numbers >= 1
    drawer_validation = DataValidation(
        type="whole",
        operator="greaterThan",
        formula1=0,
        allow_blank=True
    )
    drawer_validation.add(f"H2:H1000")
    ws.add_data_validation(drawer_validation)
    
    # Data validation for storage_box_index (Column I) - numbers >= 1
    storage_box_validation = DataValidation(
        type="whole",
        operator="greaterThan",
        formula1=0,
        allow_blank=True
    )
    storage_box_validation.add(f"I2:I1000")
    ws.add_data_validation(storage_box_validation)
    
    # Data validation for location_type (Column J)
    location_type_validation = DataValidation(
        type="list",
        formula1='"NONE,BOX,PARTITION"',
        allow_blank=False
    )
    location_type_validation.add(f"J2:J1000")
    ws.add_data_validation(location_type_validation)
    
    # Data validation for location_index (Column K) - numbers 1-15
    location_index_validation = DataValidation(
        type="whole",
        operator="between",
        formula1=1,
        formula2=15,
        allow_blank=True
    )
    location_index_validation.add(f"K2:K1000")
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

    required_columns = {"name", "category", "quantity", "storage_type"}
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
            storage_type = str(row["storage_type"]).strip().upper()

            # Extract optional fields
            cabinet_number = (
                int(row["cabinet_number"])
                if "cabinet_number" in df.columns and not pd.isna(row["cabinet_number"])
                else None
            )
            shelf_number = (
                int(row["shelf_number"])
                if "shelf_number" in df.columns and not pd.isna(row["shelf_number"])
                else None
            )
            container_code = (
                str(row["container_code"]).strip()
                if "container_code" in df.columns and not pd.isna(row["container_code"])
                else None
            )
            drawer_index = (
                int(row["drawer_index"])
                if "drawer_index" in df.columns and not pd.isna(row["drawer_index"])
                else None
            )
            storage_box_index = (
                int(row["storage_box_index"])
                if "storage_box_index" in df.columns and not pd.isna(row["storage_box_index"])
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
            remarks = (
                str(row["remarks"]).strip()
                if "remarks" in df.columns and not pd.isna(row["remarks"])
                else None
            )

            if category not in CATEGORIES:
                raise ValueError(f"Invalid category: {category}")

            if storage_type not in ["CABINET", "DRAWER", "STORAGE_BOX"]:
                raise ValueError(f"Invalid storage_type: {storage_type}")

            # Validate and resolve container_id based on storage_type
            container_id = None
            if storage_type == "CABINET":
                if cabinet_number is None:
                    raise ValueError("cabinet_number is required for CABINET storage")
                if shelf_number is None:
                    raise ValueError("shelf_number is required for CABINET storage")
                
                if container_code:
                    container = (
                        db.query(Container)
                        .filter(Container.code == container_code)
                        .first()
                    )
                    if not container:
                        raise ValueError(f"Container {container_code} not found")
                    if container.cabinet_number != cabinet_number:
                        raise ValueError(f"Container {container_code} does not belong to cabinet {cabinet_number}")
                    container_id = container.id
            elif storage_type == "DRAWER":
                if drawer_index is None:
                    raise ValueError("drawer_index is required for DRAWER storage")
            elif storage_type == "STORAGE_BOX":
                if storage_box_index is None:
                    raise ValueError("storage_box_index is required for STORAGE_BOX storage")

            if location_type not in ["NONE", "BOX", "PARTITION"]:
                raise ValueError("Invalid location_type")

            if location_type != "NONE" and not location_index:
                raise ValueError("location_index required when location_type is not NONE")

            if storage_type == "STORAGE_BOX" and location_type != "NONE":
                raise ValueError("STORAGE_BOX cannot have BOX or PARTITION location_type")

            # Extract is_controlled field
            is_controlled = False
            if "is_controlled" in df.columns and not pd.isna(row["is_controlled"]):
                controlled_val = str(row["is_controlled"]).strip().upper()
                is_controlled = controlled_val in ["YES", "TRUE", "1", "Y"]

            components_to_import.append({
                "index": idx,
                "row_index": idx + 2,
                "name": name,
                "category": category,
                "quantity": quantity,
                "storage_type": storage_type,
                "cabinet_number": cabinet_number,
                "shelf_number": shelf_number,
                "container_id": container_id,
                "drawer_index": drawer_index,
                "storage_box_index": storage_box_index,
                "location_type": location_type,
                "location_index": location_index,
                "remarks": remarks,
                "is_controlled": is_controlled
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
        controlled_component_ids = []  # Track IDs of controlled components for email notification
        placeholder_path = os.path.join(UPLOAD_DIR, "placeholder.svg")
        
        for comp_data in components:
            is_controlled = comp_data.get("is_controlled", False)
            
            # Create component with placeholder image initially
            component = Component(
                name=comp_data["name"],
                category=comp_data["category"],
                quantity=comp_data["quantity"],
                remarks=comp_data.get("remarks"),
                image_path=placeholder_path,
                storage_type=comp_data["storage_type"],
                cabinet_number=comp_data.get("cabinet_number"),
                shelf_number=comp_data.get("shelf_number"),
                container_id=comp_data.get("container_id"),
                drawer_index=comp_data.get("drawer_index"),
                storage_box_index=comp_data.get("storage_box_index"),
                location_type=comp_data["location_type"],
                location_index=comp_data.get("location_index"),
                is_deleted=False,
                is_controlled=is_controlled
            )
            
            db.add(component)
            db.flush()  # Get the ID without committing
            
            created_components.append({
                "id": component.id,
                "index": comp_data.get("index", len(created_components))  # Map back to original index
            })
            
            # Track controlled component IDs for email notification
            if is_controlled:
                controlled_component_ids.append(component.id)
        
        db.commit()
        
        # Send email notification for controlled components
        if controlled_component_ids:
            try:
                # Query controlled components to get their details including created_at
                controlled_comps = db.query(Component).filter(Component.id.in_(controlled_component_ids)).all()
                controlled_components_data = []
                
                for comp in controlled_comps:
                    controlled_components_data.append({
                        "name": comp.name,
                        "category": comp.category,
                        "quantity": comp.quantity,
                        "remarks": comp.remarks,
                        "date_added": comp.created_at
                    })
                
                admin_emails = get_admin_email_list(db)
                if admin_emails:
                    email_service.send_controlled_components_batch_summary(
                        components=controlled_components_data,
                        admin_emails=admin_emails
                    )
            except Exception as e:
                logger.error(f"Failed to send controlled components batch summary email: {e}")
        
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
