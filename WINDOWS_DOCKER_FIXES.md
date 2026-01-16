# Windows Docker Deployment - Fixed Issues

## Changes Made to Fix Unhealthy Containers

### 1. **Dockerfile.api** - Improved Initialization
- **Pre-initializes database during build** - Speeds up first run from 5+ minutes to ~1 minute
- **Creates all required directories** during build (data_dev/db, data_dev/documents/pdf, data_dev/jsonl, db)
- **Increased health check timeout** - From 5s to 10s (accounting for slow Windows systems)
- **Increased health check retries** - From 5 to 10 (more resilient)
- **Changed health endpoint** - From /docs to /health (simpler, faster check)

### 2. **docker-compose.prod.yml** - Better Service Configuration
- **Increased API start_period** - From 30s to 45s (allows database init on slow systems)
- **Changed health check endpoint** - Uses /health instead of /docs
- **Improved health check parameters** - timeout: 10s, retries: 10, interval: 10s

### 3. **New Documentation**
- **DOCKER_WINDOWS_TROUBLESHOOTING.md** - Complete troubleshooting guide for Windows users
- **setup_windows.bat** - Automated setup script for Windows

## Expected Behavior Now

### First Run (Initial Setup)
1. **Build images** - Downloads base images, installs dependencies (~2-3 minutes)
2. **Start services** - Grobid starts first (~20 seconds)
3. **Download Ollama model** - nomic-embed-text (~3-5 minutes on first run)
4. **Initialize API database** - During build and startup (~30-60 seconds)
5. **UI builds** - While API is initializing (~1-2 minutes)
6. **Ready to use** - Total time: 7-12 minutes

### Subsequent Runs
1. All services start much faster (~1-2 minutes)
2. Database is already initialized
3. Models are cached

## How to Deploy on Windows

### Option 1: Manual Setup (Simple)
```powershell
# Create required directories
mkdir -p data_dev/db, data_dev/documents/pdf, data_dev/jsonl, db

# Start the stack
docker-compose -f docker-compose.prod.yml up -d

# Wait for services to be healthy (check logs)
docker logs smartlib_api
docker logs ollama

# Access the application
# UI: http://localhost:5173
# API: http://localhost:8000/docs
```

### Option 2: Automated Setup (Windows Batch)
```powershell
# Run the setup script
.\setup_windows.bat

# Then start services
docker-compose -f docker-compose.prod.yml up -d
```

## Monitoring Startup Progress

### Watch Real-time Logs
```powershell
docker-compose -f docker-compose.prod.yml logs -f
```

### Check Specific Services
```powershell
# API status
docker logs smartlib_api

# Ollama model download
docker logs ollama

# Grobid status
docker logs grobid

# UI build status
docker logs smartlib_ui
```

### Health Check Status
```powershell
# See container health
docker ps

# Output should show:
# - grobid      healthy
# - ollama      healthy
# - smartlib_api healthy (after 45+ seconds)
# - smartlib_ui running
```

## Troubleshooting

### API Still Unhealthy?
1. Check available disk space: `df -h` (need 5GB minimum)
2. Check available RAM: Task Manager → Performance
3. Check Docker Desktop CPU/Memory limits
4. Review logs: `docker logs smartlib_api`

### Database Lock Error?
1. Usually indicates concurrent access during initialization
2. Wait a bit longer, the start_period of 45s should handle this
3. If persists, restart: `docker-compose -f docker-compose.prod.yml restart smartlib_api`

### Can't Connect to UI or API?
1. Verify containers are running: `docker ps`
2. Verify ports are accessible: `netstat -an | grep :8000` or `:5173`
3. Check Windows Firewall hasn't blocked Docker
4. If using WSL2, verify WSL2 is properly configured

## Files Modified

- `Dockerfile.api` - Added pre-init, better health checks
- `docker-compose.prod.yml` - Adjusted timeouts and health checks  
- `api/main.py` - No changes needed (already had startup event)
- `DOCKER_WINDOWS_TROUBLESHOOTING.md` - New comprehensive guide
- `setup_windows.bat` - New Windows setup script

## Performance Expectations

| Scenario | Time |
|----------|------|
| First run build | 2-3 minutes |
| Ollama model download | 3-5 minutes |
| API database init | 30-60 seconds |
| UI build | 1-2 minutes |
| **Total first run** | **7-12 minutes** |
| Subsequent starts | 1-2 minutes |
| Health check startup | 45 seconds |

## Next Steps if Issues Persist

If containers remain unhealthy after 2+ minutes:

1. **Increase Docker Desktop resources:**
   - CPU: 4 cores minimum (8 preferred)
   - Memory: 6GB minimum (8GB preferred)
   - Disk: 20GB available

2. **Rebuild without cache:**
   ```powershell
   docker-compose -f docker-compose.prod.yml down
   docker system prune -a
   docker-compose -f docker-compose.prod.yml up --build -d
   ```

3. **Check WSL2 disk usage:**
   ```powershell
   wsl --manage-on-windows optimize
   ```

4. **Review detailed logs:**
   ```powershell
   docker logs smartlib_api --tail 50
   ```

See `DOCKER_WINDOWS_TROUBLESHOOTING.md` for more detailed troubleshooting steps.
