FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && \
    apt-get install -y gcc g++ curl && \
    pip install --upgrade pip && \
    rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy your app
COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Set env vars
ENV FLASK_ENV=production
ENV FLASK_APP=app.py
ENV PYTHONUNBUFFERED=1

# Expose the port Flask runs on (Render uses PORT env var)
EXPOSE $PORT

# Run with Gunicorn for production (Render-optimized)
CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 300 --max-requests 1000 --max-requests-jitter 100 app:app"] 