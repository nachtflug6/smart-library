FROM mcr.microsoft.com/devcontainers/python:3.11

# System packages needed for PDF tooling and Node.js
USER root
RUN apt-get update && apt-get install -y --no-install-recommends \
    poppler-utils \
    ghostscript \
    default-jre \
    sqlite3 \
    libglib2.0-0 \
    libgl1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js and npm
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace

# Install Python dependencies (cached) - as root for better compatibility
COPY requirements.txt /workspace/
RUN pip install -r /workspace/requirements.txt

# Install UI dependencies upfront - as root
COPY ui/package.json ui/package-lock.json* /workspace/ui/
RUN cd /workspace/ui && npm install

# Fix workspace ownership for vscode user
RUN chown -R vscode:vscode /workspace

# Use vscode user for development
USER vscode

# # Copy the entire project
# COPY . /workspace/
# RUN pip install --user -e /workspace/

CMD ["sleep", "infinity"]