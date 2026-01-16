# Docker Compose Troubleshooting for Windows

## Issue: API Container Unhealthy

If you see `✘ Container smartlib_api Error dependency api failed to start`, follow these steps:

### Root Causes and Solutions

#### 1. **Database Initialization Timeout**
The API needs time to create and initialize the database on first startup.

**Solution:**
- The health check start_period has been increased to 60 seconds
- The API performs database initialization asynchronously during startup
- Initial startup takes longer (~30-60 seconds)

#### 2. **Path Issues on Windows**
Docker volumes may have path issues on Windows with WSL2.

**Solution:**
```powershell
# Use absolute paths in docker-compose
# Ensure data directories exist before running:
mkdir -p ./data_dev/db
mkdir -p ./db
```

#### 3. **Ollama Model Not Ready**
The embedding model may not be downloaded yet when API tries to use it.

**Solution:**
- Wait for ollama container to be fully healthy (ollama list should work)
- The start_period: 300s for ollama ensures the model is downloaded
- Verify: `docker logs ollama` should show the model is pulled

### Debugging Steps

1. **Check API logs:**
```powershell
docker logs smartlib_api
```
Look for any errors during database initialization.

2. **Check Ollama logs:**
```powershell
docker logs ollama
```
Verify that nomic-embed-text model was pulled successfully.

3. **Check Grobid logs:**
```powershell
docker logs grobid
```
Should show it's ready on port 8070.

4. **Manually test API health:**
```powershell
# After services stabilize
curl http://localhost:8000/docs
curl http://localhost:8000/health
```

### If Issues Persist

1. **Clean up and rebuild:**
```powershell
docker-compose -f docker-compose.prod.yml down
docker volume prune
docker image prune
docker-compose -f docker-compose.prod.yml up --build
```

2. **Check Windows Disk Space:**
Ensure you have at least 5GB free disk space for:
- Ollama model (~3-4GB)
- Grobid image (~2GB)
- Python dependencies (~500MB)

3. **Verify WSL2 Resources:**
If using WSL2, check that it has enough:
- CPU: At least 2 cores assigned
- Memory: At least 4GB available
- Disk: At least 10GB free in WSL

```powershell
# View WSL resource allocation
wsl --list --verbose
```

4. **Check Docker Desktop Settings:**
- Ensure WSL2 backend is enabled
- Give Docker at least 4GB RAM
- Set CPU limit to at least 2 cores
- Ensure "Resource Saver" is disabled during setup

### Final Check

Once all containers show healthy/running:
```powershell
docker ps
```

You should see:
- ✔ Container grobid (Healthy)
- ✔ Container ollama (Healthy)  
- ✔ Container smartlib_api (Healthy)
- ✔ Container smartlib_ui (Running)

Then access the application:
- UI: http://localhost:5173
- API: http://localhost:8000/docs

### Performance Notes

- **First startup:** 2-5 minutes (downloading models)
- **Subsequent startups:** 30-60 seconds (database initialization)
- **Embedding requests:** May be slow on first request while CPU optimizes
