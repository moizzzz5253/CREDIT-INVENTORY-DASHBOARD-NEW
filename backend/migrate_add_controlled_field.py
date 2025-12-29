"""
Migration script to add is_controlled field to Component table.
This script adds the is_controlled boolean field to track components that cannot be borrowed.

Run this script once before starting the application with the new controlled component feature.
"""
import sqlite3
from pathlib import Path
import shutil
from datetime import datetime

DB_PATH = Path(__file__).parent / "inventory.db"
BACKUP_DIR = Path(__file__).parent / "database_backups"
BACKUP_PATH = BACKUP_DIR / f"inventory_backup_controlled_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"

def backup_database():
    """Create a backup of the database before migration"""
    BACKUP_DIR.mkdir(exist_ok=True)
    if DB_PATH.exists():
        shutil.copy2(DB_PATH, BACKUP_PATH)
        print(f"✓ Database backed up to: {BACKUP_PATH}")
    else:
        print("⚠ Database not found, skipping backup")

def migrate_database():
    """Apply migration to add is_controlled field"""
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    
    try:
        # Check if migration has already been applied
        cursor.execute("PRAGMA table_info(components)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if "is_controlled" in columns:
            print("✓ Migration already applied (is_controlled column exists)")
            return
        
        print("Starting migration...")
        
        # Add is_controlled column
        print("Adding is_controlled to components table...")
        try:
            cursor.execute("ALTER TABLE components ADD COLUMN is_controlled BOOLEAN DEFAULT 0 NOT NULL")
            print("✓ Added is_controlled to components")
        except sqlite3.OperationalError as e:
            if "duplicate column" in str(e).lower():
                print("⚠ is_controlled already exists in components")
            else:
                raise
        
        # Commit changes
        conn.commit()
        print("✓ Migration completed successfully")
        
    except Exception as e:
        conn.rollback()
        print(f"✗ Migration failed: {e}")
        raise
    
    finally:
        conn.close()

if __name__ == "__main__":
    print("=" * 60)
    print("Controlled Component Migration Script")
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
    print("=" * 60)

