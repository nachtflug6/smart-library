@echo off
REM Windows setup script for smart-library Docker deployment

echo.
echo ==========================================
echo Smart Library - Windows Docker Setup
echo ==========================================
echo.

REM Check if Docker is installed
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Docker is not installed or not in PATH
    echo Please install Docker Desktop from https://www.docker.com/products/docker-desktop
    exit /b 1
)

echo ✓ Docker is installed

REM Check if Docker daemon is running
docker ps >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Docker daemon is not running
    echo Please start Docker Desktop
    exit /b 1
)

echo ✓ Docker daemon is running

REM Create required directories
echo.
echo Creating data directories...
if not exist "data_dev\db" mkdir data_dev\db
if not exist "data_dev\documents\pdf" mkdir data_dev\documents\pdf
if not exist "data_dev\jsonl" mkdir data_dev\jsonl
if not exist "db" mkdir db

echo ✓ Directories created

REM Check disk space
echo.
echo Checking disk space...
for /f "tokens=3" %%A in ('dir ^| find "bytes free"') do set FREE_SPACE=%%A

echo Free disk space: %FREE_SPACE% MB
if %FREE_SPACE% lss 5000 (
    echo WARNING: Less than 5GB free disk space
    echo Download may fail or system may be slow
)

echo.
echo ==========================================
echo Setup Complete!
echo ==========================================
echo.
echo Next steps:
echo 1. Run: docker-compose -f docker-compose.prod.yml up -d
echo 2. Wait for all containers to show healthy (1-5 minutes)
echo 3. Access the UI at: http://localhost:5173
echo 4. View logs: docker logs smartlib_api
echo.
echo For troubleshooting, see: DOCKER_WINDOWS_TROUBLESHOOTING.md
echo.
