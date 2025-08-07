# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Build args for secrets (will be passed from Cloud Build)
ARG SECRET_MANAGER_KEY
ARG GCP_PROJECT_ID
ARG GCS_BUCKET_NAME

# Set environment variables
ENV SECRET_MANAGER_KEY=${SECRET_MANAGER_KEY}
ENV GCP_PROJECT_ID=${GCP_PROJECT_ID}
ENV GCS_BUCKET_NAME=${GCS_BUCKET_NAME}
ENV FLASK_APP=app.py
ENV FLASK_ENV=production
ENV PORT=8080

# Expose port
EXPOSE 8080

# Create a non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Run the application
CMD ["python", "-m", "gunicorn", "--bind", "0.0.0.0:8080", "--workers", "2", "--timeout", "120", "app:app"] 
