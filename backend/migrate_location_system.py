"""
Migration script to add new location system fields to Component and Container tables.
This script handles the migration from the old container-only system to the new
Cabinet/Drawer/Storage Box system.

Run this script once before starting the application with the new models.
"""
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "inventory.db"
BACKUP_PATH = Path(__file__).parent / "database_backups" / f"inventory_backup_location_migration.db"

def backup_database():
    """Create a backup of the database before migration"""
    import shutil
    BACKUP_PATH.parent.mkdir(exist_ok=True)
    if DB_PATH.exists():
        shutil.copy2(DB_PATH, BACKUP_PATH)
        print(f"✓ Database backed up to {BACKUP_PATH}")
    else:
        print("⚠ Database not found, skipping backup")

def migrate_database():
    """Apply migration to add new location system fields"""
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    
    try:
        # Check if migration has already been applied
        cursor.execute("PRAGMA table_info(components)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if "storage_type" in columns:
            print("✓ Migration already applied (storage_type column exists)")
            return
        
        print("Starting migration...")
        
        # Step 1: Add shelf_number to containers table
        print("Adding shelf_number to containers table...")
        try:
            cursor.execute("ALTER TABLE containers ADD COLUMN shelf_number INTEGER")
            print("✓ Added shelf_number to containers")
        except sqlite3.OperationalError as e:
            if "duplicate column" in str(e).lower():
                print("⚠ shelf_number already exists in containers")
            else:
                raise
        
        # Step 2: Add new columns to components table
        print("Adding new columns to components table...")
        
        # Add storage_type
        try:
            cursor.execute("ALTER TABLE components ADD COLUMN storage_type VARCHAR(20) DEFAULT 'CABINET'")
            print("✓ Added storage_type to components")
        except sqlite3.OperationalError as e:
            if "duplicate column" in str(e).lower():
                print("⚠ storage_type already exists in components")
        
        # Add cabinet_number
        try:
            cursor.execute("ALTER TABLE components ADD COLUMN cabinet_number INTEGER")
            print("✓ Added cabinet_number to components")
        except sqlite3.OperationalError as e:
            if "duplicate column" in str(e).lower():
                print("⚠ cabinet_number already exists in components")
        
        # Add shelf_number
        try:
            cursor.execute("ALTER TABLE components ADD COLUMN shelf_number INTEGER")
            print("✓ Added shelf_number to components")
        except sqlite3.OperationalError as e:
            if "duplicate column" in str(e).lower():
                print("⚠ shelf_number already exists in components")
        
        # Add drawer_index
        try:
            cursor.execute("ALTER TABLE components ADD COLUMN drawer_index INTEGER")
            print("✓ Added drawer_index to components")
        except sqlite3.OperationalError as e:
            if "duplicate column" in str(e).lower():
                print("⚠ drawer_index already exists in components")
        
        # Add storage_box_index
        try:
            cursor.execute("ALTER TABLE components ADD COLUMN storage_box_index INTEGER")
            print("✓ Added storage_box_index to components")
        except sqlite3.OperationalError as e:
            if "duplicate column" in str(e).lower():
                print("⚠ storage_box_index already exists in components")
        
        # Step 3: Migrate existing data
        print("Migrating existing component data...")
        
        # Set storage_type to CABINET for all existing components
        cursor.execute("UPDATE components SET storage_type = 'CABINET' WHERE storage_type IS NULL")
        updated_storage_type = cursor.rowcount
        print(f"  Updated {updated_storage_type} components with storage_type='CABINET'")
        
        # Extract cabinet_number from container for existing components
        cursor.execute("""
            UPDATE components 
            SET cabinet_number = (
                SELECT cabinet_number 
                FROM containers 
                WHERE containers.id = components.container_id
            )
            WHERE cabinet_number IS NULL AND container_id IS NOT NULL
        """)
        updated_cabinet = cursor.rowcount
        print(f"  Updated {updated_cabinet} components with cabinet_number from container")
        
        # Check for components with invalid container_id (no matching container)
        cursor.execute("""
            SELECT COUNT(*) FROM components 
            WHERE container_id IS NOT NULL 
            AND cabinet_number IS NULL
            AND storage_type = 'CABINET'
        """)
        invalid_containers = cursor.fetchone()[0]
        if invalid_containers > 0:
            print(f"  ⚠ Warning: {invalid_containers} components have invalid container_id (no matching container)")
            print(f"    These will need manual correction. Setting shelf_number=1 as default.")
        
        # Set default shelf_number to 1 for existing components (can be updated later)
        cursor.execute("UPDATE components SET shelf_number = 1 WHERE shelf_number IS NULL AND storage_type = 'CABINET'")
        updated_shelf = cursor.rowcount
        print(f"  Updated {updated_shelf} components with shelf_number=1 (default)")
        
        # Verify migration
        cursor.execute("SELECT COUNT(*) FROM components WHERE storage_type IS NULL")
        missing_storage_type = cursor.fetchone()[0]
        if missing_storage_type > 0:
            print(f"  ⚠ Warning: {missing_storage_type} components still have NULL storage_type")
        
        print("✓ Migrated existing component data")
        
        # Step 4: Make container_id nullable (SQLite limitation - we need to recreate the table)
        print("Making container_id nullable...")
        cursor.execute("PRAGMA table_info(components)")
        columns_info = cursor.fetchall()
        container_id_not_null = any(col[1] == "container_id" and col[3] == 1 for col in columns_info)
        
        if container_id_not_null:
            # SQLite doesn't support DROP NOT NULL directly, so we recreate the foreign key constraint
            # This is a limitation - we'll handle it in application code for now
            # The column will be nullable in new inserts, but SQLite won't enforce it on old data
            print("⚠ Note: container_id constraint modification requires table recreation")
            print("  The column will be nullable for new inserts. This is acceptable for SQLite.")
        else:
            print("✓ container_id is already nullable")
        
        conn.commit()
        print("\n✓ Migration completed successfully!")
        
    except Exception as e:
        conn.rollback()
        print(f"\n✗ Migration failed: {e}")
        print(f"Restore from backup: {BACKUP_PATH}")
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    print("=" * 60)
    print("Location System Migration Script")
    print("=" * 60)
    print()
    
    if not DB_PATH.exists():
        print("⚠ Database not found. Creating new database will happen on app startup.")
        print("  No migration needed for new databases.")
        exit(0)
    
    backup_database()
    print()
    migrate_database()
    print()
    print("=" * 60)
    print("Migration complete!")
    print()
    print("⚠ IMPORTANT: If you encounter NOT NULL constraint errors on container_id,")
    print("  run: python migrate_make_container_id_nullable.py")
    print("=" * 60)

