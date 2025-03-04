#!/bin/bash

echo "Building md-vectorizer Docker image..."
# Using --no-cache to ensure fresh dependencies
docker-compose build

echo "Build complete!"