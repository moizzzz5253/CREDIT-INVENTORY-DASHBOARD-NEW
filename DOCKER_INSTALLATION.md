# Docker Installation Guide for Windows

## Step 1: Install Docker Desktop

1. **Download Docker Desktop for Windows**
   - Go to: https://www.docker.com/products/docker-desktop/
   - Click "Download for Windows"
   - The installer will be downloaded (Docker Desktop Installer.exe)

2. **Run the Installer**
   - Double-click `Docker Desktop Installer.exe`
   - Follow the installation wizard
   - Make sure "Use WSL 2 instead of Hyper-V" is checked (recommended)
   - Click "Ok" when installation completes

3. **Restart Your Computer** (if prompted)

4. **Start Docker Desktop**
   - Launch Docker Desktop from the Start menu
   - Wait for Docker to start (whale icon in system tray should be steady)
   - You may need to accept the service agreement

5. **Verify Installation**
   - Open PowerShell or Command Prompt
   - Run: `docker --version`
   - You should see something like: `Docker version 24.x.x`

## Step 2: Verify Docker Compose

Modern Docker Desktop includes Docker Compose as a plugin. Try both commands:

```powershell
# New syntax (Docker Compose V2)
docker compose version

# Old syntax (Docker Compose V1 - may not work on newer versions)
docker-compose --version
```

**Note**: Newer Docker Desktop versions use `docker compose` (without hyphen) instead of `docker-compose`.

## Step 3: Run the Application

Once Docker is installed and running:

```powershell
# Navigate to project directory
cd C:\cursor-IDE\CREDIT-INVENTORY-DASHBOARD-NEW

# Try the new syntax first
docker compose up -d --build

# If that doesn't work, try the old syntax
docker-compose up -d --build
```

## Troubleshooting

### Docker Desktop won't start
- Make sure virtualization is enabled in BIOS
- Check Windows features: Enable "Virtual Machine Platform" and "Windows Subsystem for Linux"
- Restart your computer

### "WSL 2 installation is incomplete"
- Install WSL 2: https://docs.microsoft.com/en-us/windows/wsl/install
- Or use Hyper-V instead (uncheck WSL 2 option during Docker installation)

### Ports already in use
- Make sure ports 80 and 8000 are not being used by other applications
- Check with: `netstat -ano | findstr :80` and `netstat -ano | findstr :8000`

### Docker commands not recognized
- Restart PowerShell/Command Prompt after installation
- Make sure Docker Desktop is running (check system tray)
- Add Docker to PATH manually if needed (usually automatic)

## Alternative: Use Docker Compose Standalone

If Docker Desktop is not an option, you can install Docker Engine and Docker Compose separately:

1. Install Docker Engine: https://docs.docker.com/engine/install/
2. Install Docker Compose: https://docs.docker.com/compose/install/

However, Docker Desktop is the easiest option for Windows.


