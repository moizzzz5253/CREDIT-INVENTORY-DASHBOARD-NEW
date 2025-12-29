"""
Database migration script to add overdue_email_sent column to borrow_transactions table.

This script safely adds the overdue_email_sent column to track whether overdue
reminder emails have been sent for each transaction.
"""

import sqlite3
import os
from pathlib import Path

# Database path
DB_PATH = Path(__file__).parent / "inventory.db"

def migrate():
    """Add overdue_email_sent column to borrow_transactions table if it doesn't exist."""
    if not DB_PATH.exists():
        print(f"Database not found at {DB_PATH}")
        print("The database will be created automatically when you run the application.")
        return
    
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    
    try:
        # Check if overdue_email_sent column already exists
        cursor.execute("PRAGMA table_info(borrow_transactions)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'overdue_email_sent' in columns:
            print("overdue_email_sent column already exists in borrow_transactions table. Migration not needed.")
            return
        
        print("Adding overdue_email_sent column to borrow_transactions table...")
        
        # Add overdue_email_sent column with default False for existing records
        cursor.execute("""
            ALTER TABLE borrow_transactions 
            ADD COLUMN overdue_email_sent INTEGER NOT NULL DEFAULT 0
        """)
        
        conn.commit()
        
        # Count existing transactions
        cursor.execute("SELECT COUNT(*) FROM borrow_transactions")
        count = cursor.fetchone()[0]
        
        print("Successfully added overdue_email_sent column to borrow_transactions table.")
        print(f"Migration completed. {count} existing transaction(s) have overdue_email_sent set to False.")
        
    except sqlite3.Error as e:
        conn.rollback()
        print(f"Error during migration: {e}")
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    print("=" * 60)
    print("Overdue Email Flag Migration Script")
    print("=" * 60)
    print()
    migrate()
    print()
    print("=" * 60)






