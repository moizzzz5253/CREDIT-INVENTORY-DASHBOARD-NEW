from app.database.models import Component


def generate_location_label(component):
    """Generate location label based on storage type"""
    # Handle None or missing storage_type (for old data before migration)
    storage_type = getattr(component, 'storage_type', None)
    
    if storage_type == "CABINET":
        cabinet_num = getattr(component, 'cabinet_number', None)
        if cabinet_num is None:
            # Fallback to old format if cabinet_number not set
            if component.container_id and component.container:
                if component.location_type == "NONE":
                    return component.container.code
                else:
                    prefix = "b" if component.location_type == "BOX" else "p"
                    return f"{component.container.code}-{prefix}{component.location_index}"
            return "Unknown Location"
        
        base = f"Cabinet {cabinet_num}"
        
        # Add shelf if specified (and > 0)
        shelf_num = getattr(component, 'shelf_number', None)
        if shelf_num is not None and shelf_num > 0:
            base += f" Shelf {shelf_num}"
        
        # Add container if present
        if component.container_id and component.container:
            base += f" {component.container.code}"
        
        # Add box/partition if present
        if component.location_type == "BOX":
            base += f"-b{component.location_index}"
        elif component.location_type == "PARTITION":
            base += f"-p{component.location_index}"
            
        return base
        
    elif storage_type == "DRAWER":
        drawer_idx = getattr(component, 'drawer_index', None)
        if drawer_idx is None:
            return "Unknown Location"
        
        base = f"Drawer {drawer_idx}"
        
        if component.location_type == "BOX":
            base += f"-b{component.location_index}"
        elif component.location_type == "PARTITION":
            base += f"-p{component.location_index}"
            
        return base
        
    elif storage_type == "STORAGE_BOX":
        storage_box_idx = getattr(component, 'storage_box_index', None)
        if storage_box_idx is None:
            return "Unknown Location"
        return f"Storage Box {storage_box_idx}"
    
    # Fallback for old data (storage_type is None or missing)
    if component.container_id and component.container:
        if component.location_type == "NONE":
            return component.container.code
        else:
            prefix = "b" if component.location_type == "BOX" else "p"
            return f"{component.container.code}-{prefix}{component.location_index}"
    
    return "Unknown Location"


def component_to_read(component):
    borrowed_qty = sum(
        b.quantity_borrowed - b.quantity_returned
        for b in component.borrow_items
    )

    # Generate location label using new system
    location_label = generate_location_label(component)
    
    # Build location object
    location = {
        "type": component.location_type,
        "index": component.location_index,
        "label": location_label
    }

    # Container info (may be None for drawers/storage boxes)
    container_info = None
    if component.container_id and component.container:
        container_info = {
            "id": component.container.id,
            "code": component.container.code,
            "cabinet_number": component.container.cabinet_number,
            "shelf_number": getattr(component.container, 'shelf_number', None)
        }

    # Safely get storage fields with defaults for old data
    storage_type = getattr(component, 'storage_type', 'CABINET')
    
    return {
        "id": component.id,
        "name": component.name,
        "category": component.category,
        "quantity": component.quantity,
        "remarks": component.remarks,
        "image_path": component.image_path,
        "container": container_info,
        "storage_type": storage_type,
        "cabinet_number": getattr(component, 'cabinet_number', None),
        "shelf_number": getattr(component, 'shelf_number', None),
        "drawer_index": getattr(component, 'drawer_index', None),
        "storage_box_index": getattr(component, 'storage_box_index', None),
        "location": location,
        "borrowed_quantity": borrowed_qty,
        "available_quantity": component.quantity - borrowed_qty,
        "created_at": component.created_at,
        "deleted_at": component.deleted_at,
    }
