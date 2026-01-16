#!/usr/bin/env python3
"""
Smart Library Production Setup Script (Cross-Platform)
Works on Windows, macOS, and Linux without modification
"""

import os
import sys
import subprocess
import time
import shutil
from pathlib import Path

# Colors for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'
    BOLD = '\033[1m'

    @staticmethod
    def disable_on_windows():
        """Disable colors on Windows if not using modern terminal"""
        if sys.platform == 'win32' and not os.environ.get('TERM'):
            Colors.GREEN = Colors.RED = Colors.YELLOW = Colors.BLUE = Colors.BOLD = Colors.END = ''

Colors.disable_on_windows()

def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'=' * 50}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'=' * 50}{Colors.END}\n")

def print_ok(text):
    print(f"{Colors.GREEN}✓{Colors.END} {text}")

def print_error(text):
    print(f"{Colors.RED}✗{Colors.END} {text}")
    sys.exit(1)

def print_info(text):
    print(f"{Colors.BLUE}→{Colors.END} {text}")

def check_docker():
    """Check if Docker is installed and running"""
    print_info("Checking Docker installation...")
    
    try:
        result = subprocess.run(['docker', '--version'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            version = result.stdout.strip()
            print_ok(f"Docker found: {version}")
        else:
            raise RuntimeError("Docker check failed")
    except (FileNotFoundError, subprocess.TimeoutExpired):
        install_url = "https://www.docker.com/products/docker-desktop"
        print_error(f"Docker not found. Install from: {install_url}")
    
    try:
        subprocess.run(['docker', 'ps'], 
                      capture_output=True, text=True, timeout=5)
        print_ok("Docker daemon is running")
    except subprocess.TimeoutExpired:
        print_error("Docker daemon is not responding. Start Docker and try again.")
    except Exception:
        print_error("Docker daemon is not running. Start Docker and try again.")

def setup_env():
    """Copy .env.example to .env if needed"""
    print_info("Setting up configuration...")
    
    env_file = Path('.env')
    env_example = Path('.env.example')
    
    if not env_file.exists():
        if env_example.exists():
            shutil.copy(env_example, env_file)
            print_ok("Created .env file from .env.example")
        else:
            print_error(".env.example not found")
    else:
        print_ok("Using existing .env file")

def run_docker_compose():
    """Start Docker Compose services"""
    print_info("Starting services (this may take 5-10 minutes on first run)...")
    print_info("  - Grobid (PDF extraction)")
    print_info("  - Ollama (embeddings)")
    print_info("  - API (FastAPI)")
    print_info("  - UI (React)")
    
    try:
        result = subprocess.run(['docker', 'compose', 'up', '-d'],
                              capture_output=True, text=True, timeout=60)
        if result.returncode != 0:
            print_error(f"Failed to start services: {result.stderr}")
        print_ok("Services started")
    except Exception as e:
        print_error(f"Error starting services: {e}")

def wait_for_services():
    """Wait for API to be healthy"""
    print_info("Waiting for services to be healthy...")
    
    max_attempts = 60
    attempt = 0
    
    while attempt < max_attempts:
        try:
            result = subprocess.run(
                ['docker', 'exec', 'smartlib_dev', 'curl', '-f', 
                 'http://localhost:8000/docs'],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                print_ok("API is ready")
                return True
        except:
            pass
        
        attempt += 1
        if attempt % 10 == 0:
            print_info(f"  Waiting... ({attempt} seconds)")
        time.sleep(1)
    
    print_error("Services took too long to start. Check: docker compose logs -f")

def init_database():
    """Initialize the database"""
    print_info("Initializing database (one-time)...")
    
    try:
        result = subprocess.run(['docker', 'exec', 'smartlib_dev', 'make', 'init'],
                              capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print_ok("Database initialized")
        else:
            print_error(f"Database initialization failed: {result.stderr}")
    except Exception as e:
        print_error(f"Error initializing database: {e}")

def verify_setup():
    """Run setup verification"""
    print_info("Verifying setup...")
    
    try:
        result = subprocess.run(['docker', 'exec', 'smartlib_dev', 'make', 'check'],
                              capture_output=True, text=True, timeout=30)
        print(result.stdout)
        if result.returncode != 0:
            print_error("Setup verification failed")
    except Exception as e:
        print_error(f"Error verifying setup: {e}")

def show_success_message():
    """Display success message with next steps"""
    print_header("✓ Setup Complete!")
    
    print(f"{Colors.BOLD}Smart Library is now running!{Colors.END}\n")
    
    print(f"{Colors.BOLD}🌐 Web UI:{Colors.END}      http://localhost:5173")
    print(f"{Colors.BOLD}📚 API Docs:{Colors.END}    http://localhost:8000/docs")
    print(f"{Colors.BOLD}🔧 API:{Colors.END}         http://localhost:8000\n")
    
    print(f"{Colors.BOLD}📖 Next Steps:{Colors.END}")
    print("  1. Open http://localhost:5173 in your browser")
    print("  2. Upload a PDF using the 'Upload PDF' button")
    print("  3. Try searching for relevant passages")
    print("  4. Label results to improve ranking\n")
    
    print(f"{Colors.BOLD}❓ Helpful Commands:{Colors.END}")
    print("  View logs:        docker compose logs -f")
    print("  Stop services:    docker compose down")
    print("  Restart:          docker compose restart")
    print("  Reset database:   docker exec smartlib_dev rm -f data_dev/db/smart_library.db && docker exec smartlib_dev make init\n")
    
    print(f"{Colors.BOLD}📚 Documentation:{Colors.END} See PRODUCTION.md for detailed troubleshooting\n")

def main():
    """Main setup flow"""
    print_header("Smart Library - Production Setup")
    
    try:
        check_docker()
        setup_env()
        run_docker_compose()
        wait_for_services()
        init_database()
        verify_setup()
        show_success_message()
        print(f"{Colors.GREEN}✓ All done!{Colors.END}\n")
        return 0
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Setup cancelled by user{Colors.END}\n")
        return 1
    except SystemExit as e:
        return e.code if isinstance(e.code, int) else 1

if __name__ == '__main__':
    sys.exit(main())
