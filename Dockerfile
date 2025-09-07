# Use Ubuntu 22.04 with Python 3.10 (default)
FROM ubuntu:22.04

# Install Python and system dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-dev \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create symlink for python
RUN ln -s /usr/bin/python3 /usr/bin/python

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install Gunicorn for production
RUN pip install gunicorn

# Copy application files
COPY app.py main.py ./
COPY templates/ ./templates/

COPY .env ./

# Create necessary directories
RUN mkdir -p uploads web_processed logs /tmp/numba_cache

# Note: Container will run as host user (1000:1000) via docker-compose.yml
# This ensures proper permissions for mounted volumes

# Expose port (Gunicorn default)
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Set environment variables
ENV FLASK_APP=app.py
ENV FLASK_ENV=production

# Run with Gunicorn (production WSGI server)
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "app:app"]