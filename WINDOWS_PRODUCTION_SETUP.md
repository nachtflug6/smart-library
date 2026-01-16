# Windows Production Setup Guide

## Quick Fix Summary

The main issue causing containers to exit immediately on Windows was that `docker-compose.prod.yml` was referencing the wrong Dockerfile for the API service. It was pointing to `.devcontainer/Dockerfile` (a development container) instead of `Dockerfile.api` (the production container).

## Changes Made

### 1. Fixed docker-compose.prod.yml
- **Before**: `dockerfile: .devcontainer/Dockerfile`
- **After**: `dockerfile: Dockerfile.api`
- This ensures the production API container uses the correct optimized image

### 2. Updated Setup Scripts
- **setup-prod.bat**: Now uses `docker-compose.prod.yml` explicitly
- **setup-prod.py**: Updated to use production compose file
- **setup-prod.sh**: Fixed for consistency across platforms

### 3. Added Windows Troubleshooting
- Added Windows-specific debugging section to PRODUCTION.md
- Includes WSL2 setup recommendations
- Port conflict detection help

## How to Run on Windows

### Option 1: Using Python Script (Recommended)
```bash
python setup-prod.py
```
This handles everything automatically:
- Checks Docker installation
- Starts all services
- Waits for services to be healthy
- Shows success message with URLs

### Option 2: Using Batch Script
```bash
setup-prod.bat
```
Similar to Python version but batch-specific

### Option 3: Manual Setup
```bash
# Start services
docker-compose -f docker-compose.prod.yml up -d

# Monitor startup
docker-compose -f docker-compose.prod.yml logs -f

# Once services are healthy, access:
# UI: http://localhost:5173
# API: http://localhost:8000/docs
```

## Verify It's Working

```bash
# Check if all containers are running
docker-compose -f docker-compose.prod.yml ps

# If any container isn't "Up", check logs
docker-compose -f docker-compose.prod.yml logs smartlib_api
docker-compose -f docker-compose.prod.yml logs grobid
docker-compose -f docker-compose.prod.yml logs ollama
docker-compose -f docker-compose.prod.yml logs smartlib_ui
```

## Windows Prerequisites

1. **Docker Desktop** (with WSL2 backend)
   - Download: https://www.docker.com/products/docker-desktop
   - Install WSL2: https://docs.microsoft.com/windows/wsl/install

2. **Sufficient Resources**
   - RAM: 8GB minimum (for Ollama embeddings)
   - Disk: 20GB+ free space (for models and data)
   - CPU: 4+ cores

3. **Administrator Privilege**
   - Run Command Prompt/PowerShell as Administrator

## Troubleshooting

### Container Exits Immediately
```bash
# Check the actual error
docker-compose -f docker-compose.prod.yml logs smartlib_api

# Common issues:
# 1. Port already in use - check with: netstat -ano | findstr :8000
# 2. Insufficient memory - allocate 8GB+ in Docker Desktop settings
# 3. WSL2 backend not enabled - check Docker Desktop settings
```

### Slow Service Startup
Ollama downloads embeddings on first run (~1-2GB, may take 2-3 minutes):
```bash
# Monitor progress
docker-compose -f docker-compose.prod.yml logs -f ollama
```

### Port Conflicts
If ports are already in use, either:
- Stop the conflicting services
- Or modify port mappings in `docker-compose.prod.yml`

```bash
# Check which ports are in use
netstat -ano | findstr :8000   # API
netstat -ano | findstr :5173   # UI
netstat -ano | findstr :8070   # Grobid
netstat -ano | findstr :11434  # Ollama
```

## Access URLs

Once running:
- **UI**: http://localhost:5173
- **API Docs**: http://localhost:8000/docs
- **API**: http://localhost:8000

## Stop Services

```bash
# Stop all containers
docker-compose -f docker-compose.prod.yml down

# Stop and remove all data (fresh restart)
docker-compose -f docker-compose.prod.yml down -v
```

## Next Steps

1. Open http://localhost:5173 in your browser
2. Upload a PDF using the "Upload PDF" button
3. Try semantic search functionality
4. Label results to improve ranking

For detailed troubleshooting, see [PRODUCTION.md](PRODUCTION.md).
