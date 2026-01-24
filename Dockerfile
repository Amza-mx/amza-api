# Use Python 3.13 (matches project requirement: requires-python = ">=3.13")
FROM python:3.13-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8000 \
    PYTHONPATH=/app/src

# Set working directory
WORKDIR /app

# Copy dependency files
COPY etc/requirements/ ./etc/requirements/

# Install production dependencies with pip
RUN pip install --no-cache-dir -r etc/requirements/prod.txt

# Copy application code
COPY . .

# Set execute permissions on entrypoint (after copying all files)
RUN chmod +x /app/entrypoint.sh

# Change to src directory where manage.py is located
WORKDIR /app/src

# Expose port
EXPOSE 8000

# Use entrypoint script with sh to ensure execution
CMD ["sh", "/app/entrypoint.sh"]
