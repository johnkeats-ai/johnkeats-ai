# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV GOOGLE_GENAI_USE_VERTEXAI TRUE
ENV GOOGLE_CLOUD_PROJECT johnkeats-ai
ENV GOOGLE_CLOUD_LOCATION us-central1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY backend/app/pyproject.toml .
# Create placeholder directories to satisfy setuptools during dependency resolution
RUN mkdir keats_agent tools && touch keats_agent/__init__.py tools/__init__.py
RUN pip install --no-cache-dir .

# Copy project
COPY backend/app/ .
# Re-install project code with actual content
RUN pip install --no-cache-dir .

# Expose port
EXPOSE 8080

# Command to run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
