from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, or_, and_
from typing import List, Dict, Any

from app.database.db import get_db
from app.database.models import Component, Container
from app.schemas.component import ComponentRead
from app.utils.component_mapper import component_to_read

router = APIRouter(
    prefix="/locations",
    tags=["Locations"]
)

# --------------------------------------------------
# GET CABINETS WITH COMPONENTS
# --------------------------------------------------
@router.get("/cabinets")
def get_cabinets_with_components(db: Session = Depends(get_db)):
    """Get list of cabinets that have components, with component counts"""
    # Get all components that could be in cabinets
    # Include: storage_type='CABINET', storage_type is None (old data), or has container
    components = (
        db.query(Component)
        .options(joinedload(Component.container))
        .outerjoin(Container, Component.container_id == Container.id)
        .filter(
            Component.is_deleted == False,
            or_(
                Component.storage_type == "CABINET",
                Component.storage_type.is_(None),
                Component.container_id.isnot(None)
            )
        )
        .all()
    )
    
    # Count by cabinet_number, deriving from container.code if needed
    cabinet_counts = {}
    for comp in components:
        cabinet_num = None
        if comp.cabinet_number is not None:
            cabinet_num = comp.cabinet_number
        elif comp.container_id and comp.container:
            # Extract cabinet number from container code (e.g., "A1" -> 1, "B2" -> 2)
            try:
                cabinet_num = int(comp.container.code[-1])
            except (ValueError, IndexError):
                continue
        
        if cabinet_num is not None:
            if cabinet_num not in cabinet_counts:
                cabinet_counts[cabinet_num] = 0
            cabinet_counts[cabinet_num] += 1
    
    return [
        {
            "cabinet_number": cab_num,
            "component_count": count
        }
        for cab_num, count in sorted(cabinet_counts.items())
    ]


# --------------------------------------------------
# GET COMPONENTS IN CABINET
# --------------------------------------------------
@router.get("/cabinets/{cabinet_number}", response_model=Dict[str, Any])
def get_cabinet_components(cabinet_number: int, db: Session = Depends(get_db)):
    """Get all components in a cabinet, grouped by shelf"""
    # Get components that are in this cabinet
    # Either have cabinet_number set, or are in containers with this cabinet number
    components = (
        db.query(Component)
        .options(joinedload(Component.container))
        .outerjoin(Container, Component.container_id == Container.id)
        .filter(
            Component.is_deleted == False,
            or_(
                and_(
                    or_(
                        Component.storage_type == "CABINET",
                        Component.storage_type.is_(None)
                    ),
                    Component.cabinet_number == cabinet_number
                ),
                and_(
                    Component.container_id.isnot(None),
                    Container.cabinet_number == cabinet_number
                )
            )
        )
        .all()
    )
    
    # Group by shelf
    shelves = {}
    for comp in components:
        # Determine shelf number
        shelf_num = comp.shelf_number if comp.shelf_number is not None else 0
        # If component is in a container, use container's shelf_number if available
        if comp.container_id and comp.container and hasattr(comp.container, 'shelf_number'):
            if comp.container.shelf_number is not None:
                shelf_num = comp.container.shelf_number
        
        if shelf_num not in shelves:
            shelves[shelf_num] = {
                "shelf_number": shelf_num,
                "containers": {},
                "bare_components": []
            }
        
        if comp.container_id and comp.container:
            container_code = comp.container.code
            if container_code not in shelves[shelf_num]["containers"]:
                shelves[shelf_num]["containers"][container_code] = []
            shelves[shelf_num]["containers"][container_code].append(component_to_read(comp))
        else:
            shelves[shelf_num]["bare_components"].append(component_to_read(comp))
    
    # Convert containers dict to list with code
    result = {}
    for shelf_num, shelf_data in shelves.items():
        containers_list = [
            {
                "code": code,
                "components": comps
            }
            for code, comps in shelf_data["containers"].items()
        ]
        result[shelf_num] = {
            "shelf_number": shelf_data["shelf_number"],
            "containers": containers_list,
            "bare_components": shelf_data["bare_components"]
        }
    
    return {
        "cabinet_number": cabinet_number,
        "shelves": result
    }


# --------------------------------------------------
# GET COMPONENTS ON SPECIFIC SHELF
# --------------------------------------------------
@router.get("/cabinets/{cabinet_number}/shelves/{shelf_number}", response_model=Dict[str, Any])
def get_shelf_components(
    cabinet_number: int,
    shelf_number: int,
    db: Session = Depends(get_db)
):
    """Get components on a specific shelf, grouped by containers and bare components"""
    components = (
        db.query(Component)
        .options(joinedload(Component.container))
        .outerjoin(Container, Component.container_id == Container.id)
        .filter(
            Component.is_deleted == False,
            or_(
                and_(
                    or_(
                        Component.storage_type == "CABINET",
                        Component.storage_type.is_(None)
                    ),
                    Component.cabinet_number == cabinet_number,
                    or_(
                        Component.shelf_number == shelf_number,
                        and_(Component.shelf_number.is_(None), shelf_number == 0)
                    )
                ),
                and_(
                    Component.container_id.isnot(None),
                    Container.cabinet_number == cabinet_number,
                    or_(
                        Container.shelf_number == shelf_number,
                        and_(Container.shelf_number.is_(None), shelf_number == 0)
                    )
                )
            )
        )
        .all()
    )
    
    containers_dict = {}
    bare_components = []
    
    for comp in components:
        if comp.container_id and comp.container:
            container_code = comp.container.code
            if container_code not in containers_dict:
                containers_dict[container_code] = {
                    "code": container_code,
                    "id": comp.container.id,
                    "components": []
                }
            containers_dict[container_code]["components"].append(component_to_read(comp))
        else:
            bare_components.append(component_to_read(comp))
    
    return {
        "cabinet_number": cabinet_number,
        "shelf_number": shelf_number,
        "containers": list(containers_dict.values()),
        "bare_components": bare_components
    }


# --------------------------------------------------
# GET DRAWERS WITH COMPONENTS
# --------------------------------------------------
@router.get("/drawers")
def get_drawers_with_components(db: Session = Depends(get_db)):
    """Get list of drawers that have components, with component counts"""
    results = (
        db.query(
            Component.drawer_index,
            func.count(Component.id).label('component_count')
        )
        .filter(
            Component.storage_type == "DRAWER",
            Component.is_deleted == False,
            Component.drawer_index.isnot(None)
        )
        .group_by(Component.drawer_index)
        .order_by(Component.drawer_index)
        .all()
    )
    
    return [
        {
            "drawer_index": row.drawer_index,
            "component_count": row.component_count
        }
        for row in results
    ]


# --------------------------------------------------
# GET COMPONENTS IN DRAWER
# --------------------------------------------------
@router.get("/drawers/{drawer_index}", response_model=Dict[str, Any])
def get_drawer_components(drawer_index: int, db: Session = Depends(get_db)):
    """Get all components in a drawer, grouped by location_type"""
    components = (
        db.query(Component)
        .filter(
            Component.storage_type == "DRAWER",
            Component.drawer_index == drawer_index,
            Component.is_deleted == False
        )
        .all()
    )
    
    grouped = {
        "NONE": [],
        "BOX": {},
        "PARTITION": {}
    }
    
    for comp in components:
        comp_read = component_to_read(comp)
        location_type = comp.location_type or "NONE"
        
        if location_type == "NONE":
            grouped["NONE"].append(comp_read)
        elif location_type == "BOX":
            box_index = comp.location_index
            if box_index not in grouped["BOX"]:
                grouped["BOX"][box_index] = []
            grouped["BOX"][box_index].append(comp_read)
        elif location_type == "PARTITION":
            partition_index = comp.location_index
            if partition_index not in grouped["PARTITION"]:
                grouped["PARTITION"][partition_index] = []
            grouped["PARTITION"][partition_index].append(comp_read)
    
    # Convert dicts to lists with index
    boxes_list = [
        {"index": idx, "components": comps}
        for idx, comps in sorted(grouped["BOX"].items())
    ]
    
    partitions_list = [
        {"index": idx, "components": comps}
        for idx, comps in sorted(grouped["PARTITION"].items())
    ]
    
    return {
        "drawer_index": drawer_index,
        "direct_components": grouped["NONE"],
        "boxes": boxes_list,
        "partitions": partitions_list
    }


# --------------------------------------------------
# GET STORAGE BOXES WITH COMPONENTS
# --------------------------------------------------
@router.get("/storage-boxes")
def get_storage_boxes_with_components(db: Session = Depends(get_db)):
    """Get list of storage boxes that have components, with component counts"""
    results = (
        db.query(
            Component.storage_box_index,
            func.count(Component.id).label('component_count')
        )
        .filter(
            Component.storage_type == "STORAGE_BOX",
            Component.is_deleted == False,
            Component.storage_box_index.isnot(None)
        )
        .group_by(Component.storage_box_index)
        .order_by(Component.storage_box_index)
        .all()
    )
    
    return [
        {
            "storage_box_index": row.storage_box_index,
            "component_count": row.component_count
        }
        for row in results
    ]


# --------------------------------------------------
# GET COMPONENTS IN STORAGE BOX
# --------------------------------------------------
@router.get("/storage-boxes/{box_index}", response_model=List[ComponentRead])
def get_storage_box_components(box_index: int, db: Session = Depends(get_db)):
    """Get all components in a storage box"""
    components = (
        db.query(Component)
        .filter(
            Component.storage_type == "STORAGE_BOX",
            Component.storage_box_index == box_index,
            Component.is_deleted == False
        )
        .all()
    )
    
    return [component_to_read(c) for c in components]

