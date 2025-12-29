# Cloudflare Tunnel Setup Guide (Windows/PowerShell)

## Quick Start

```powershell
# 1. Run setup (one-time)
.\setup-cloudflare-tunnel.ps1

# 2. Generate config
.\generate-tunnel-config.ps1 -TunnelName "credit-inventory" -ApiDomain "api.yourdomain.com" -AppDomain "app.yourdomain.com"

# 3. Add DNS records in Cloudflare Dashboard

# 4. Start services
.\start-tunnel.ps1

# 5. Stop services (when done)
.\stop-tunnel.ps1
```

**See `TUNNEL_QUICK_START.md` for condensed reference.**

---

## Detailed Setup

## 1. Download and Install cloudflared

```powershell
# Navigate to a temporary directory
cd $env:TEMP

# Download cloudflared for Windows (64-bit)
Invoke-WebRequest -Uri "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe" -OutFile "cloudflared.exe"

# Move to a permanent location (e.g., create cloudflare directory in user folder)
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\cloudflare" | Out-Null
Move-Item -Force "$env:TEMP\cloudflared.exe" "$env:USERPROFILE\cloudflare\cloudflared.exe"

# Add to PATH (for current session)
$env:Path += ";$env:USERPROFILE\cloudflare"

# Add to PATH permanently (optional, requires restart or new PowerShell session)
[Environment]::SetEnvironmentVariable("Path", [Environment]::GetEnvironmentVariable("Path", "User") + ";$env:USERPROFILE\cloudflare", "User")

# Verify installation
cloudflared.exe --version
```

## 2. Tunnel Creation and Authentication

```powershell
# Login to Cloudflare (opens browser)
cloudflared.exe tunnel login

# Create a new tunnel (replace 'credit-inventory' with your desired tunnel name)
cloudflared.exe tunnel create credit-inventory

# This creates a tunnel and saves credentials to:
# C:\Users\<YourUsername>\.cloudflared\<tunnel-id>.json
```

**Note:** After login, you'll get a tunnel ID. Save it for the config file.

## 3. Configuration File (config.yml)

**Option A: Auto-generate config (Recommended)**
```powershell
.\generate-tunnel-config.ps1 -TunnelName "credit-inventory" -ApiDomain "api.yourdomain.com" -AppDomain "app.yourdomain.com"
```

**Option B: Manual creation**

Create the file: `C:\Users\<YourUsername>\.cloudflared\config.yml`

```yaml
tunnel: <YOUR-TUNNEL-ID>
credentials-file: C:\Users\<YourUsername>\.cloudflared\<YOUR-TUNNEL-ID>.json

ingress:
  # Backend API routes (must come before catch-all)
  - hostname: api.yourdomain.com
    service: http://localhost:8000
  
  # Frontend routes
  - hostname: app.yourdomain.com
    service: http://localhost:5173
  
  # Catch-all: 404 for unmatched requests
  - service: http_status:404
```

**Alternative: Using Single Domain with Path Routing**

If you only have one domain and want to use paths:

```yaml
tunnel: <YOUR-TUNNEL-ID>
credentials-file: C:\Users\<YourUsername>\.cloudflared\<YOUR-TUNNEL-ID>.json

ingress:
  # Backend API - all /api requests
  - path: /api/*
    service: http://localhost:8000
  
  # Backend static files
  - path: /qr_codes/*
    service: http://localhost:8000
  - path: /uploads/*
    service: http://localhost:8000
  
  # Frontend - everything else
  - service: http://localhost:5173
```

**To find your tunnel ID:**
```powershell
cloudflared.exe tunnel list
```

## 4. Route DNS in Cloudflare Dashboard

1. Go to Cloudflare Dashboard → Your Domain → DNS
2. Add DNS records (Type: CNAME):
   - Name: `api` → Content: `<YOUR-TUNNEL-ID>.cfargotunnel.com`
   - Name: `app` → Content: `<YOUR-TUNNEL-ID>.cfargotunnel.com`
   - Or use wildcard: `*` → `<YOUR-TUNNEL-ID>.cfargotunnel.com`
3. Proxy status: Proxied (orange cloud)

## 5. Run Commands

### Terminal 1: Start Backend
```powershell
cd "C:\Cursor IDE\CREDIT-INVENTORY-DASHBOARD-NEW\backend"

# For tunnel: bind to localhost only (more secure)
uvicorn app.main:app --host 127.0.0.1 --port 8000

# OR use your existing script (modify run_dev.py to use 127.0.0.1)
python run_dev.py
```

### Terminal 2: Start Frontend
```powershell
cd "C:\Cursor IDE\CREDIT-INVENTORY-DASHBOARD-NEW\frontend2"

# For tunnel: Vite should bind to localhost
npm run dev -- --host 127.0.0.1 --port 5173

# OR modify vite.config.js to always use localhost in tunnel mode
```

### Terminal 3: Start Cloudflare Tunnel
```powershell
# Start tunnel (runs as long as this terminal is open)
cloudflared.exe tunnel run credit-inventory

# OR specify config explicitly
cloudflared.exe tunnel --config "C:\Users\$env:USERNAME\.cloudflared\config.yml" run
```

## 6. Windows Firewall Considerations

Cloudflare Tunnel makes **outbound** connections, so:

✅ **No inbound firewall rules needed** - tunnel connects out to Cloudflare

⚠️ **Ensure services listen on localhost:**
- Backend: `--host 127.0.0.1` (not `0.0.0.0`)
- Frontend: Vite `--host 127.0.0.1`

**If you must allow inbound (not recommended for tunnel):**
```powershell
# Only needed if binding to 0.0.0.0 (not recommended)
New-NetFirewallRule -DisplayName "FastAPI Backend" -Direction Inbound -LocalPort 8000 -Protocol TCP -Action Allow
New-NetFirewallRule -DisplayName "Vite Frontend" -Direction Inbound -LocalPort 5173 -Protocol TCP -Action Allow
```

## 7. Stop Everything and Revert to Dev Mode

### Stop Tunnel
```powershell
# In the tunnel terminal: Ctrl+C

# Or find and kill the process
Get-Process cloudflared | Stop-Process
```

### Stop Services
```powershell
# In backend terminal: Ctrl+C
# In frontend terminal: Ctrl+C
```

### Revert Backend (if you changed host)
```powershell
# Original dev mode (binds to local IP for LAN access)
cd "C:\Cursor IDE\CREDIT-INVENTORY-DASHBOARD-NEW\backend"
python run_dev.py
```

### Revert Frontend
```powershell
# Original dev mode
cd "C:\Cursor IDE\CREDIT-INVENTORY-DASHBOARD-NEW\frontend2"
npm run dev
```

## 8. Production-Aware Considerations

### Backend Configuration
- ✅ Update CORS in `backend/app/main.py` to allow your tunnel domains:
  ```python
  allow_origins=[
      "https://app.yourdomain.com",
      "https://api.yourdomain.com",
      # Remove "*" in production
  ]
  ```

### Frontend API Configuration
- Update frontend API base URL using environment variable:
  - Create `frontend2/.env.tunnel` with: `VITE_API_URL=https://api.yourdomain.com`
  - Or set in shell: `$env:VITE_API_URL="https://api.yourdomain.com"`
  - The frontend already reads from `import.meta.env.VITE_API_URL` (see `frontend2/src/api/axios.js`)

### Environment Variables
- Copy `frontend2/.env.tunnel.example` to `frontend2/.env.tunnel` and configure
- Keep sensitive data in `.env` (never commit)
- Load tunnel env: `Get-Content frontend2\.env.tunnel | ForEach-Object { if ($_ -match '^([^#][^=]+)=(.*)$') { [Environment]::SetEnvironmentVariable($matches[1], $matches[2], 'Process') } }`

### Security
- ✅ Tunnel is encrypted end-to-end
- ✅ No public ports exposed
- ⚠️ Update CORS origins (remove `"*"`)
- ⚠️ Add authentication if not already present
- ⚠️ Use HTTPS only (Cloudflare provides this)

### Monitoring
```powershell
# View tunnel logs
cloudflared.exe tunnel info credit-inventory

# List all tunnels
cloudflared.exe tunnel list

# Delete tunnel (if needed)
cloudflared.exe tunnel delete credit-inventory
```

## Quick Reference

**Start All Services:**
```powershell
# Terminal 1
cd backend; uvicorn app.main:app --host 127.0.0.1 --port 8000

# Terminal 2  
cd frontend2; npm run dev -- --host 127.0.0.1 --port 5173

# Terminal 3
cloudflared.exe tunnel run credit-inventory
```

**Stop All:**
- `Ctrl+C` in each terminal

**Test:**
- Frontend: `https://app.yourdomain.com`
- Backend: `https://api.yourdomain.com` or `https://api.yourdomain.com/`

