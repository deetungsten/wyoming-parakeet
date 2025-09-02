#!/bin/bash
set -e

echo "Building Wyoming Parakeet for Jetson Orin Nano..."

# Create directories if they don't exist
mkdir -p data cache

# Build the Docker image
echo "Building Docker image..."
docker build -f Dockerfile.jetson -t wyoming-parakeet:jetson .

# Check if build was successful
if [ $? -eq 0 ]; then
    echo "✅ Build successful!"
    echo ""
    echo "To run the container:"
    echo "  docker-compose -f docker-compose.jetson.yml up -d"
    echo ""
    echo "To view logs:"
    echo "  docker-compose -f docker-compose.jetson.yml logs -f"
    echo ""
    echo "To stop:"
    echo "  docker-compose -f docker-compose.jetson.yml down"
    echo ""
    echo "The server will be available at tcp://localhost:10300"
else
    echo "❌ Build failed!"
    exit 1
fi