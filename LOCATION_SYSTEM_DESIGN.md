# Location System Redesign - Design Document

## Current System Analysis

### Current Structure:
- **Components** have:
  - `container_id` (required, FK to Container)
  - `location_type` (NONE | BOX | PARTITION)
  - `location_index` (optional, 1-15)
  
- **Containers** have:
  - `code` (e.g., A1, B2, C3) - where letter is container and number is cabinet
  - `cabinet_number` (integer)
  - `qr_path`

- **Location Labels:**
  - "A1" (direct in container)
  - "A1-b1" (in box 1 of container A1)
  - "A1-p14" (in partition 14 of container A1)

### Issues with Current System:
1. No shelf information
2. Containers don't have explicit shelf assignments
3. Cannot store items in drawers or storage boxes
4. Cannot store items "bare" (without container) in cabinets

## New Requirements

### Physical Structure:
- **3 Cabinets** (numbered 1-3, but system should support 1-10)
- **Each cabinet has 5 shelves** (numbered 1-5, with option 0 for no shelf)
- **Each shelf can fit max 4 containers** (containers A-T = 20 total per cabinet)
- **Containers**: A1-T1 (cabinet 1), A2-T2 (cabinet 2), A3-T3 (cabinet 3)

### Storage Options:

1. **Cabinet**
   - Select cabinet (1-10)
   - Select shelf (0-5, where 0 = no shelf)
   - If shelf > 0: Select container (A1-T1 for cabinet 1, etc.)
   - Optional: Box/Partition with index
   - **Location format:**
     - With container: "Cabinet 1 Shelf 2 A2" or "Cabinet 1 Shelf 2 A2-b1"
     - Bare (no container): "Cabinet 1 Shelf 4"

2. **Drawer**
   - Select drawer index (1, 2, 3...)
   - Optional: Box/Partition with index
   - **Location format:**
     - "Drawer 1" or "Drawer 1-b2" or "Drawer 1-p4"

3. **Storage Box**
   - Select storage box index (1, 2, 3...)
   - **Location format:** "Storage Box 1"

## Design Strategy

### Recommended Approach: Add New Columns to Component Table

**Rationale:**
- Simpler migration path
- Easier to query
- Maintains backward compatibility (we can migrate existing data)
- Clear data integrity constraints

### Database Schema Changes:

```sql
ALTER TABLE components ADD COLUMN storage_type VARCHAR(20) DEFAULT 'CABINET';
-- Options: CABINET, DRAWER, STORAGE_BOX

ALTER TABLE components ADD COLUMN cabinet_number INTEGER;
-- For CABINET storage type

ALTER TABLE components ADD COLUMN shelf_number INTEGER;
-- For CABINET storage type (0-5, where 0 = no shelf)

ALTER TABLE components MODIFY container_id INTEGER NULL;
-- Make nullable since drawers/storage boxes don't have containers

ALTER TABLE containers ADD COLUMN shelf_number INTEGER;
-- Store which shelf the container is on (1-5, or NULL if not assigned)

ALTER TABLE components ADD COLUMN drawer_index INTEGER;
-- For DRAWER storage type

ALTER TABLE components ADD COLUMN storage_box_index INTEGER;
-- For STORAGE_BOX storage type
```

### Component Model Changes:

```python
class Component(Base):
    # ... existing fields ...
    
    # Storage location
    storage_type = Column(String(20), default="CABINET", nullable=False)
    # CABINET | DRAWER | STORAGE_BOX
    
    # For CABINET storage
    cabinet_number = Column(Integer, nullable=True)
    shelf_number = Column(Integer, nullable=True)  # 0-5, 0 = no shelf
    container_id = Column(Integer, ForeignKey("containers.id"), nullable=True)  # Made nullable
    
    # For DRAWER storage
    drawer_index = Column(Integer, nullable=True)
    
    # For STORAGE_BOX storage
    storage_box_index = Column(Integer, nullable=True)
    
    # Existing location fields (for box/partition within container/drawer)
    location_type = Column(String(20), default="NONE", nullable=False)  # NONE | BOX | PARTITION
    location_index = Column(Integer, nullable=True)
```

### Container Model Changes:

```python
class Container(Base):
    # ... existing fields ...
    shelf_number = Column(Integer, nullable=True)  # 1-5, NULL if not assigned to shelf
```

### Location Label Generation Logic:

```python
def generate_location_label(component):
    if component.storage_type == "CABINET":
        base = f"Cabinet {component.cabinet_number}"
        if component.shelf_number and component.shelf_number > 0:
            base += f" Shelf {component.shelf_number}"
        
        if component.container_id:  # In a container
            base += f" {component.container.code}"
        
        # Add box/partition if present
        if component.location_type == "BOX":
            base += f"-b{component.location_index}"
        elif component.location_type == "PARTITION":
            base += f"-p{component.location_index}"
            
        return base
        
    elif component.storage_type == "DRAWER":
        base = f"Drawer {component.drawer_index}"
        if component.location_type == "BOX":
            base += f"-b{component.location_index}"
        elif component.location_type == "PARTITION":
            base += f"-p{component.location_index}"
        return base
        
    elif component.storage_type == "STORAGE_BOX":
        return f"Storage Box {component.storage_box_index}"
```

### Validation Rules:

1. **CABINET storage:**
   - `cabinet_number` required (1-10)
   - `shelf_number` required (0-5)
   - If `shelf_number > 0`: `container_id` optional
   - If `container_id` provided: container must exist and container.cabinet_number must match
   - `drawer_index` must be NULL
   - `storage_box_index` must be NULL

2. **DRAWER storage:**
   - `drawer_index` required (>= 1)
   - `cabinet_number`, `shelf_number`, `container_id` must be NULL
   - `storage_box_index` must be NULL
   - `location_type` can be BOX/PARTITION/NONE

3. **STORAGE_BOX storage:**
   - `storage_box_index` required (>= 1)
   - `cabinet_number`, `shelf_number`, `container_id`, `drawer_index` must be NULL
   - `location_type` must be NONE (no boxes/partitions in storage boxes)

## Migration Strategy

1. Add new columns with NULL defaults
2. Migrate existing data:
   - Set `storage_type = 'CABINET'`
   - Extract `cabinet_number` from container.code (last character)
   - Set `shelf_number = NULL` (will need manual assignment or default to 1)
   - Keep existing `container_id`
   - Keep existing `location_type` and `location_index`
3. Update all code that reads/writes components
4. Update frontend forms
5. Update Excel templates

## Frontend Form Flow

### Add Component Form:

```
1. Storage Type: [Cabinet ▼] [Drawer] [Storage Box]

2a. If Cabinet:
    - Cabinet: [1 ▼] (dropdown 1-10)
    - Shelf: [0 ▼] (dropdown 0-5)
    - If Shelf > 0:
      - Container: [A1 ▼] (filtered by cabinet, show only containers for selected cabinet)
    - Box/Partition: [None ▼] [Box] [Partition]
      - If Box/Partition selected:
        - Index: [1] (1-15)

2b. If Drawer:
    - Drawer Index: [1] (number input)
    - Box/Partition: [None ▼] [Box] [Partition]
      - If Box/Partition selected:
        - Index: [1] (1-15)

2c. If Storage Box:
    - Storage Box Index: [1] (number input)
```

## Implementation Order

1. Update database models
2. Create migration script
3. Update component_mapper for location label generation
4. Update component creation/update endpoints
5. Update frontend forms
6. Update Excel templates
7. Test thoroughly

