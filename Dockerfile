FROM python:3.11-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose default local port (Railway will provide $PORT in production)
EXPOSE 8000

# Use $PORT if provided by platform (e.g., Railway), fallback to 8000
ENV PORT=8000

# Run the application using shell form to expand $PORT variable
CMD uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}

