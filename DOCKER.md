# Docker Deployment Guide for doffin-mcp

This guide explains how to run the doffin-mcp server in a secure Docker environment to address security concerns about running it as your user account.

## Overview

The Docker setup provides:
- **Security**: Runs with a non-root user (`mcpuser`) inside the container
- **Isolation**: Network and filesystem isolation from the host system
- **Resource limits**: CPU and memory constraints to prevent resource exhaustion
- **Read-only filesystem**: Container runs with read-only root filesystem for added security
- **Easy deployment**: Simple commands to build and run

## Quick Start

### 1. Build and Run with Docker

```bash
# Build the Docker image
docker build -t doffin-mcp:latest .

# Run the container (stdio mode for MCP communication)
docker run --rm -i --name doffin-mcp-stdio doffin-mcp:latest
```

### 2. Build and Run with Docker Compose (Recommended)

```bash
# Build and start the service
docker compose up --build -d

# View logs
docker compose logs -f doffin-mcp

# Stop the service
docker compose down
```

### 3. Testing the Setup

```bash
# Test that the container works
docker run --rm doffin-mcp:latest python -c "import mcp_doffin; print('OK')"

# Test with docker compose
docker compose run --rm doffin-mcp python -c "import mcp_doffin; print('OK')"
```

## Claude Desktop Integration

To use the dockerized MCP server with Claude Desktop, you have several options:

### Option 1: Docker with stdio (Recommended)

Create or update `~/.claude/mcp-servers/doffin-docker.json`:

```json
{
  "command": "docker",
  "args": [
    "run", 
    "--rm", 
    "--interactive",
    "--name", "doffin-mcp-stdio",
    "doffin-mcp:latest"
  ],
  "env": {
    "NO_COLOR": "1"
  }
}
```

### Option 2: Docker Compose

Create or update `~/.claude/mcp-servers/doffin-compose.json`:

```json
{
  "command": "docker",
  "args": [
    "compose",
    "-f", "/absolute/path/to/doffin-mcp/docker-compose.yml",
    "run", 
    "--rm",
    "doffin-mcp"
  ],
  "env": {
    "NO_COLOR": "1"
  }
}
```

**Important**: Replace `/absolute/path/to/doffin-mcp/` with the actual path to your doffin-mcp directory.

### Option 3: Long-running Container

If you prefer to keep a container running:

```bash
# Start the container in the background
docker compose up -d

# Configure Claude Desktop to use the running container
```

Create `~/.claude/mcp-servers/doffin-persistent.json`:

```json
{
  "command": "docker",
  "args": [
    "exec",
    "-i",
    "doffin-mcp-server",
    "python", "mcp_doffin.py"
  ],
  "env": {
    "NO_COLOR": "1"
  }
}
```

## Security Features

The Docker setup includes several security measures:

1. **Non-root user**: Container runs as `mcpuser` (UID/GID 1000)
2. **Read-only filesystem**: Root filesystem is read-only
3. **No new privileges**: Prevents privilege escalation
4. **Resource limits**: CPU and memory constraints
5. **Network isolation**: Custom bridge network
6. **Minimal attack surface**: Only essential packages installed

## Configuration

### Environment Variables

You can customize the behavior using environment variables:

```yaml
# In docker-compose.yml
environment:
  - NO_COLOR=1
  - USER_AGENT=MCP-Doffin/1.0 (+your-contact@example.com)
```

Or with docker run:

```bash
docker run --rm -i -e NO_COLOR=1 -e USER_AGENT="Custom-Agent/1.0" doffin-mcp:latest
```

### Resource Limits

Adjust resource limits in `docker-compose.yml`:

```yaml
deploy:
  resources:
    limits:
      memory: 512M
      cpus: '0.5'
    reservations:
      memory: 256M
      cpus: '0.25'
```

## Troubleshooting

### Container won't start

```bash
# Check container logs
docker compose logs doffin-mcp

# Run container interactively for debugging
docker run --rm -it doffin-mcp:latest /bin/bash
```

### MCP connection issues with Claude Desktop

1. Ensure the container can be reached:
   ```bash
   docker run --rm doffin-mcp:latest python -c "import mcp_doffin; print('OK')"
   ```

2. Check that the correct path is specified in the Claude Desktop configuration

3. Verify Claude Desktop has restarted after configuration changes

### Performance issues

1. Increase resource limits in `docker-compose.yml`
2. Monitor resource usage:
   ```bash
   docker stats doffin-mcp-server
   ```

### SSL/Certificate issues

If you encounter SSL issues during build:

```bash
# Rebuild with no cache
docker build --no-cache -t doffin-mcp:latest .
```

The Dockerfile includes trusted host settings to handle common SSL issues.

## Maintenance

### Updating the container

```bash
# Pull latest code and rebuild
git pull
docker compose down
docker compose up --build -d
```

### Viewing logs

```bash
# Follow logs in real-time
docker compose logs -f doffin-mcp

# View recent logs
docker compose logs --tail=50 doffin-mcp
```

### Health checks

The container includes a health check that validates the MCP server can be imported:

```bash
# Check container health
docker compose ps
```

## Advanced Usage

### Custom network configuration

```yaml
# Custom network with specific subnet
networks:
  doffin-network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16
```

### Persistent logging

```yaml
# Add volume for logs
volumes:
  - ./logs:/app/logs:rw
```

### Development mode

For development, you can mount the source code:

```yaml
# In docker-compose.override.yml
services:
  doffin-mcp:
    volumes:
      - ./mcp-doffin:/app:ro
```

## Comparison with Direct Installation

| Aspect | Direct Installation | Docker |
|--------|-------------------|---------|
| Security | Runs as your user | Runs as isolated user |
| Isolation | None | Full container isolation |
| Dependencies | System-wide | Container-only |
| Resource control | Limited | Full control |
| Portability | OS-dependent | Cross-platform |
| Complexity | Simple | Moderate |

The Docker approach provides significantly better security isolation while maintaining the same functionality.