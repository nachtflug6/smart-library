# Smart Library - Quick Start Guide

**For colleagues: Get up and running in 5 minutes!**

## Prerequisites

- Docker Desktop (with Docker Compose)
  - **Windows**: [Docker Desktop for Windows](https://www.docker.com/products/docker-desktop) (requires WSL 2)
  - **macOS**: [Docker Desktop for Mac](https://www.docker.com/products/docker-desktop)
  - **Linux**: [Docker Engine](https://docs.docker.com/engine/install/)
- ~20GB free disk space
- 8GB+ RAM

## 1️⃣ Clone & Setup

```bash
git clone <repo-url> smart-library
cd smart-library
```

### Windows Users

```batch
REM Run setup batch file (works in Command Prompt or PowerShell)
setup-prod.bat
```

Or use Python (works everywhere):
```bash
python setup-prod.py
```

### macOS & Linux Users

```bash
# Run automated setup (handles everything)
./setup-prod.sh

# Or use Python version (also works)
python3 setup-prod.py
```

### All Platforms (Python Alternative)

```bash
# This works on Windows, Mac, and Linux
python setup-prod.py
```

⏱️ **First run takes 10-15 minutes** (building images and downloading models one time only)

## Manual Setup (Alternative)

If you prefer to run commands manually instead of using the setup scripts:

```powershell
# Windows PowerShell
cd your-workspace
git pull
docker compose -f docker-compose.prod.yml build --no-cache
docker compose -f docker-compose.prod.yml up -d
```

```bash
# macOS / Linux
cd your-workspace
git pull
docker-compose -f docker-compose.prod.yml build --no-cache
docker-compose -f docker-compose.prod.yml up -d
```

## 2️⃣ Access the Application

Once setup completes:

```
🌐 Open in browser: http://localhost:5173
```

## 3️⃣ Try It Out

1. **Upload a PDF**
   - Click "Upload PDF" (top-right button)
   - Select any PDF file
   - Wait for processing (~10-30 seconds)

2. **Search**
   - Type a query in the search bar: `machine learning models`
   - Results show relevant text chunks with page numbers
   - Scores indicate relevance (color-coded)

3. **View PDF**
   - Click "View PDF" on any result
   - See the source page with highlights

4. **Improve Results**
   - Click 👍 (thumbs up) for relevant results
   - Click 👎 (thumbs down) for irrelevant
   - Click "Rerank with Feedback" to refine results

## 📚 Key URLs

| Service | URL | Purpose |
|---------|-----|---------|
| **Web UI** | http://localhost:5173 | Upload & search documents |
| **API Docs** | http://localhost:8000/docs | Interactive API reference |
| **API** | http://localhost:8000 | REST endpoints |

## ⚙️ Managing Services

```bash
# View what's running
docker ps

# View logs (helpful for troubleshooting)
docker-compose logs -f

# Stop everything
docker-compose down

# Restart all services
docker-compose restart

# Reset database (remove all documents)
docker exec smartlib_dev rm -f data_dev/db/smart_library.db && \
docker exec smartlib_dev make init
```

## 🆘 Troubleshooting

### Platform-Specific Issues

#### Windows

**Problem: Setup script won't run**
- Use `setup-prod.bat` instead of `setup-prod.sh`
- Or use Python: `python setup-prod.py`
- Make sure Docker Desktop is running with WSL 2 backend

**Problem: Path errors or file not found**
- File paths on Windows use backslashes - Docker handles this automatically
- If you get path errors, try using Python setup: `python setup-prod.py`

**Problem: WSL 2 not enabled**
- Open PowerShell as Administrator and run:
```powershell
wsl --install
wsl --set-default-version 2
```
- Restart your computer and Docker

#### macOS

**Problem: "docker not found" in Terminal**
- Make sure Docker Desktop is running (check the menu bar)
- Try: `docker ps` to verify it's working

**Problem: Out of memory**
- Go to Docker Desktop → Settings → Resources
- Increase "Memory" (recommend 8GB+)
- Restart Docker

#### Linux

**Problem: Permission denied (cannot run Docker)**
```bash
# Add your user to docker group
sudo usermod -aG docker $USER
# Log out and log back in, or run:
newgrp docker
```

**Problem: "docker compose" command not found**
- Install Docker Compose: `sudo apt install docker-compose`
- Or use `docker-compose` (with hyphen)

### General Issues

**"Connection refused" when starting**

Wait a bit! On first run, Ollama downloads ~2GB of models. Monitor progress:

```bash
docker compose logs -f ollama
# When you see "Listening on", it's ready
```

**API/UI not accessible**

```bash
# Check if containers are running
docker compose ps

# Restart everything
docker compose down
docker compose up -d
```

**Out of disk space**

Ollama models take ~3-4GB. Free up space and:

```bash
docker compose restart ollama
```

### GPU support

If you have an NVIDIA GPU and want to use it:

1. Install NVIDIA Container Toolkit: https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html

2. Uncomment GPU sections in `docker-compose.yml`:

```yaml
# runtime: nvidia
# deploy:
#   resources:
#     reservations:
#       devices:
#         - capabilities: [gpu]
```

3. Restart: `docker-compose restart`

## 📖 Full Documentation

For detailed setup, architecture, and troubleshooting:
- See **PRODUCTION.md** for comprehensive guide

## 🎯 What's Included

✅ **PDF Processing** - Automatic text extraction and structuring  
✅ **Semantic Search** - Find relevant passages, not just keywords  
✅ **Vector Database** - Fast similarity search  
✅ **Web UI** - Upload, search, and browse results  
✅ **REST API** - Integrate into your workflows  
✅ **CLI Tools** - Command-line interface  
✅ **Feedback Loop** - Label results to improve ranking  

## 💡 Tips

- **Batch uploads**: Upload multiple PDFs, they'll be processed automatically
- **Search operators**: Plain text queries work best (e.g., "climate change impacts")
- **Page references**: Results include exact page numbers for verification
- **Reranking**: After labeling a few results, rerank to improve accuracy

## ❓ Questions?

1. Check logs: `docker-compose logs -f`
2. Read PRODUCTION.md for detailed troubleshooting
3. Check API docs: http://localhost:8000/docs
4. Browse examples in `notebooks/`

---

**Happy searching! 🔍**
