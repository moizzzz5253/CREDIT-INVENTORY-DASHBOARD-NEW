# Migration Instructions for Location System

## Two-Step Migration Process

Due to SQLite limitations, migrating to the new location system requires **two migration scripts**:

### Step 1: Add New Columns
Run the first migration to add new storage location columns:

```bash
cd backend
python migrate_location_system.py
```

This will:
- Add `shelf_number` to containers table
- Add `storage_type`, `cabinet_number`, `shelf_number`, `drawer_index`, `storage_box_index` to components table
- Migrate existing data (sets defaults for existing components)
- Create a backup of your database

### Step 2: Make container_id Nullable (REQUIRED)
After Step 1, you **must** run the second migration:

```bash
cd backend
python migrate_make_container_id_nullable.py
```

This will:
- Recreate the components table with `container_id` as nullable
- Preserve all existing data
- Create a backup before making changes

**Why is this needed?** SQLite doesn't support `ALTER TABLE` to change a column from NOT NULL to nullable. The table must be recreated.

## Error You'll See Without Step 2

If you skip Step 2, you'll see this error when creating components with DRAWER or STORAGE_BOX storage types:

```
sqlalchemy.exc.IntegrityError: (sqlite3.IntegrityError) NOT NULL constraint failed: components.container_id
```

This happens because drawers and storage boxes don't use containers, so `container_id` must be NULL.

## Full Migration Process

```bash
# 1. Stop your application if it's running

# 2. Navigate to backend directory
cd backend

# 3. Run first migration (adds new columns)
python migrate_location_system.py

# 4. Run second migration (makes container_id nullable)
python migrate_make_container_id_nullable.py

# 5. Start your application
# Backend: uvicorn app.main:app --reload --port 8000
# Frontend: cd frontend2 && npm run dev
```

## Verification

After both migrations, verify:

```bash
# Using sqlite3 command line (optional)
sqlite3 inventory.db

# Check that container_id is nullable
PRAGMA table_info(components);

# Look for container_id row - the "notnull" column should be 0 (nullable)
```

## Rollback

If something goes wrong:

1. **Stop the application immediately**
2. **Restore from backup**:
   ```bash
   # For Step 1 backup:
   cp database_backups/inventory_backup_location_migration.db inventory.db
   
   # For Step 2 backup:
   cp database_backups/inventory_backup_container_nullable.db inventory.db
   ```
3. **Review error messages** and fix issues
4. **Retry migration** (migrations are idempotent where possible)

## New Database

If you're creating a **new database** (no existing data):
- You can skip both migrations
- The application will create tables with the correct schema automatically
- Just start the application normally

## Troubleshooting

### Migration script says "already applied"
- This is normal if you've run it before
- Check if the columns exist: `PRAGMA table_info(components);`

### Foreign key constraint errors
- Make sure containers table exists before migrating components
- Check that all container_id values in existing data are valid (or will be set to NULL)

### Data loss concerns
- Both scripts create automatic backups
- Check `database_backups/` folder
- Test with a copy of your database first if concerned

