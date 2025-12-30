# Setup Requirements - What You Need to Install

## For Fresh Installation

If you're setting up this system on a new machine, here's everything you need:

### 1. Docker Desktop (REQUIRED)

**What it is**: Containerization platform that runs the entire application

**Download**: https://www.docker.com/products/docker-desktop/

**Installation**:
- Download the installer for your OS
- Run the installer
- Follow the setup wizard
- Restart your computer if prompted
- Launch Docker Desktop and wait for it to start

**Verify**: Open terminal/PowerShell and run:
```bash
docker --version
docker compose version
```

**Why you need it**: The entire application runs in Docker containers. Without Docker, you cannot run the system.

---

### 2. Git (Optional - Only if cloning from GitHub)

**What it is**: Version control system

**Download**: https://git-scm.com/downloads

**Why you need it**: Only if you're cloning the repository from GitHub. If you download as ZIP, you don't need Git.

---

## That's It!

**You only need Docker Desktop** to run this system. Everything else (Python, Node.js, databases, etc.) is included in the Docker containers.

---

## What's NOT Required

You do NOT need to install:
- ❌ Python (included in backend container)
- ❌ Node.js (included in frontend container)
- ❌ SQLite (included in backend container)
- ❌ nginx (included in frontend container)
- ❌ Any Python packages (installed in container)
- ❌ Any npm packages (installed in container)

---

## Quick Setup After Installation

Once Docker Desktop is installed:

1. **Clone or download the repository**
   ```bash
   git clone <repository-url>
   cd CREDIT-INVENTORY-DASHBOARD-NEW
   ```

2. **Create environment file**
   ```bash
   cp env.example .env
   ```

3. **Start the application**
   ```bash
   docker compose up -d --build
   ```

4. **Access the dashboard**
   - Open browser: http://localhost

That's it! The system is running.

---

## System Requirements

- **Operating System**: Windows 10/11, macOS 10.15+, or Linux
- **RAM**: Minimum 4GB (8GB recommended)
- **Disk Space**: 2GB free space
- **Ports**: 80 and 8000 must be available
- **Internet**: Required for initial Docker image downloads

---

## Troubleshooting Installation

### Docker won't install
- **Windows**: Enable virtualization in BIOS, enable WSL 2
- **Mac**: Ensure you have an Intel or Apple Silicon Mac
- **Linux**: Install Docker Engine separately

### Docker Desktop won't start
- Check system requirements
- Restart your computer
- Check Docker Desktop logs

### Ports already in use
- Stop other services using ports 80 or 8000
- Or change ports in `docker-compose.yml`

---

## Next Steps

After installation:
1. Read `QUICK_START.md` for detailed setup instructions
2. Read `DOCKER_SETUP.md` for advanced configuration
3. Access the dashboard at http://localhost

---

## Summary

**Minimum Requirements**:
- ✅ Docker Desktop
- ✅ 4GB RAM
- ✅ 2GB disk space
- ✅ Internet connection (for first run)

**Everything else is handled automatically by Docker!**

