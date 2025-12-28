FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Set Python path to include backend root for agent imports
ENV PYTHONPATH=/app:$PYTHONPATH

# Create non-root user for security
RUN useradd -m -u 1000 user
USER user

# Expose port (HuggingFace Spaces uses 7860)
EXPOSE 7860

# Run application
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "7860"]
