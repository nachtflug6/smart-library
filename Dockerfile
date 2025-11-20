FROM mcr.microsoft.com/devcontainers/python:3.11

# System packages needed for PDF tooling
USER root
RUN apt-get update && apt-get install -y --no-install-recommends \
    poppler-utils \
    ghostscript \
    default-jre \
    sqlite3 \
    libglib2.0-0 \
    libgl1 \
    && rm -rf /var/lib/apt/lists/*

# Use vscode user after system install
USER vscode

WORKDIR /workspaces/smart-library
