# Docker Setup Guide for CREDIT Inventory Dashboard

This guide will help you containerize and run the CREDIT Inventory Dashboard using Docker and Docker Compose.

## Prerequisites

- Docker Desktop (Windows/Mac) or Docker Engine + Docker Compose (Linux)
  - Download: https://www.docker.com/products/docker-desktop/
  - See `DOCKER_INSTALLATION.md` for detailed installation instructions
- At least 2GB of free disk space
- Ports 80 and 8000 available on your system

**Note**: Modern Docker Desktop uses `docker compose` (without hyphen). Older versions use `docker-compose`. Both commands are shown in examples below.

## Quick Start

1. **Clone/Navigate to the project directory**
   ```bash
   cd CREDIT-INVENTORY-DASHBOARD-NEW
   ```

2. **Create environment file**
   ```bash
   cp env.example .env
   ```

3. **Edit `.env` file** (optional, defaults work for local development)
   - Set `VITE_API_URL=http://localhost:8000` for local Docker setup
   - Set `FRONTEND_URL=http://localhost` for local Docker setup
   - Configure email settings if needed (optional)

4. **Build and start containers**
   ```bash
   # Modern Docker Desktop (try this first)
   docker compose up -d --build
   
   # OR older versions
   docker-compose up -d --build
   ```

5. **Access the application**
   - Frontend: http://localhost
   - Backend API: http://localhost:8000
   - Backend Health: http://localhost:8000/

## Architecture

The application consists of two containers:

- **Backend Container** (`credit-backend`)
  - FastAPI application
  - Runs on port 8000
  - Handles API requests, database operations, file uploads

- **Frontend Container** (`credit-frontend`)
  - React/Vite application served by nginx
  - Runs on port 80
  - Proxies API requests to backend container

## Environment Variables

### Required Variables

- `VITE_API_URL` - Backend API URL (default: `http://localhost:8000`)
- `FRONTEND_URL` - Frontend URL for QR code generation (default: `http://localhost`)

### Optional Variables

- `API_PORT` - Backend port (default: `8000`)
- `FRONTEND_PORT` - Frontend port (default: `80`)
- `SMTP_HOST` - SMTP server for email (optional)
- `SMTP_PORT` - SMTP port (default: `587`)
- `SMTP_USER` - SMTP username (optional)
- `SMTP_PASSWORD` - SMTP password (optional)
- `SMTP_FROM_EMAIL` - Sender email address (optional)
- `SMTP_FROM_NAME` - Sender name (optional)
- `SMTP_USE_TLS` - Use TLS for SMTP (default: `true`)

## Volume Mounts

The following directories are mounted as volumes for data persistence:

- `./backend/inventory.db` → Database file (SQLite)
- `./backend/qr_codes/` → Generated QR code images
- `./backend/uploads/` → Uploaded component images
- `./backend/database_backups/` → Database backup files

**Important**: These files persist on your host machine, so data is preserved even when containers are removed.

## Common Commands

### Start containers
```bash
# Modern syntax
docker compose up -d
# OR
docker-compose up -d
```

### Stop containers
```bash
docker compose down
# OR
docker-compose down
```

### View logs
```bash
# All services
docker compose logs -f
# OR
docker-compose logs -f

# Specific service
docker compose logs -f backend
docker compose logs -f frontend
```

### Rebuild containers (after code changes)
```bash
docker compose up -d --build
# OR
docker-compose up -d --build
```

### Restart a specific service
```bash
docker compose restart backend
docker compose restart frontend
```

### Execute commands in containers
```bash
# Backend shell
docker compose exec backend bash
# OR
docker-compose exec backend bash

# Frontend shell
docker compose exec frontend sh
```

### Check container status
```bash
docker compose ps
# OR
docker-compose ps
```

## Production Deployment

### 1. Update Environment Variables

Edit `.env` file with production values:

```env
VITE_API_URL=https://api.yourdomain.com
FRONTEND_URL=https://yourdomain.com
```

### 2. Configure Reverse Proxy

Set up nginx or another reverse proxy on your host to:
- Handle SSL/TLS certificates
- Route traffic to containers
- Configure domain names

Example nginx configuration (on host):
```nginx
server {
    listen 80;
    server_name yourdomain.com;
    
    location / {
        proxy_pass http://localhost:80;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}

server {
    listen 80;
    server_name api.yourdomain.com;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 3. Security Considerations

- Change default admin password after first login
- Use strong SMTP passwords
- Configure firewall rules
- Use HTTPS in production
- Regularly backup `inventory.db` file
- Review CORS settings in `frontend2/nginx.conf` for production

## Troubleshooting

### Containers won't start

1. **Check if ports are in use**
   ```bash
   # Windows
   netstat -ano | findstr :80
   netstat -ano | findstr :8000
   
   # Linux/Mac
   lsof -i :80
   lsof -i :8000
   ```

2. **Check Docker logs**
   ```bash
   docker-compose logs
   ```

3. **Verify Docker is running**
   ```bash
   docker ps
   ```

### Frontend can't connect to backend

1. **Check environment variables**
   - Ensure `VITE_API_URL` is set correctly in `.env`
   - Rebuild frontend: `docker-compose up -d --build frontend`

2. **Check network connectivity**
   ```bash
   docker-compose exec frontend wget -O- http://backend:8000/
   ```

3. **Verify backend is running**
   ```bash
   curl http://localhost:8000/
   ```

### Database issues

1. **Check database file permissions**
   ```bash
   ls -la backend/inventory.db
   ```

2. **Verify volume mount**
   ```bash
   docker-compose exec backend ls -la /app/inventory.db
   ```

3. **Backup database**
   ```bash
   cp backend/inventory.db backend/database_backups/inventory_backup_$(date +%Y%m%d_%H%M%S).db
   ```

### QR codes not working

1. **Check FRONTEND_URL environment variable**
   - Should be the public URL where frontend is accessible
   - Not localhost if accessing from other devices

2. **Verify QR code directory**
   ```bash
   docker-compose exec backend ls -la /app/qr_codes
   ```

### Email not working

1. **Verify SMTP settings in `.env`**
2. **Check backend logs for SMTP errors**
   ```bash
   docker-compose logs backend | grep -i smtp
   ```

3. **Test SMTP connection**
   ```bash
   docker-compose exec backend python check_env_config.py
   ```

### Performance Issues

1. **Check container resources**
   ```bash
   docker stats
   ```

2. **Increase Docker memory limit** (Docker Desktop → Settings → Resources)

3. **Optimize database** (if large)
   ```bash
   docker-compose exec backend python -c "import sqlite3; conn = sqlite3.connect('inventory.db'); conn.execute('VACUUM'); conn.close()"
   ```

## Development Workflow

### Making Code Changes

1. **Backend changes**: Restart backend container
   ```bash
   docker-compose restart backend
   ```

2. **Frontend changes**: Rebuild frontend container
   ```bash
   docker-compose up -d --build frontend
   ```

### Running in Development Mode

For active development, you may prefer running services directly:

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend:**
```bash
cd frontend2
npm install
npm run dev
```

## Backup and Restore

### Backup Database

```bash
# Copy database file
cp backend/inventory.db backend/database_backups/inventory_backup_$(date +%Y%m%d_%H%M%S).db

# Or use Docker
docker-compose exec backend cp /app/inventory.db /app/database_backups/inventory_backup_$(date +%Y%m%d_%H%M%S).db
```

### Restore Database

```bash
# Stop containers
docker-compose down

# Replace database file
cp backend/database_backups/inventory_backup_YYYYMMDD_HHMMSS.db backend/inventory.db

# Start containers
docker-compose up -d
```

## Cleanup

### Remove containers and networks
```bash
docker-compose down
```

### Remove containers, networks, and volumes
```bash
docker-compose down -v
```

**Warning**: This will delete all data in volumes. Make sure to backup first!

### Remove images
```bash
docker-compose down --rmi all
```

## Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)

## Support

For issues specific to this application, check:
- Backend logs: `docker-compose logs backend`
- Frontend logs: `docker-compose logs frontend`
- Container status: `docker-compose ps`

