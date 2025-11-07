FROM python:3.11-slim

# System packages needed for PDF + table extraction
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    poppler-utils \
    ghostscript \
    default-jre \
    libglib2.0-0 \
    libgl1 \
    && rm -rf /var/lib/apt/lists/*

# Work inside /app
WORKDIR /app

# Install Python dependencies first (better caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy everything else
COPY . .

# No forcing the smartlib CLI – you drop into a shell
ENTRYPOINT ["bash"]
