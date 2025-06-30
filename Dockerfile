# Use Python 3.11 slim image for better performance
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    wget \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_APP=app.py \
    FLASK_ENV=production \
    FLASK_RUN_HOST=0.0.0.0 \
    FLASK_RUN_PORT=5000

# Copy requirements first for better Docker layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Create necessary directories
RUN mkdir -p /app/cache/rag \
    && mkdir -p /app/static \
    && mkdir -p /app/templates \
    && mkdir -p /app/utils \
    && mkdir -p /app/Books

# Copy application files
COPY app.py .
COPY env_template.txt .

# Copy utility modules
COPY utils/ ./utils/

# Copy static files and templates
COPY static/ ./static/
COPY templates/ ./templates/

# Copy investment books
COPY Books/ ./Books/

# Create a non-root user for security
RUN useradd --create-home --shell /bin/bash appuser && \
    chown -R appuser:appuser /app
USER appuser

# Expose port 5000
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Command to run the application
CMD ["python", "app.py"] 