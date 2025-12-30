# How to Check Docker Logs

## Quick Commands

### View all logs (both services)
```powershell
docker compose logs
```

### View logs for specific service
```powershell
# Backend logs
docker compose logs backend

# Frontend logs
docker compose logs frontend
```

### View last 50 lines (most recent)
```powershell
docker compose logs --tail 50

# For specific service
docker compose logs backend --tail 50
docker compose logs frontend --tail 50
```

### Follow logs in real-time (like tail -f)
```powershell
docker compose logs -f

# For specific service
docker compose logs -f backend
docker compose logs -f frontend
```

### View logs since a specific time
```powershell
docker compose logs --since 10m    # Last 10 minutes
docker compose logs --since 1h     # Last 1 hour
docker compose logs --since 2024-01-01T00:00:00
```

### View logs with timestamps
```powershell
docker compose logs -t
```

## Alternative: Direct Docker Commands

If `docker compose` doesn't work, use `docker-compose` (with hyphen):
```powershell
docker-compose logs
docker-compose logs backend
docker-compose logs frontend --tail 50 -f
```

## Check Container Status

```powershell
# List all containers
docker compose ps

# Or
docker ps
```

## Execute Commands Inside Containers

```powershell
# Backend shell
docker compose exec backend bash

# Frontend shell
docker compose exec frontend sh

# Run a specific command
docker compose exec backend python --version
```

## Common Issues to Look For

1. **Database errors**: Look for "OperationalError", "readonly database"
2. **Connection errors**: Look for "Connection refused", "Cannot connect"
3. **Permission errors**: Look for "Permission denied", "EACCES"
4. **Build errors**: Check build logs with `docker compose build`

