# Quick Start - Windows Docker

## Prerequisites
- Docker Desktop installed and running
- At least 5GB free disk space
- WSL2 backend enabled in Docker Desktop

## One-Command Startup

```powershell
# Navigate to project directory
cd C:\path\to\smart-library

# Create data directories (one time only)
mkdir data_dev\db, data_dev\documents\pdf, data_dev\jsonl, db

# Start all services
docker-compose -f docker-compose.prod.yml up -d

# Wait 1-5 minutes for services to initialize...

# Check status
docker ps
```

## Access the Application

Once all containers show **healthy/running**:
- **UI**: http://localhost:5173
- **API Docs**: http://localhost:8000/docs

## Monitor Startup

```powershell
# Watch real-time logs
docker-compose -f docker-compose.prod.yml logs -f

# Or check individual services
docker logs smartlib_api
docker logs ollama
docker logs grobid
```

## Stop Services

```powershell
docker-compose -f docker-compose.prod.yml down
```

## Troubleshooting

### API/UI containers unhealthy?
1. Wait another 30 seconds (first run initialization)
2. Check logs: `docker logs smartlib_api`
3. Ensure you have 5GB+ free disk space
4. See `DOCKER_WINDOWS_TROUBLESHOOTING.md` for detailed help

### Port already in use?
```powershell
# If 5173 or 8000 are taken, modify docker-compose.prod.yml:
# Change "8000:8000" to "8001:8000" for example
# Change "5173:5173" to "5174:5173"
```

### Build issues?
```powershell
# Clean and rebuild
docker-compose -f docker-compose.prod.yml down -v
docker system prune -a
docker-compose -f docker-compose.prod.yml up --build -d
```

## Expected Startup Times

- **First run**: 5-12 minutes (downloading models ~3-5 min)
- **Subsequent runs**: 1-2 minutes
- **Database init**: ~30-60 seconds
- **Health checks pass**: After 45 seconds

## Support

For more detailed troubleshooting:
- See `DOCKER_WINDOWS_TROUBLESHOOTING.md`
- See `WINDOWS_DOCKER_FIXES.md` for what was changed
- Check Docker Desktop logs in File → Preferences → Docker Engine
