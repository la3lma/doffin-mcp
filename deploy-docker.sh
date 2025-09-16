#!/bin/bash

# doffin-mcp Docker Deployment Script
# This script helps you deploy the doffin-mcp server using Docker

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check Docker setup
check_docker() {
    if ! command_exists docker; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! docker info >/dev/null 2>&1; then
        print_error "Docker daemon is not running. Please start Docker."
        exit 1
    fi
    
    print_success "Docker is available and running"
}

# Function to build the Docker image
build_image() {
    print_status "Building doffin-mcp Docker image..."
    
    if docker build -t doffin-mcp:latest .; then
        print_success "Docker image built successfully"
    else
        print_error "Failed to build Docker image"
        exit 1
    fi
}

# Function to test the image
test_image() {
    print_status "Testing the Docker image..."
    
    if docker run --rm doffin-mcp:latest python -c "import mcp_doffin; print('MCP server test successful')"; then
        print_success "Docker image test passed"
    else
        print_error "Docker image test failed"
        exit 1
    fi
}

# Function to start with docker compose
start_compose() {
    print_status "Starting doffin-mcp with Docker Compose..."
    
    if command_exists docker-compose; then
        COMPOSE_CMD="docker-compose"
    elif docker compose version >/dev/null 2>&1; then
        COMPOSE_CMD="docker compose"
    else
        print_error "Docker Compose is not available"
        exit 1
    fi
    
    if $COMPOSE_CMD up --build -d; then
        print_success "doffin-mcp service started successfully"
        print_status "View logs with: $COMPOSE_CMD logs -f doffin-mcp"
        print_status "Stop service with: $COMPOSE_CMD down"
    else
        print_error "Failed to start doffin-mcp service"
        exit 1
    fi
}

# Function to stop compose services
stop_compose() {
    print_status "Stopping doffin-mcp services..."
    
    if command_exists docker-compose; then
        COMPOSE_CMD="docker-compose"
    elif docker compose version >/dev/null 2>&1; then
        COMPOSE_CMD="docker compose"
    else
        print_error "Docker Compose is not available"
        exit 1
    fi
    
    if $COMPOSE_CMD down; then
        print_success "doffin-mcp services stopped"
    else
        print_error "Failed to stop services"
        exit 1
    fi
}

# Function to show Claude Desktop configuration
show_claude_config() {
    print_status "Claude Desktop Configuration:"
    echo ""
    echo "Create or update ~/.claude/mcp-servers/doffin-docker.json:"
    echo ""
    cat << 'EOF'
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
EOF
    echo ""
    print_warning "Remember to restart Claude Desktop after updating the configuration!"
}

# Function to show usage
usage() {
    echo "Usage: $0 {build|test|start|stop|config|all|help}"
    echo ""
    echo "Commands:"
    echo "  build   - Build the Docker image"
    echo "  test    - Test the built Docker image"
    echo "  start   - Start the service with Docker Compose"
    echo "  stop    - Stop the Docker Compose services"
    echo "  config  - Show Claude Desktop configuration"
    echo "  all     - Build, test, and start (recommended for first setup)"
    echo "  help    - Show this help message"
}

# Main script logic
case "${1:-help}" in
    build)
        check_docker
        build_image
        ;;
    test)
        check_docker
        test_image
        ;;
    start)
        check_docker
        start_compose
        ;;
    stop)
        check_docker
        stop_compose
        ;;
    config)
        show_claude_config
        ;;
    all)
        check_docker
        build_image
        test_image
        start_compose
        echo ""
        show_claude_config
        ;;
    help|--help|-h)
        usage
        ;;
    *)
        print_error "Unknown command: $1"
        echo ""
        usage
        exit 1
        ;;
esac