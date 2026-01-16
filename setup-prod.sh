#!/bin/bash
set -e

# Smart Library Production Setup Script
# Minimal setup for colleagues to get running

echo ""
echo "================================================"
echo "Smart Library - Production Setup"
echo "================================================"
echo ""

# Check Docker installation
echo "✓ Checking Docker installation..."
if ! command -v docker &> /dev/null; then
    echo "✗ Docker not found. Please install Docker Desktop:"
    echo "  https://www.docker.com/products/docker-desktop"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "✗ Docker Compose not found. Please update Docker Desktop."
    exit 1
fi

echo "  Docker: $(docker --version)"
echo "  Docker Compose: $(docker-compose --version)"
echo ""

# Check Docker daemon
echo "✓ Checking Docker daemon..."
if ! docker ps &> /dev/null; then
    echo "✗ Docker daemon not running. Start Docker Desktop and try again."
    exit 1
fi
echo "  Docker daemon is running"
echo ""

# Copy environment file if not exists
echo "✓ Setting up configuration..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "  Created .env (you can customize if needed)"
else
    echo "  Using existing .env"
fi
echo ""

# Start services
echo "✓ Building Docker images (first time only)..."
echo "  - API (FastAPI)"
echo "  - UI (React)"
echo ""

docker-compose -f docker-compose.prod.yml build --no-cache
if [ $? -ne 0 ]; then
    echo "✗ Failed to build Docker images"
    exit 1
fi

echo "  Images built successfully"
echo ""

echo "✓ Starting services (this may take 5-10 minutes on first run)..."
echo "  - Grobid (PDF extraction)"
echo "  - Ollama (embeddings & LLM)"
echo "  - API (FastAPI)"
echo "  - UI (React)"
echo ""

docker-compose -f docker-compose.prod.yml up -d

# Wait for services
echo "✓ Waiting for services to be healthy..."
max_attempts=60
attempt=0

while [ $attempt -lt $max_attempts ]; do
    if docker exec smartlib_api curl -s http://localhost:8000/docs > /dev/null 2>&1; then
        echo "  API is ready"
        break
    fi
    attempt=$((attempt + 1))
    if [ $((attempt % 10)) -eq 0 ]; then
        echo "  Waiting... ($attempt seconds)"
    fi
    sleep 1
done

echo ""

# Initialize database
echo "✓ Database initialization (one-time)..."
echo "  This is typically handled automatically by the API service on startup."
echo ""

# Success message
echo "================================================"
echo "✓ Setup Complete!"
echo "================================================"
echo ""
echo "Smart Library is now running!"
echo ""
echo "🌐 Web UI:      http://localhost:5173"
echo "📚 API Docs:    http://localhost:8000/docs"
echo "🔧 API:         http://localhost:8000"
echo ""
echo "📖 Next Steps:"
echo "  1. Open http://localhost:5173 in your browser"
echo "  2. Upload a PDF using the 'Upload PDF' button"
echo "  3. Try searching for relevant passages"
echo "  4. Label results to improve ranking"
echo ""
echo "❓ Helpful Commands:"
echo "  View logs:        docker-compose -f docker-compose.prod.yml logs -f"
echo "  Stop services:    docker-compose -f docker-compose.prod.yml down"
echo "  Restart:          docker-compose -f docker-compose.prod.yml restart"
echo ""
echo "📚 Documentation:  See PRODUCTION.md for detailed troubleshooting"
echo ""
