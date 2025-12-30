# Fixing Database Read-Only Issue on Windows

## The Problem
On Windows, when you mount a SQLite database file directly into a Docker container, it becomes read-only because Windows file permissions don't translate properly to Linux containers.

## Solution 1: Fix Windows File Permissions (Recommended)

1. **Remove read-only attribute in Windows:**
   ```powershell
   # Navigate to your project
   cd C:\cursor-IDE\CREDIT-INVENTORY-DASHBOARD-NEW\backend
   
   # Remove read-only attribute
   attrib -r inventory.db
   ```

2. **Ensure the file is writable:**
   - Right-click `inventory.db` → Properties
   - Uncheck "Read-only" if checked
   - Click OK

3. **Rebuild containers:**
   ```powershell
   docker compose down
   docker compose up -d --build
   ```

## Solution 2: Use Named Docker Volume (Alternative)

If Solution 1 doesn't work, we can use a Docker named volume instead of a bind mount. This avoids Windows permission issues entirely.

Update `docker-compose.yml` to use a named volume:

```yaml
volumes:
  - database-data:/app/data
```

And add at the bottom:
```yaml
volumes:
  database-data:
```

**Note**: With this approach, the database will be stored inside Docker's volume system, not directly in your `backend` folder. You'll need to backup/restore differently.

## Solution 3: Copy Database on Startup (Workaround)

The entrypoint script can copy the database file on startup to ensure it's writable. This is already implemented in the current setup.

## Verify the Fix

After applying a solution, check the database is writable:

```powershell
docker compose exec backend ls -la /app/data/inventory.db
```

The permissions should show `-rw-rw-rw-` or similar (writable).

## Current Status

The current setup uses:
- Database mounted to `/app/data/inventory.db`
- Entrypoint script that tries to fix permissions
- Environment variable `DATABASE_PATH` to specify the path

If you still see "readonly database" errors, try Solution 1 first (fix Windows permissions).

