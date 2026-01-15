.PHONY: dev api ui init help check

help:
	@echo "Smart Library Development Commands"
	@echo "==================================="
	@echo "make init       - Initialize database (run once on first setup)"
	@echo "make check      - Verify all dependencies and setup"
	@echo "make dev        - Start both API and UI servers"
	@echo "make api        - Start API server only (port 8000)"
	@echo "make ui         - Start UI server only (port 5173)"
	@echo ""

init:
	@echo "Initializing Smart Library..."
	@echo "1. Initializing database schema..."
	smartlib init
	@echo "✓ Database initialized"
	@echo ""
	@echo "Next steps:"
	@echo "- Make sure docker-compose services are running (grobid, ollama)"
	@echo "- Run 'make check' to verify everything"
	@echo "- Run 'make dev' to start development servers"

check:
	@echo "Checking Smart Library setup..."
	@echo ""
	@echo "✓ Python dependencies:"
	@python -c "import fastapi, uvicorn, pydantic; print('  FastAPI, uvicorn, pydantic installed')"
	@echo ""
	@echo "✓ Node.js dependencies:"
	@test -d ui/node_modules && echo "  npm dependencies installed" || echo "  ⚠ npm dependencies not installed - run 'cd ui && npm install'"
	@echo ""
	@echo "✓ Database:"
	@test -f data_dev/db/smart_library.db && echo "  Database exists" || echo "  ⚠ Database not initialized - run 'make init'"
	@echo ""
	@echo "✓ External Services (docker-compose):"
	@echo "  Check: grobid (port 8070), ollama (port 11434)"
	@echo "  Run: docker-compose up -d"
	@echo ""
	@echo "All checks complete!"

dev: api ui
	@echo ""
	@echo "================================================"
	@echo "Smart Library is running!"
	@echo "================================================"
	@echo "UI:  http://localhost:5173"
	@echo "API: http://localhost:8000"
	@echo "API Docs: http://localhost:8000/docs"
	@echo "================================================"

api:
	@echo "Starting API on port 8000..."
	@echo "Press Ctrl+C to stop"
	python -m uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload

ui:
	@echo "Starting UI on port 5173..."
	@echo "Press Ctrl+C to stop"
	cd ui && npm run dev
