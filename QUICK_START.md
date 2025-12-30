# Quick Start Guide - CREDIT Inventory Dashboard

This guide will help you quickly set up and run the CREDIT Inventory Dashboard using Docker.

## Prerequisites

### Required Software

1. **Docker Desktop** (Windows/Mac/Linux)
   - Download: https://www.docker.com/products/docker-desktop/
   - Install and start Docker Desktop
   - Verify installation: `docker --version`

2. **Git** (if cloning from GitHub)
   - Usually comes pre-installed
   - Verify: `git --version`

### System Requirements

- **OS**: Windows 10/11, macOS, or Linux
- **RAM**: Minimum 4GB (8GB recommended)
- **Disk Space**: At least 2GB free
- **Ports**: 80 (frontend) and 8000 (backend) must be available

## Installation Steps

### 1. Clone or Download the Repository

```bash
git clone <your-repository-url>
cd CREDIT-INVENTORY-DASHBOARD-NEW
```

Or download and extract the ZIP file.

### 2. Create Environment File

```bash
# Windows PowerShell
cp env.example .env

# Linux/Mac
cp env.example .env
```

### 3. Configure Environment Variables (Optional)

Edit `.env` file if you need to customize:
- `VITE_API_URL` - Backend API URL (default: `http://localhost:8000`)
- `FRONTEND_URL` - Frontend URL (default: `http://localhost`)
- Email settings (optional - only if you need email notifications)

**Note**: Default values work for local development. You only need to change these for production or if using a different setup.

### 4. Build and Start Containers

```bash
# Build and start all containers
docker compose up -d --build

# Or if using older Docker version
docker-compose up -d --build
```

This will:
- Build the backend container (Python/FastAPI)
- Build the frontend container (React/nginx)
- Create Docker volumes for data persistence
- Start both services

### 5. Access the Application

Once containers are running:
- **Frontend Dashboard**: http://localhost
- **Backend API**: http://localhost:8000
- **Backend Health Check**: http://localhost:8000/

## Common Commands

### Start containers
```bash
docker compose up -d
```

### Stop containers
```bash
docker compose down
```

### View logs
```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f backend
docker compose logs -f frontend
```

### Restart a service
```bash
docker compose restart backend
docker compose restart frontend
```

### Rebuild after code changes
```bash
docker compose up -d --build
```

## First-Time Setup

1. **Access the dashboard**: http://localhost
2. **Initialize containers** (if not already done):
   - Go to "Containers" page
   - Click "Init Containers" button
   - This creates all container entries (A1-T3)

3. **Set up admin account**:
   - Default password: `admin123`
   - Change it in "Account Settings" after first login

## Data Persistence

Your data is stored in Docker volumes:
- **Database**: `credit-inventory-dashboard-new_database-data`
- **Uploads**: `credit-inventory-dashboard-new_uploads-data`
- **QR Codes**: `credit-inventory-dashboard-new_qr-codes-data`

**Important**: Data persists even when containers are stopped. To completely remove data:
```bash
docker compose down -v  # Removes volumes too
```

## Troubleshooting

### Containers won't start
- Check if Docker Desktop is running
- Verify ports 80 and 8000 are not in use
- Check logs: `docker compose logs`

### Permission errors (Windows)
- See `WINDOWS_DATABASE_FIX.md` for solutions
- The current setup uses Docker volumes to avoid permission issues

### Frontend can't connect to backend
- Check backend is running: `docker compose ps`
- Verify environment variables in `.env`
- Check logs: `docker compose logs backend`

### Database errors
- Check logs: `docker compose logs backend`
- Verify database volume exists: `docker volume ls`
- See `DOCKER_SETUP.md` for detailed troubleshooting

## Email Configuration (Optional)

If you want email notifications:

1. **For Gmail**:
   - Enable 2-Step Verification
   - Generate App Password: https://myaccount.google.com/apppasswords
   - Update `.env` with your credentials

2. **For Outlook**:
   - Enable POP/IMAP in settings
   - Use your regular password
   - Update `.env` with your credentials

3. **Restart backend**:
   ```bash
   docker compose restart backend
   ```

## Production Deployment

For production, you'll need to:
1. Update environment variables with production URLs
2. Set up a reverse proxy (nginx/Apache) for SSL
3. Configure domain names
4. Set up regular backups

See `DOCKER_SETUP.md` for detailed production instructions.

## Additional Documentation

- `DOCKER_SETUP.md` - Comprehensive Docker setup guide
- `DOCKER_INSTALLATION.md` - Docker installation instructions
- `DOCKER_LOGS_GUIDE.md` - How to check logs
- `WINDOWS_DATABASE_FIX.md` - Windows-specific fixes

## Support

For issues:
1. Check the logs: `docker compose logs`
2. Review the documentation files
3. Check GitHub issues (if applicable)

## What's Included

This containerized setup includes:
- ✅ FastAPI backend with SQLite database
- ✅ React frontend with nginx
- ✅ Automatic data persistence
- ✅ Health checks
- ✅ Production-ready configuration
- ✅ Email notification support (optional)
- ✅ QR code generation
- ✅ File upload support

Enjoy using the CREDIT Inventory Dashboard!

