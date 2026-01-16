#!/bin/bash
# Start script for smart-library development environment

set -e

echo "Starting smart-library stack..."

# Initialize database if needed
echo "Initializing database..."
python -m smart_library.cli.initialize init || true

# Install the package in development mode
echo "Installing package..."
pip install -e . -q

# Start the API server
echo "Starting API server on port 8000..."
python -m uvicorn api.main:app --host 0.0.0.0 --port 8000 &
API_PID=$!

# Start the UI development server
echo "Starting UI server on port 5173..."
cd /workspace/ui
npm install -q
npm run dev -- --host &
UI_PID=$!

echo ""
echo "✓ smart-library stack started!"
echo ""
echo "Access the application at:"
echo "  - UI: http://localhost:5173"
echo "  - API: http://localhost:8000/docs"
echo ""

# Keep the container running
wait $API_PID $UI_PID
