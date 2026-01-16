# Smart Library - Quick Start Guide

**For colleagues: Get up and running in 5 minutes!**

## Prerequisites

- Docker Desktop (with Docker Compose)
- ~20GB free disk space
- 8GB+ RAM

## 1️⃣ Clone & Setup

```bash
git clone <repo-url> smart-library
cd smart-library

# Run automated setup (handles everything)
./setup-prod.sh

# ⏱️ This takes 5-10 minutes (downloading models, first time only)
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

### "Connection refused" when starting

**Wait a bit!** On first run, Ollama downloads ~2GB of models. Monitor progress:

```bash
docker-compose logs -f ollama
# When you see "Listening on 127.0.0.1:11434", it's ready
```

### API/UI not accessible

```bash
# Check if containers are running
docker-compose ps

# Restart everything
docker-compose down
docker-compose up -d
```

### Out of disk space

Ollama models take ~3-4GB. Free up space and:

```bash
docker-compose restart ollama
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
