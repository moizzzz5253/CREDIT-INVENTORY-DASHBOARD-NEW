# Cloudflare Tunnel Quick Start

## One-Time Setup

```powershell
# 1. Run setup script
.\setup-cloudflare-tunnel.ps1

# 2. After login and tunnel creation, edit config:
# C:\Users\<YourUsername>\.cloudflared\config.yml
# (See CLOUDFLARE_TUNNEL_SETUP.md for config template)

# 3. Add DNS records in Cloudflare Dashboard
# CNAME: api.yourdomain.com → <tunnel-id>.cfargotunnel.com
# CNAME: app.yourdomain.com → <tunnel-id>.cfargotunnel.com
```

## Start Services

```powershell
# Option 1: Use helper script (opens 3 windows)
.\start-tunnel.ps1

# Option 2: Manual (3 separate terminals)
# Terminal 1:
cd backend
uvicorn app.main:app --host 127.0.0.1 --port 8000

# Terminal 2:
cd frontend2
$env:VITE_API_URL="https://api.yourdomain.com"
npm run dev -- --host 127.0.0.1 --port 5173

# Terminal 3:
cloudflared.exe tunnel run credit-inventory
```

## Stop Services

```powershell
# Option 1: Use helper script
.\stop-tunnel.ps1

# Option 2: Manual
# Close the 3 PowerShell windows
# Or: Ctrl+C in each terminal
```

## Revert to Dev Mode

```powershell
# Just run your normal dev commands:
cd backend
python run_dev.py

cd frontend2
npm run dev
```

## Configuration Notes

- **Frontend API URL**: Set `VITE_API_URL` env var or create `frontend2/.env.tunnel`
- **Backend CORS**: Update `backend/app/main.py` to allow your tunnel domains
- **No Firewall Changes**: Tunnel uses outbound connections only
- **Tunnel Config**: `C:\Users\<YourUsername>\.cloudflared\config.yml`

