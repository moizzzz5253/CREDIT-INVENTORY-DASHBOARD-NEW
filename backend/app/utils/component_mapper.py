from app.database.models import Component


def component_to_read(component):
    borrowed_qty = sum(
        b.quantity_borrowed - b.quantity_returned
        for b in component.borrow_items
    )

    # ---- LOCATION NORMALIZATION (FIX) ----
    if component.location_type == "NONE":
        location = {
            "type": "NONE",
            "index": None,
            "label": component.container.code
        }
    else:
        prefix = "b" if component.location_type == "BOX" else "p"
        location = {
            "type": component.location_type,
            "index": component.location_index,
            "label": f"{component.container.code}-{prefix}{component.location_index}"
        }

    return {
        "id": component.id,
        "name": component.name,
        "category": component.category,
        "quantity": component.quantity,
        "remarks": component.remarks,
        "image_path": component.image_path,
        "container": {
            "id": component.container.id,
            "code": component.container.code,
            "cabinet_number": component.container.cabinet_number
        },
        "location": location,
        "borrowed_quantity": borrowed_qty,
        "available_quantity": component.quantity - borrowed_qty,
        "created_at": component.created_at,
        "deleted_at": component.deleted_at,
    }
