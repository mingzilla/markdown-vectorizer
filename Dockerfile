FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install specific versions to ensure compatibility in the correct order
RUN pip install --no-cache-dir huggingface_hub==0.12.0
RUN pip install --no-cache-dir sentence-transformers==2.2.2
RUN pip install --no-cache-dir langchain==0.0.266
RUN pip install --no-cache-dir llama-index==0.8.4
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY vectorizer.py .
COPY utils.py .
COPY api.py .
COPY entrypoint.sh .

# Create necessary directories
RUN mkdir -p /volumes/input /volumes/index /volumes/models

# Set permissions
RUN chmod -R 777 /volumes
RUN chmod +x /app/entrypoint.sh

# Set env variables
ENV FLASK_APP=api.py
ENV PYTHONUNBUFFERED=1
ENV TRANSFORMERS_CACHE=/volumes/models
ENV HF_HOME=/volumes/models

# Expose port for API
EXPOSE 5000

# Use entrypoint script
CMD ["/app/entrypoint.sh"]