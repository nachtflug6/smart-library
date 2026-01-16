@echo off
REM Smart Library Production Setup Script for Windows
REM Run as Administrator recommended

setlocal enabledelayedexpansion

echo.
echo ================================================
echo Smart Library - Production Setup (Windows)
echo ================================================
echo.

REM Check Docker installation
echo Checking Docker installation...
docker --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker not found. Please install Docker Desktop for Windows:
    echo https://www.docker.com/products/docker-desktop
    echo.
    echo Important: During installation, enable "WSL 2" backend (Windows Subsystem for Linux 2)
    pause
    exit /b 1
)

echo [OK] Docker is installed
docker --version
echo.

REM Check Docker daemon
echo Checking Docker daemon...
docker ps >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker daemon is not running. Start Docker Desktop and try again.
    pause
    exit /b 1
)
echo [OK] Docker daemon is running
echo.

REM Copy environment file if not exists
echo Setting up configuration...
if not exist .env (
    copy .env.example .env
    echo [OK] Created .env file
) else (
    echo [OK] Using existing .env file
)
echo.

REM Start services
echo Starting services (this may take 5-10 minutes on first run)...
echo   - Grobid (PDF extraction)
echo   - Ollama (embeddings ^& LLM)
echo   - API (FastAPI)
echo   - UI (React)
echo.

docker compose up -d
if errorlevel 1 (
    echo [ERROR] Failed to start services
    pause
    exit /b 1
)

REM Wait for services
echo.
echo Waiting for services to be healthy...
set "max_attempts=60"
set "attempt=0"

:wait_loop
if !attempt! geq !max_attempts! (
    echo [TIMEOUT] Services took too long to start
    echo Check logs: docker compose logs -f
    pause
    exit /b 1
)

docker exec smartlib_dev curl -s http://localhost:8000/docs >nul 2>&1
if errorlevel 0 (
    echo [OK] API is ready
    goto health_ok
)

set /a attempt=!attempt!+1
if %attempt% == 10 (echo   Waiting... ^(!attempt! seconds^))
if %attempt% == 20 (echo   Waiting... ^(!attempt! seconds^))
if %attempt% == 30 (echo   Waiting... ^(!attempt! seconds^))
if %attempt% == 40 (echo   Waiting... ^(!attempt! seconds^))
if %attempt% == 50 (echo   Waiting... ^(!attempt! seconds^))

timeout /t 1 /nobreak >nul 2>&1
goto wait_loop

:health_ok
echo.

REM Initialize database
echo Initializing database (one-time)...
docker exec smartlib_dev make init
if errorlevel 1 (
    echo [ERROR] Database initialization failed
    pause
    exit /b 1
)
echo [OK] Database initialized
echo.

REM Health check
echo Verifying setup...
docker exec smartlib_dev make check
echo.

REM Success message
echo ================================================
echo [SUCCESS] Setup Complete!
echo ================================================
echo.
echo Smart Library is now running!
echo.
echo Web UI:      http://localhost:5173
echo API Docs:    http://localhost:8000/docs
echo API:         http://localhost:8000
echo.
echo Next Steps:
echo   1. Open http://localhost:5173 in your browser
echo   2. Upload a PDF using the 'Upload PDF' button
echo   3. Try searching for relevant passages
echo   4. Label results to improve ranking
echo.
echo Helpful Commands:
echo   View logs:        docker compose logs -f
echo   Stop services:    docker compose down
echo   Restart:          docker compose restart
echo   Reset database:   docker exec smartlib_dev rm -f data_dev/db/smart_library.db ^&^& docker exec smartlib_dev make init
echo.
echo Documentation: See PRODUCTION.md for detailed troubleshooting
echo.
pause
