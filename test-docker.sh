#!/bin/bash

echo "======================================"
echo "Testing Docker Build"
echo "======================================"
echo ""

cd "$(dirname "$0")/backend"

echo "[1/3] Building Docker image..."
docker build -t interview-video-generator:test .

if [ $? -ne 0 ]; then
    echo "❌ Docker build failed!"
    exit 1
fi

echo ""
echo "[2/3] Verifying FFmpeg installation in image..."
docker run --rm interview-video-generator:test ffmpeg -version

if [ $? -ne 0 ]; then
    echo "❌ FFmpeg not found in Docker image!"
    exit 1
fi

echo ""
echo "[3/3] Checking Python packages..."
docker run --rm interview-video-generator:test pip list | grep -E "(fastapi|pymongo|openai)"

echo ""
echo "======================================"
echo "✅ Docker build test completed successfully!"
echo "======================================"
echo ""
echo "To run the container:"
echo "  docker-compose up -d"
echo ""
echo "To clean up test image:"
echo "  docker rmi interview-video-generator:test"
