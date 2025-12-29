"""
Migration script to add email2 column to admin table.
Run this once to add the second email field to existing admin records.
"""
import sqlite3
import os
from pathlib import Path

# Get database path
db_path = Path(__file__).parent / "inventory.db"

if not db_path.exists():
    print(f"Database not found at {db_path}")
    exit(1)

print(f"Connecting to database: {db_path}")
conn = sqlite3.connect(str(db_path))
cursor = conn.cursor()

try:
    # Check if email2 column already exists
    cursor.execute("PRAGMA table_info(admin)")
    columns = [column[1] for column in cursor.fetchall()]
    
    if "email2" in columns:
        print("✓ email2 column already exists. No migration needed.")
    else:
        print("Adding email2 column to admin table...")
        cursor.execute("ALTER TABLE admin ADD COLUMN email2 TEXT")
        conn.commit()
        print("✓ Successfully added email2 column to admin table")
    
    # Verify the column was added
    cursor.execute("PRAGMA table_info(admin)")
    columns = [column[1] for column in cursor.fetchall()]
    print(f"\nCurrent admin table columns: {', '.join(columns)}")
    
except Exception as e:
    print(f"Error: {e}")
    conn.rollback()
finally:
    conn.close()
    print("\nMigration completed.")

