FROM python:3.11.10-slim

# Set environment variables for Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=5000

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Copy Python dependencies
COPY pyproject.toml ./
RUN pip install --no-cache-dir -e .

# Copy application code
COPY . .

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash app
RUN chown -R app:app /app
USER app

# Expose port
EXPOSE $PORT

# Run the application with optimized settings for Heroku
CMD gunicorn --bind 0.0.0.0:$PORT --workers 4 --threads 16 --timeout 120 --keep-alive 10 --max-requests 2000 --max-requests-jitter 200 --worker-class sync --worker-connections 1000 --preload main:app