#!/bin/bash

echo "Building md-vectorizer Docker image..."
# Build with explicit image name to ensure consistency
docker build -t md-vectorizer .

echo "Build complete!"
echo "Image name: md-vectorizer"