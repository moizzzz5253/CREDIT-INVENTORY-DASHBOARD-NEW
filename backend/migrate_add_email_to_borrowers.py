"""
Database migration script to add email column to borrowers table.

This script safely adds the email column to the existing borrowers table
without deleting any data. For existing borrowers, email will be set to
an empty string initially, but new borrowers will require an email.

Run this script once before starting the application after the model update.
"""

import sqlite3
import os
from pathlib import Path

# Database path
DB_PATH = Path(__file__).parent / "inventory.db"

def migrate():
    """Add email column to borrowers table if it doesn't exist."""
    if not DB_PATH.exists():
        print(f"Database not found at {DB_PATH}")
        print("The database will be created automatically when you run the application.")
        return
    
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    
    try:
        # Check if email column already exists
        cursor.execute("PRAGMA table_info(borrowers)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'email' in columns:
            print("Email column already exists in borrowers table. Migration not needed.")
            return
        
        print("Adding email column to borrowers table...")
        
        # Add email column with a default empty string for existing records
        # This allows the migration to work without breaking existing data
        cursor.execute("""
            ALTER TABLE borrowers 
            ADD COLUMN email TEXT NOT NULL DEFAULT ''
        """)
        
        # Create index on email column for better query performance
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS ix_borrowers_email 
            ON borrowers(email)
        """)
        
        conn.commit()
        
        # Count existing borrowers
        cursor.execute("SELECT COUNT(*) FROM borrowers")
        count = cursor.fetchone()[0]
        
        print("Successfully added email column to borrowers table.")
        print("Created index on email column.")
        print(f"Migration completed. {count} existing borrower(s) have empty email (can be updated later).")
        print("\nNote: Existing borrowers have empty email. You may want to update them manually.")
        
    except sqlite3.Error as e:
        conn.rollback()
        print(f"Error during migration: {e}")
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    print("=" * 60)
    print("Borrower Email Migration Script")
    print("=" * 60)
    print()
    migrate()
    print()
    print("=" * 60)

