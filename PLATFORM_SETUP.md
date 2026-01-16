# Smart Library - Platform Setup Guide

Complete installation instructions for Windows, macOS, and Linux.

## 🪟 Windows Setup

### Prerequisites
- Windows 10 or later (Pro, Enterprise, or Home with WSL 2)
- At least 20GB free disk space
- 8GB+ RAM

### Step 1: Enable WSL 2

WSL 2 (Windows Subsystem for Linux 2) is **required** for Docker Desktop on Windows.

**Option A: Automatic (PowerShell - Admin)**
```powershell
# Run PowerShell as Administrator
wsl --install
wsl --set-default-version 2
# Restart your computer
```

**Option B: Manual Setup**
1. Open "Control Panel" → "Programs" → "Turn Windows features on or off"
2. Check "Windows Subsystem for Linux"
3. Check "Virtual Machine Platform"
4. Click "OK" and restart

### Step 2: Install Docker Desktop

1. Download [Docker Desktop for Windows](https://www.docker.com/products/docker-desktop)
2. Run the installer and follow prompts
3. Choose "WSL 2" backend when prompted (important!)
4. Restart Windows

### Step 3: Verify Installation

Open PowerShell or Command Prompt and run:
```powershell
docker --version
docker ps
```

Both should work without errors.

### Step 4: Clone & Setup

```powershell
# Clone repository
git clone <repo-url> smart-library
cd smart-library

# Run setup (choose one)
setup-prod.bat                    # Windows batch file
# OR
python setup-prod.py              # Python (works everywhere)
```

### Common Windows Issues

**"Docker is not installed"**
- Make sure Docker Desktop is fully started (check system tray)
- Try opening Docker Desktop manually from Start Menu

**"WSL 2 not installed"**
```powershell
# Run PowerShell as Administrator
wsl --install
# Restart computer
```

**"Permission denied" or "Access is denied"**
- Restart Docker Desktop
- Run setup script from Command Prompt or PowerShell as Administrator

**Setup script won't run**
- Try: `python setup-prod.py` instead of `.bat`
- Check that you're in the correct directory

---

## 🍎 macOS Setup

### Prerequisites
- macOS 11 (Big Sur) or later
- Intel or Apple Silicon (M1/M2/M3) Mac
- At least 20GB free disk space
- 8GB+ RAM

### Step 1: Install Docker Desktop

1. Download [Docker Desktop for Mac](https://www.docker.com/products/docker-desktop)
   - **Choose the correct version:**
     - Intel Mac: "Docker.dmg"
     - Apple Silicon (M1/M2/M3): "Docker.dmg" (select "Apple Silicon")

2. Open the DMG file and drag Docker icon to Applications folder
3. Launch Docker from Applications folder
4. Enter your Mac password when prompted (needed for privileged helper)

### Step 2: Verify Installation

Open Terminal and run:
```bash
docker --version
docker ps
```

Both should work without errors.

### Step 3: Clone & Setup

```bash
# Clone repository
git clone <repo-url> smart-library
cd smart-library

# Run setup (choose one)
./setup-prod.sh                   # Bash script
# OR
python3 setup-prod.py             # Python (works everywhere)
```

### Common macOS Issues

**"docker not found" in Terminal**
- Make sure Docker Desktop is running (check menu bar at top)
- Try: `open -a Docker`

**"Cannot connect to Docker daemon"**
- Docker Desktop might not be running
- Check: Applications → Docker.app
- Start Docker and wait 30 seconds for it to initialize

**Out of memory errors**
1. Click Docker icon in menu bar → Preferences
2. Click "Resources"
3. Increase "Memory" to 8GB or more
4. Click "Apply & Restart"

**Permission denied during setup**
```bash
# Grant Docker permission
sudo chmod 666 /var/run/docker.sock
```

---

## 🐧 Linux Setup

### Prerequisites
- Ubuntu 20.04+ or equivalent distribution
- At least 20GB free disk space
- 8GB+ RAM
- sudo access

### Step 1: Install Docker Engine

**Ubuntu/Debian:**
```bash
# Update package manager
sudo apt update
sudo apt install -y apt-transport-https ca-certificates curl software-properties-common

# Add Docker repository
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"

# Install Docker
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Start Docker service
sudo systemctl start docker
sudo systemctl enable docker  # Start on boot
```

**Fedora/RHEL/CentOS:**
```bash
sudo dnf install -y docker
sudo systemctl start docker
sudo systemctl enable docker
```

### Step 2: Configure User Permissions

By default, Docker requires `sudo`. Allow your user to run Docker without sudo:

```bash
# Add user to docker group
sudo usermod -aG docker $USER

# Apply group changes
newgrp docker

# Test without sudo
docker ps
```

### Step 3: Verify Installation

```bash
docker --version
docker ps
docker compose version
```

All should work without errors.

### Step 4: Clone & Setup

```bash
# Clone repository
git clone <repo-url> smart-library
cd smart-library

# Run setup (choose one)
./setup-prod.sh                   # Bash script
# OR
python3 setup-prod.py             # Python (works everywhere)
```

### Common Linux Issues

**"docker: command not found"**
```bash
# Docker might not be in PATH
# Log out and log back in:
logout
# Then log back in and try again
docker ps
```

**"Permission denied" when running docker**
```bash
# Add user to docker group and activate group
sudo usermod -aG docker $USER
newgrp docker
docker ps
```

**"Cannot connect to Docker daemon"**
```bash
# Docker daemon might not be running
sudo systemctl start docker
docker ps
```

**Setup script has permission errors**
```bash
# Make scripts executable
chmod +x setup-prod.sh
./setup-prod.sh
```

---

## 🔧 Universal Commands (All Platforms)

Once setup is complete, these commands work on Windows, macOS, and Linux:

```bash
# View running containers
docker compose ps

# View logs (helpful for troubleshooting)
docker compose logs -f

# View specific service logs
docker compose logs -f ollama
docker compose logs -f grobid

# Stop all services
docker compose down

# Restart all services
docker compose restart

# Restart specific service
docker compose restart ollama

# Reset database
docker exec smartlib_dev rm -f data_dev/db/smart_library.db
docker exec smartlib_dev make init
```

---

## ✅ Verify Everything is Working

After setup, you should see:

```bash
$ docker compose ps
NAME                COMMAND              STATUS              PORTS
grobid              "/docker-entrypoint…" Up (healthy)        0.0.0.0:8070->8070/tcp, 0.0.0.0:8071->8071/tcp
ollama              "/bin/sh -c 'ollama…" Up (healthy)        0.0.0.0:11434->11434/tcp
smartlib_dev        "sleep infinity"     Up (healthy)        0.0.0.0:8000->8000/tcp, 0.0.0.0:5173->5173/tcp
```

Open in browser:
- **UI**: http://localhost:5173
- **API Docs**: http://localhost:8000/docs

---

## 🆘 Still Having Issues?

1. **Check setup logs:**
   ```bash
   docker compose logs -f
   ```

2. **Restart everything:**
   ```bash
   docker compose down
   docker compose up -d
   ```

3. **Check Docker status:**
   - **Windows**: Open Docker Desktop from Start Menu
   - **macOS**: Open Docker from Applications folder
   - **Linux**: `systemctl status docker`

4. **See detailed troubleshooting:** [PRODUCTION.md](PRODUCTION.md)

---

## 📚 Next Steps

1. Open http://localhost:5173 in your browser
2. Upload a PDF file
3. Try semantic search
4. Label results to improve ranking
5. Check API docs: http://localhost:8000/docs

Enjoy! 🚀
