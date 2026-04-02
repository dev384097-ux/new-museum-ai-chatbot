# Use official Python image as a parent image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libjpeg-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download NLTK data (optional, but good practice if needed)
# RUN python -m nltk.downloader punkt

# Copy project files
COPY . .

# Create data directory if it doesn't exist
RUN mkdir -p data

# Expose the port the app runs on
EXPOSE 5000

# Healthcheck to monitor app status
HEALTHCHECK --interval=30s --timeout=3s \
  CMD curl -f http://localhost:5000/ || exit 1

# Start Gunicorn with the dedicated config file
CMD ["gunicorn", "--config", "gunicorn_config.py", "app:app"]
