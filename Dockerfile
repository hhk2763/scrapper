# Dockerfile for Shipping Intelligence API
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY database_schema.sql .
COPY database_manager.py .
COPY data_ingestion.py .
COPY api_server.py .
COPY analytics.py .
COPY shipping_intelligence.db .

# Expose API port
EXPOSE 5000

# Set environment variables
ENV FLASK_APP=api_server.py
ENV FLASK_ENV=production

# Run the API server
CMD ["python", "api_server.py"]
