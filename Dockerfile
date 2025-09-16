# Use Python 3.12 slim base image for security and smaller size
FROM python:3.12-slim

# Set environment variables for Python optimization and UTF-8 support
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8

# Create a non-root user for security
RUN groupadd --gid 1000 mcpuser && \
    useradd --uid 1000 --gid 1000 --create-home --shell /bin/bash mcpuser

# Set working directory
WORKDIR /app

# Install system dependencies (minimal set)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        ca-certificates \
        curl \
    && rm -rf /var/lib/apt/lists/* && \
    update-ca-certificates

# Copy requirements first to leverage Docker layer caching
COPY mcp-doffin/requirements.txt ./

# Install Python dependencies with trusted hosts for SSL issues
RUN pip install --no-cache-dir --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org -r requirements.txt

# Copy application code
COPY mcp-doffin/ ./

# Change ownership of application files to non-root user
RUN chown -R mcpuser:mcpuser /app

# Switch to non-root user
USER mcpuser

# Expose port (not strictly necessary for stdio MCP, but good practice)
EXPOSE 8000

# Default command to run the MCP server
CMD ["python", "mcp_doffin.py"]