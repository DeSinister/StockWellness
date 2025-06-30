#!/bin/bash

# StockWellness Docker Management Script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if .env file exists
check_env_file() {
    if [ ! -f ".env" ]; then
        print_warning ".env file not found. Creating from template..."
        cp env_template.txt .env
        print_warning "Please edit .env file with your API keys before running the application!"
        return 1
    fi
    return 0
}

# Build Docker image
build_image() {
    print_status "Building StockWellness Docker image..."
    docker build -t stockwellness:latest .
    print_status "Image built successfully!"
}

# Run container with docker-compose
run_compose() {
    check_env_file
    print_status "Starting StockWellness with docker-compose..."
    docker-compose up -d
    print_status "Application started! Access it at http://localhost:5000"
    print_status "Use 'docker-compose logs -f' to view logs"
}

# Run container directly
run_direct() {
    check_env_file
    print_status "Starting StockWellness container..."
    docker run -d \
        --name stockwellness \
        -p 5000:5000 \
        --env-file .env \
        -v "$(pwd)/cache:/app/cache" \
        stockwellness:latest
    print_status "Container started! Access it at http://localhost:5000"
}

# Stop and remove containers
stop() {
    print_status "Stopping StockWellness..."
    docker-compose down 2>/dev/null || true
    docker stop stockwellness 2>/dev/null || true
    docker rm stockwellness 2>/dev/null || true
    print_status "Stopped."
}

# Show usage
usage() {
    echo "Usage: $0 {build|run|compose|stop|logs}"
    echo ""
    echo "Commands:"
    echo "  build   - Build the Docker image"
    echo "  run     - Run container directly"
    echo "  compose - Run with docker-compose (recommended)"
    echo "  stop    - Stop and remove containers"
    echo "  logs    - Show application logs"
    echo ""
}

# Show logs
show_logs() {
    if docker-compose ps stockwellness >/dev/null 2>&1; then
        docker-compose logs -f stockwellness
    elif docker ps --filter "name=stockwellness" --format "table {{.Names}}" | grep -q stockwellness; then
        docker logs -f stockwellness
    else
        print_error "No running StockWellness container found"
        exit 1
    fi
}

# Main script logic
case "$1" in
    build)
        build_image
        ;;
    run)
        build_image
        run_direct
        ;;
    compose)
        build_image
        run_compose
        ;;
    stop)
        stop
        ;;
    logs)
        show_logs
        ;;
    *)
        usage
        exit 1
        ;;
esac 