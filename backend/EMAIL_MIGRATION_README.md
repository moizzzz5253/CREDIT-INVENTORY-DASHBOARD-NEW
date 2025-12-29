# Borrower Email Integration - Migration Guide

## Overview
This migration adds an `email` field to the borrower details. The email will be used for:
- Sending overdue alerts
- Notifying borrow and return transaction details

## Changes Made

### Backend Changes
1. **Database Model** (`app/database/models.py`)
   - Added `email` column to `Borrower` model (NOT NULL, indexed)

2. **Schemas** (`app/schemas/borrower.py`)
   - Added `email: EmailStr` to `BorrowerCreate` and `BorrowerRead` schemas
   - Email validation is enforced via Pydantic's `EmailStr`

3. **Routers Updated**
   - `app/routers/borrow.py`: Includes email when creating borrowers and in active borrows
   - `app/routers/history.py`: Includes email in history records
   - `app/routers/reports.py`: Includes email in Excel exports

4. **Mappers** (`app/utils/borrow_mapper.py`)
   - Updated to include email in borrower data mapping

### Frontend Changes
1. **BorrowNew.jsx**
   - Added email input field (required)
   - Added email validation (basic regex)
   - Updated form state and validation logic

2. **BorrowActive.jsx**
   - Displays email in borrower cards
   - Includes email in search functionality
   - Shows email in return modal

3. **History.jsx**
   - Displays email in history records
   - Includes email in search functionality

## Migration Steps

### Step 1: Run the Migration Script
Before starting the application, run the migration script to add the email column to the existing database:

```bash
cd backend
python migrate_add_email_to_borrowers.py
```

This script will:
- Check if the email column already exists
- Add the email column with a default empty string for existing borrowers
- Create an index on the email column
- Preserve all existing borrower data

### Step 2: Verify Migration
After running the migration, you can verify it worked by checking the database:
- The `borrowers` table should now have an `email` column
- Existing borrowers will have empty email strings (can be updated later)

### Step 3: Start the Application
After migration, start the application as usual. New borrowers will require an email address.

## Important Notes

1. **Existing Borrowers**: Existing borrowers in the database will have empty email strings after migration. You may want to update them manually or through the application.

2. **Email Validation**: 
   - Frontend: Basic regex validation
   - Backend: Pydantic's `EmailStr` provides strict email validation

3. **Database Safety**: The migration script is safe and non-destructive:
   - It only adds a new column
   - It doesn't modify or delete existing data
   - It can be run multiple times safely (checks if column exists)

4. **Future Email Features**: The email field is now ready for:
   - Overdue alert notifications
   - Borrow transaction notifications
   - Return transaction notifications

## Testing Checklist

- [ ] Run migration script successfully
- [ ] Create a new borrow with email - should work
- [ ] Create a new borrow without email - should fail validation
- [ ] View active borrows - email should be displayed
- [ ] Search by email in active borrows - should work
- [ ] View history - email should be displayed
- [ ] Export reports - email should be included
- [ ] Verify existing borrowers still work (with empty email)

## Rollback (if needed)

If you need to rollback this change:
1. Remove the email column from the database:
   ```sql
   -- Note: SQLite doesn't support DROP COLUMN directly
   -- You would need to recreate the table or use a more complex migration
   ```
2. Revert the code changes using git

However, since this is an additive change, rollback is typically not necessary.






