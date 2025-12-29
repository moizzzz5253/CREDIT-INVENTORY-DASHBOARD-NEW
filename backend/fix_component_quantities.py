"""
Migration script to fix component quantities.

This script ensures that component.quantity represents the TOTAL quantity,
not the available quantity. It calculates the true total by adding back
all currently borrowed quantities.
"""

import sqlite3
from pathlib import Path

# Database path
DB_PATH = Path(__file__).parent / "inventory.db"

def fix_quantities():
    """Fix component quantities to represent total quantity."""
    if not DB_PATH.exists():
        print(f"Database not found at {DB_PATH}")
        return
    
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    
    try:
        print("Fixing component quantities...")
        print("=" * 60)
        
        # Get all components
        cursor.execute("SELECT id, quantity FROM components WHERE is_deleted = 0")
        components = cursor.fetchall()
        
        fixed_count = 0
        
        for component_id, current_quantity in components:
            # Calculate total borrowed quantity for this component
            cursor.execute("""
                SELECT COALESCE(SUM(quantity_borrowed - quantity_returned), 0)
                FROM borrow_items
                WHERE component_id = ?
            """, (component_id,))
            
            borrowed_qty = cursor.fetchone()[0] or 0
            
            # True total = current quantity + borrowed quantity
            # (because current quantity was reduced when borrowing)
            true_total = current_quantity + borrowed_qty
            
            if true_total != current_quantity:
                # Update component with true total
                cursor.execute("""
                    UPDATE components
                    SET quantity = ?
                    WHERE id = ?
                """, (true_total, component_id))
                
                print(f"Component ID {component_id}: {current_quantity} -> {true_total} "
                      f"(added {borrowed_qty} borrowed)")
                fixed_count += 1
        
        conn.commit()
        
        print("=" * 60)
        print(f"Migration completed. Fixed {fixed_count} component(s).")
        print()
        print("Now component.quantity represents TOTAL quantity.")
        print("Available quantity = component.quantity - borrowed_quantity")
        
    except sqlite3.Error as e:
        conn.rollback()
        print(f"Error during migration: {e}")
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    print("=" * 60)
    print("Component Quantity Fix Script")
    print("=" * 60)
    print()
    print("This script fixes component quantities to represent TOTAL quantity.")
    print("It adds back all currently borrowed quantities.")
    print()
    fix_quantities()
    print()
    print("=" * 60)

