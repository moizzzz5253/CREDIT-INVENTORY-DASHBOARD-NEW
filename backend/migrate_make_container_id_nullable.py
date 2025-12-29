"""
Migration script to make container_id nullable in components table.
This requires recreating the table because SQLite doesn't support ALTER TABLE MODIFY.

Run this AFTER migrate_location_system.py if you encounter NOT NULL constraint errors.
"""
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "inventory.db"
BACKUP_PATH = Path(__file__).parent / "database_backups" / f"inventory_backup_container_nullable.db"

def backup_database():
    """Create a backup of the database before migration"""
    import shutil
    BACKUP_PATH.parent.mkdir(exist_ok=True)
    if DB_PATH.exists():
        shutil.copy2(DB_PATH, BACKUP_PATH)
        print(f"✓ Database backed up to {BACKUP_PATH}")
    else:
        print("⚠ Database not found")

def make_container_id_nullable():
    """Recreate components table with container_id as nullable"""
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    
    try:
        print("Making container_id nullable...")
        
        # Check current schema
        cursor.execute("PRAGMA table_info(components)")
        columns = cursor.fetchall()
        container_id_info = [col for col in columns if col[1] == "container_id"]
        
        if not container_id_info:
            print("⚠ container_id column not found")
            return
        
        container_id_nullable = container_id_info[0][3] == 0  # 0 means nullable, 1 means NOT NULL
        
        if container_id_nullable:
            print("✓ container_id is already nullable")
            return
        
        print("  container_id is currently NOT NULL, recreating table...")
        
        # Step 1: Create new table with nullable container_id
        cursor.execute("""
            CREATE TABLE components_new (
                id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(150) NOT NULL,
                category VARCHAR(100) NOT NULL,
                quantity INTEGER NOT NULL,
                remarks VARCHAR(500),
                image_path VARCHAR NOT NULL,
                storage_type VARCHAR(20) NOT NULL DEFAULT 'CABINET',
                cabinet_number INTEGER,
                shelf_number INTEGER,
                container_id INTEGER,
                drawer_index INTEGER,
                storage_box_index INTEGER,
                location_type VARCHAR(20) NOT NULL DEFAULT 'NONE',
                location_index INTEGER,
                is_deleted BOOLEAN NOT NULL DEFAULT 0,
                deleted_reason VARCHAR,
                deleted_at DATETIME,
                created_at DATETIME NOT NULL,
                updated_at DATETIME,
                FOREIGN KEY(container_id) REFERENCES containers(id)
            )
        """)
        
        # Step 2: Copy data from old table to new table
        cursor.execute("""
            INSERT INTO components_new (
                id, name, category, quantity, remarks, image_path,
                storage_type, cabinet_number, shelf_number, container_id,
                drawer_index, storage_box_index, location_type, location_index,
                is_deleted, deleted_reason, deleted_at, created_at, updated_at
            )
            SELECT 
                id, name, category, quantity, remarks, image_path,
                COALESCE(storage_type, 'CABINET'), cabinet_number, shelf_number, container_id,
                drawer_index, storage_box_index, COALESCE(location_type, 'NONE'), location_index,
                is_deleted, deleted_reason, deleted_at, created_at, updated_at
            FROM components
        """)
        
        # Step 3: Drop old table
        cursor.execute("DROP TABLE components")
        
        # Step 4: Rename new table to original name
        cursor.execute("ALTER TABLE components_new RENAME TO components")
        
        # Step 5: Recreate indexes if any (basic indexes)
        cursor.execute("CREATE INDEX IF NOT EXISTS ix_components_storage_type ON components(storage_type)")
        cursor.execute("CREATE INDEX IF NOT EXISTS ix_components_cabinet_number ON components(cabinet_number)")
        cursor.execute("CREATE INDEX IF NOT EXISTS ix_components_container_id ON components(container_id)")
        
        conn.commit()
        print("✓ Successfully recreated components table with nullable container_id")
        
    except Exception as e:
        conn.rollback()
        print(f"\n✗ Migration failed: {e}")
        print(f"Restore from backup: {BACKUP_PATH}")
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    print("=" * 60)
    print("Make container_id Nullable Migration")
    print("=" * 60)
    print()
    
    if not DB_PATH.exists():
        print("⚠ Database not found.")
        exit(0)
    
    backup_database()
    print()
    make_container_id_nullable()
    print()
    print("=" * 60)
    print("Migration complete!")
    print("=" * 60)

