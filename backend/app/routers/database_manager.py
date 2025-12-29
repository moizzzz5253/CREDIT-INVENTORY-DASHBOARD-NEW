from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import text
from io import BytesIO
import shutil
from datetime import datetime, date
import os
import pandas as pd

from app.database.db import get_db, engine
from app.database.models import Component, BorrowItem, Container, BorrowTransaction, Borrower, BorrowStatus, User
from app.utils.user_resolver import resolve_user
from app.routers.constants import CATEGORIES

router = APIRouter(
    prefix="/database",
    tags=["Database Management"]
)


@router.post("/restructure")
def restructure_database(db: Session = Depends(get_db)):
    """
    Restructure database by:
    1. Removing all deleted components
    2. Reordering component IDs sequentially (1, 2, 3...)
    3. Updating all foreign key references (BorrowItem.component_id)
    4. Preserving all borrow relationships
    
    WARNING: This operation is irreversible. A backup is created automatically.
    """
    try:
        # Step 1: Create backup
        backup_path = create_database_backup()
        
        # Step 2: Get all active components ordered by current ID
        active_components = (
            db.query(Component)
            .filter(Component.is_deleted == False)
            .order_by(Component.id)
            .all()
        )
        
        if not active_components:
            raise HTTPException(400, "No active components found to restructure")
        
        # Step 3: Check if there are deleted components to remove
        deleted_count = (
            db.query(Component)
            .filter(Component.is_deleted == True)
            .count()
        )
        
        # Step 4: Create mapping of old ID -> new ID
        id_mapping = {}
        for new_id, component in enumerate(active_components, start=1):
            old_id = component.id
            if old_id != new_id:
                id_mapping[old_id] = new_id
        
        # Proceed with restructuring if there are deleted components OR if IDs need reshuffling
        if not id_mapping and deleted_count == 0:
            return {
                "message": "Database already properly structured",
                "backup_path": backup_path
            }
        
        # Step 5: Use table recreation approach (safest for SQLite)
        # Disable foreign keys temporarily
        db.execute(text("PRAGMA foreign_keys=OFF"))
        
        # Step 5a: Create new components table
        db.execute(text("""
            CREATE TABLE components_new (
                id INTEGER PRIMARY KEY,
                name VARCHAR(150) NOT NULL,
                category VARCHAR(100) NOT NULL,
                quantity INTEGER NOT NULL,
                remarks VARCHAR(500),
                image_path VARCHAR NOT NULL,
                container_id INTEGER NOT NULL,
                location_type VARCHAR(20) NOT NULL DEFAULT 'NONE',
                location_index INTEGER,
                is_deleted BOOLEAN DEFAULT 0,
                deleted_reason VARCHAR,
                deleted_at DATETIME,
                created_at DATETIME NOT NULL,
                updated_at DATETIME,
                FOREIGN KEY(container_id) REFERENCES containers(id)
            )
        """))
        
        # Step 5b: Copy active components with new sequential IDs
        for new_id, component in enumerate(active_components, start=1):
            db.execute(text("""
                INSERT INTO components_new 
                (id, name, category, quantity, remarks, image_path, container_id, 
                 location_type, location_index, is_deleted, deleted_reason, deleted_at, created_at, updated_at)
                VALUES (:id, :name, :category, :quantity, :remarks, :image_path, :container_id,
                        :location_type, :location_index, :is_deleted, :deleted_reason, :deleted_at, :created_at, :updated_at)
            """), {
                'id': new_id,
                'name': component.name,
                'category': component.category,
                'quantity': component.quantity,
                'remarks': component.remarks,
                'image_path': component.image_path,
                'container_id': component.container_id,
                'location_type': component.location_type,
                'location_index': component.location_index,
                'is_deleted': 0,
                'deleted_reason': None,
                'deleted_at': None,
                'created_at': component.created_at,
                'updated_at': component.updated_at
            })
        
        db.flush()
        
        # Step 5c: Update BorrowItem.component_id references using mapping
        # (Now that new table exists with new IDs)
        updated_borrow_items = 0
        for old_id, new_id in id_mapping.items():
            result = db.execute(text("""
                UPDATE borrow_items 
                SET component_id = :new_id 
                WHERE component_id = :old_id
            """), {'old_id': old_id, 'new_id': new_id})
            updated_borrow_items += result.rowcount
        
        db.flush()
        
        # Step 5d: Drop old table and rename new one
        db.execute(text("DROP TABLE components"))
        db.execute(text("ALTER TABLE components_new RENAME TO components"))
        
        # Step 5e: Re-enable foreign keys
        db.execute(text("PRAGMA foreign_keys=ON"))
        
        db.commit()
        
        return {
            "message": "Database restructured successfully",
            "active_components_restructured": len(active_components),
            "deleted_components_removed": deleted_count,
            "borrow_item_references_updated": updated_borrow_items,
            "id_mappings": len(id_mapping),
            "backup_path": backup_path
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(500, f"Error restructuring database: {str(e)}")


def create_database_backup():
    """Create a backup of the database file"""
    # Get database path from engine
    db_url = str(engine.url)
    if db_url.startswith('sqlite:///'):
        # SQLite URL format: sqlite:///./inventory.db
        db_path = db_url.replace('sqlite:///', '').replace('./', '')
        if not os.path.isabs(db_path):
            # Relative path - make it relative to current working directory
            db_path = os.path.join(os.getcwd(), db_path.lstrip('./'))
        
        if not os.path.exists(db_path):
            raise HTTPException(500, f"Database file not found: {db_path}")
        
        # Create backups directory if it doesn't exist
        backup_dir = "database_backups"
        os.makedirs(backup_dir, exist_ok=True)
        
        # Create backup filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"inventory_backup_{timestamp}.db"
        backup_path = os.path.join(backup_dir, backup_filename)
        
        # Copy database file
        shutil.copy2(db_path, backup_path)
        
        return backup_path
    else:
        raise HTTPException(500, "Database backup only supported for SQLite databases")


@router.post("/restructure/upload-excel")
def restructure_from_excel(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Restructure database by uploading modified Excel file from export-full.
    
    Key behavior:
    - Removes components marked as deleted (Is Deleted = True)
    - Imports/updates borrowers and borrow transactions from Excel
    - Updates borrow items (quantities borrowed/returned)
    - Keeps component IDs as they appear in Excel (NO reshuffling)
    - Validates all data before applying changes
    
    WARNING: This is a DESTRUCTIVE operation. See RISKS_AND_WARNINGS.md for details.
    
    The Excel file must contain sheets: Components, Borrow Items, Borrow Transactions
    """
    if not file.filename.endswith(".xlsx"):
        raise HTTPException(400, "Only .xlsx files are supported")
    
    try:
        # Create backup first
        backup_path = create_database_backup()
        
        # Read Excel file
        df_components = pd.read_excel(file.file, sheet_name="Components")
        df_borrow_items = pd.read_excel(file.file, sheet_name="Borrow Items")
        df_borrow_transactions = pd.read_excel(file.file, sheet_name="Borrow Transactions")
        
        # Validate required columns - updated for new storage system
        required_components_cols = ["ID", "Name", "Category", "Quantity", "Storage Type", "Is Deleted"]
        required_borrow_items_cols = ["ID", "Transaction ID", "Component ID", "Quantity Borrowed", "Quantity Returned"]
        required_borrow_tx_cols = ["ID", "Borrower Name", "TP ID", "Phone", "Email", "PIC Name", "Reason", "Expected Return Date", "Status", "Borrowed At"]
        
        if not all(col in df_components.columns for col in required_components_cols):
            raise HTTPException(400, f"Missing required columns in Components sheet. Required: {required_components_cols}")
        if not all(col in df_borrow_items.columns for col in required_borrow_items_cols):
            raise HTTPException(400, f"Missing required columns in Borrow Items sheet. Required: {required_borrow_items_cols}")
        if not all(col in df_borrow_transactions.columns for col in required_borrow_tx_cols):
            raise HTTPException(400, f"Missing required columns in Borrow Transactions sheet. Required: {required_borrow_tx_cols}")
        
        # Validate and prepare data
        errors = []
        all_components_data = []  # All components (including deleted)
        active_components_data = []  # Only active components (is_deleted = False)
        active_component_ids = set()  # Set of active component IDs for fast lookup
        
        # Process ALL Components first (to identify which are deleted)
        for idx, row in df_components.iterrows():
            try:
                comp_id = int(row["ID"])
                is_deleted = bool(row.get("Is Deleted", False))
                
                # Skip validation for deleted components, but track them
                if is_deleted:
                    all_components_data.append({
                        "id": comp_id,
                        "is_deleted": True
                    })
                    continue
                
                # Validate active components
                name = str(row["Name"]).strip()
                if not name:
                    errors.append(f"Row {idx+2} (Components): Name is required")
                    continue
                
                category = str(row["Category"]).strip()
                if category not in CATEGORIES:
                    errors.append(f"Row {idx+2} (Components): Invalid category '{category}'. Must be one of: {CATEGORIES}")
                    continue
                
                quantity = int(row["Quantity"])
                if quantity < 0:
                    errors.append(f"Row {idx+2} (Components): Quantity cannot be negative")
                    continue
                
                # Parse new storage system fields
                storage_type = str(row.get("Storage Type", "CABINET")).strip().upper() if pd.notna(row.get("Storage Type")) else "CABINET"
                if storage_type not in ["CABINET", "DRAWER", "STORAGE_BOX"]:
                    errors.append(f"Row {idx+2} (Components): Invalid storage_type '{storage_type}'. Must be CABINET, DRAWER, or STORAGE_BOX")
                    continue
                
                # Storage-specific fields
                cabinet_number = int(row["Cabinet Number"]) if pd.notna(row.get("Cabinet Number")) else None
                shelf_number = int(row["Shelf Number"]) if pd.notna(row.get("Shelf Number")) else None
                drawer_index = int(row["Drawer Index"]) if pd.notna(row.get("Drawer Index")) else None
                storage_box_index = int(row["Storage Box Index"]) if pd.notna(row.get("Storage Box Index")) else None
                
                # Container code - optional, only for CABINET storage
                container_code = None
                container_id = None
                if storage_type == "CABINET":
                    container_code_val = row.get("Container Code")
                    if pd.notna(container_code_val) and str(container_code_val).strip() and str(container_code_val).strip().lower() != "nan":
                        container_code = str(container_code_val).strip()
                        container = db.query(Container).filter(Container.code == container_code).first()
                        if not container:
                            errors.append(f"Row {idx+2} (Components): Container '{container_code}' not found in database")
                            continue
                        container_id = container.id
                    
                    # Validate cabinet and shelf for CABINET storage
                    if cabinet_number is None:
                        errors.append(f"Row {idx+2} (Components): Cabinet Number is required for CABINET storage")
                        continue
                    if shelf_number is None:
                        errors.append(f"Row {idx+2} (Components): Shelf Number is required for CABINET storage")
                        continue
                    if not (1 <= cabinet_number <= 10):
                        errors.append(f"Row {idx+2} (Components): Cabinet Number must be between 1 and 10")
                        continue
                    if not (0 <= shelf_number <= 5):
                        errors.append(f"Row {idx+2} (Components): Shelf Number must be between 0 and 5")
                        continue
                    
                    # Validate container belongs to cabinet if provided
                    if container_id and container.cabinet_number != cabinet_number:
                        errors.append(f"Row {idx+2} (Components): Container '{container_code}' does not belong to cabinet {cabinet_number}")
                        continue
                
                elif storage_type == "DRAWER":
                    if drawer_index is None or drawer_index < 1:
                        errors.append(f"Row {idx+2} (Components): Drawer Index is required and must be >= 1 for DRAWER storage")
                        continue
                
                elif storage_type == "STORAGE_BOX":
                    if storage_box_index is None or storage_box_index < 1:
                        errors.append(f"Row {idx+2} (Components): Storage Box Index is required and must be >= 1 for STORAGE_BOX storage")
                        continue
                
                # Location type/index (for boxes/partitions in containers or drawers)
                location_type = str(row.get("Location Type", "NONE")).strip().upper() if pd.notna(row.get("Location Type")) else "NONE"
                location_index = int(row["Location Index"]) if pd.notna(row.get("Location Index")) else None
                
                # Only allow box/partition for CABINET with container or DRAWER
                if storage_type == "STORAGE_BOX" and location_type != "NONE":
                    errors.append(f"Row {idx+2} (Components): STORAGE_BOX cannot have BOX or PARTITION location_type")
                    continue
                
                if (storage_type == "CABINET" and container_id) or storage_type == "DRAWER":
                    if location_type not in ["NONE", "BOX", "PARTITION"]:
                        errors.append(f"Row {idx+2} (Components): Invalid location_type '{location_type}'. Must be NONE, BOX, or PARTITION")
                        continue
                    
                    if location_type != "NONE" and location_index is None:
                        errors.append(f"Row {idx+2} (Components): location_index is required when location_type is '{location_type}'")
                        continue
                    
                    if location_index is not None and (location_index < 1 or location_index > 15):
                        errors.append(f"Row {idx+2} (Components): location_index must be between 1 and 15")
                        continue
                else:
                    # For bare cabinet or storage box, location_type must be NONE
                    if location_type != "NONE":
                        location_type = "NONE"
                        location_index = None
                
                # Parse dates safely (handle %d/%m/%Y %H:%M:%S format)
                # Convert pandas Timestamp to Python datetime for SQLite compatibility
                try:
                    created_at_str = row.get("Created At")
                    if pd.notna(created_at_str):
                        # Try parsing with dayfirst=True for %d/%m/%Y format
                        created_at_ts = pd.to_datetime(created_at_str, dayfirst=True, errors='coerce')
                        if pd.isna(created_at_ts):
                            # Fallback to default parsing
                            created_at_ts = pd.to_datetime(created_at_str, errors='coerce')
                        if pd.isna(created_at_ts):
                            created_at = datetime.utcnow()
                        else:
                            # Convert pandas Timestamp to Python datetime
                            created_at = created_at_ts.to_pydatetime()
                    else:
                        created_at = datetime.utcnow()
                except:
                    created_at = datetime.utcnow()
                
                active_components_data.append({
                    "id": comp_id,
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
                    "remarks": str(row.get("Remarks", "")) if pd.notna(row.get("Remarks")) else None,
                    "image_path": str(row.get("Image Path", "uploads/components/placeholder.svg")) if pd.notna(row.get("Image Path")) else "uploads/components/placeholder.svg",
                    "created_at": created_at,
                    "updated_at": datetime.utcnow(),
                    "is_deleted": False
                })
                active_component_ids.add(comp_id)
                all_components_data.append({"id": comp_id, "is_deleted": False})
                
            except ValueError as e:
                errors.append(f"Row {idx+2} (Components): Invalid data type - {str(e)}")
            except Exception as e:
                errors.append(f"Row {idx+2} (Components): {str(e)}")
        
        if not active_components_data:
            raise HTTPException(400, {
                "message": "No active components found in Excel file",
                "errors": errors,
                "backup_path": backup_path
            })
        
        # Process Borrow Transactions first (to establish transaction IDs)
        borrowers_map = {}  # Maps (name, tp_id, phone, email) tuple to borrower_id
        borrow_transactions_data = []
        transaction_ids_set = set()
        
        for idx, row in df_borrow_transactions.iterrows():
            try:
                tx_id = int(row["ID"])
                borrower_name = str(row["Borrower Name"]).strip().upper()
                borrower_tp_id = str(row["TP ID"]).strip().upper()
                borrower_phone = str(row["Phone"]).strip()
                borrower_email = str(row["Email"]).strip().lower()
                pic_name = str(row["PIC Name"]).strip()
                
                if not borrower_name or not borrower_tp_id or not borrower_phone or not borrower_email:
                    errors.append(f"Row {idx+2} (Borrow Transactions): Borrower information is incomplete")
                    continue
                
                # Create borrower key for deduplication
                borrower_key = (borrower_name, borrower_tp_id, borrower_phone, borrower_email)
                if borrower_key not in borrowers_map:
                    # Assign a temporary ID (will be reassigned during insert)
                    borrowers_map[borrower_key] = len(borrowers_map) + 1
                
                # Validate status
                status_str = str(row.get("Status", "ACTIVE")).strip().upper()
                if status_str not in ["ACTIVE", "OVERDUE", "COMPLETED"]:
                    errors.append(f"Row {idx+2} (Borrow Transactions): Invalid status '{status_str}'. Must be ACTIVE, OVERDUE, or COMPLETED")
                    continue
                
                # Parse expected return date
                try:
                    expected_return_str = row.get("Expected Return Date")
                    if pd.notna(expected_return_str):
                        expected_return_ts = pd.to_datetime(expected_return_str, dayfirst=True, errors='coerce')
                        if pd.isna(expected_return_ts):
                            expected_return_ts = pd.to_datetime(expected_return_str, errors='coerce')
                        if pd.isna(expected_return_ts):
                            errors.append(f"Row {idx+2} (Borrow Transactions): Invalid Expected Return Date format")
                            continue
                        expected_return = expected_return_ts.date()
                    else:
                        errors.append(f"Row {idx+2} (Borrow Transactions): Expected Return Date is required")
                        continue
                except Exception as e:
                    errors.append(f"Row {idx+2} (Borrow Transactions): Invalid Expected Return Date format - {str(e)}")
                    continue
                
                # Parse borrowed_at date
                try:
                    borrowed_at_str = row.get("Borrowed At")
                    if pd.notna(borrowed_at_str):
                        borrowed_at_ts = pd.to_datetime(borrowed_at_str, dayfirst=True, errors='coerce')
                        if pd.isna(borrowed_at_ts):
                            borrowed_at_ts = pd.to_datetime(borrowed_at_str, errors='coerce')
                        if pd.isna(borrowed_at_ts):
                            borrowed_at = datetime.utcnow()
                        else:
                            borrowed_at = borrowed_at_ts.to_pydatetime()
                    else:
                        borrowed_at = datetime.utcnow()
                except:
                    borrowed_at = datetime.utcnow()
                
                reason = str(row.get("Reason", "")).strip()
                if not reason:
                    errors.append(f"Row {idx+2} (Borrow Transactions): Reason is required")
                    continue
                
                if tx_id in transaction_ids_set:
                    errors.append(f"Row {idx+2} (Borrow Transactions): Duplicate Transaction ID {tx_id}")
                    continue
                
                transaction_ids_set.add(tx_id)
                
                borrow_transactions_data.append({
                    "id": tx_id,
                    "borrower_key": borrower_key,
                    "borrower_name": borrower_name,
                    "borrower_tp_id": borrower_tp_id,
                    "borrower_phone": borrower_phone,
                    "borrower_email": borrower_email,
                    "pic_name": pic_name,
                    "reason": reason,
                    "expected_return_date": expected_return,
                    "status": status_str,
                    "borrowed_at": borrowed_at
                })
            except ValueError as e:
                errors.append(f"Row {idx+2} (Borrow Transactions): Invalid data type - {str(e)}")
            except Exception as e:
                errors.append(f"Row {idx+2} (Borrow Transactions): {str(e)}")
        
        # Process Borrow Items - only keep those referencing ACTIVE components and valid transactions
        borrow_items_data = []
        deleted_component_ids = {comp["id"] for comp in all_components_data if comp.get("is_deleted", False)}
        
        for idx, row in df_borrow_items.iterrows():
            try:
                item_id = int(row["ID"])
                transaction_id = int(row["Transaction ID"])
                component_id = int(row["Component ID"])
                qty_borrowed = int(row["Quantity Borrowed"])
                qty_returned = int(row.get("Quantity Returned", 0)) if pd.notna(row.get("Quantity Returned")) else 0
                
                # Validate transaction exists
                if transaction_id not in transaction_ids_set:
                    errors.append(f"Row {idx+2} (Borrow Items): Transaction ID {transaction_id} not found in Borrow Transactions sheet")
                    continue
                
                # Skip borrow items referencing deleted components (silently skip - expected behavior)
                if component_id in deleted_component_ids:
                    continue
                
                # Skip borrow items referencing components that don't exist in active components
                # This can happen if the Excel file was manually edited and component IDs were removed
                if component_id not in active_component_ids:
                    # Skip instead of error - the component might have been deleted/removed from the Excel file
                    continue
                
                if qty_borrowed <= 0:
                    errors.append(f"Row {idx+2} (Borrow Items): Quantity borrowed must be greater than 0")
                    continue
                
                if qty_returned < 0:
                    errors.append(f"Row {idx+2} (Borrow Items): Quantity returned cannot be negative")
                    continue
                
                if qty_returned > qty_borrowed:
                    errors.append(f"Row {idx+2} (Borrow Items): Quantity returned ({qty_returned}) exceeds quantity borrowed ({qty_borrowed})")
                    continue
                
                borrow_items_data.append({
                    "id": item_id,
                    "transaction_id": transaction_id,
                    "component_id": component_id,
                    "quantity_borrowed": qty_borrowed,
                    "quantity_returned": qty_returned
                })
            except ValueError as e:
                errors.append(f"Row {idx+2} (Borrow Items): Invalid data type - {str(e)}")
            except Exception as e:
                errors.append(f"Row {idx+2} (Borrow Items): {str(e)}")
        
        if errors:
            raise HTTPException(400, {
                "message": "Validation errors found",
                "errors": errors[:50],  # Limit to first 50 errors
                "total_errors": len(errors),
                "backup_path": backup_path
            })
        
        # Validate component quantities vs borrowed quantities
        quantity_errors = []
        for comp in active_components_data:
            comp_id = comp["id"]
            total_borrowed = sum(
                item["quantity_borrowed"] - item["quantity_returned"]
                for item in borrow_items_data
                if item["component_id"] == comp_id
            )
            if total_borrowed > comp["quantity"]:
                quantity_errors.append(
                    f"Component '{comp['name']}' (ID: {comp_id}): Total borrowed quantity ({total_borrowed}) exceeds available quantity ({comp['quantity']})"
                )
        
        if quantity_errors:
            raise HTTPException(400, {
                "message": "Quantity validation errors",
                "errors": quantity_errors,
                "backup_path": backup_path
            })
        
        # All validations passed - proceed with restructuring
        # Disable foreign keys
        db.execute(text("PRAGMA foreign_keys=OFF"))
        
        try:
            # Step 1: Delete all existing data (in correct order due to foreign keys)
            db.execute(text("DELETE FROM return_events"))  # Delete return events first (they reference borrow_items)
            db.execute(text("DELETE FROM borrow_items"))
            db.execute(text("DELETE FROM borrow_transactions"))
            db.execute(text("DELETE FROM borrowers"))
            db.execute(text("DELETE FROM components"))
            db.flush()
            
            # Step 2: Insert borrowers first (need borrower IDs for transactions)
            borrower_id_map = {}  # Maps borrower_key to actual inserted borrower_id
            borrowers_to_insert = []
            seen_borrower_keys = set()  # Track which borrowers we've already collected
            
            # Collect unique borrowers from transactions
            for tx in borrow_transactions_data:
                borrower_key = tx["borrower_key"]
                if borrower_key not in seen_borrower_keys:
                    seen_borrower_keys.add(borrower_key)
                    borrowers_to_insert.append({
                        "key": borrower_key,
                        "name": tx["borrower_name"],
                        "tp_id": tx["borrower_tp_id"],
                        "phone": tx["borrower_phone"],
                        "email": tx["borrower_email"]
                    })
            
            # Insert borrowers and build ID mapping
            for borrower in borrowers_to_insert:
                cursor = db.execute(text("""
                    INSERT INTO borrowers (name, tp_id, phone, email)
                    VALUES (:name, :tp_id, :phone, :email)
                """), {
                    'name': borrower["name"],
                    'tp_id': borrower["tp_id"],
                    'phone': borrower["phone"],
                    'email': borrower["email"]
                })
                borrower_id = cursor.lastrowid
                borrower_id_map[borrower["key"]] = borrower_id
            
            db.flush()
            
            # Step 3: Insert borrow transactions
            for tx in borrow_transactions_data:
                borrower_key = tx["borrower_key"]
                borrower_id = borrower_id_map[borrower_key]
                
                # Resolve PIC name to User ID (creates user if doesn't exist)
                pic_user = resolve_user(db, tx["pic_name"])
                
                # Convert status string to BorrowStatus enum
                status_enum = BorrowStatus[tx["status"]]
                
                db.execute(text("""
                    INSERT INTO borrow_transactions 
                    (id, borrower_id, borrowed_by_id, reason, expected_return_date, status, borrowed_at, overdue_email_sent)
                    VALUES (:id, :borrower_id, :borrowed_by_id, :reason, :expected_return_date, :status, :borrowed_at, :overdue_email_sent)
                """), {
                    'id': tx["id"],
                    'borrower_id': borrower_id,
                    'borrowed_by_id': pic_user.id,
                    'reason': tx["reason"],
                    'expected_return_date': tx["expected_return_date"],
                    'status': status_enum.value,
                    'borrowed_at': tx["borrowed_at"],
                    'overdue_email_sent': False
                })
            
            db.flush()
            
            # Step 4: Insert active components with their ORIGINAL IDs (no reshuffling)
            for comp in active_components_data:
                db.execute(text("""
                    INSERT INTO components 
                    (id, name, category, quantity, remarks, image_path, 
                     storage_type, cabinet_number, shelf_number, container_id, drawer_index, storage_box_index,
                     location_type, location_index, is_deleted, deleted_reason, deleted_at, created_at, updated_at)
                    VALUES (:id, :name, :category, :quantity, :remarks, :image_path,
                            :storage_type, :cabinet_number, :shelf_number, :container_id, :drawer_index, :storage_box_index,
                            :location_type, :location_index, :is_deleted, :deleted_reason, :deleted_at, :created_at, :updated_at)
                """), {
                    'id': comp["id"],  # Keep original ID from Excel
                    'name': comp["name"],
                    'category': comp["category"],
                    'quantity': comp["quantity"],
                    'remarks': comp["remarks"],
                    'image_path': comp["image_path"],
                    'storage_type': comp["storage_type"],
                    'cabinet_number': comp["cabinet_number"],
                    'shelf_number': comp["shelf_number"],
                    'container_id': comp["container_id"],
                    'drawer_index': comp["drawer_index"],
                    'storage_box_index': comp["storage_box_index"],
                    'location_type': comp["location_type"],
                    'location_index': comp["location_index"],
                    'is_deleted': 0,
                    'deleted_reason': None,
                    'deleted_at': None,
                    'created_at': comp["created_at"],
                    'updated_at': comp["updated_at"]
                })
            
            db.flush()
            
            # Step 5: Insert borrow items (only those referencing active components and valid transactions)
            # Keep original IDs but ensure no conflicts
            for item in borrow_items_data:
                db.execute(text("""
                    INSERT INTO borrow_items 
                    (id, transaction_id, component_id, quantity_borrowed, quantity_returned)
                    VALUES (:id, :transaction_id, :component_id, :quantity_borrowed, :quantity_returned)
                """), {
                    'id': item["id"],  # Keep original ID from Excel
                    'transaction_id': item["transaction_id"],
                    'component_id': item["component_id"],  # Already validated to exist in active components
                    'quantity_borrowed': item["quantity_borrowed"],
                    'quantity_returned': item["quantity_returned"]
                })
            
            db.flush()
            
            # Step 6: Re-enable foreign keys
            db.execute(text("PRAGMA foreign_keys=ON"))
            
            db.commit()
            
            deleted_components_count = len([c for c in all_components_data if c.get("is_deleted", False)])
            removed_borrow_items_count = len([item for _, item in df_borrow_items.iterrows() 
                                             if int(item["Component ID"]) in deleted_component_ids])
            
            return {
                "message": "Database restructured successfully from Excel file",
                "active_components_imported": len(active_components_data),
                "deleted_components_removed": deleted_components_count,
                "borrowers_imported": len(borrowers_to_insert),
                "borrow_transactions_imported": len(borrow_transactions_data),
                "borrow_items_imported": len(borrow_items_data),
                "borrow_items_removed_for_deleted_components": removed_borrow_items_count,
                "backup_path": backup_path
            }
            
        except Exception as e:
            db.rollback()
            db.execute(text("PRAGMA foreign_keys=ON"))  # Re-enable even on error
            raise HTTPException(500, f"Error during database restructuring: {str(e)}")
        
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(500, f"Error processing Excel file: {str(e)}")


@router.get("/restructure/preview")
def preview_restructure(db: Session = Depends(get_db)):
    """
    Preview what changes would be made during restructuring
    without actually making changes
    """
    active_components = (
        db.query(Component)
        .filter(Component.is_deleted == False)
        .order_by(Component.id)
        .all()
    )
    
    deleted_components = (
        db.query(Component)
        .filter(Component.is_deleted == True)
        .count()
    )
    
    # Create ID mapping preview
    id_mapping = []
    for new_id, component in enumerate(active_components, start=1):
        old_id = component.id
        if old_id != new_id:
            # Count borrow items that reference this component
            borrow_item_count = db.query(BorrowItem).filter(
                BorrowItem.component_id == old_id
            ).count()
            
            id_mapping.append({
                "old_id": old_id,
                "new_id": new_id,
                "component_name": component.name,
                "affected_borrow_items": borrow_item_count
            })
    
    return {
        "total_active_components": len(active_components),
        "components_to_delete": deleted_components,
        "id_changes_required": len(id_mapping),
        "id_mapping_preview": id_mapping[:50],  # Limit to first 50 for preview
        "note": "This is a preview. No changes have been made."
    }

